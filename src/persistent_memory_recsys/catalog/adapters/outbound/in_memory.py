from collections.abc import Sequence

from persistent_memory_recsys.catalog.application.ports import (
    CatalogReader,
    SemanticIdAssigner,
    SemanticMappingWriter,
)
from persistent_memory_recsys.catalog.domain.models import CatalogItem, ItemSemanticMapping


class InMemoryCatalogStore(CatalogReader, SemanticMappingWriter):
    def __init__(self) -> None:
        self._items = (
            CatalogItem(
                item_id="item-utility-jacket",
                title="Utility Short Jacket",
                brand="BrandA",
                category="outerwear",
                price_bucket="mid",
                inventory_status="in_stock",
                style_tags=("minimal", "utility"),
                color_tags=("black",),
                size_options=("S", "M", "L"),
            ),
            CatalogItem(
                item_id="item-light-cardigan",
                title="Light Cardigan",
                brand="BrandB",
                category="outerwear",
                price_bucket="mid",
                inventory_status="in_stock",
                style_tags=("minimal", "casual"),
                color_tags=("charcoal",),
                size_options=("M", "L"),
            ),
            CatalogItem(
                item_id="item-wide-denim",
                title="Wide Denim Pants",
                brand="BrandC",
                category="bottoms",
                price_bucket="mid",
                inventory_status="in_stock",
                style_tags=("casual",),
                color_tags=("blue",),
                size_options=("M", "L"),
            ),
            CatalogItem(
                item_id="item-formal-derby",
                title="Formal Derby Shoes",
                brand="BrandX",
                category="formal_shoes",
                price_bucket="mid",
                inventory_status="in_stock",
                style_tags=("formal",),
                color_tags=("black",),
                size_options=("270", "280"),
            ),
            CatalogItem(
                item_id="item-graphic-tee",
                title="Graphic Tee",
                brand="BrandA",
                category="tops",
                price_bucket="low",
                inventory_status="out_of_stock",
                style_tags=("street",),
                color_tags=("white",),
                size_options=("M", "L"),
            ),
        )
        self._semantic_mappings: tuple[ItemSemanticMapping, ...] = ()
        self._active_semantic_version = "sid_v0"

    def list_active_items(self) -> Sequence[CatalogItem]:
        return tuple(item for item in self._items if item.is_active)

    def list_semantic_mappings(self) -> Sequence[ItemSemanticMapping]:
        return self._semantic_mappings

    def get_active_semantic_version(self) -> str:
        return self._active_semantic_version

    def replace_semantic_mappings(
        self,
        mappings: Sequence[ItemSemanticMapping],
        *,
        semantic_version: str,
    ) -> None:
        self._semantic_mappings = tuple(mappings)
        self._active_semantic_version = semantic_version


class DeterministicSemanticIdAssigner(SemanticIdAssigner):
    def assign(
        self,
        items: Sequence[CatalogItem],
        *,
        semantic_version: str,
    ) -> Sequence[ItemSemanticMapping]:
        category_map = {
            category: index
            for index, category in enumerate(
                sorted({item.category for item in items}),
                start=1,
            )
        }
        brand_map = {
            brand: index
            for index, brand in enumerate(
                sorted({item.brand for item in items}),
                start=1,
            )
        }
        descriptor_map = {
            descriptor: index
            for index, descriptor in enumerate(
                sorted(
                    {
                        self._build_descriptor(item)
                        for item in items
                    }
                ),
                start=1,
            )
        }
        item_rank_map = {
            item_id: index
            for index, item_id in enumerate(
                sorted(item.item_id for item in items),
                start=1,
            )
        }

        mappings = []
        for item in items:
            descriptor = self._build_descriptor(item)
            semantic_id = " ".join(
                (
                    f"sid_{category_map[item.category]}",
                    f"sid_{brand_map[item.brand]}",
                    f"sid_{descriptor_map[descriptor]}",
                    f"sid_{item_rank_map[item.item_id]}",
                )
            )
            mappings.append(
                ItemSemanticMapping(
                    item_id=item.item_id,
                    semantic_id=semantic_id,
                    semantic_version=semantic_version,
                )
            )

        return tuple(mappings)

    def _build_descriptor(self, item: CatalogItem) -> tuple[str, str, str]:
        primary_style = item.style_tags[0] if item.style_tags else "none"
        primary_color = item.color_tags[0] if item.color_tags else "none"
        return (primary_style, primary_color, item.price_bucket)
