from fastapi import APIRouter

from persistent_memory_recsys.constraint.application.use_cases import (
    GetActiveStaticIndexUseCase,
    RebuildActiveStaticIndexUseCase,
)


def build_constraint_router(
    active_static_index_use_case: GetActiveStaticIndexUseCase,
    rebuild_active_static_index_use_case: RebuildActiveStaticIndexUseCase,
) -> APIRouter:
    router = APIRouter(tags=["constraint"])

    @router.get("/constraints/static-index")
    def get_active_static_index() -> dict[str, object]:
        return active_static_index_use_case.execute()

    @router.post("/constraints/static-index/rebuild")
    def rebuild_active_static_index() -> dict[str, object]:
        return rebuild_active_static_index_use_case.execute()

    return router
