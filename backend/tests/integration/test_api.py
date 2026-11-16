from __future__ import annotations

import io
import zipfile
from uuid import uuid4

from app.main import app
from tests.asgi_client import ASGITestClient


client = ASGITestClient(app)


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


def test_dynamic_calculation_memory_is_idempotent() -> None:
    with client:
        fixture = client.get("/api/v1/fixtures/T78_2019").json()
        first = client.post("/api/v1/calculation-memory", json={"inputs": fixture})
        second = client.post("/api/v1/calculation-memory", json={"inputs": fixture})

    assert first.status_code == 200
    assert first.headers["content-type"].startswith("application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    assert first.headers["x-tank650-input-sha256"] == second.headers["x-tank650-input-sha256"]
    assert first.content == second.content
    with zipfile.ZipFile(io.BytesIO(first.content)) as package:
        assert "word/document.xml" in package.namelist()
        document_xml = package.read("word/document.xml").decode("utf-8")
    assert "Memoria de cálculo mecánico" in document_xml
    assert "Apéndice de trazabilidad de fórmulas" in document_xml


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


def test_v2_revision_read_models_and_geometry() -> None:
    token = uuid4().hex[:8]
    with client:
        fixture = client.get("/api/v1/fixtures/T78_2019").json()
        project = client.post("/api/v1/projects", json={"name": f"UX V2 {token}", "tank_tag": "T-78"}).json()
        scenario = client.post(f"/api/v1/projects/{project['id']}/scenarios", json={"name": "BASELINE"}).json()
        revision = client.post(f"/api/v1/scenarios/{scenario['id']}/revisions", json={"inputs": fixture}).json()

        inputs = client.get(f"/api/v1/revisions/{revision['id']}/inputs")
        assert inputs.status_code == 200
        assert inputs.json()["inputs"]["project"]["tank_tag"] == "T-78"

        geometry = client.get(f"/api/v1/revisions/{revision['id']}/geometry")
        assert geometry.status_code == 200
        spec = geometry.json()
        assert spec["schema_version"] == "2.0"
        assert len(spec["courses"]) == 8
        assert len(spec["courses"][0]["plates"]) == 24
        assert spec["courses"][0]["plates"][0]["id"] == "C01-P01"
        assert spec["physical_roof"]["type"] == "aluminum_geodesic_dome"

        run = client.post(f"/api/v1/revisions/{revision['id']}/runs").json()
        summary = client.get(f"/api/v1/runs/{run['run_id']}/summary")
        assert summary.status_code == 200
        assert round(summary.json()["summary"]["seismic"]["J"], 4) == 2.4059

        module = client.get(f"/api/v1/runs/{run['run_id']}/results/shell")
        assert module.status_code == 200
        assert len(module.json()["result"]["values"]["courses"]) == 8

        trace = client.get(f"/api/v1/runs/{run['run_id']}/trace/API650_12E_5_6_3_2_ONE_FOOT_DESIGN")
        assert trace.status_code == 200
        assert len(trace.json()["traces"]) == 8

        history = client.get(f"/api/v1/scenarios/{scenario['id']}/history")
        assert history.status_code == 200
        assert len(history.json()["revisions"][0]["runs"]) == 1
