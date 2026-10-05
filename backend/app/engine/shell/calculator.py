from __future__ import annotations

from app.domain.models import AcceptanceCheck, FormulaTrace, ModuleResult
from app.engine.common import MM_TO_IN, M_TO_FT
from app.engine.registry import formula


DESIGN = formula(
    "API650_12E_5_6_3_2_ONE_FOOT_DESIGN",
    "td",
    "One-foot design shell thickness in the native imperial equation units used by TANK",
    "API 650 12th Ed. 5.6.3.2",
    "mm",
    "(2.6*D_ft*(H_ft-1)*G/(Sd_psi*E)+CA_in)*25.4",
)
HYDRO = formula(
    "API650_12E_5_6_3_2_ONE_FOOT_HYDRO",
    "tt",
    "One-foot hydrotest shell thickness",
    "API 650 12th Ed. 5.6.3.2",
    "mm",
    "2.6*D_ft*(H_ft-1)/(St_psi*E)*25.4",
)
MINIMUM = formula(
    "API650_12E_5_6_1_1_MIN_SHELL",
    "tmin",
    "Minimum nominal shell thickness for the T-78 diameter range",
    "API 650 12th Ed. 5.6.1.1",
    "mm",
    "max(calculated_thickness, minimum_nominal_thickness)",
)


def calculate_shell(data: dict) -> ModuleResult:
    geometry = data["geometry"]
    material = data["materials"]["shell"]
    shell = data["shell"]
    diameter_ft = geometry["nominal_diameter_m"] * M_TO_FT
    liquid_height_ft = geometry["design_liquid_height_m"] * M_TO_FT
    course_height_ft = geometry["course_height_m"] * M_TO_FT
    gravity = data["product"]["specific_gravity"]
    design_stress_psi = material["design_stress_psi"]
    hydro_stress_psi = material["hydrotest_stress_psi"]
    efficiency = shell["joint_efficiency"]
    corrosion_in = shell["corrosion_allowance_mm"] * MM_TO_IN
    minimum_mm = shell["minimum_nominal_thickness_mm"]
    traces: list[FormulaTrace] = []
    checks: list[AcceptanceCheck] = []
    rows: list[dict] = []

    for index, course in enumerate(shell["courses"]):
        effective_height_ft = liquid_height_ft - index * course_height_ft
        design_raw = (
            2.6 * diameter_ft * (effective_height_ft - 1.0) * gravity
            / (design_stress_psi * efficiency)
            + corrosion_in
        ) * 25.4
        hydro_raw = (
            2.6 * diameter_ft * (effective_height_ft - 1.0)
            / (hydro_stress_psi * efficiency)
        ) * 25.4
        design_required = max(design_raw, minimum_mm)
        hydro_required = max(hydro_raw, minimum_mm)
        governing = max(design_required, hydro_required)
        selected = course["thickness_mm"]
        utilization = governing / selected
        pressure_utilization = max(design_raw, hydro_raw) / selected
        status = "PASS" if selected + 1e-9 >= governing else "FAIL"
        base_inputs = {
            "D_ft": diameter_ft,
            "H_ft": effective_height_ft,
            "G": gravity,
            "E": efficiency,
        }
        traces.extend(
            [
                FormulaTrace(
                    DESIGN.id, DESIGN.symbol, f"Course {index + 1}: {DESIGN.description}",
                    DESIGN.reference, DESIGN.expression,
                    {**base_inputs, "Sd_psi": design_stress_psi, "CA_in": corrosion_in},
                    design_raw, round(design_required, 4), "mm",
                ),
                FormulaTrace(
                    HYDRO.id, HYDRO.symbol, f"Course {index + 1}: {HYDRO.description}",
                    HYDRO.reference, HYDRO.expression,
                    {**base_inputs, "St_psi": hydro_stress_psi},
                    hydro_raw, round(hydro_required, 4), "mm",
                ),
            ]
        )
        checks.append(
            AcceptanceCheck(
                f"SHELL_COURSE_{index + 1}", f"Shell course {index + 1}", governing, selected,
                "mm", utilization, selected - governing, status, DESIGN.reference,
                f"Selected {selected:.3f} mm vs governing {governing:.4f} mm.",
            )
        )
        rows.append(
            {
                "course": index + 1,
                "height_m": course["height_m"],
                "design_mm": round(design_required, 4),
                "hydrotest_mm": round(hydro_required, 4),
                "selected_mm": selected,
                "utilization": pressure_utilization,
                "minimum_utilization": minimum_mm / selected,
                "status": status,
            }
        )

    return ModuleResult(
        status="PASS" if all(check.status == "PASS" for check in checks) else "FAIL",
        values={"courses": rows, "max_utilization": max(row["utilization"] for row in rows)},
        checks=checks,
        traces=traces,
    )
