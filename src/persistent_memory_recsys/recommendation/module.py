from dataclasses import dataclass

from persistent_memory_recsys.catalog.module import CatalogModule
from persistent_memory_recsys.constraint.module import ConstraintModule
from persistent_memory_recsys.memory.module import MemoryModule
from persistent_memory_recsys.preference.module import PreferenceModule
from persistent_memory_recsys.recommendation.application.use_cases import (
    GenerateHomeRecommendationPreviewUseCase,
)
from persistent_memory_recsys.shared.domain.module_status import (
    ModuleReadiness,
    ModuleStatus,
)


@dataclass(slots=True)
class RecommendationModule:
    home_preview_use_case: GenerateHomeRecommendationPreviewUseCase
    status: ModuleStatus


def build_recommendation_module(
    *,
    memory: MemoryModule,
    preference: PreferenceModule,
    catalog: CatalogModule,
    constraint: ConstraintModule,
) -> RecommendationModule:
    return RecommendationModule(
        home_preview_use_case=GenerateHomeRecommendationPreviewUseCase(
            memory_snapshot_reader=memory.memory_snapshot_reader,
            preference_state_reader=preference.preference_state_reader,
            catalog_reader=catalog.catalog_reader,
            constraint_profile_builder=constraint.constraint_profile_builder,
            constraint_decoder=constraint.constraint_decoder,
            static_index_manager=constraint.static_index_manager,
        ),
        status=ModuleStatus(
            bounded_context="recommendation",
            description="생성형 추천 오케스트레이션 경계.",
            readiness=ModuleReadiness.FOUNDATIONAL,
            next_step="휴리스틱 후보 정렬을 모델 기반 semantic 생성으로 교체한다.",
        ),
    )
