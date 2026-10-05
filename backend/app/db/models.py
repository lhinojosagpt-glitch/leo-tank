from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _id() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    name: Mapped[str] = mapped_column(String(180))
    tank_tag: Mapped[str] = mapped_column(String(80), index=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    scenarios: Mapped[list["DesignScenario"]] = relationship(back_populates="project")


class DesignScenario(Base):
    __tablename__ = "design_scenarios"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(180))
    source_variant_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    project: Mapped[Project] = relationship(back_populates="scenarios")
    revisions: Mapped[list["ScenarioRevision"]] = relationship(back_populates="scenario")


class ScenarioRevision(Base):
    __tablename__ = "scenario_revisions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("design_scenarios.id"), index=True)
    revision_number: Mapped[int] = mapped_column(Integer)
    derived_from_revision_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    input_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    changes_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    scenario: Mapped[DesignScenario] = relationship(back_populates="revisions")
    runs: Mapped[list["CalculationRun"]] = relationship(back_populates="revision")


class CalculationRun(Base):
    __tablename__ = "calculation_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    revision_id: Mapped[str] = mapped_column(ForeignKey("scenario_revisions.id"), index=True)
    status: Mapped[str] = mapped_column(String(40), default="CREATED")
    engine_version: Mapped[str] = mapped_column(String(40))
    standard_profile: Mapped[str] = mapped_column(String(80))
    input_sha256: Mapped[str] = mapped_column(String(64), index=True)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revision: Mapped[ScenarioRevision] = relationship(back_populates="runs")


class VariantBatch(Base):
    __tablename__ = "variant_batches"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    baseline_revision_id: Mapped[str] = mapped_column(String(36), index=True)
    name: Mapped[str] = mapped_column(String(180))
    status: Mapped[str] = mapped_column(String(40), default="CREATED")
    result_matrix_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Artifact(Base):
    __tablename__ = "artifacts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    run_id: Mapped[str] = mapped_column(String(36), index=True)
    artifact_type: Mapped[str] = mapped_column(String(20))
    path: Mapped[str] = mapped_column(Text)
    sha256: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_id)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
