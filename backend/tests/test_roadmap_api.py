import copy
import json
import re

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.main import app
from app.services import roadmap as roadmap_service
from app.services.roadmap import RoadmapService, get_roadmap, get_roadmap_service, load_roadmap

client = TestClient(app)

USE_STAGE_IDS = [
    "ai-basics",
    "assistant-setup",
    "prompting",
    "files-projects",
    "apps-connectors",
    "mcp",
    "skills-assistants",
    "agents",
    "agent-safety",
    "workflows",
]
BUILD_STAGE_IDS = [
    "llm-fundamentals",
    "prompt-engineering",
    "llm-apis",
    "embeddings-rag",
    "tools-agents",
    "evaluation-safety",
    "shipping-llm-apps",
]

MINIMAL = {
    "version": "1",
    "updated": "2026-01-01",
    "tracks": [{"id": "use", "order": 1, "title": "Use", "description": "D"}],
    "stages": [
        {
            "id": "s1", "track": "use", "order": 1, "title": "S", "summary": "S",
            "takeaway": "Short and sweet.", "icon": "💡", "color": "#1D4ED8",
            "level": "beginner", "estimated_time": "1 week", "goals": [],
            "topics": [{"title": "T", "takeaway": "Tiny.", "example": "Try this."}],
            "example": {
                "title": "E", "scenario": "S", "steps": ["Do it."], "expected_result": "Done.",
            },
            "resources": [{
                "id": "r1", "title": "T", "url": "https://example.com", "provider": "P",
                "type": "docs", "level": "beginner", "cost": "free", "description": "D",
            }],
        }
    ],
}


def write_data(tmp_path, data):
    path = tmp_path / "roadmap.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture(autouse=True)
def all_tracks_enabled():
    """Most tests cover both tracks; the 'disabled tracks' tests override this."""
    app.dependency_overrides[get_roadmap_service] = lambda: RoadmapService(get_roadmap(), ["use", "build"])
    yield
    app.dependency_overrides.clear()


def use_only():
    app.dependency_overrides[get_roadmap_service] = lambda: RoadmapService(get_roadmap(), ["use"])


# --- tracks -----------------------------------------------------------------

def test_list_tracks_returns_use_first_with_counts():
    response = client.get("/api/tracks")
    assert response.status_code == 200
    tracks = response.json()
    assert [(t["id"], t["title"], t["stage_count"]) for t in tracks] == [
        ("use", "Use AI Assistants", 10),
        ("build", "Build with AI (for developers)", 7),
    ]
    assert all(t.keys() == {"id", "title", "description", "stage_count"} and t["description"] for t in tracks)


# --- stages -----------------------------------------------------------------

def test_list_stages_without_track_returns_all_use_first():
    stages = client.get("/api/stages").json()
    assert [s["id"] for s in stages] == USE_STAGE_IDS + BUILD_STAGE_IDS


@pytest.mark.parametrize("track,expected", [("use", USE_STAGE_IDS), ("build", BUILD_STAGE_IDS)])
def test_list_stages_filtered_by_track(track, expected):
    stages = client.get("/api/stages", params={"track": track}).json()
    assert [s["id"] for s in stages] == expected
    assert [s["order"] for s in stages] == list(range(1, len(expected) + 1))
    assert all(s["track"] == track for s in stages)


def test_stage_summaries_include_mindmap_fields_but_not_resources():
    stage = client.get("/api/stages").json()[0]
    assert {"track", "takeaway", "icon", "color", "topics", "resource_count"} <= stage.keys()
    assert "resources" not in stage and "goals" not in stage and "example" not in stage
    assert stage["topics"][0].keys() == {"title", "takeaway", "example"}


def test_get_stage_returns_full_detail_with_example():
    response = client.get("/api/stages/mcp")
    assert response.status_code == 200
    stage = response.json()
    assert stage["track"] == "use"
    assert stage["takeaway"] and stage["icon"] and stage["color"].startswith("#")
    assert stage["goals"] and stage["resources"]
    assert all(r["url"].startswith("https://") for r in stage["resources"])
    example = stage["example"]
    assert example.keys() == {"title", "scenario", "steps", "prompt", "code", "expected_result"}
    assert example["steps"] and example["prompt"] and example["expected_result"]
    assert example["code"]["language"] == "json"
    assert "@modelcontextprotocol/server-filesystem" in json.loads(example["code"]["content"])["mcpServers"]["filesystem"]["args"]


def test_optional_example_fields_are_null_when_absent():
    example = client.get("/api/stages/ai-basics").json()["example"]
    assert example["prompt"] and example["code"] is None


