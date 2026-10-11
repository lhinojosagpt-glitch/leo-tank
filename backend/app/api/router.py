from __future__ import annotations

import copy
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import ENGINE_VERSION
from app.api.schemas import DirectCalculation, ProjectCreate, RevisionCreate, ScenarioCreate, VariantBatchRequest
from app.config import API_KEY, ROOT
from app.db.models import AuditEvent, CalculationRun, DesignScenario, Project, ScenarioRevision, VariantBatch
from app.db.session import SessionLocal, engine
from app.engine.common import load_fixture, unwrap
from app.engine.runner import calculate
from app.openscad import write_scad
from app.reports import MEMORY_FORMAT_VERSION, write_calculation_memory, write_html_report, write_json_report, write_pdf_report

router = APIRouter(prefix="/api/v1")


def session() -> Session:
    with SessionLocal() as db:
        yield db


def write_access(x_api_key: str | None = Header(default=None)) -> None:
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(401, detail={"code": "INVALID_API_KEY", "message": "A valid X-API-Key is required."})


def _audit(db: Session, event: str, entity_type: str, entity_id: str, payload: dict | None = None) -> None:
    db.add(AuditEvent(event_type=event, entity_type=entity_type, entity_id=entity_id, payload_json=payload or {}))


def _apply_changes(target: dict, changes: dict[str, Any]) -> dict:
    result = copy.deepcopy(target)
    for path, value in changes.items():
        cursor: Any = result
        parts = path.replace("]", "").replace("[", ".").split(".")
        for part in parts[:-1]:
            cursor = cursor[int(part)] if isinstance(cursor, list) else cursor[part]
        leaf = parts[-1]
        if isinstance(cursor, list):
            cursor[int(leaf)] = value
        else:
            cursor[leaf] = value
    return result


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "engine_version": ENGINE_VERSION, "profile": "API650_12E_T78"}


@router.get("/fixtures/T78_2019")
def fixture() -> dict:
    raw, _ = load_fixture(ROOT / "data" / "fixtures" / "T78_2019.json")
    return raw


@router.post("/calculate", dependencies=[Depends(write_access)])
def direct_calculation(body: DirectCalculation) -> dict:
    return calculate(unwrap(body.inputs)).to_dict()


@router.post("/calculation-memory", dependencies=[Depends(write_access)])
def create_calculation_memory(body: DirectCalculation) -> FileResponse:
    """Recalculate the submitted draft and return its deterministic Word memory."""
    inputs = unwrap(body.inputs)
    result = calculate(inputs).to_dict()
    raw_tag = str(inputs.get("project", {}).get("tank_tag", "T-78"))
    tank_tag = "".join(character if character.isalnum() or character in "-_" else "-" for character in raw_tag).strip("-") or "T-78"
    version = MEMORY_FORMAT_VERSION.replace(".", "-")
    filename = f"Memoria_Calculo_{tank_tag}_{result['input_sha256'][:12]}_v{version}.docx"
    target = ROOT / "reports" / "generated" / "calculation-memories" / filename
    write_calculation_memory(inputs, result, target)
    return FileResponse(
        target,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
        headers={
            "ETag": f'"{result["input_sha256"]}"',
            "X-TANK650-Input-SHA256": result["input_sha256"],
            "X-TANK650-Engine-Version": result["engine_version"],
        },
    )


@router.get("/projects")
def list_projects(db: Session = Depends(session)) -> list[dict]:
    projects = db.scalars(select(Project).order_by(Project.created_at.desc())).all()
    return [{"id": p.id, "name": p.name, "tank_tag": p.tank_tag, "metadata": p.metadata_json, "created_at": p.created_at} for p in projects]


