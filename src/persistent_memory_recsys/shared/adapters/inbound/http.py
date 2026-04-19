from fastapi import APIRouter

from persistent_memory_recsys.shared.domain.module_status import SystemStatus


def build_system_router(system_status: SystemStatus) -> APIRouter:
    router = APIRouter(tags=["system"])

    @router.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/system/status")
    def get_system_status() -> dict[str, object]:
        return system_status.as_dict()

    return router
