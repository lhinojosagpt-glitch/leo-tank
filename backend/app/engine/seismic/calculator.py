from __future__ import annotations

import math

from app.domain.models import AcceptanceCheck, FormulaTrace, ModuleResult
from app.engine.common import FTLB_TO_NM, LB_TO_N, M_TO_FT, MM_TO_IN, PSI_TO_KPA
from app.engine.registry import formula


def _def(formula_id: str, symbol: str, description: str, reference: str, unit: str, expression: str):
    return formula(formula_id, symbol, description, reference, unit, expression)


SS = _def("API650_12E_E_4_3_1_SS", "Ss", "Mapped MCE at 0.2 s", "API 650 Annex E.4.3-1", "g", "2.5*Sp")
S1 = _def("API650_12E_E_4_3_2_S1", "S1", "Mapped MCE at 1.0 s", "API 650 Annex E.4.3-2", "g", "1.25*Sp")
TS = _def("API650_12E_E_2_2_TS", "Ts", "Transition period", "API 650 Annex E.2.2", "s", "Fv*S1/(Fa*Ss)")
KS = _def("API650_12E_E_4_5_2_KS", "Ks", "Sloshing period coefficient", "API 650 Annex E.4.5.2-c", "s/ft^0.5", "0.578/sqrt(tanh(3.68*H/D))")
TC = _def("API650_12E_E_4_5_2_TC", "Tc", "Convective sloshing period", "API 650 Annex E.4.5.2-b", "s", "Ks*sqrt(D)")
SDS = _def("API650_12E_E_4_6_1_SDS", "SDS", "Design spectral acceleration", "API 650 Annex E.4.6.1-1", "g", "2.5*Q*Fa*Sp")
AI = _def("API650_12E_E_4_6_1_AI", "Ai", "Impulsive spectral acceleration", "API 650 Annex E.4.6.1-1", "g", "max(SDS*I/Rwi, lower_bound)")
AC = _def("API650_12E_E_4_6_1_AC", "Ac", "Convective spectral acceleration", "API 650 Annex E.4.6.1-5", "g", "min(2.5*K*Q*Fa*Sp*(I/Rwc)*Ts*TL/Tc^2, Ai)")
WC = _def("API650_12E_E_6_1_1_3_WC", "Wc", "Effective convective liquid weight", "API 650 Annex E.6.1.1-3", "N", "0.230*(D/H)*Wp*tanh(3.67*H/D)")
WI = _def("API650_12E_E_6_1_1_1_WI", "Wi", "Effective impulsive liquid weight", "API 650 Annex E.6.1.1-1", "N", "Wp*tanh(0.866*D/H)/(0.866*D/H)")
TOTAL_SHEAR = _def("API650_12E_E_6_1_1_V", "V", "Total design base shear", "API 650 Annex E.6.1-1", "N", "sqrt(Vc^2+Vi^2)")
MRW = _def("API650_12E_E_6_1_5_1_MRW", "Mrw", "Ringwall overturning moment", "API 650 Annex E.6.1.5-1", "N*m", "sqrt((Ai*(Wi*Xi+Ws*Xs+Wr*Xr))^2+(Ac*Wc*Xc)^2)")
MS = _def("API650_12E_E_6_1_5_2_MS", "Ms", "Slab overturning moment", "API 650 Annex E.6.1.5-2", "N*m", "sqrt((Ai*(Wi*Xis+Ws*Xs+Wr*Xr))^2+(Ac*Wc*Xcs)^2)")
J_DEF = _def("API650_12E_E_6_2_1_1_J", "J", "Anchorage ratio", "API 650 Annex E.6.2.1.1.1-1", "1", "Mrw/(D^2*(wt*(1-0.4*Av)+wa-0.4*wint))")
HOOP = _def("API650_12E_E_6_1_4_6_HOOP", "sigma_h", "Combined seismic hoop stress", "API 650 Annex E.6.1.4-6", "kPa", "(sqrt(Ni^2+Nc^2+(Av*Nh/2.5)^2)+Nh)/t")


