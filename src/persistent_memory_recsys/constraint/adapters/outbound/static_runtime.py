from __future__ import annotations

from dataclasses import dataclass
from itertools import groupby

from persistent_memory_recsys.constraint.domain.models import StaticIndexSummary


def semantic_id_to_tokens(semantic_id: str) -> tuple[int, ...]:
    tokens: list[int] = []

    for raw_token in semantic_id.split():
        suffix = raw_token.rsplit("_", maxsplit=1)[-1]
        tokens.append(int(suffix))

    if not tokens:
        msg = "semantic_id must contain at least one token"
        raise ValueError(msg)

    return tuple(tokens)


@dataclass(frozen=True, slots=True)
class CompiledStaticIndex:
    summary: StaticIndexSummary
    packed_csr: tuple[tuple[int, int], ...]
    csr_indptr: tuple[int, ...]
    start_mask: tuple[bool, ...]
    dense_mask: tuple[tuple[bool, ...], ...]
    dense_states: tuple[tuple[int, ...], ...]

    def contains(self, semantic_id: str) -> bool:
        tokens = semantic_id_to_tokens(semantic_id)

        if len(tokens) != self.summary.semantic_id_length:
            return False

        if self.summary.semantic_id_length < self.summary.dense_lookup_layers:
            return False

        first_token = tokens[0]
        if first_token >= self.summary.vocab_size or not self.start_mask[first_token]:
            return False

        second_token = tokens[1]
        if second_token >= self.summary.vocab_size:
            return False

        if not self.dense_mask[first_token][second_token]:
            return False

        state = self.dense_states[first_token][second_token]

        for token in tokens[self.summary.dense_lookup_layers :]:
            if state + 1 >= len(self.csr_indptr):
                return False

            start = self.csr_indptr[state]
            end = self.csr_indptr[state + 1]
            next_state = _find_transition(self.packed_csr[start:end], token)

            if next_state is None:
                return False

            state = next_state

        return state == 0


def build_compiled_static_index(
    semantic_ids: tuple[str, ...],
    *,
    semantic_version: str,
    static_index_version: str,
) -> CompiledStaticIndex:
    if not semantic_ids:
        return CompiledStaticIndex(
            summary=StaticIndexSummary(
                static_index_version=static_index_version,
                semantic_version=semantic_version,
                item_count=0,
                semantic_id_length=0,
                vocab_size=0,
                dense_lookup_layers=2,
                layer_max_branches=(),
            ),
            packed_csr=(),
            csr_indptr=(0, 0),
            start_mask=(),
            dense_mask=(),
            dense_states=(),
        )

    token_sequences = tuple(sorted({semantic_id_to_tokens(value) for value in semantic_ids}))
    semantic_id_length = len(token_sequences[0])

    if any(len(sequence) != semantic_id_length for sequence in token_sequences):
        msg = "all semantic IDs must have the same length"
        raise ValueError(msg)

    if semantic_id_length < 2:
        msg = "STATIC preview adapter currently expects semantic IDs with at least 2 tokens"
        raise ValueError(msg)

    vocab_size = max(max(sequence) for sequence in token_sequences) + 1
    prefix_state_ids = _assign_prefix_state_ids(token_sequences, vocab_size=vocab_size)
    transitions = _build_transitions(token_sequences, prefix_state_ids)
    packed_csr, csr_indptr = _build_csr(transitions, vocab_size=vocab_size)
    start_mask, dense_mask, dense_states = _build_dense_lookup(
        token_sequences,
        prefix_state_ids,
        vocab_size=vocab_size,
    )
    layer_max_branches = _calculate_layer_max_branches(token_sequences)

    return CompiledStaticIndex(
        summary=StaticIndexSummary(
            static_index_version=static_index_version,
            semantic_version=semantic_version,
            item_count=len(token_sequences),
            semantic_id_length=semantic_id_length,
            vocab_size=vocab_size,
            dense_lookup_layers=2,
            layer_max_branches=layer_max_branches,
        ),
        packed_csr=packed_csr,
        csr_indptr=csr_indptr,
        start_mask=start_mask,
        dense_mask=dense_mask,
        dense_states=dense_states,
    )


