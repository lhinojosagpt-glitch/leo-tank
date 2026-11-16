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


class DesignStudyRequest(BaseModel):
    check_id: str
    objective: str = "MINIMUM_CHANGE_PASS"
    variables: list[str] = Field(default_factory=list)
    target_utilization: float = Field(default=1.0, gt=0, le=1.0)
    max_simulations: int = Field(default=500, ge=1, le=500)


class ApplyRecommendationRequest(BaseModel):
    selected_variables: list[str] | None = None


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

