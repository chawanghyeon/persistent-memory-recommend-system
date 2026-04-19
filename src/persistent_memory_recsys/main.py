from fastapi import FastAPI

from persistent_memory_recsys.bootstrap.container import build_container
from persistent_memory_recsys.catalog.adapters.inbound.http import build_catalog_router
from persistent_memory_recsys.constraint.adapters.inbound.http import (
    build_constraint_router,
)
from persistent_memory_recsys.recommendation.adapters.inbound.http import (
    build_recommendation_router,
)
from persistent_memory_recsys.shared.adapters.inbound.http import build_system_router


container = build_container()


def create_app() -> FastAPI:
    app = FastAPI(
        title="장기기억 기반 추천 시스템",
        description="DDD 기반 모듈형 모놀리스 구조의 장기기억 생성형 추천 백엔드.",
        version="0.1.0",
    )
    app.include_router(build_system_router(container.system_status), prefix="/api/v1")
    app.include_router(
        build_catalog_router(
            container.catalog.list_active_semantic_mappings_use_case,
            container.catalog.regenerate_semantic_mappings_use_case,
        ),
        prefix="/api/v1",
    )
    app.include_router(
        build_constraint_router(
            container.constraint.active_static_index_use_case,
            container.constraint.rebuild_active_static_index_use_case,
        ),
        prefix="/api/v1",
    )
    app.include_router(
        build_recommendation_router(container.recommendation.home_preview_use_case),
        prefix="/api/v1",
    )
    return app


app = create_app()
