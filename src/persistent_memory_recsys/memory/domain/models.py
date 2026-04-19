from dataclasses import dataclass, field
from enum import StrEnum


class MemoryType(StrEnum):
    FACT = "fact_memory"
    PREFERENCE = "preference_memory"
    NEGATIVE = "negative_memory"
    SESSION = "session_memory"
    TRAJECTORY = "trajectory_memory"


class MemoryStatus(StrEnum):
    CANDIDATE = "candidate"
    ACTIVE = "active"
    STALE = "stale"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"
    DELETED = "deleted"


@dataclass(frozen=True, slots=True)
class UserMemory:
    memory_id: str
    user_id: str
    memory_type: MemoryType
    status: MemoryStatus
    content_text: str
    content_json: dict[str, object] = field(default_factory=dict)
    topic_tags: tuple[str, ...] = ()
    confidence_score: float = 0.0
    importance_score: float = 0.0
    recency_score: float = 0.0


@dataclass(frozen=True, slots=True)
class MemorySnapshot:
    user_id: str
    active_memories: tuple[UserMemory, ...] = ()
    hard_blocks: dict[str, tuple[str, ...]] = field(default_factory=dict)
