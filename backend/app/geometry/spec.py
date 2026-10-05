from __future__ import annotations

import math
from typing import Any


def _values(modules: dict[str, Any] | None, name: str) -> dict:
    if not modules or name not in modules:
        return {}
    module = modules[name]
    return module.values if hasattr(module, "values") else module.get("values", {})


def build_geometry_spec(data: dict, modules: dict[str, Any] | None = None) -> dict:
    geometry = data["geometry"]
    anchor = data["anchorage"]
    shell_values = _values(modules, "shell")
    seismic_values = _values(modules, "seismic")
    anchorage_values = _values(modules, "anchorage")
    shell_results = {row["course"]: row for row in shell_values.get("courses", [])}
    hoop_results = {row["course"]: row for row in seismic_values.get("hoop", [])}
    plate_count = 24
    plate_angle_deg = 360.0 / plate_count
    developed_width_m = math.pi * geometry["internal_diameter_m"] / plate_count
    courses = []
    z = 0.0
    for index, course in enumerate(data["shell"]["courses"], start=1):
        result = shell_results.get(index, {})
        hoop = hoop_results.get(index, {})
        stagger_deg = plate_angle_deg / 2 if index % 2 == 0 else 0.0
        plates = [
            {
                "id": f"C{index:02d}-P{plate:02d}",
                "name": f"Plate C{index:02d}-P{plate:02d}",
                "entity_type": "shell_plate",
                "course": index,
                "plate": plate,
                "start_angle_deg": (stagger_deg + (plate - 1) * plate_angle_deg) % 360,
                "angle_deg": plate_angle_deg,
                "nominal_width_m": 6.0,
                "developed_width_m": developed_width_m,
                "height_m": course["height_m"],
                "thickness_mm": course["thickness_mm"],
                "material": course["material"],
                "corrosion_allowance_mm": data["shell"]["corrosion_allowance_mm"],
                "required_design_mm": result.get("design_mm"),
                "required_hydrotest_mm": result.get("hydrotest_mm"),
                "selected_mm": result.get("selected_mm", course["thickness_mm"]),
                "utilization": result.get("utilization"),
                "hoop_utilization": hoop.get("utilization"),
                "status": result.get("status", "NOT_CALCULATED"),
            }
            for plate in range(1, plate_count + 1)
        ]
        courses.append(
            {
                "id": f"course-{index}",
                "name": f"Course {index}",
                "entity_type": "shell_course",
                "elevation_m": z,
                "height_m": course["height_m"],
                "thickness_mm": course["thickness_mm"],
                "material": course["material"],
                "corrosion_allowance_mm": data["shell"]["corrosion_allowance_mm"],
                "plate_count": plate_count,
                "stagger_angle_deg": stagger_deg,
                "required_design_mm": result.get("design_mm"),
                "required_hydrotest_mm": result.get("hydrotest_mm"),
                "selected_mm": result.get("selected_mm", course["thickness_mm"]),
                "utilization": result.get("utilization"),
                "hoop_utilization": hoop.get("utilization"),
                "status": result.get("status", "NOT_CALCULATED"),
                "plates": plates,
            }
        )
        z += course["height_m"]

    radius_m = geometry["nominal_diameter_m"] / 2 + anchor["offset_m"]
    anchor_cases = anchorage_values.get("load_cases", [])
    governing_anchor = max(anchor_cases, key=lambda row: row.get("utilization", 0), default={})
    anchors = [
        {
            "id": f"anchor-{i + 1:02d}",
            "name": f"Anchor A-{i + 1:02d}",
            "entity_type": "anchor",
            "angle_deg": i * 360 / anchor["selected_bolts"],
            "radius_m": radius_m,
            "diameter_mm": anchor["diameter_mm"],
            "material": data["materials"]["anchors"]["name"],
            "corrosion_allowance_mm": anchor["corrosion_allowance_mm"],
            "load_N": governing_anchor.get("load_per_bolt_N"),
            "stress_kPa": governing_anchor.get("stress_kPa"),
            "allowable_kPa": governing_anchor.get("allowable_kPa"),
            "utilization": governing_anchor.get("utilization"),
            "status": governing_anchor.get("status", "NOT_CALCULATED"),
        }
        for i in range(anchor["selected_bolts"])
    ]

    tank_radius_m = geometry["nominal_diameter_m"] / 2
    dome_height_m = round(geometry["nominal_diameter_m"] * 0.12, 3)
    dome_sphere_radius_m = (tank_radius_m**2 + dome_height_m**2) / (2 * dome_height_m)
    return {
        "schema_version": "2.0",
        "tank_tag": data["project"]["tank_tag"],
        "nominal_diameter_m": geometry["nominal_diameter_m"],
        "internal_diameter_m": geometry["internal_diameter_m"],
        "shell_height_m": geometry["shell_height_m"],
        "bottom_slope_percent": geometry["bottom_slope_percent"],
        "courses": courses,
        "bottom": {
            "entity_type": "bottom",
            "central_thickness_mm": data["bottom"]["central_selected_mm"],
            "annular_thickness_mm": data["bottom"]["annular_selected_mm"],
            "annular_width_mm": data["bottom"]["annular_selected_width_mm"],
            "slope_percent": geometry["bottom_slope_percent"],
            "sump_diameter_m": 1.58,
            "layout": {
                "basis": "AFC drawing DMM-2019-10119-M-018",
                "representation": "AFC_INFORMED_REPRESENTATIVE",
                "central_procurement_plates": 115,
                "annular_procurement_plates": 12,
                "closure_plates": 5,
                "nominal_plate_length_m": 6.0,
                "nominal_plate_width_m": 2.4,
                "representative_row_spacing_m": 2.4,
            },
        },
        "physical_roof": {
            **data["roof"]["physical_roof"],
            "entity_type": "roof",
            "representation": "REPRESENTATIVE",
            "base_radius_m": tank_radius_m,
            "springline_z_m": geometry["shell_height_m"],
            "cap_height_m": dome_height_m,
            "sphere_radius_m": dome_sphere_radius_m,
            "frequency": 6,
            "azimuth_segments": 24,
            "show_panels": True,
            "show_struts": True,
            "show_hubs": True,
            "engineering_scope": "SUPPLIER_SCOPE_NOT_IMPLEMENTED",
        },
        "analysis_roof": data["roof"]["analysis_roof"],
        "wind_girder": data["wind_girder"],
        "anchors": anchors,
        "anchor_chairs": {**data["anchor_chair"], "entity_type": "anchor_chair", "count": anchor["selected_bolts"]},
        "anchor_spacing_m": 2 * math.pi * radius_m / anchor["selected_bolts"],
        "plate_layout": {
            "basis": "AFC drawing DMM-2019-10119-M-019",
            "representation": "AFC_INFORMED_REPRESENTATIVE",
            "plates_per_course": plate_count,
            "total_shell_plates": plate_count * len(courses),
            "nominal_procurement_width_m": 6.0,
            "developed_sector_width_m": developed_width_m,
            "staggering": "half_plate_between_adjacent_courses",
        },
        "visualization_note": "Plate layout is AFC-informed and representative. Thickness exaggeration is a display mode only; calculation geometry is unchanged.",
    }
