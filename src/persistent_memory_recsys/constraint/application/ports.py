from collections.abc import Sequence
from typing import Protocol

from persistent_memory_recsys.constraint.domain.models import (
    ConstraintCandidate,
    ConstraintDecodingResult,
    ConstraintProfile,
    StaticIndexSummary,
)
from persistent_memory_recsys.memory.domain.models import MemorySnapshot
from persistent_memory_recsys.preference.domain.models import PreferenceState


class ConstraintProfileBuilder(Protocol):
    def build_home_profile(
        self,
        user_id: str,
        *,
        memory_snapshot: MemorySnapshot | None = None,
        preference_state: PreferenceState | None = None,
    ) -> ConstraintProfile:
        """Build a home-surface constraint profile."""


class ConstraintDecoder(Protocol):
    def decode(
        self,
        candidates: Sequence[ConstraintCandidate],
        constraint_profile: ConstraintProfile,
    ) -> ConstraintDecodingResult:
        """Run constrained decoding and return the selected candidates."""


class StaticIndexManager(Protocol):
    def describe_active_index(self) -> StaticIndexSummary:
        """Return metadata for the active STATIC index snapshot."""

    def rebuild_active_index(self) -> StaticIndexSummary:
        """Rebuild the active STATIC index snapshot."""
