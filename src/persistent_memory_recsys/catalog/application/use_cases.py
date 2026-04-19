from dataclasses import asdict, dataclass

from persistent_memory_recsys.catalog.application.ports import (
    CatalogReader,
    SemanticIdAssigner,
    SemanticMappingWriter,
)


@dataclass(slots=True)
class ListActiveSemanticMappingsUseCase:
    catalog_reader: CatalogReader

    def execute(self) -> dict[str, object]:
        mappings = tuple(self.catalog_reader.list_semantic_mappings())
        return {
            "semantic_version": self.catalog_reader.get_active_semantic_version(),
            "count": len(mappings),
            "mappings": [asdict(mapping) for mapping in mappings],
        }


@dataclass(slots=True)
class RegenerateSemanticMappingsUseCase:
    catalog_reader: CatalogReader
    semantic_mapping_writer: SemanticMappingWriter
    semantic_id_assigner: SemanticIdAssigner

    def execute(self, *, semantic_version: str = "sid_v1") -> dict[str, object]:
        active_items = tuple(self.catalog_reader.list_active_items())
        mappings = tuple(
            self.semantic_id_assigner.assign(
                active_items,
                semantic_version=semantic_version,
            )
        )
        self.semantic_mapping_writer.replace_semantic_mappings(
            mappings,
            semantic_version=semantic_version,
        )
        return {
            "semantic_version": semantic_version,
            "item_count": len(active_items),
            "mapping_count": len(mappings),
        }