def _trace(defn, inputs: dict, raw: float, digits: int = 5) -> FormulaTrace:
    return FormulaTrace(
        defn.id, defn.symbol, defn.description, defn.reference, defn.expression,
        inputs, raw, round(raw, digits), defn.unit,
    )


def calculate_seismic(data: dict) -> ModuleResult:
    g = data["product"]["specific_gravity"]
    geom = data["geometry"]
    s = data["seismic"]
    shell = data["shell"]
    weights = data["weights"]
    d_ft = geom["nominal_diameter_m"] * M_TO_FT
    h_ft = geom["design_liquid_height_m"] * M_TO_FT
    sp, fa, fv = s["Sp"], s["Fa"], s["Fv"]
    ss = 2.5 * sp
    s1 = 1.25 * sp
    ts = fv * s1 / (fa * ss)
    ks = 0.578 / math.sqrt(math.tanh(3.68 * h_ft / d_ft))
    tc = ks * math.sqrt(d_ft)
    sds = 2.5 * s["Q"] * fa * sp
    ai_unbounded = sds * s["importance_factor"] / s["Rwi"]
    ai = max(ai_unbounded, s["Ai_lower_bound"])
    ac = min(
        2.5 * s["K"] * s["Q"] * fa * sp * (s["importance_factor"] / s["Rwc"])
        * ts * s["TL_s"] / tc**2,
        ai,
    )
    wp_lb = weights["operating_fluid_lb"]
    wc_lb = 0.230 * (d_ft / h_ft) * wp_lb * math.tanh(3.67 * h_ft / d_ft)
    wi_lb = wp_lb * math.tanh(0.866 * d_ft / h_ft) / (0.866 * d_ft / h_ft)
    ws_lb = weights["shell_and_attachments_lb"]
    wr_lb = weights["roof_seismic_lb"]
    wf_lb = weights["bottom_lb"]
    vc_lb = ac * wc_lb
    vi_lb = ai * (ws_lb + wr_lb + wf_lb + wi_lb)
    total_lb = math.sqrt(vc_lb**2 + vi_lb**2)

    ratio = h_ft / d_ft
    xc_ft = (1 - (math.cosh(3.67 * ratio) - 1) / (3.67 * ratio * math.sinh(3.67 * ratio))) * h_ft
    xi_ft = 0.375 * h_ft
    xcs_ft = (1 - (math.cosh(3.67 * ratio) - 1.937) / (3.67 * ratio * math.sinh(3.67 * ratio))) * h_ft
    xis_ft = 0.375 * (1 + 1.333 * ((0.866 * d_ft / h_ft) / math.tanh(0.866 * d_ft / h_ft) - 1)) * h_ft
    xs_ft, xr_ft = weights["shell_cg_ft"], weights["roof_cg_ft"]
    mrw_ftlb = math.sqrt((ai * (wi_lb * xi_ft + ws_lb * xs_ft + wr_lb * xr_ft)) ** 2 + (ac * wc_lb * xc_ft) ** 2)
    ms_ftlb = math.sqrt((ai * (wi_lb * xis_ft + ws_lb * xs_ft + wr_lb * xr_ft)) ** 2 + (ac * wc_lb * xcs_ft) ** 2)
    av = 0.47 * sds
    ge = (1 - 0.4 * av) * g
    ta_in = data["bottom"]["annular_effective_thickness_mm"] * MM_TO_IN
    fy_psi = data["materials"]["bottom"]["yield_strength_psi"]
    wa_lbft = min(7.9 * ta_in * math.sqrt(fy_psi * h_ft * ge), 1.28 * h_ft * d_ft * ge)
    wt_lbft = (wr_lb + weights["shell_only_lb"]) / (d_ft * math.pi)
    wint_lbft = s["internal_pressure_line_load_lb_ft"]
    j = mrw_ftlb / (d_ft**2 * (wt_lbft * (1 - 0.4 * av) + wa_lbft - 0.4 * wint_lbft))

    traces = [
        _trace(SS, {"Sp": sp}, ss), _trace(S1, {"Sp": sp}, s1),
        _trace(TS, {"Fv": fv, "S1": s1, "Fa": fa, "Ss": ss}, ts),
        _trace(KS, {"H_ft": h_ft, "D_ft": d_ft}, ks),
        _trace(TC, {"Ks": ks, "D_ft": d_ft}, tc, 4),
        _trace(SDS, {"Q": s["Q"], "Fa": fa, "Sp": sp}, sds, 4),
        _trace(AI, {"SDS": sds, "I": s["importance_factor"], "Rwi": s["Rwi"], "lower_bound": s["Ai_lower_bound"]}, ai, 5),
        _trace(AC, {"K": s["K"], "Q": s["Q"], "Fa": fa, "Sp": sp, "I": s["importance_factor"], "Rwc": s["Rwc"], "Ts": ts, "TL": s["TL_s"], "Tc": tc, "Ai": ai}, ac, 6),
        _trace(WC, {"D_ft": d_ft, "H_ft": h_ft, "Wp_lb": wp_lb}, wc_lb * LB_TO_N, 0),
        _trace(WI, {"D_ft": d_ft, "H_ft": h_ft, "Wp_lb": wp_lb}, wi_lb * LB_TO_N, 0),
        _trace(TOTAL_SHEAR, {"Vc_lb": vc_lb, "Vi_lb": vi_lb}, total_lb * LB_TO_N, 0),
        _trace(MRW, {"Ai": ai, "Wi_lb": wi_lb, "Xi_ft": xi_ft, "Ws_lb": ws_lb, "Xs_ft": xs_ft, "Wr_lb": wr_lb, "Xr_ft": xr_ft, "Ac": ac, "Wc_lb": wc_lb, "Xc_ft": xc_ft}, mrw_ftlb * FTLB_TO_NM, 0),
        _trace(MS, {"Ai": ai, "Wi_lb": wi_lb, "Xis_ft": xis_ft, "Ws_lb": ws_lb, "Xs_ft": xs_ft, "Wr_lb": wr_lb, "Xr_ft": xr_ft, "Ac": ac, "Wc_lb": wc_lb, "Xcs_ft": xcs_ft}, ms_ftlb * FTLB_TO_NM, 0),
        _trace(J_DEF, {"Mrw_ftlb": mrw_ftlb, "D_ft": d_ft, "wt_lb_ft": wt_lbft, "Av": av, "wa_lb_ft": wa_lbft, "wint_lb_ft": wint_lbft}, j, 4),
    ]

    if j <= 0.785:
        anchorage_class, auto_status = "AUTO_ANCHORED_NO_UPLIFT", "PASS"
    elif j <= 1.54:
        anchorage_class, auto_status = "UPLIFT_REGIME_CHECK_REQUIRED", "REVIEW"
    else:
        anchorage_class, auto_status = "MECHANICAL_ANCHORAGE_REQUIRED", "FAIL"
    checks = [
        AcceptanceCheck("SEISMIC_BASE_SHEAR", "Base shear resistance", total_lb * LB_TO_N, s["shear_resistance_N"], "N", total_lb * LB_TO_N / s["shear_resistance_N"], s["shear_resistance_N"] - total_lb * LB_TO_N, "PASS" if total_lb * LB_TO_N <= s["shear_resistance_N"] else "FAIL", "API 650 Annex E.7.6-1", "Sliding resistance compared with total design base shear."),
        AcceptanceCheck("AUTO_ANCHORAGE", "Self-anchored stability", j, 1.54, "ratio", j / 1.54, 1.54 - j, auto_status, "API 650 Annex E.6.2.1.1", anchorage_class.replace("_", " ").title()),
    ]

    hoop_rows = []
    allowable_kpa = min(0.9 * min(data["materials"]["shell"]["yield_strength_psi"], data["materials"]["weld"]["yield_strength_psi"]), data["materials"]["shell"]["design_stress_psi"] * 1.33) * PSI_TO_KPA
    for index, course in enumerate(shell["courses"]):
        y_ft = h_ft - index * geom["course_height_m"] * M_TO_FT
        ni = math.tanh(0.866 * d_ft / h_ft) * 4.5 * ai * g * d_ft * h_ft * ((y_ft / h_ft) - 0.5 * (y_ft / h_ft) ** 2)
        nc = math.cosh(3.68 * (h_ft - y_ft) / d_ft) / math.cosh(3.68 * h_ft / d_ft) * 0.98 * ac * g * d_ft**2
        nh = 0.0361 * g * y_ft * 12 * d_ft * 12 / 2
        t_in = course["thickness_mm"] * MM_TO_IN
        stress_psi = (math.sqrt(ni**2 + nc**2 + (av * nh / 2.5) ** 2) + nh) / t_in
        stress_kpa = stress_psi * PSI_TO_KPA
        utilization = stress_kpa / allowable_kpa
        status = "PASS" if utilization <= 1 else "FAIL"
        hoop_rows.append({"course": index + 1, "stress_kPa": stress_kpa, "allowable_kPa": allowable_kpa, "utilization": utilization, "margin_kPa": allowable_kpa - stress_kpa, "status": status})
        traces.append(_trace(HOOP, {"course": index + 1, "Ni_lb_in": ni, "Nc_lb_in": nc, "Nh_lb_in": nh, "Av": av, "thickness_in": t_in}, stress_kpa, 2))
        checks.append(AcceptanceCheck(f"SEISMIC_HOOP_COURSE_{index + 1}", f"Seismic hoop stress course {index + 1}", stress_kpa, allowable_kpa, "kPa", utilization, allowable_kpa - stress_kpa, status, HOOP.reference, f"Course {index + 1} combined hoop stress."))

    values = {
        "Sp": sp, "Ss": ss, "S1": s1, "Fa": fa, "Fv": fv, "Ts_s": ts, "Ks": ks,
        "Tc_s": tc, "SDS": sds, "Ai": ai, "Ac": ac,
        "Wc_N": wc_lb * LB_TO_N, "Wi_N": wi_lb * LB_TO_N,
        "Vc_N": vc_lb * LB_TO_N, "Vi_N": vi_lb * LB_TO_N, "V_N": total_lb * LB_TO_N,
        "Xc_m": xc_ft / M_TO_FT, "Xi_m": xi_ft / M_TO_FT,
        "Xcs_m": xcs_ft / M_TO_FT, "Xis_m": xis_ft / M_TO_FT,
        "Mrw_Nm": mrw_ftlb * FTLB_TO_NM, "Ms_Nm": ms_ftlb * FTLB_TO_NM,
        "Av": av, "Ge": ge, "wa_N_cm": wa_lbft * 0.0145939029372,
        "wt_N_cm": wt_lbft * 0.0145939029372, "J": j,
        "anchorage_classification": anchorage_class,
        "required_anchor_bolts": max(math.ceil(math.pi * d_ft / 10), 4),
        "shell_compressive_stress_kPa": s["shell_compressive_stress_kPa"],
        "shell_allowable_stress_kPa": s["shell_allowable_stress_kPa"],
        "sloshing_height_m": s["sloshing_height_m"],
        "required_freeboard_m": s["required_freeboard_m"],
        "hoop": hoop_rows,
        "max_hoop_utilization": max(row["utilization"] for row in hoop_rows),
    }
    status = "PASS" if all(c.status in {"PASS", "REVIEW"} for c in checks if c.check_id != "AUTO_ANCHORAGE") else "FAIL"
    return ModuleResult(status=status, values=values, checks=checks, traces=traces)
