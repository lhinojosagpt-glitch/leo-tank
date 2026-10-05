from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


Status = Literal[
    "PASS", "WARNING", "FAIL", "REVIEW", "NOT_APPLICABLE", "NOT_IMPLEMENTED", "CALCULATED"
]


@dataclass(frozen=True)
class FormulaTrace:
    formula_id: str
    symbol: str
    description: str
    reference: str
    expression: str
    inputs: dict[str, Any]
    raw_result: float
    display_result: float
    unit: str
    status: Status = "CALCULATED"
    rounding: str = "round-half-even for display only"


@dataclass(frozen=True)
class AcceptanceCheck:
    check_id: str
    title: str
    demand: float | None
    capacity: float | None
    unit: str
    utilization: float | None
    margin: float | None
    status: Status
    standard_reference: str
    message: str


@dataclass
class ModuleResult:
    status: Status
    values: dict[str, Any] = field(default_factory=dict)
    checks: list[AcceptanceCheck] = field(default_factory=list)
    traces: list[FormulaTrace] = field(default_factory=list)


@dataclass
class CalculationResult:
    engine_version: str
    standard_profile: str
    overall_status: str
    input_sha256: str
    summary: dict[str, Any]
    modules: dict[str, ModuleResult]
    geometry: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