def _assign_prefix_state_ids(
    token_sequences: tuple[tuple[int, ...], ...],
    *,
    vocab_size: int,
) -> dict[tuple[int, ...], int]:
    state_ids: dict[tuple[int, ...], int] = {}
    next_state_id = vocab_size + 1

    first_tokens = sorted({sequence[0] for sequence in token_sequences})
    for token in first_tokens:
        state_ids[(token,)] = token + 1

    prefix_lengths = range(2, len(token_sequences[0]))
    for prefix_length in prefix_lengths:
        prefixes = sorted({sequence[:prefix_length] for sequence in token_sequences})
        for prefix in prefixes:
            state_ids[prefix] = next_state_id
            next_state_id += 1

    return state_ids


def _build_transitions(
    token_sequences: tuple[tuple[int, ...], ...],
    prefix_state_ids: dict[tuple[int, ...], int],
) -> tuple[tuple[int, int, int], ...]:
    transitions: set[tuple[int, int, int]] = set()
    semantic_id_length = len(token_sequences[0])

    for sequence in token_sequences:
        for depth in range(1, semantic_id_length):
            parent_prefix = sequence[:depth]
            parent_state = prefix_state_ids[parent_prefix]
            token = sequence[depth]

            if depth == semantic_id_length - 1:
                child_state = 0
            else:
                child_state = prefix_state_ids[sequence[: depth + 1]]

            transitions.add((parent_state, token, child_state))

    return tuple(sorted(transitions))


def _build_csr(
    transitions: tuple[tuple[int, int, int], ...],
    *,
    vocab_size: int,
) -> tuple[tuple[tuple[int, int], ...], tuple[int, ...]]:
    if not transitions:
        return (), (0, 0)

    max_state = max(parent_state for parent_state, _, _ in transitions)
    packed_rows: list[tuple[int, int]] = []
    indptr: list[int] = [0]
    transition_groups = {
        parent_state: tuple((token, child_state) for _, token, child_state in group)
        for parent_state, group in groupby(transitions, key=lambda row: row[0])
    }

    for state in range(max_state + 1):
        state_rows = transition_groups.get(state, ())
        packed_rows.extend(state_rows)
        indptr.append(len(packed_rows))

    packed_rows.extend((vocab_size, 0) for _ in range(vocab_size))
    indptr.append(len(packed_rows))

    return tuple(packed_rows), tuple(indptr)


def _build_dense_lookup(
    token_sequences: tuple[tuple[int, ...], ...],
    prefix_state_ids: dict[tuple[int, ...], int],
    *,
    vocab_size: int,
) -> tuple[tuple[bool, ...], tuple[tuple[bool, ...], ...], tuple[tuple[int, ...], ...]]:
    start_mask = [False] * vocab_size
    dense_mask = [[False] * vocab_size for _ in range(vocab_size)]
    dense_states = [[0] * vocab_size for _ in range(vocab_size)]

    for sequence in token_sequences:
        first_token, second_token = sequence[:2]
        start_mask[first_token] = True
        dense_mask[first_token][second_token] = True
        dense_states[first_token][second_token] = prefix_state_ids[(first_token, second_token)]

    return (
        tuple(start_mask),
        tuple(tuple(row) for row in dense_mask),
        tuple(tuple(row) for row in dense_states),
    )


def _calculate_layer_max_branches(
    token_sequences: tuple[tuple[int, ...], ...],
) -> tuple[int, ...]:
    semantic_id_length = len(token_sequences[0])
    layer_max_branches = [0] * semantic_id_length
    layer_max_branches[0] = len({sequence[0] for sequence in token_sequences})

    for prefix_length in range(1, semantic_id_length):
        grouped: dict[tuple[int, ...], set[int]] = {}

        for sequence in token_sequences:
            prefix = sequence[:prefix_length]
            next_token = sequence[prefix_length]
            grouped.setdefault(prefix, set()).add(next_token)

        layer_max_branches[prefix_length] = max(
            (len(tokens) for tokens in grouped.values()),
            default=0,
        )

    return tuple(layer_max_branches)


def _find_transition(
    transitions: tuple[tuple[int, int], ...],
    token: int,
) -> int | None:
    for edge_token, child_state in transitions:
        if edge_token == token:
            return child_state

    return None