def test_every_use_stage_has_hands_on_example_and_topic_examples():
    for stage in get_roadmap().stages:
        if stage.track != "use":
            continue
        assert stage.example.steps and all(step.strip() for step in stage.example.steps), stage.id
        assert stage.example.prompt or stage.example.code, f"{stage.id} needs a prompt or code to try"
        assert all(t.example.strip() for t in stage.topics), stage.id
        assert 3 <= len(stage.resources) <= 6, stage.id


def words(text):
    return len(text.split())


def sentences(text):
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s])


USE_STAGES = [s for s in get_roadmap().stages if s.track == "use"]


@pytest.mark.parametrize("stage", USE_STAGES, ids=lambda s: s.id)
def test_use_stage_is_short_explanation_plus_example_to_try(stage):
    ex = stage.example
    assert 2 <= sentences(stage.summary) <= 3 and words(stage.summary) <= 60
    assert sentences(ex.scenario) <= 2 and words(ex.scenario) <= 25
    assert len(ex.steps) <= (8 if stage.id == "mcp" else 5)
    assert all(words(step) <= 20 for step in ex.steps), [s for s in ex.steps if words(s) > 20]
    assert ex.prompt is None or words(ex.prompt) <= 40
    assert sentences(ex.expected_result) == 1 and words(ex.expected_result) <= 25


