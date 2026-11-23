import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.roadmap import RoadmapService, get_roadmap, get_roadmap_service, load_roadmap

client = TestClient(app)

EXPECTED_STAGE_IDS = [
    "llm-fundamentals",
    "prompt-engineering",
    "llm-apis",
    "embeddings-rag",
    "tools-agents",
    "evaluation-safety",
    "shipping-llm-apps",
]


def test_list_stages_returns_seven_in_order():
    response = client.get("/api/stages")
    assert response.status_code == 200
    stages = response.json()
    assert [s["id"] for s in stages] == EXPECTED_STAGE_IDS
    assert [s["order"] for s in stages] == list(range(1, 8))
    assert all("resources" not in s and 3 <= s["resource_count"] <= 7 for s in stages)


def test_get_stage_returns_goals_and_resources():
    response = client.get("/api/stages/prompt-engineering")
    assert response.status_code == 200
    stage = response.json()
    assert stage["title"] == "Prompt Engineering"
    assert stage["goals"]
    assert all(r["url"].startswith("https://") for r in stage["resources"])


def test_get_unknown_stage_returns_404():
    response = client.get("/api/stages/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Stage 'does-not-exist' not found"


def test_resources_unfiltered_returns_all_with_stage_info():
    resources = client.get("/api/resources").json()
    total = sum(len(s.resources) for s in get_roadmap().stages)
    assert len(resources) == total
    assert {"stage_id", "stage_title"} <= resources[0].keys()


@pytest.mark.parametrize("field,value", [("level", "advanced"), ("type", "course"), ("cost", "free")])
def test_resources_filter_by_field(field, value):
    resources = client.get("/api/resources", params={field: value}).json()
    assert resources
    assert all(r[field] == value for r in resources)


def test_resources_combined_filters_and_case_insensitive_search():
    resources = client.get("/api/resources", params={"q": "RAG", "level": "intermediate"}).json()
    assert {r["id"] for r in resources} >= {"langchain-rag"}
    assert all(r["level"] == "intermediate" for r in resources)


def test_resources_search_with_no_match_returns_empty_list():
    response = client.get("/api/resources", params={"q": "zzz-no-such-thing"})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    "params", [{"level": "expert"}, {"type": "podcast"}, {"cost": "cheap"}, {"q": "x" * 101}]
)
def test_resources_invalid_params_return_422(params):
    assert client.get("/api/resources", params=params).status_code == 422


def test_bundled_data_has_unique_ids():
    roadmap = get_roadmap()
    ids = [r.id for s in roadmap.stages for r in s.resources]
    assert len(ids) == len(set(ids))


def test_load_roadmap_rejects_duplicate_resource_ids(tmp_path):
    resource = {
        "id": "dup", "title": "T", "url": "https://example.com", "provider": "P",
        "type": "docs", "level": "beginner", "cost": "free", "description": "D",
    }
    stage = {
        "id": "s1", "order": 1, "title": "S", "summary": "S", "level": "beginner",
        "estimated_time": "1 week", "goals": [], "topics": [], "resources": [resource, resource],
    }
    path = tmp_path / "roadmap.json"
    path.write_text(json.dumps({"version": "1", "updated": "2026-01-01", "stages": [stage]}))
    with pytest.raises(ValueError, match="Duplicate resource ids"):
        load_roadmap(path)


def test_service_can_be_overridden_with_custom_data(tmp_path):
    path = tmp_path / "roadmap.json"
    path.write_text(json.dumps({"version": "1", "updated": "2026-01-01", "stages": []}))
    app.dependency_overrides[get_roadmap_service] = lambda: RoadmapService(load_roadmap(path))
    try:
        assert client.get("/api/stages").json() == []
        assert client.get("/api/stages/llm-fundamentals").status_code == 404
    finally:
        app.dependency_overrides.clear()
