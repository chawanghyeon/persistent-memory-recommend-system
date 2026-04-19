from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CatalogItem:
    item_id: str
    title: str
    brand: str
    category: str
    price_bucket: str
    inventory_status: str = "unknown"
    style_tags: tuple[str, ...] = ()
    color_tags: tuple[str, ...] = ()
    size_options: tuple[str, ...] = ()
    policy_flags: tuple[str, ...] = ()
    is_active: bool = True
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ItemSemanticMapping:
    item_id: str
    semantic_id: str
    semantic_version: str
    is_active: bool = True
