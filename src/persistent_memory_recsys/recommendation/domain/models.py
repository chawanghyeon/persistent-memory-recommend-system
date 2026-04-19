from dataclasses import dataclass, field

from persistent_memory_recsys.constraint.domain.models import ConstraintReport
from persistent_memory_recsys.memory.domain.models import MemorySnapshot
from persistent_memory_recsys.preference.domain.models import PreferenceState


@dataclass(frozen=True, slots=True)
class RecommendationReadiness:
    orchestration: str
    memory_integration: str
    constraint_integration: str
    next_step: str


@dataclass(frozen=True, slots=True)
class HomeRecommendation:
    request_id: str
    user_id: str
    surface_type: str
    recommended_item_ids: tuple[str, ...] = ()
    semantic_ids: tuple[str, ...] = ()
    memory_snapshot: MemorySnapshot | None = None
    preference_state: PreferenceState | None = None
    constraint_report: ConstraintReport | None = None
    readiness: RecommendationReadiness | None = None
    metadata: dict[str, object] = field(default_factory=dict)
