from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str
    tank_tag: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScenarioCreate(BaseModel):
    name: str = "BASELINE"


class RevisionCreate(BaseModel):
    inputs: dict[str, Any]
    derived_from_revision_id: str | None = None
    changes: dict[str, Any] = Field(default_factory=dict)


class DirectCalculation(BaseModel):
    inputs: dict[str, Any]


class VariantSpec(BaseModel):
    name: str
    changes: dict[str, Any]


class VariantBatchRequest(BaseModel):
    name: str = "Variant batch"
    baseline_inputs: dict[str, Any]
    variants: list[VariantSpec]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

