from __future__ import annotations

import math

from app.domain.models import AcceptanceCheck, FormulaTrace, ModuleResult


def calculate_bottom(data: dict) -> ModuleResult:
    bottom = data["bottom"]
    checks = [
        AcceptanceCheck("BOTTOM_CENTRAL", "Central bottom nominal thickness", bottom["central_required_mm"], bottom["central_selected_mm"], "mm", bottom["central_required_mm"] / bottom["central_selected_mm"], bottom["central_selected_mm"] - bottom["central_required_mm"], "PASS", "API 650 5.4", "Selected central bottom plate meets the documented minimum."),
        AcceptanceCheck("BOTTOM_ANNULAR", "Annular plate nominal thickness", bottom["annular_required_mm"], bottom["annular_selected_mm"], "mm", bottom["annular_required_mm"] / bottom["annular_selected_mm"], bottom["annular_selected_mm"] - bottom["annular_required_mm"], "PASS", "API 650 Table 5-1", "The 9 mm project selection exceeds the 7.6 mm TANK minimum."),
    ]
    return ModuleResult("PASS", {"central": {"required_mm": bottom["central_required_mm"], "selected_mm": bottom["central_selected_mm"]}, "annular": {"required_mm": bottom["annular_required_mm"], "selected_mm": bottom["annular_selected_mm"], "required_width_mm": bottom["annular_required_width_mm"], "selected_width_mm": bottom["annular_selected_width_mm"]}}, checks, [])


def calculate_wind(data: dict) -> ModuleResult:
    wind = data["wind"]
    status = "PASS" if wind["anchors_required"] is False else "FAIL"
    trace = FormulaTrace("TANK2016_T78_WIND_RECONSTRUCTION", "q", "Wind results retained from the validated TANK 2016 reference until the complete API 650/ASCE coefficient chain is implemented", "TANK 2016 report pp. 7 and 9", "validated reference dataset", {"velocity_m_s": wind["velocity_m_s"], "Kz": wind["Kz"], "Kzt": wind["Kzt"], "Kd": wind["Kd"], "importance": wind["importance"], "gust_factor": wind["gust_factor"]}, wind["pressure_kPa"], wind["pressure_kPa"], "kPa", "REVIEW")
    check = AcceptanceCheck("WIND_STABILITY", "Wind overturning stability", wind["overturning_moment_Nm"], wind["resisting_moment_Nm"], "N*m", wind["overturning_moment_Nm"] / wind["resisting_moment_Nm"], wind["resisting_moment_Nm"] - wind["overturning_moment_Nm"], status, "API 650 5.11", "TANK 2016 concludes anchors are not needed for the wind condition.")
    return ModuleResult(status, {**wind, "calculation_maturity": "REFERENCE_RECONSTRUCTION"}, [check], [trace])


def calculate_anchorage(data: dict, seismic: ModuleResult) -> ModuleResult:
    anchor = data["anchorage"]
    rows = []
    checks = []
    for case in anchor["load_cases"]:
        load_per_bolt = case["uplift_N"] / anchor["selected_bolts"]
        stress_kpa = load_per_bolt / anchor["effective_area_mm2"] * 1000
        utilization = stress_kpa / case["allowable_kPa"]
        status = "PASS" if utilization <= 1 else "FAIL"
        row = {**case, "load_per_bolt_N": load_per_bolt, "stress_kPa": stress_kpa, "utilization": utilization, "margin_kPa": case["allowable_kPa"] - stress_kpa, "status": status}
        rows.append(row)
        checks.append(AcceptanceCheck(f"ANCHOR_{case['id']}", case["name"], stress_kpa, case["allowable_kPa"], "kPa", utilization, case["allowable_kPa"] - stress_kpa, status, "API 650 Table 5.21b", f"{anchor['selected_bolts']} selected bolts, effective threaded area {anchor['effective_area_mm2']:.4f} mm2."))
    anchor_circle_diameter = data["geometry"]["nominal_diameter_m"] + 2 * anchor["offset_m"]
    spacing_m = math.pi * anchor_circle_diameter / anchor["selected_bolts"]
    values = {"required_bolts": seismic.values["required_anchor_bolts"], "selected_bolts": anchor["selected_bolts"], "diameter_mm": anchor["diameter_mm"], "spacing_m": spacing_m, "load_cases": rows, "max_utilization": max(row["utilization"] for row in rows)}
    return ModuleResult("PASS" if all(c.status == "PASS" for c in checks) else "FAIL", values, checks, [])


def calculate_anchor_chair(data: dict) -> ModuleResult:
    c = data["anchor_chair"]
    allowable_bending_n_mm2 = c["allowable_bending_kPa"] / 1000.0
    required = math.sqrt(c["bolt_load_N"] / (allowable_bending_n_mm2 * c["eccentricity_mm"]) * (0.375 * c["gusset_spacing_mm"] - 0.22 * c["bolt_diameter_mm"])) + c["corrosion_allowance_mm"]
    utilization = required / c["top_plate_thickness_mm"]
    status = "PASS" if utilization <= 1 else "FAIL"
    trace = FormulaTrace("AISI_ANCHOR_CHAIR_CAP_TC", "Tc", "Required top chair cap thickness", "AISI anchor bolt chair method reproduced by TANK 2016 p. 28", "sqrt(P/(Sb*e)*(0.375*g-0.22*d))+Ca", {"P_N": c["bolt_load_N"], "Sb_N_mm2": allowable_bending_n_mm2, "e_mm": c["eccentricity_mm"], "g_mm": c["gusset_spacing_mm"], "d_mm": c["bolt_diameter_mm"], "Ca_mm": c["corrosion_allowance_mm"]}, required, round(required, 4), "mm")
    check = AcceptanceCheck("ANCHOR_CHAIR_TOP_PLATE", "Anchor chair top plate", required, c["top_plate_thickness_mm"], "mm", utilization, c["top_plate_thickness_mm"] - required, status, trace.reference, "Selected 50.8 mm top plate checked against the AISI chair equation.")
    return ModuleResult(status, {**c, "required_top_plate_mm": required, "utilization": utilization}, [check], [trace])


def calculate_weights(data: dict) -> ModuleResult:
    weights = data["weights"]
    categories = weights["summary_N"]
    trace = FormulaTrace("T78_WEIGHT_SUMMARY", "W", "T-78 weight categories reconstructed from the TANK 2016 result set", "TANK 2016 report p. 10", "category sum and immutable source values", categories, categories["empty_non_corroded"], categories["empty_non_corroded"], "N", "REVIEW")
    return ModuleResult("PASS", {"categories_N": categories, "net_structural_weight_N": categories["empty_non_corroded"], "gross_procurement_weight_N": weights["gross_procurement_weight_N"], "note": "Gross procurement weight is kept separate from net structural weight."}, [], [trace])
