from __future__ import annotations

from app import ENGINE_VERSION
from dataclasses import replace

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
    formula_by_check = {
        "AUTO_ANCHORAGE": "API650_12E_E_6_2_1_1_J",
        "SEISMIC_BASE_SHEAR": "API650_12E_E_7_6_BASE_SHEAR",
        "WIND_STABILITY": "TANK2016_T78_WIND_RECONSTRUCTION",
        "ANCHOR_CHAIR_TOP_PLATE": "AISI_ANCHOR_CHAIR_CAP_TC",
    }
    for module_name, module in modules.items():
        enriched = []
        for check in module.checks:
            entity = None
            if "COURSE_" in check.check_id:
                entity = f"course-{check.check_id.rsplit('_', 1)[-1]}"
            classification = None
            if check.status == "FAIL":
                classification = "ALTERNATIVE_PATH_FAIL" if check.check_id == "AUTO_ANCHORAGE" else "DESIGN_FAIL"
            formula_id = formula_by_check.get(check.check_id)
            if check.check_id.startswith("SHELL_COURSE_"):
                formula_id = "API650_12E_5_6_3_2_ONE_FOOT_DESIGN"
            elif check.check_id.startswith("SEISMIC_HOOP_COURSE_"):
                formula_id = "API650_12E_E_6_1_4_6_HOOP"
            elif check.check_id.startswith("ANCHOR_"):
                formula_id = "API650_12E_TABLE_5_21B_BOLT_STRESS"
            elif check.check_id.startswith("BOTTOM_"):
                formula_id = "API650_12E_5_4_BOTTOM_MINIMUM"
            enriched.append(replace(
                check,
                module=module_name,
                short_title=check.title,
                description=check.message,
                formula_id=formula_id,
                related_entity=entity,
                fail_classification=classification,
            ))
        module.checks = enriched
    engineering_pass = all(module.status in {"PASS", "REVIEW"} for module in modules.values())
    overall = "PASS_WITH_MECHANICAL_ANCHORAGE" if engineering_pass and seismic.values["J"] > 1.54 else ("PASS" if engineering_pass else "FAIL")
    summary = {
        "overall_status": overall,
        "shell": {"status": shell.status, "max_utilization": shell.values["max_utilization"]},
        "bottom": {"status": bottom.status},
        "wind": {"status": wind.status, "anchors_required": wind.values["anchors_required"]},
        "seismic": {"status": seismic.status, "J": seismic.values["J"], "max_hoop_utilization": seismic.values["max_hoop_utilization"]},
        "auto_anchor": {"status": next(c.status for c in seismic.checks if c.check_id == "AUTO_ANCHORAGE"), "classification": seismic.values["anchorage_classification"], "fail_classification": "ALTERNATIVE_PATH_FAIL" if seismic.values["J"] > 1.54 and anchorage.status == "PASS" else None},
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
