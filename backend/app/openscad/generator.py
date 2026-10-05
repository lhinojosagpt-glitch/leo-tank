from __future__ import annotations

from pathlib import Path


def render_scad(spec: dict) -> str:
    courses = "\n".join(
        f"course({course['elevation_m'] * 1000:.3f}, {course['height_m'] * 1000:.3f}, {course['thickness_mm']:.3f});"
        for course in spec["courses"]
    )
    seams = "\n".join(
        f"course_seams({course['elevation_m'] * 1000:.3f}, {course['height_m'] * 1000:.3f}, {course.get('stagger_angle_deg', 0):.3f}, {course.get('plate_count', 24)});"
        for course in spec["courses"]
    )
    roof = spec.get("physical_roof", {})
    roof_height = roof.get("cap_height_m", spec["nominal_diameter_m"] * 0.12) * 1000
    shell_height = spec["shell_height_m"] * 1000
    return f'''// TANK650 ENGINE v0.2 parametric model - generated, do not hand edit
// Plate seams and roof framing are representative visualization geometry.
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

module seam_rod(z, h, a) {{
  rotate([0,0,a]) translate([tank_radius+6,0,z]) color("#526778") cube([10,8,h]);
}}

module course_seams(z, h, offset, count) {{
  for (i=[0:count-1]) seam_rod(z, h, offset+i*360/count);
}}

module geodesic_roof() {{
  // Dome envelope is clipped to its springline and joined to the top shell edge.
  color([0.72,0.82,0.86,0.34])
    translate([0,0,{shell_height:.3f}])
      scale([1,1,{roof_height / (spec['nominal_diameter_m'] * 500):.6f}])
        intersection() {{ sphere(r=tank_radius); translate([-tank_radius,-tank_radius,0]) cube([2*tank_radius,2*tank_radius,tank_radius]); }}
  // Representative meridional struts and horizontal rings.
  for (a=[0:15:345]) rotate([0,0,a])
    color("#d7e1e7") hull() {{
      translate([tank_radius,0,{shell_height:.3f}]) sphere(r=18,$fn=16);
      translate([0,0,{shell_height + roof_height:.3f}]) sphere(r=18,$fn=16);
    }}
  for (f=[0.25,0.5,0.75])
    color("#d7e1e7") translate([0,0,{shell_height:.3f}+{roof_height:.3f}*f])
      rotate_extrude() translate([tank_radius*(1-f*f),0,0]) circle(r=14,$fn=12);
}}

color("#aebbc8") union() {{
{courses}
}}

{seams}

color("#8093a6") cylinder(h={spec['bottom']['central_thickness_mm']:.3f}, r=tank_radius);

geodesic_roof();

for (i=[0:anchor_count-1]) {{
  rotate([0,0,i*360/anchor_count]) translate([anchor_radius,0,0]) anchor();
}}
'''


def write_scad(spec: dict, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_scad(spec), encoding="utf-8")
    return target
