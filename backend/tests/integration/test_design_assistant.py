from __future__ import annotations

from uuid import uuid4

from app.main import app
from tests.asgi_client import ASGITestClient


client = ASGITestClient(app)


def _baseline():
    fixture = client.get("/api/v1/fixtures/T78_2019").json()
    token = uuid4().hex[:8]
    project = client.post("/api/v1/projects", json={"name": f"Assistant {token}", "tank_tag": "T-78"}).json()
    scenario = client.post(f"/api/v1/projects/{project['id']}/scenarios", json={"name": "BASELINE"}).json()
    revision = client.post(f"/api/v1/scenarios/{scenario['id']}/revisions", json={"inputs": fixture}).json()
    run = client.post(f"/api/v1/revisions/{revision['id']}/runs").json()
    return fixture, scenario, revision, run


def test_design_assistant_is_deterministic_auditable_and_non_mutating() -> None:
    with client:
        fixture, scenario, revision, run = _baseline()
        analysis = client.post(f"/api/v1/runs/{run['run_id']}/design-assistant/analyze")
        assert analysis.status_code == 200
        auto = next(row for row in analysis.json()["failed_checks"] if row["check_id"] == "AUTO_ANCHORAGE")
        assert auto["classification"] == "ALTERNATIVE_PATH_FAIL"
        assert [row["id"] for row in auto["adjustable_variables"]] == ["annular_plate_thickness"]
        assert {row["classification"] for row in auto["fixed_variables"]} == {"PROJECT_CONDITION", "STANDARD_DEFINED"}

        created = client.post(
            f"/api/v1/runs/{run['run_id']}/design-assistant/studies",
            json={"check_id": "AUTO_ANCHORAGE", "variables": ["annular_plate_thickness"], "objective": "MINIMUM_CHANGE_PASS"},
        )
        assert created.status_code == 200
        assert created.json()["summary"]["passing_candidates"] == 0
        study_id = created.json()["study_id"]
        recommendations = client.get(f"/api/v1/design-studies/{study_id}/recommendations").json()["recommendations"]
        assert recommendations == []
        variants = client.get(f"/api/v1/design-studies/{study_id}/variants").json()["variants"]
        assert variants and all(row["candidate_run_id"] for row in variants)

        # Controlled real FAIL -> PASS case for partial draft adoption.
        failing = fixture.copy()
        failing = __import__("copy").deepcopy(fixture)
        failing["shell"]["courses"][5]["thickness_mm"] = 8.0
        successor = client.post(f"/api/v1/scenarios/{scenario['id']}/revisions", json={"inputs": failing, "derived_from_revision_id": revision["id"], "changes": {"shell.courses[5].thickness_mm": {"old": 9.5, "new": 8.0}}}).json()
        failing_run = client.post(f"/api/v1/revisions/{successor['id']}/runs").json()
        created = client.post(f"/api/v1/runs/{failing_run['run_id']}/design-assistant/studies", json={"check_id": "SEISMIC_HOOP_COURSE_6", "variables": ["course_6_thickness"]})
        assert created.status_code == 200
        study_id = created.json()["study_id"]
        first = client.get(f"/api/v1/design-studies/{study_id}/recommendations").json()["recommendations"][0]
        assert first["candidate_run_id"] and first["target_check"]["status"] == "PASS"

        applied = client.post(
            f"/api/v1/design-studies/{study_id}/recommendations/{first['id']}/apply",
            json={"selected_variables": ["shell.courses[5].thickness_mm"]},
        )
        assert applied.status_code == 200
        assert applied.json()["requires_recalculation"] is True
        assert applied.json()["original_revision_unchanged"] is True
        original = client.get(f"/api/v1/revisions/{revision['id']}/inputs").json()
        assert original["inputs"]["bottom"]["annular_selected_mm"] == fixture["bottom"]["annular_selected_mm"]


def test_fixed_project_condition_cannot_be_optimized() -> None:
    with client:
        _, _, _, run = _baseline()
        response = client.post(
            f"/api/v1/runs/{run['run_id']}/design-assistant/studies",
            json={"check_id": "AUTO_ANCHORAGE", "variables": ["seismic_acceleration"]},
        )
        assert response.status_code == 422
