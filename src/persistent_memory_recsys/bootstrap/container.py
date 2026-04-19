from dataclasses import dataclass

from persistent_memory_recsys.catalog.module import CatalogModule, build_catalog_module
from persistent_memory_recsys.constraint.module import (
    ConstraintModule,
    build_constraint_module,
)
from persistent_memory_recsys.interaction.module import (
    InteractionModule,
    build_interaction_module,
)
from persistent_memory_recsys.memory.module import MemoryModule, build_memory_module
from persistent_memory_recsys.preference.module import (
    PreferenceModule,
    build_preference_module,
)
from persistent_memory_recsys.recommendation.module import (
    RecommendationModule,
    build_recommendation_module,
)
from persistent_memory_recsys.shared.domain.module_status import SystemStatus


@dataclass(slots=True)
class ApplicationContainer:
    interaction: InteractionModule
    memory: MemoryModule
    preference: PreferenceModule
    catalog: CatalogModule
    constraint: ConstraintModule
    recommendation: RecommendationModule
    system_status: SystemStatus


def build_container() -> ApplicationContainer:
    interaction = build_interaction_module()
    memory = build_memory_module()
    preference = build_preference_module()
    catalog = build_catalog_module()
    constraint = build_constraint_module(catalog=catalog)
    recommendation = build_recommendation_module(
        memory=memory,
        preference=preference,
        catalog=catalog,
        constraint=constraint,
    )

    system_status = SystemStatus(
        app_name="장기기억 기반 추천 시스템",
        architecture="DDD 기반 모듈형 모놀리스와 헥사고날 경계",
        package_name="persistent_memory_recsys",
        module_statuses=(
            interaction.status,
            memory.status,
            preference.status,
            catalog.status,
            recommendation.status,
            constraint.status,
        ),
        current_phase="1단계 기반 구현",
        next_milestone="각 바운디드 컨텍스트의 유스케이스와 영속성 어댑터를 구현한다.",
    )

    return ApplicationContainer(
        interaction=interaction,
        memory=memory,
        preference=preference,
        catalog=catalog,
        constraint=constraint,
        recommendation=recommendation,
        system_status=system_status,
    )
