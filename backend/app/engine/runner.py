from __future__ import annotations

from app import ENGINE_VERSION
from app.domain.models import CalculationResult
from app.engine.common import canonical_sha256
from app.engine.other import (
    calculate_anchor_chair,
    calculate_anchorage,
    calculate_bottom,
    calculate_weights,
    calculate_wind,
)
from app.engine.seismic import calculate_seismic
from app.engine.shell import calculate_shell
from app.geometry import build_geometry_spec


def calculate(data: dict) -> CalculationResult:
    shell = calculate_shell(data)
    seismic = calculate_seismic(data)
    bottom = calculate_bottom(data)
    wind = calculate_wind(data)
    anchorage = calculate_anchorage(data, seismic)
    chairs = calculate_anchor_chair(data)
    weights = calculate_weights(data)
    modules = {
        "shell": shell,
        "bottom": bottom,
        "wind": wind,
        "seismic": seismic,
        "anchorage": anchorage,
        "anchor_chairs": chairs,
        "weights": weights,
    }
    engineering_pass = all(module.status in {"PASS", "REVIEW"} for module in modules.values())
    overall = "PASS_WITH_MECHANICAL_ANCHORAGE" if engineering_pass and seismic.values["J"] > 1.54 else ("PASS" if engineering_pass else "FAIL")
    summary = {
        "overall_status": overall,
        "shell": {"status": shell.status, "max_utilization": shell.values["max_utilization"]},
        "bottom": {"status": bottom.status},
        "wind": {"status": wind.status, "anchors_required": wind.values["anchors_required"]},
        "seismic": {"status": seismic.status, "J": seismic.values["J"], "max_hoop_utilization": seismic.values["max_hoop_utilization"]},
        "auto_anchor": {"status": "FAIL", "classification": seismic.values["anchorage_classification"]},
        "anchorage": {"required": True, "selected_bolts": anchorage.values["selected_bolts"], "status": anchorage.status, "max_utilization": anchorage.values["max_utilization"]},
        "weights": {"empty_N": weights.values["categories_N"]["empty_non_corroded"]},
    }
    return CalculationResult(
        ENGINE_VERSION,
        data["standard_profile"]["id"],
        overall,
        canonical_sha256(data),
        summary,
        modules,
        build_geometry_spec(data, modules),
    )
