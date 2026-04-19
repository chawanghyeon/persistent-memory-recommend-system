from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ConstraintProfile:
    user_id: str
    allowed_inventory_statuses: tuple[str, ...] = ("in_stock",)
    blocked_brands: tuple[str, ...] = ()
    blocked_categories: tuple[str, ...] = ()
    required_sizes: tuple[str, ...] = ()
    max_items: int = 3
    soft_constraints: dict[str, int] = field(default_factory=dict)
    policy_version: str = "policy_v1"

    @property
    def hard_constraints_applied(self) -> tuple[str, ...]:
        applied: list[str] = []

        if self.allowed_inventory_statuses:
            applied.append("allowed_inventory_statuses")
        if self.blocked_brands:
            applied.append("blocked_brands")
        if self.blocked_categories:
            applied.append("blocked_categories")
        if self.required_sizes:
            applied.append("required_sizes")

        return tuple(applied)


@dataclass(frozen=True, slots=True)
class ConstraintCandidate:
    item_id: str
    semantic_id: str
    brand: str
    category: str
    inventory_status: str
    size_options: tuple[str, ...] = ()
    ranking_score: float = 0.0


@dataclass(frozen=True, slots=True)
class StaticIndexSummary:
    static_index_version: str
    semantic_version: str
    item_count: int
    semantic_id_length: int
    vocab_size: int
    dense_lookup_layers: int
    layer_max_branches: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class ConstraintReport:
    hard_constraints_applied: tuple[str, ...] = ()
    soft_constraints_relaxed: tuple[str, ...] = ()
    decoder_status: str = "not_started"
    candidate_count: int = 0
    accepted_count: int = 0
    rejected_count: int = 0
    static_index: StaticIndexSummary | None = None


@dataclass(frozen=True, slots=True)
class ConstraintDecodingResult:
    recommended_item_ids: tuple[str, ...] = ()
    semantic_ids: tuple[str, ...] = ()
    report: ConstraintReport = field(default_factory=ConstraintReport)
