from dataclasses import dataclass

from persistent_memory_recsys.catalog.adapters.outbound.in_memory import (
    DeterministicSemanticIdAssigner,
    InMemoryCatalogStore,
)
from persistent_memory_recsys.catalog.application.ports import CatalogReader
from persistent_memory_recsys.catalog.application.use_cases import (
    ListActiveSemanticMappingsUseCase,
    RegenerateSemanticMappingsUseCase,
)
from persistent_memory_recsys.shared.domain.module_status import (
    ModuleReadiness,
    ModuleStatus,
)


@dataclass(slots=True)
class CatalogModule:
    catalog_reader: CatalogReader
    list_active_semantic_mappings_use_case: ListActiveSemanticMappingsUseCase
    regenerate_semantic_mappings_use_case: RegenerateSemanticMappingsUseCase
    status: ModuleStatus


def build_catalog_module() -> CatalogModule:
    catalog_store = InMemoryCatalogStore()
    semantic_id_assigner = DeterministicSemanticIdAssigner()
    regenerate_semantic_mappings_use_case = RegenerateSemanticMappingsUseCase(
        catalog_reader=catalog_store,
        semantic_mapping_writer=catalog_store,
        semantic_id_assigner=semantic_id_assigner,
    )
    regenerate_semantic_mappings_use_case.execute()

    return CatalogModule(
        catalog_reader=catalog_store,
        list_active_semantic_mappings_use_case=ListActiveSemanticMappingsUseCase(
            catalog_reader=catalog_store,
        ),
        regenerate_semantic_mappings_use_case=regenerate_semantic_mappings_use_case,
        status=ModuleStatus(
            bounded_context="catalog",
            description="카탈로그 상품, semantic ID, 트라이 메타데이터 경계.",
            readiness=ModuleReadiness.FOUNDATIONAL,
            next_step="인메모리 카탈로그 데이터를 영속성 기반 semantic registry 어댑터로 교체한다.",
        ),
    )
