from __future__ import annotations

from pathlib import Path

import cadquery as cq

from _cad_common import C, ROOT, export_colored, rack_dimensions, safe_chamfer, safe_fillet

OUT = ROOT / "cad/custom_parts/step"


def base_plate():
    holes = []
    for x in (-220, 220):
        for y in (-145, 145):
            holes.append((x, y))
    for x in (-170, 170):
        holes.append((x, -120))
        holes.append((x, 120))
    part = cq.Workplane("XY").box(C.base_length, C.base_width, C.base_thickness)
    part = part.faces(">Z").workplane().pushPoints(holes).hole(5, depth=C.base_thickness + 2)
    part = safe_chamfer(part, 1.5)
    feet = cq.Workplane("XY")
    for x, y in [(-220, -150), (220, -150), (-220, 150), (220, 150)]:
        feet = feet.union(cq.Workplane("XY").box(35, 25, 8).translate((x, y, -9)))
    return part.union(feet)


def tube_rack():
    length, width = rack_dimensions()
    points = []
    x0 = -((C.rack_cols - 1) * C.tube_pitch) / 2
    y0 = -((C.rack_rows - 1) * C.tube_pitch) / 2
    for r in range(C.rack_rows):
        for c in range(C.rack_cols):
            points.append((x0 + c * C.tube_pitch, y0 + r * C.tube_pitch))
    part = cq.Workplane("XY").box(length, width, C.rack_thickness)
    part = part.faces(">Z").workplane().pushPoints(points).hole(C.tube_hole_diameter, depth=C.rack_thickness + 2)
    part = part.faces(">Z").workplane().rect(length - 16, width - 16).cutBlind(-2)
    return safe_fillet(part, 1.2)


def test_tube_set():
    length, width = rack_dimensions()
    x0 = -((C.rack_cols - 1) * C.tube_pitch) / 2
    y0 = -((C.rack_rows - 1) * C.tube_pitch) / 2
    asm = cq.Assembly(name="test_tube_set")
    idx = 0
    for r in range(C.rack_rows):
        for c in range(C.rack_cols):
            x = x0 + c * C.tube_pitch
            y = y0 + r * C.tube_pitch
            tube = cq.Workplane("XY").circle(C.tube_outer_diameter / 2).extrude(C.tube_height)
            tube = tube.faces(">Z").workplane().circle(C.tube_outer_diameter / 2).extrude(C.cap_height)
            tube = safe_fillet(tube, 0.6)
            idx += 1
            asm.add(tube, name=f"tube_{idx:02d}", loc=cq.Location(cq.Vector(x, y, 0)), color=cq.Color(0.8, 0.02, 0.02, 0.55))
    return asm


def y_axis_mounting_blocks():
    blocks = cq.Workplane("XY")
    for x in (-170, 170):
        for y in (-120, 120):
            b = cq.Workplane("XY").box(42, 26, 18).faces(">Z").workplane().rect(26, 14).hole(5)
            blocks = blocks.union(b.translate((x, y, 0)))
    return safe_fillet(blocks, 1.0)


def x_axis_beam():
    beam = cq.Workplane("XY").box(420, 26, 38)
    holes = [(x, 0) for x in range(-180, 181, 60)]
    beam = beam.faces(">Z").workplane().pushPoints(holes).hole(4.5, depth=40)
    return safe_chamfer(beam, 1.0)


def z_axis_mounting_plate():
    holes = [(-20, -35), (20, -35), (-20, 35), (20, 35), (0, 0)]
    return safe_fillet(cq.Workplane("XY").box(70, 95, 6).faces(">Z").workplane().pushPoints(holes).hole(4), 0.8)


def motor_mounting_plates():
    plate = cq.Workplane("XY").box(56, 56, 5)
    holes = [(-15.5, -15.5), (15.5, -15.5), (-15.5, 15.5), (15.5, 15.5)]
    plate = plate.faces(">Z").workplane().pushPoints(holes).hole(3.5)
    plate = plate.faces(">Z").workplane().circle(11).cutBlind(-6)
    plates = cq.Workplane("XY")
    for i, x in enumerate((-70, 0, 70)):
        plates = plates.union(plate.translate((x, 0, 0)))
    return safe_chamfer(plates, 0.6)


def gripper_adapter():
    holes = [(-18, -12), (18, -12), (-18, 12), (18, 12)]
    p = cq.Workplane("XY").box(64, 38, 8).faces(">Z").workplane().pushPoints(holes).hole(4)
    p = p.faces(">Z").workplane().circle(9).hole(5)
    return safe_fillet(p, 0.8)


def sensor_bracket():
    vertical = cq.Workplane("XY").box(35, 5, 55).translate((0, -12, 20))
    foot = cq.Workplane("XY").box(42, 28, 5)
    face = cq.Workplane("XY").box(34, 5, 28).translate((0, 8, 48))
    bracket = foot.union(vertical).union(face)
    bracket = bracket.faces(">Z").workplane().pushPoints([(-12, 0), (12, 0)]).hole(4)
    return safe_fillet(bracket, 0.8)


def control_box_mount():
    base = cq.Workplane("XY").box(170, 32, 6)
    posts = cq.Workplane("XY")
    for x in (-65, 65):
        posts = posts.union(cq.Workplane("XY").box(14, 24, 38).translate((x, 0, 22)))
    return safe_chamfer(base.union(posts), 0.8)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    parts = {
        "base_plate.step": (base_plate(), (0.68, 0.70, 0.72, 1)),
        "input_tube_rack.step": (tube_rack(), (0.12, 0.42, 0.82, 1)),
        "output_tube_rack.step": (tube_rack(), (0.12, 0.62, 0.42, 1)),
        "y_axis_mounting_blocks.step": (y_axis_mounting_blocks(), (0.25, 0.25, 0.25, 1)),
        "x_axis_beam.step": (x_axis_beam(), (0.85, 0.85, 0.80, 1)),
        "z_axis_mounting_plate.step": (z_axis_mounting_plate(), (0.75, 0.75, 0.78, 1)),
        "motor_mounting_plates.step": (motor_mounting_plates(), (0.2, 0.2, 0.22, 1)),
        "gripper_adapter.step": (gripper_adapter(), (0.45, 0.45, 0.48, 1)),
        "sensor_bracket.step": (sensor_bracket(), (0.1, 0.1, 0.1, 1)),
        "control_box_mount.step": (control_box_mount(), (0.2, 0.2, 0.2, 1)),
    }
    for filename, (obj, color) in parts.items():
        export_colored(obj, OUT / filename, color=color, name=filename[:-5])

    tube_asm = test_tube_set()
    tube_asm.save(str(OUT / "test_tube_set.step"), exportType="STEP")
    print(f"Generated custom STEP parts in {OUT}")


if __name__ == "__main__":
    main()
