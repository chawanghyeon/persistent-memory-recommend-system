from collections.abc import Sequence

from persistent_memory_recsys.catalog.application.ports import CatalogReader
from persistent_memory_recsys.constraint.adapters.outbound.static_runtime import (
    CompiledStaticIndex,
    build_compiled_static_index,
)
from persistent_memory_recsys.constraint.application.ports import (
    ConstraintDecoder,
    ConstraintProfileBuilder,
    StaticIndexManager,
)
from persistent_memory_recsys.constraint.domain.models import (
    ConstraintCandidate,
    ConstraintDecodingResult,
    ConstraintProfile,
    ConstraintReport,
    StaticIndexSummary,
)
from persistent_memory_recsys.memory.domain.models import MemorySnapshot
from persistent_memory_recsys.preference.domain.models import PreferenceState


class InMemoryConstraintProfileBuilder(ConstraintProfileBuilder):
    def build_home_profile(
        self,
        user_id: str,
        *,
        memory_snapshot: MemorySnapshot | None = None,
        preference_state: PreferenceState | None = None,
    ) -> ConstraintProfile:
        blocked_brands = set()
        blocked_categories = set()

        if memory_snapshot is not None:
            blocked_brands.update(memory_snapshot.hard_blocks.get("brands", ()))
            blocked_categories.update(memory_snapshot.hard_blocks.get("categories", ()))

        if preference_state is not None:
            blocked_brands.update(preference_state.blocked_brands)
            blocked_categories.update(preference_state.blocked_categories)

        return ConstraintProfile(
            user_id=user_id,
            allowed_inventory_statuses=("in_stock",),
            blocked_brands=tuple(sorted(blocked_brands)),
            blocked_categories=tuple(sorted(blocked_categories)),
            max_items=3,
            soft_constraints={"max_same_brand": 2, "max_same_category": 2},
        )


class InMemoryStaticIndexStore(StaticIndexManager):
    def __init__(self, catalog_reader: CatalogReader) -> None:
        self._catalog_reader = catalog_reader
        self._active_index = build_compiled_static_index(
            (),
            semantic_version="sid_v0",
            static_index_version="static_sid_v0",
        )

    def describe_active_index(self) -> StaticIndexSummary:
        return self._active_index.summary

    def rebuild_active_index(self) -> StaticIndexSummary:
        active_mappings = tuple(
            mapping
            for mapping in self._catalog_reader.list_semantic_mappings()
            if mapping.is_active
        )
        semantic_ids = tuple(mapping.semantic_id for mapping in active_mappings)
        semantic_version = self._catalog_reader.get_active_semantic_version()
        static_index_version = f"static_{semantic_version}"
        self._active_index = build_compiled_static_index(
            semantic_ids,
            semantic_version=semantic_version,
            static_index_version=static_index_version,
        )
        return self._active_index.summary

    def get_active_index(self) -> CompiledStaticIndex:
        return self._active_index


class InMemoryStaticConstraintDecoder(ConstraintDecoder):
    def __init__(self, static_index_store: InMemoryStaticIndexStore) -> None:
        self._static_index_store = static_index_store

    def decode(
        self,
        candidates: Sequence[ConstraintCandidate],
        constraint_profile: ConstraintProfile,
    ) -> ConstraintDecodingResult:
        active_index = self._static_index_store.get_active_index()

        if active_index.summary.item_count == 0:
            report = ConstraintReport(
                hard_constraints_applied=constraint_profile.hard_constraints_applied,
                decoder_status="활성 STATIC 인덱스 없음",
                candidate_count=len(candidates),
                rejected_count=len(candidates),
                static_index=active_index.summary,
            )
            return ConstraintDecodingResult(report=report)

        accepted_item_ids: list[str] = []
        accepted_semantic_ids: list[str] = []
        accepted_brands: dict[str, int] = {}
        accepted_categories: dict[str, int] = {}
        rejected_count = 0

        for candidate in candidates:
            if not self._passes_hard_filters(candidate, constraint_profile):
                rejected_count += 1
                continue

            if not active_index.contains(candidate.semantic_id):
                rejected_count += 1
                continue

            if not self._passes_soft_limits(
                candidate,
                constraint_profile,
                accepted_brands,
                accepted_categories,
            ):
                rejected_count += 1
                continue

            accepted_item_ids.append(candidate.item_id)
            accepted_semantic_ids.append(candidate.semantic_id)
            accepted_brands[candidate.brand] = accepted_brands.get(candidate.brand, 0) + 1
            accepted_categories[candidate.category] = (
                accepted_categories.get(candidate.category, 0) + 1
            )

            if len(accepted_item_ids) >= constraint_profile.max_items:
                break

        decoder_status = "STATIC 검증 완료" if accepted_item_ids else "유효한 후보 없음"
        report = ConstraintReport(
            hard_constraints_applied=constraint_profile.hard_constraints_applied,
            decoder_status=decoder_status,
            candidate_count=len(candidates),
            accepted_count=len(accepted_item_ids),
            rejected_count=rejected_count,
            static_index=active_index.summary,
        )
        return ConstraintDecodingResult(
            recommended_item_ids=tuple(accepted_item_ids),
            semantic_ids=tuple(accepted_semantic_ids),
            report=report,
        )

    def _passes_hard_filters(
        self,
        candidate: ConstraintCandidate,
        constraint_profile: ConstraintProfile,
    ) -> bool:
        if (
            constraint_profile.allowed_inventory_statuses
            and candidate.inventory_status not in constraint_profile.allowed_inventory_statuses
        ):
            return False

        if candidate.brand in constraint_profile.blocked_brands:
            return False

        if candidate.category in constraint_profile.blocked_categories:
            return False

        if constraint_profile.required_sizes and not set(candidate.size_options).intersection(
            constraint_profile.required_sizes
        ):
            return False

        return True

    def _passes_soft_limits(
        self,
        candidate: ConstraintCandidate,
        constraint_profile: ConstraintProfile,
        accepted_brands: dict[str, int],
        accepted_categories: dict[str, int],
    ) -> bool:
        max_same_brand = constraint_profile.soft_constraints.get("max_same_brand")
        max_same_category = constraint_profile.soft_constraints.get("max_same_category")

        if max_same_brand is not None and accepted_brands.get(candidate.brand, 0) >= max_same_brand:
            return False

        if (
            max_same_category is not None
            and accepted_categories.get(candidate.category, 0) >= max_same_category
        ):
            return False

        return True
