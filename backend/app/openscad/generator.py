from __future__ import annotations

from pathlib import Path


def render_scad(spec: dict) -> str:
    courses = "\n".join(
        f"course({course['elevation_m'] * 1000:.3f}, {course['height_m'] * 1000:.3f}, {course['thickness_mm']:.3f});"
        for course in spec["courses"]
    )
    return f'''// TANK650 ENGINE parametric model - generated, do not hand edit
$fn = 180;
tank_radius = {spec['nominal_diameter_m'] * 500:.3f};
anchor_radius = {spec['anchors'][0]['radius_m'] * 1000:.3f};
anchor_count = {len(spec['anchors'])};
anchor_diameter = {spec['anchors'][0]['diameter_mm']:.3f};

module course(z, h, t) {{
  translate([0,0,z]) difference() {{
    cylinder(h=h, r=tank_radius + t);
    translate([0,0,-0.1]) cylinder(h=h+0.2, r=tank_radius);
  }}
}}

module anchor() {{
  color("#c77b30") cylinder(h=700, d=anchor_diameter);
}}

color("#aebbc8") union() {{
{courses}
}}

color("#8093a6") cylinder(h={spec['bottom']['central_thickness_mm']:.3f}, r=tank_radius);

for (i=[0:anchor_count-1]) {{
  rotate([0,0,i*360/anchor_count]) translate([anchor_radius,0,0]) anchor();
}}
'''


def write_scad(spec: dict, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_scad(spec), encoding="utf-8")
    return target

