from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class DesignVariable:
    id: str
    name: str
    symbol: str
    module: str
    path: str
    unit: str
    classification: str
    editable: bool
    derived: bool
    standard_defined: bool
    minimum: float | None
    maximum: float | None
    increment: float | None
    discrete_values: tuple[float, ...]
    affects_checks: tuple[str, ...]
    influence: str
    source: str

    def public(self, inputs: dict[str, Any]) -> dict[str, Any]:
        value: Any = inputs
        for part in self.path.replace("]", "").replace("[", ".").split("."):
            value = value[int(part)] if isinstance(value, list) else value[part]
        return {**asdict(self), "current_value": value, "discrete_values": list(self.discrete_values), "affects_checks": list(self.affects_checks)}


VARIABLES = (
    DesignVariable("annular_plate_thickness", "Espesor nominal del anillo anular", "ta", "bottom", "bottom.annular_selected_mm", "mm", "USER_DESIGN_VARIABLE", True, False, False, 9.0, 25.0, None, (9.5, 10.0, 12.0, 14.0, 16.0, 19.0, 22.0, 25.0), ("AUTO_ANCHORAGE", "BOTTOM_ANNULAR"), "FAVORABLE_UP", "API 650 plate selection / project catalog"),
    DesignVariable("anchor_count", "Número de pernos", "n", "anchorage", "anchorage.selected_bolts", "und", "USER_DESIGN_VARIABLE", True, False, False, 4, 160, 4, tuple(range(64, 161, 4)), ("ANCHOR_DESIGN_PRESSURE", "ANCHOR_SEISMIC_OPE", "ANCHOR_DESIGN_PRESSURE_SEISMIC"), "FAVORABLE_UP", "API 650 anchorage layout"),
    DesignVariable("anchor_chair_top_plate", "Espesor de placa superior de silla", "tc", "anchorage", "anchor_chair.top_plate_thickness_mm", "mm", "USER_DESIGN_VARIABLE", True, False, False, 25.4, 76.2, None, (50.8, 57.2, 63.5, 69.9, 76.2), ("ANCHOR_CHAIR_TOP_PLATE",), "FAVORABLE_UP", "AISI/TANK chair design"),
    DesignVariable("course_6_thickness", "Espesor seleccionado del curso 6", "t6", "shell", "shell.courses[5].thickness_mm", "mm", "USER_DESIGN_VARIABLE", True, False, False, 8.0, 25.0, None, (9.5, 12.0, 14.0, 16.0, 19.0, 22.0, 25.0), ("SHELL_COURSE_6", "SEISMIC_HOOP_COURSE_6"), "FAVORABLE_UP", "API 650 plate selection / project catalog"),
)

FIXED_VARIABLES = (
    {"id": "seismic_acceleration", "name": "Aceleración pico", "path": "seismic.Sp", "unit": "g", "classification": "PROJECT_CONDITION", "editable": False, "influence": "ADVERSE_UP", "source": "Project seismic basis"},
    {"id": "tank_diameter", "name": "Diámetro nominal", "path": "geometry.nominal_diameter_m", "unit": "m", "classification": "PROJECT_CONDITION", "editable": False, "influence": "CONTEXT", "source": "Project geometry"},
    {"id": "auto_anchor_limit", "name": "Límite J autoanclado", "value": 1.54, "unit": "ratio", "classification": "STANDARD_DEFINED", "editable": False, "influence": "FIXED", "source": "API 650 Annex E.6.2.1.1"},
)


def variables_for(check_id: str, inputs: dict[str, Any]) -> list[dict[str, Any]]:
    return [item.public(inputs) for item in VARIABLES if check_id in item.affects_checks]


def fixed_for(check_id: str, inputs: dict[str, Any]) -> list[dict[str, Any]]:
    if check_id != "AUTO_ANCHORAGE":
        return []
    result = []
    for item in FIXED_VARIABLES:
        row = dict(item)
        if "path" in row:
            value: Any = inputs
            for part in row["path"].split("."):
                value = value[part]
            row["current_value"] = value
        else:
            row["current_value"] = row.pop("value")
        result.append(row)
    return result
