from fastapi import APIRouter

from persistent_memory_recsys.catalog.application.use_cases import (
    ListActiveSemanticMappingsUseCase,
    RegenerateSemanticMappingsUseCase,
)


def build_catalog_router(
    list_active_semantic_mappings_use_case: ListActiveSemanticMappingsUseCase,
    regenerate_semantic_mappings_use_case: RegenerateSemanticMappingsUseCase,
) -> APIRouter:
    router = APIRouter(tags=["catalog"])

    @router.get("/catalog/semantic-mappings")
    def list_active_semantic_mappings() -> dict[str, object]:
        return list_active_semantic_mappings_use_case.execute()

    @router.post("/catalog/semantic-mappings/regenerate")
    def regenerate_semantic_mappings() -> dict[str, object]:
        return regenerate_semantic_mappings_use_case.execute()

    return router
