from dataclasses import asdict, dataclass
from uuid import uuid4

from persistent_memory_recsys.catalog.application.ports import CatalogReader
from persistent_memory_recsys.catalog.domain.models import CatalogItem, ItemSemanticMapping
from persistent_memory_recsys.constraint.application.ports import (
    ConstraintDecoder,
    ConstraintProfileBuilder,
    StaticIndexManager,
)
from persistent_memory_recsys.constraint.domain.models import ConstraintCandidate
from persistent_memory_recsys.memory.application.ports import MemorySnapshotReader
from persistent_memory_recsys.preference.application.ports import PreferenceStateReader
from persistent_memory_recsys.preference.domain.models import PreferenceState
from persistent_memory_recsys.recommendation.domain.models import (
    HomeRecommendation,
    RecommendationReadiness,
)


@dataclass(slots=True)
class GenerateHomeRecommendationPreviewUseCase:
    memory_snapshot_reader: MemorySnapshotReader
    preference_state_reader: PreferenceStateReader
    catalog_reader: CatalogReader
    constraint_profile_builder: ConstraintProfileBuilder
    constraint_decoder: ConstraintDecoder
    static_index_manager: StaticIndexManager

    def readiness_summary(self) -> RecommendationReadiness:
        return RecommendationReadiness(
            orchestration="기반 구현",
            memory_integration="미리보기 상태 연결 완료",
            constraint_integration="STATIC 인덱스 미리보기 연결 완료",
            next_step="휴리스틱 후보 정렬을 모델 기반 semantic ID 생성으로 교체한다.",
        )

    def execute(self, user_id: str) -> HomeRecommendation:
        memory_snapshot = self.memory_snapshot_reader.get_snapshot(user_id)
        preference_state = self.preference_state_reader.get_active_state(user_id)
        active_items = tuple(self.catalog_reader.list_active_items())
        semantic_mappings = tuple(self.catalog_reader.list_semantic_mappings())
        ranked_candidates = self._build_ranked_candidates(
            active_items=active_items,
            semantic_mappings=semantic_mappings,
            preference_state=preference_state,
        )
        constraint_profile = self.constraint_profile_builder.build_home_profile(
            user_id,
            memory_snapshot=memory_snapshot,
            preference_state=preference_state,
        )
        decoding_result = self.constraint_decoder.decode(ranked_candidates, constraint_profile)

        return HomeRecommendation(
            request_id=str(uuid4()),
            user_id=user_id,
            surface_type="home",
            recommended_item_ids=decoding_result.recommended_item_ids,
            semantic_ids=decoding_result.semantic_ids,
            memory_snapshot=memory_snapshot,
            preference_state=preference_state,
            constraint_report=decoding_result.report,
            readiness=self.readiness_summary(),
            metadata={
                "active_catalog_items": len(active_items),
                "semantic_mappings": len(semantic_mappings),
                "candidate_count": len(ranked_candidates),
                "constraint_profile": asdict(constraint_profile),
                "static_index": asdict(self.static_index_manager.describe_active_index()),
            },
        )

    def _build_ranked_candidates(
        self,
        *,
        active_items: tuple[CatalogItem, ...],
        semantic_mappings: tuple[ItemSemanticMapping, ...],
        preference_state: PreferenceState,
    ) -> tuple[ConstraintCandidate, ...]:
        items_by_id = {item.item_id: item for item in active_items if item.is_active}
        candidates: list[ConstraintCandidate] = []

        for mapping in semantic_mappings:
            item = items_by_id.get(mapping.item_id)
            if item is None or not mapping.is_active:
                continue

            candidates.append(
                ConstraintCandidate(
                    item_id=item.item_id,
                    semantic_id=mapping.semantic_id,
                    brand=item.brand,
                    category=item.category,
                    inventory_status=item.inventory_status,
                    size_options=item.size_options,
                    ranking_score=self._score_candidate(item, preference_state),
                )
            )

        candidates.sort(key=lambda candidate: candidate.ranking_score, reverse=True)
        return tuple(candidates)

    def _score_candidate(self, item: CatalogItem, preference_state: PreferenceState) -> float:
        score = 0.0

        if item.category in preference_state.preferred_categories:
            score += 10.0

        score += sum(2.0 for like in preference_state.likes if like in item.style_tags)
        score += sum(1.0 for like in preference_state.likes if like in item.color_tags)

        if item.inventory_status == "in_stock":
            score += 0.5

        return score