def test_get_unknown_stage_returns_404():
    response = client.get("/api/stages/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Stage 'does-not-exist' not found"


# --- resources --------------------------------------------------------------

def test_resources_unfiltered_returns_all_with_stage_info():
    resources = client.get("/api/resources").json()
    assert len(resources) == sum(len(s.resources) for s in get_roadmap().stages)
    assert {"track", "stage_id", "stage_title"} <= resources[0].keys()


@pytest.mark.parametrize(
    "field,value",
    [("track", "use"), ("track", "build"), ("level", "advanced"), ("type", "course"), ("cost", "free"), ("cost", "paid")],
)
def test_resources_filter_by_field(field, value):
    resources = client.get("/api/resources", params={field: value}).json()
    assert resources
    assert all(r[field] == value for r in resources)


def test_resources_combined_filters_and_case_insensitive_search():
    resources = client.get("/api/resources", params={"q": "RAG", "level": "intermediate", "track": "build"}).json()
    assert "langchain-rag" in {r["id"] for r in resources}
    assert all(r["level"] == "intermediate" and r["track"] == "build" for r in resources)


def test_resources_search_with_no_match_returns_empty_list():
    response = client.get("/api/resources", params={"q": "zzz-no-such-thing"})
    assert response.status_code == 200
    assert response.json() == []


# --- mind map ---------------------------------------------------------------

def test_mindmap_returns_exact_shape():
    response = client.get("/api/tracks/use/mindmap")
    assert response.status_code == 200
    body = response.json()
    assert body.keys() == {"track", "stages"}
    assert body["track"]["id"] == "use" and body["track"].keys() == {"id", "title", "description"}
    assert [s["id"] for s in body["stages"]] == USE_STAGE_IDS
    for stage in body["stages"]:
        assert stage.keys() == {"id", "title", "icon", "color", "takeaway", "example", "topics"}
        assert stage["example"].keys() == {"title"} and stage["example"]["title"]
        assert all(t.keys() == {"title", "takeaway", "example"} for t in stage["topics"])


def test_mindmap_for_track_missing_from_data_returns_404(tmp_path):
    path = write_data(tmp_path, MINIMAL)
    app.dependency_overrides[get_roadmap_service] = lambda: RoadmapService(load_roadmap(path))
    response = client.get("/api/tracks/build/mindmap")
    assert response.status_code == 404
    assert response.json()["detail"] == "Track 'build' not found"


# --- enabled / disabled tracks ----------------------------------------------

def test_default_settings_enable_only_use_track():
    assert Settings(_env_file=None).enabled_track_list == ["use"]


def test_default_service_follows_enabled_tracks_setting(monkeypatch):
    app.dependency_overrides.clear()
    monkeypatch.setattr(roadmap_service, "get_settings", lambda: Settings(_env_file=None, enabled_tracks="use"))
    assert [t["id"] for t in client.get("/api/tracks").json()] == ["use"]


@pytest.mark.parametrize("value,error", [("use,ml", "unknown track ids"), (" , ", "at least one track")])
def test_enabled_tracks_setting_rejects_invalid_values(value, error):
    with pytest.raises(ValidationError, match=error):
        Settings(_env_file=None, enabled_tracks=value)


def test_disabled_track_is_hidden_everywhere():
    use_only()
    assert [t["id"] for t in client.get("/api/tracks").json()] == ["use"]
    assert [s["id"] for s in client.get("/api/stages").json()] == USE_STAGE_IDS
    resources = client.get("/api/resources").json()
    assert resources and all(r["track"] == "use" for r in resources)
    assert client.get("/api/tracks/use/mindmap").status_code == 200


@pytest.mark.parametrize("url", ["/api/stages", "/api/resources"])
def test_disabled_and_unknown_track_query_get_the_same_422(url):
    use_only()
    errors = {}
    for track in ("build", "ml"):
        response = client.get(url, params={"track": track})
        assert response.status_code == 422
        [error] = response.json()["detail"]
        assert error["loc"] == ["query", "track"] and error["input"] == track
        errors[track] = error["msg"]
    assert errors["build"] == errors["ml"] == "Input should be 'use'"


def test_track_query_lists_all_enabled_tracks_in_error():
    [error] = client.get("/api/stages", params={"track": "ml"}).json()["detail"]
    assert error["msg"] == "Input should be 'use' or 'build'"


@pytest.mark.parametrize("track", ["build", "ml"])
def test_disabled_and_unknown_track_mindmap_get_the_same_404(track):
    use_only()
    response = client.get(f"/api/tracks/{track}/mindmap")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Track '{track}' not found"


def test_disabled_track_mindmap_and_stage_return_404():
    use_only()
    response = client.get("/api/tracks/build/mindmap")
    assert response.status_code == 404
    assert response.json()["detail"] == "Track 'build' not found"
    for stage_id in BUILD_STAGE_IDS:
        assert client.get(f"/api/stages/{stage_id}").status_code == 404


def test_disabled_track_data_is_kept_in_file():
    assert {s.id for s in get_roadmap().stages if s.track == "build"} == set(BUILD_STAGE_IDS)


# --- validation errors ------------------------------------------------------

@pytest.mark.parametrize(
    "url,params",
    [
        ("/api/stages", {"track": "ml"}),
        ("/api/resources", {"track": "ml"}),
        ("/api/resources", {"level": "expert"}),
        ("/api/resources", {"type": "podcast"}),
        ("/api/resources", {"cost": "cheap"}),
        ("/api/resources", {"q": "x" * 101}),
    ],
)
def test_invalid_params_return_422(url, params):
    assert client.get(url, params=params).status_code == 422


# --- data integrity ---------------------------------------------------------

def _relative_luminance(hex_color: str) -> float:
    def channel(c: int) -> float:
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def test_bundled_stage_colors_meet_wcag_aa_contrast_with_white_text():
    for stage in get_roadmap().stages:
        ratio = 1.05 / (_relative_luminance(stage.color) + 0.05)
        assert ratio >= 4.5, f"{stage.id} color {stage.color} contrast {ratio:.2f}"


def test_minimal_data_loads(tmp_path):
    assert load_roadmap(write_data(tmp_path, MINIMAL)).stages[0].id == "s1"


def _mutated(mutate):
    data = copy.deepcopy(MINIMAL)
    mutate(data)
    return data


@pytest.mark.parametrize(
    "mutate,error",
    [
        (lambda d: d["stages"].append(copy.deepcopy(d["stages"][0])), "Duplicate stage ids"),
        (lambda d: d["stages"][0]["resources"].append(d["stages"][0]["resources"][0]), "Duplicate resource ids"),
        (lambda d: d["stages"][0].update(track="build"), "undefined tracks"),
        (lambda d: d["stages"][0].update(takeaway=" ".join(["word"] * 13)), "12 words or fewer"),
        (lambda d: d["stages"][0]["topics"][0].update(takeaway=" ".join(["word"] * 13)), "12 words or fewer"),
        (lambda d: d["stages"][0].update(color="blue"), "String should match pattern"),
        (lambda d: d["stages"][0].pop("example"), "example\n  Field required"),
        (lambda d: d["stages"][0]["example"].update(steps=[]), "at least 1 item"),
        (lambda d: d["stages"][0]["example"].pop("expected_result"), "expected_result\n  Field required"),
        (lambda d: d["stages"][0]["example"].update(code={"language": "json"}), "content\n  Field required"),
        (lambda d: d["stages"][0]["topics"][0].pop("example"), "example\n  Field required"),
    ],
)
def test_load_roadmap_rejects_invalid_data(tmp_path, mutate, error):
    with pytest.raises(ValueError, match=error):
        load_roadmap(write_data(tmp_path, _mutated(mutate)))
