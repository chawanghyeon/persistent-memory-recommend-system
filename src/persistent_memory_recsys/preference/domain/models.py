from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PreferenceState:
    user_id: str
    likes: tuple[str, ...] = ()
    dislikes: tuple[str, ...] = ()
    preferred_categories: tuple[str, ...] = ()
    blocked_brands: tuple[str, ...] = ()
    blocked_categories: tuple[str, ...] = ()
    price_sensitivity: str = "unknown"
    exploration_tolerance: int = 0
    recent_shift: str | None = None
    state_confidence: float = 0.0
    text_summary: str = ""
    extra_attributes: dict[str, object] = field(default_factory=dict)
