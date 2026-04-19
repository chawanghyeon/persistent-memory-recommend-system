from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class UserEventType(StrEnum):
    IMPRESSION = "impression"
    PRODUCT_CLICK = "product_click"
    DETAIL_VIEW = "detail_view"
    SAVE = "save"
    CART_ADD = "cart_add"
    PURCHASE = "purchase"
    HIDE = "hide"
    DISLIKE = "dislike"
    FILTER_APPLY = "filter_apply"
    PREFERENCE_EDIT = "preference_edit"


@dataclass(frozen=True, slots=True)
class UserEvent:
    event_id: str
    user_id: str
    event_type: UserEventType
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    session_id: str | None = None
    item_id: str | None = None
    surface_type: str | None = None
    properties: dict[str, object] = field(default_factory=dict)
