from __future__ import annotations

import math


def build_geometry_spec(data: dict) -> dict:
    geometry = data["geometry"]
    anchor = data["anchorage"]
    courses = []
    z = 0.0
    for index, course in enumerate(data["shell"]["courses"], start=1):
        courses.append(
            {
                "id": f"course-{index}",
                "name": f"Course {index}",
                "elevation_m": z,
                "height_m": course["height_m"],
                "thickness_mm": course["thickness_mm"],
                "material": course["material"],
            }
        )
        z += course["height_m"]
    radius_m = geometry["nominal_diameter_m"] / 2 + anchor["offset_m"]
    anchors = [
        {
            "id": f"anchor-{i + 1:02d}",
            "name": f"Bolt {i + 1:02d}",
            "angle_deg": i * 360 / anchor["selected_bolts"],
            "radius_m": radius_m,
            "diameter_mm": anchor["diameter_mm"],
        }
        for i in range(anchor["selected_bolts"])
    ]
    return {
        "schema_version": "1.0",
        "tank_tag": data["project"]["tank_tag"],
        "nominal_diameter_m": geometry["nominal_diameter_m"],
        "internal_diameter_m": geometry["internal_diameter_m"],
        "shell_height_m": geometry["shell_height_m"],
        "bottom_slope_percent": geometry["bottom_slope_percent"],
        "courses": courses,
        "bottom": {
            "central_thickness_mm": data["bottom"]["central_selected_mm"],
            "annular_thickness_mm": data["bottom"]["annular_selected_mm"],
            "annular_width_mm": data["bottom"]["annular_selected_width_mm"],
        },
        "physical_roof": data["roof"]["physical_roof"],
        "analysis_roof": data["roof"]["analysis_roof"],
        "wind_girder": data["wind_girder"],
        "anchors": anchors,
        "anchor_spacing_m": 2 * math.pi * radius_m / anchor["selected_bolts"],
        "visualization_note": "Thickness exaggeration is a display mode only; calculation geometry is preserved here.",
    }

