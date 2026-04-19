from dataclasses import dataclass

from persistent_memory_recsys.catalog.module import CatalogModule
from persistent_memory_recsys.constraint.adapters.outbound.in_memory import (
    InMemoryConstraintProfileBuilder,
    InMemoryStaticConstraintDecoder,
    InMemoryStaticIndexStore,
)
from persistent_memory_recsys.constraint.application.ports import (
    ConstraintDecoder,
    ConstraintProfileBuilder,
    StaticIndexManager,
)
from persistent_memory_recsys.constraint.application.use_cases import (
    GetActiveStaticIndexUseCase,
    RebuildActiveStaticIndexUseCase,
)
from persistent_memory_recsys.shared.domain.module_status import (
    ModuleReadiness,
    ModuleStatus,
)


@dataclass(slots=True)
class ConstraintModule:
    constraint_profile_builder: ConstraintProfileBuilder
    constraint_decoder: ConstraintDecoder
    static_index_manager: StaticIndexManager
    active_static_index_use_case: GetActiveStaticIndexUseCase
    rebuild_active_static_index_use_case: RebuildActiveStaticIndexUseCase
    status: ModuleStatus


def build_constraint_module(*, catalog: CatalogModule) -> ConstraintModule:
    static_index_store = InMemoryStaticIndexStore(catalog.catalog_reader)
    static_index_store.rebuild_active_index()
    constraint_decoder = InMemoryStaticConstraintDecoder(static_index_store)

    return ConstraintModule(
        constraint_profile_builder=InMemoryConstraintProfileBuilder(),
        constraint_decoder=constraint_decoder,
        static_index_manager=static_index_store,
        active_static_index_use_case=GetActiveStaticIndexUseCase(
            static_index_manager=static_index_store,
        ),
        rebuild_active_static_index_use_case=RebuildActiveStaticIndexUseCase(
            static_index_manager=static_index_store,
        ),
        status=ModuleStatus(
            bounded_context="constraint",
            description="제약 프로필 생성과 STATIC 디코딩 경계.",
            readiness=ModuleReadiness.FOUNDATIONAL,
            next_step="인메모리 STATIC 어댑터를 영속성 기반 snapshot 저장소와 런타임으로 교체한다.",
        ),
    )