@router.post("/projects", dependencies=[Depends(write_access)])
def create_project(body: ProjectCreate, db: Session = Depends(session)) -> dict:
    project = Project(name=body.name, tank_tag=body.tank_tag, metadata_json=body.metadata)
    db.add(project)
    db.flush()
    _audit(db, "PROJECT_CREATED", "project", project.id)
    db.commit()
    return {"id": project.id, "name": project.name, "tank_tag": project.tank_tag}


@router.get("/projects/{project_id}/scenarios")
def list_scenarios(project_id: str, db: Session = Depends(session)) -> list[dict]:
    rows = db.scalars(select(DesignScenario).where(DesignScenario.project_id == project_id)).all()
    return [{"id": row.id, "name": row.name, "project_id": row.project_id} for row in rows]


@router.post("/projects/{project_id}/scenarios", dependencies=[Depends(write_access)])
def create_scenario(project_id: str, body: ScenarioCreate, db: Session = Depends(session)) -> dict:
    if db.get(Project, project_id) is None:
        raise HTTPException(404, "Project not found")
    scenario = DesignScenario(project_id=project_id, name=body.name)
    db.add(scenario)
    db.flush()
    _audit(db, "SCENARIO_CREATED", "scenario", scenario.id)
    db.commit()
    return {"id": scenario.id, "name": scenario.name}


@router.get("/scenarios/{scenario_id}/revisions")
def list_revisions(scenario_id: str, db: Session = Depends(session)) -> list[dict]:
    rows = db.scalars(select(ScenarioRevision).where(ScenarioRevision.scenario_id == scenario_id).order_by(ScenarioRevision.revision_number)).all()
    return [{"id": row.id, "revision_number": row.revision_number, "derived_from_revision_id": row.derived_from_revision_id, "locked": row.locked, "changes": row.changes_json, "created_at": row.created_at, "runs": [{"id": run.id, "status": run.status, "engine_version": run.engine_version, "created_at": run.created_at, "completed_at": run.completed_at} for run in row.runs]} for row in rows]


@router.post("/scenarios/{scenario_id}/revisions", dependencies=[Depends(write_access)])
def create_revision(scenario_id: str, body: RevisionCreate, db: Session = Depends(session)) -> dict:
    if db.get(DesignScenario, scenario_id) is None:
        raise HTTPException(404, "Scenario not found")
    number = (db.scalar(select(func.max(ScenarioRevision.revision_number)).where(ScenarioRevision.scenario_id == scenario_id)) or 0) + 1
    revision = ScenarioRevision(scenario_id=scenario_id, revision_number=number, derived_from_revision_id=body.derived_from_revision_id, input_json=body.inputs, changes_json=body.changes)
    db.add(revision)
    db.flush()
    _audit(db, "REVISION_CREATED", "revision", revision.id, {"revision_number": number, "changes": body.changes})
    db.commit()
    return {"id": revision.id, "revision_number": revision.revision_number}


@router.get("/revisions/{revision_id}/inputs")
def get_revision_inputs(revision_id: str, db: Session = Depends(session)) -> dict:
    revision = db.get(ScenarioRevision, revision_id)
    if revision is None:
        raise HTTPException(404, "Revision not found")
    return {"revision_id": revision.id, "revision_number": revision.revision_number, "locked": revision.locked, "inputs": revision.input_json}


@router.post("/revisions/{revision_id}/derive", dependencies=[Depends(write_access)])
def derive_revision(revision_id: str, db: Session = Depends(session)) -> dict:
    revision = db.get(ScenarioRevision, revision_id)
    if revision is None:
        raise HTTPException(404, "Revision not found")
    return calculate(unwrap(revision.input_json)).to_dict()


@router.get("/revisions/{revision_id}/geometry")
def get_revision_geometry(revision_id: str, db: Session = Depends(session)) -> dict:
    revision = db.get(ScenarioRevision, revision_id)
    if revision is None:
        raise HTTPException(404, "Revision not found")
    return calculate(unwrap(revision.input_json)).geometry


