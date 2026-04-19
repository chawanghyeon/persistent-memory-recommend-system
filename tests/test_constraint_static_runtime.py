from persistent_memory_recsys.catalog.module import build_catalog_module
from persistent_memory_recsys.constraint.domain.models import ConstraintCandidate, ConstraintProfile
from persistent_memory_recsys.constraint.module import build_constraint_module


def test_static_decoder_validates_semantic_paths_and_hard_filters() -> None:
    catalog = build_catalog_module()
    constraint = build_constraint_module(catalog=catalog)

    result = constraint.constraint_decoder.decode(
        (
            ConstraintCandidate(
                item_id="item-formal-derby",
                semantic_id="sid_2 sid_4 sid_2 sid_1",
                brand="BrandX",
                category="formal_shoes",
                inventory_status="in_stock",
                size_options=("270",),
                ranking_score=10.0,
            ),
            ConstraintCandidate(
                item_id="item-invalid",
                semantic_id="sid_9 sid_9 sid_9 sid_9",
                brand="BrandZ",
                category="outerwear",
                inventory_status="in_stock",
                size_options=("M",),
                ranking_score=9.0,
            ),
            ConstraintCandidate(
                item_id="item-utility-jacket",
                semantic_id="sid_3 sid_1 sid_3 sid_4",
                brand="BrandA",
                category="outerwear",
                inventory_status="in_stock",
                size_options=("M",),
                ranking_score=8.0,
            ),
        ),
        ConstraintProfile(
            user_id="test-user",
            blocked_brands=("BrandX",),
            blocked_categories=("formal_shoes",),
            max_items=3,
        ),
    )

    assert result.recommended_item_ids == ("item-utility-jacket",)
    assert result.semantic_ids == ("sid_3 sid_1 sid_3 sid_4",)
    assert result.report.decoder_status == "STATIC 검증 완료"
    assert result.report.candidate_count == 3
    assert result.report.accepted_count == 1
    assert result.report.rejected_count == 2


def test_static_decoder_exposes_active_index_metadata() -> None:
    catalog = build_catalog_module()
    constraint = build_constraint_module(catalog=catalog)

    summary = constraint.static_index_manager.describe_active_index()

    assert summary.static_index_version == "static_sid_v1"
    assert summary.semantic_version == "sid_v1"
    assert summary.item_count == 5
    assert summary.semantic_id_length == 4
