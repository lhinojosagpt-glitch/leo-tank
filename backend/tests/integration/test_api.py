from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    with client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_direct_fixture_calculation() -> None:
    with client:
        fixture = client.get("/api/v1/fixtures/T78_2019").json()
        response = client.post("/api/v1/calculate", json={"inputs": fixture})
    assert response.status_code == 200
    body = response.json()
    assert body["overall_status"] == "PASS_WITH_MECHANICAL_ANCHORAGE"
    assert body["summary"]["seismic"]["J"] > 1.54


def test_immutable_revision_run_and_variant_batch() -> None:
    token = uuid4().hex[:8]
    with client:
        fixture = client.get("/api/v1/fixtures/T78_2019").json()
        project = client.post("/api/v1/projects", json={"name": f"T-78 test {token}", "tank_tag": "T-78"}).json()
        scenario = client.post(f"/api/v1/projects/{project['id']}/scenarios", json={"name": "BASELINE"}).json()
        revision = client.post(f"/api/v1/scenarios/{scenario['id']}/revisions", json={"inputs": fixture, "changes": {}}).json()
        run = client.post(f"/api/v1/revisions/{revision['id']}/runs")
        assert run.status_code == 200
        assert run.json()["overall_status"] == "PASS_WITH_MECHANICAL_ANCHORAGE"
        revisions = client.get(f"/api/v1/scenarios/{scenario['id']}/revisions").json()
        assert revisions[0]["locked"] is True

        successor = client.post(f"/api/v1/scenarios/{scenario['id']}/revisions", json={"inputs": fixture, "derived_from_revision_id": revision["id"], "changes": {"seismic.Sp": {"old": 0.45, "new": 0.50}}})
        assert successor.status_code == 200
        assert successor.json()["revision_number"] == 2

        batch = client.post("/api/v1/variant-batches", json={"name": "Golden batch", "baseline_inputs": fixture, "variants": [{"name": "SG 0.90", "changes": {"product.specific_gravity": 0.90}}, {"name": "Sp 0.50", "changes": {"seismic.Sp": 0.50}}]})
        assert batch.status_code == 200
        assert len(batch.json()["matrix"]) == 2