@router.post("/revisions/{revision_id}/runs", dependencies=[Depends(write_access)])
def create_run(revision_id: str, db: Session = Depends(session)) -> dict:
    revision = db.get(ScenarioRevision, revision_id)
    if revision is None:
        raise HTTPException(404, "Revision not found")
    _audit(db, "CALCULATION_STARTED", "revision", revision.id)
    result = calculate(unwrap(revision.input_json))
    run = CalculationRun(revision_id=revision.id, status="COMPLETED", engine_version=result.engine_version, standard_profile=result.standard_profile, input_sha256=result.input_sha256, result_json=result.to_dict(), completed_at=datetime.now(timezone.utc))
    revision.locked = True
    db.add(run)
    db.flush()
    _audit(db, "CALCULATION_COMPLETED", "run", run.id, {"overall_status": result.overall_status})
    db.commit()
    return {"run_id": run.id, **result.to_dict()}


@router.get("/runs/{run_id}")
def get_run(run_id: str, db: Session = Depends(session)) -> dict:
    run = db.get(CalculationRun, run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    return {"id": run.id, "revision_id": run.revision_id, "status": run.status, "result": run.result_json}


@router.get("/runs/{run_id}/summary")
def get_run_summary(run_id: str, db: Session = Depends(session)) -> dict:
    run = db.get(CalculationRun, run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    return {"run_id": run.id, "status": run.status, "summary": run.result_json.get("summary", {}), "overall_status": run.result_json.get("overall_status")}


@router.get("/runs/{run_id}/results/{module_name}")
def get_run_module(run_id: str, module_name: str, db: Session = Depends(session)) -> dict:
    run = db.get(CalculationRun, run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    module = run.result_json.get("modules", {}).get(module_name)
    if module is None:
        raise HTTPException(404, "Module result not found")
    return {"run_id": run.id, "module": module_name, "result": module}


@router.get("/runs/{run_id}/trace/{formula_id}")
def get_formula_trace(run_id: str, formula_id: str, db: Session = Depends(session)) -> dict:
    run = db.get(CalculationRun, run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    matches = [trace for module in run.result_json.get("modules", {}).values() for trace in module.get("traces", []) if trace.get("formula_id") == formula_id]
    if not matches:
        raise HTTPException(404, "Formula trace not found")
    return {"run_id": run.id, "formula_id": formula_id, "traces": matches}


@router.get("/scenarios/{scenario_id}/history")
def get_scenario_history(scenario_id: str, db: Session = Depends(session)) -> dict:
    scenario = db.get(DesignScenario, scenario_id)
    if scenario is None:
        raise HTTPException(404, "Scenario not found")
    revisions = db.scalars(select(ScenarioRevision).where(ScenarioRevision.scenario_id == scenario_id).order_by(ScenarioRevision.revision_number)).all()
    return {
        "scenario": {"id": scenario.id, "name": scenario.name},
        "revisions": [{"id": revision.id, "revision_number": revision.revision_number, "derived_from_revision_id": revision.derived_from_revision_id, "locked": revision.locked, "changes": revision.changes_json, "created_at": revision.created_at, "runs": [{"id": run.id, "status": run.status, "input_sha256": run.input_sha256, "created_at": run.created_at, "completed_at": run.completed_at} for run in revision.runs]} for revision in revisions],
    }


@router.get("/runs/{run_id}/trace")
def get_trace(run_id: str, db: Session = Depends(session)) -> dict:
    run = db.get(CalculationRun, run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    return {name: module.get("traces", []) for name, module in run.result_json.get("modules", {}).items()}


@router.get("/runs/{run_id}/checks")
def get_checks(run_id: str, db: Session = Depends(session)) -> dict:
    run = db.get(CalculationRun, run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    return {name: module.get("checks", []) for name, module in run.result_json.get("modules", {}).items()}


@router.post("/variant-batches", dependencies=[Depends(write_access)])
def run_variant_batch(body: VariantBatchRequest, db: Session = Depends(session)) -> dict:
    matrix = []
    for index, variant in enumerate(body.variants, start=1):
        inputs = _apply_changes(unwrap(body.baseline_inputs), variant.changes)
        result = calculate(inputs)
        matrix.append({"variant_id": index, "variant_name": variant.name, "status": result.overall_status, "total_weight": result.summary["weights"]["empty_N"], "max_shell_utilization": result.summary["shell"]["max_utilization"], "max_seismic_hoop_utilization": result.summary["seismic"]["max_hoop_utilization"], "J": result.summary["seismic"]["J"], "anchor_required": result.summary["anchorage"]["required"], "bolt_utilization": result.summary["anchorage"]["max_utilization"], "overall_status": result.overall_status, "changes": variant.changes})
    batch = VariantBatch(baseline_revision_id="direct", name=body.name, status="COMPLETED", result_matrix_json=matrix)
    db.add(batch)
    db.flush()
    _audit(db, "VARIANT_BATCH_COMPLETED", "variant_batch", batch.id, {"count": len(matrix)})
    db.commit()
    return {"batch_id": batch.id, "status": batch.status, "matrix": matrix}


@router.post("/runs/{run_id}/export/scad", dependencies=[Depends(write_access)])
def export_scad(run_id: str, db: Session = Depends(session)) -> FileResponse:
    run = db.get(CalculationRun, run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    target = ROOT / "models" / "generated" / f"{run_id}.scad"
    write_scad(run.result_json["geometry"], target)
    return FileResponse(target, media_type="text/plain", filename=f"T78-{run_id}.scad")


@router.get("/runs/{run_id}/export/json")
def export_json(run_id: str, db: Session = Depends(session)) -> PlainTextResponse:
    run = db.get(CalculationRun, run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    return PlainTextResponse(json.dumps(run.result_json, indent=2, ensure_ascii=False), media_type="application/json")


@router.post("/runs/{run_id}/reports", dependencies=[Depends(write_access)])
def create_reports(run_id: str, db: Session = Depends(session)) -> dict:
    run = db.get(CalculationRun, run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    folder = ROOT / "reports" / "generated" / run_id
    outputs = {
        "json": write_json_report(run.result_json, folder / "calculation.json"),
        "html": write_html_report(run.result_json, folder / "calculation.html"),
        "pdf": write_pdf_report(run.result_json, folder / "calculation.pdf"),
    }
    _audit(db, "REPORT_GENERATED", "run", run.id, {key: str(path.relative_to(ROOT)) for key, path in outputs.items()})
    db.commit()
    return {key: f"/api/v1/reports/{run_id}/{key}" for key in outputs}


@router.get("/reports/{run_id}/{format_name}")
def download_report(run_id: str, format_name: str) -> FileResponse:
    suffixes = {"json": "json", "html": "html", "pdf": "pdf"}
    if format_name not in suffixes:
        raise HTTPException(404, "Unknown report format")
    path = ROOT / "reports" / "generated" / run_id / f"calculation.{suffixes[format_name]}"
    if not path.exists():
        raise HTTPException(404, "Report not generated")
    media = {"json": "application/json", "html": "text/html", "pdf": "application/pdf"}[format_name]
    return FileResponse(path, media_type=media, filename=f"TANK650-{run_id}.{suffixes[format_name]}")


@router.post("/system/backup", dependencies=[Depends(write_access)])
def backup_database() -> dict:
    if not str(engine.url).startswith("sqlite"):
        raise HTTPException(501, "Only SQLite backup is implemented")
    source = Path(engine.url.database or "")
    if not source.exists():
        raise HTTPException(404, "Database file not found")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = ROOT / "data" / "backups" / f"tank650-{stamp}.sqlite3"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise HTTPException(409, "Backup already exists")
    shutil.copy2(source, target)
    return {"path": str(target.relative_to(ROOT)), "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
