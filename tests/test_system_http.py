from fastapi.testclient import TestClient

from persistent_memory_recsys.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_system_status_exposes_bounded_contexts() -> None:
    response = client.get("/api/v1/system/status")

    assert response.status_code == 200

    payload = response.json()
    assert payload["architecture"] == "DDD 기반 모듈형 모놀리스와 헥사고날 경계"
    assert len(payload["bounded_contexts"]) == 6


def test_home_recommendation_preview_returns_skeleton_payload() -> None:
    response = client.get("/api/v1/recommendations/home/test-user")

    assert response.status_code == 200

    payload = response.json()
    assert payload["user_id"] == "test-user"
    assert payload["surface_type"] == "home"
    assert payload["recommended_item_ids"] == [
        "item-utility-jacket",
        "item-light-cardigan",
        "item-wide-denim",
    ]
    assert payload["semantic_ids"] == [
        "sid_3 sid_1 sid_3 sid_4",
        "sid_3 sid_2 sid_4 sid_3",
        "sid_1 sid_3 sid_1 sid_5",
    ]
    assert payload["constraint_report"]["decoder_status"] == "STATIC 검증 완료"
    assert payload["constraint_report"]["static_index"]["item_count"] == 5
    assert payload["readiness"]["orchestration"] == "기반 구현"


def test_static_index_endpoint_returns_active_snapshot_summary() -> None:
    response = client.get("/api/v1/constraints/static-index")

    assert response.status_code == 200

    payload = response.json()
    assert payload["static_index_version"] == "static_sid_v1"
    assert payload["semantic_version"] == "sid_v1"
    assert payload["item_count"] == 5
    assert payload["semantic_id_length"] == 4


def test_catalog_semantic_mapping_endpoint_returns_generated_mappings() -> None:
    response = client.get("/api/v1/catalog/semantic-mappings")

    assert response.status_code == 200

    payload = response.json()
    assert payload["semantic_version"] == "sid_v1"
    assert payload["count"] == 5
    assert payload["mappings"][0]["item_id"] == "item-utility-jacket"
    assert payload["mappings"][0]["semantic_id"] == "sid_3 sid_1 sid_3 sid_4"


def test_static_index_rebuild_endpoint_returns_summary() -> None:
    response = client.post("/api/v1/constraints/static-index/rebuild")

    assert response.status_code == 200

    payload = response.json()
    assert payload["static_index_version"] == "static_sid_v1"
    assert payload["item_count"] == 5
