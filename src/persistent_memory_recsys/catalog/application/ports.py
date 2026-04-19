from collections.abc import Sequence
from typing import Protocol

from persistent_memory_recsys.catalog.domain.models import CatalogItem, ItemSemanticMapping


class CatalogReader(Protocol):
    def list_active_items(self) -> Sequence[CatalogItem]:
        """Return active catalog items."""

    def list_semantic_mappings(self) -> Sequence[ItemSemanticMapping]:
        """Return active semantic mappings."""

    def get_active_semantic_version(self) -> str:
        """Return the active semantic version."""


class SemanticMappingWriter(Protocol):
    def replace_semantic_mappings(
        self,
        mappings: Sequence[ItemSemanticMapping],
        *,
        semantic_version: str,
    ) -> None:
        """Replace active semantic mappings."""


class SemanticIdAssigner(Protocol):
    def assign(
        self,
        items: Sequence[CatalogItem],
        *,
        semantic_version: str,
    ) -> Sequence[ItemSemanticMapping]:
        """Assign semantic IDs to catalog items."""
