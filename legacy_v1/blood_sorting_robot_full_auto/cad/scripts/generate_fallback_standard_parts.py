from __future__ import annotations

from pathlib import Path

import cadquery as cq

from _cad_common import C, ROOT, cylinder_x, export_colored, safe_chamfer, safe_fillet

OUT = ROOT / "cad/standard_parts/fallback_generated"


def nema17_motor():
    body = cq.Workplane("XY").box(42, 42, 40).translate((0, 0, 20))
    front = cq.Workplane("XY").box(42, 42, 3).translate((0, 0, 41.5))
    boss = cq.Workplane("XY").circle(11).extrude(4).translate((0, 0, 43))
    shaft = cq.Workplane("XY").circle(2.5).extrude(18).translate((0, 0, 46))
    holes = [(-15.5, -15.5), (15.5, -15.5), (-15.5, 15.5), (15.5, 15.5)]
    front = front.faces(">Z").workplane().pushPoints(holes).hole(3)
    return safe_chamfer(body.union(front).union(boss).union(shaft), 0.8)


def mgn12_rail(length=None):
    length = length or C.x_rail_length
    rail = cq.Workplane("XY").box(length, 12, 8)
    holes = [(x, 0) for x in range(int(-length / 2 + 25), int(length / 2), 50)]
    rail = rail.faces(">Z").workplane().pushPoints(holes).hole(3.5)
    groove1 = cq.Workplane("XY").box(length + 1, 2, 2).translate((0, 4.2, 4.1))
    groove2 = cq.Workplane("XY").box(length + 1, 2, 2).translate((0, -4.2, 4.1))
    return safe_chamfer(rail.cut(groove1).cut(groove2), 0.4)


def mgn12_slider():
    block = cq.Workplane("XY").box(46, 27, 13).translate((0, 0, 6.5))
    holes = [(-15, -8), (15, -8), (-15, 8), (15, 8)]
    block = block.faces(">Z").workplane().pushPoints(holes).hole(3)
    return safe_fillet(block, 0.8)


def t8_lead_screw():
    screw = cylinder_x(240, 4)
    nut = cq.Workplane("XY").box(22, 22, 12).translate((0, 0, 0))
    return screw.union(nut)


def gt2_belt():
    top = cq.Workplane("XY").box(260, 6, 3).translate((0, 16, 0))
    bottom = cq.Workplane("XY").box(260, 6, 3).translate((0, -16, 0))
    left = cq.Workplane("XY").box(6, 32, 3).translate((-130, 0, 0))
    right = cq.Workplane("XY").box(6, 32, 3).translate((130, 0, 0))
    return safe_fillet(top.union(bottom).union(left).union(right), 1.2)


def coupling():
    cyl = cq.Workplane("XY").circle(9).extrude(24)
    bore = cq.Workplane("XY").circle(3.2).extrude(26)
    slot = cq.Workplane("XY").box(24, 2, 12).translate((0, 0, 12))
    return safe_chamfer(cyl.cut(bore).cut(slot), 0.5)


def bearing_block():
    base = cq.Workplane("XY").box(34, 18, 8)
    tower = cq.Workplane("XY").box(24, 10, 22).translate((0, 0, 12))
    hole = cq.Workplane("YZ").circle(5).extrude(36).translate((-18, 0, 12))
    block = base.union(tower).cut(hole)
    block = block.faces(">Z").workplane().pushPoints([(-11, 0), (11, 0)]).hole(4)
    return safe_chamfer(block, 0.6)


def profile_2020(length=260):
    p = cq.Workplane("XY").box(length, 20, 20)
    for y in (-8, 8):
        p = p.cut(cq.Workplane("XY").box(length + 1, 3, 6).translate((0, y, 0)))
    for z in (-8, 8):
        p = p.cut(cq.Workplane("XY").box(length + 1, 6, 3).translate((0, 0, z)))
    return safe_chamfer(p, 0.5)


def cable_chain():
    chain = cq.Workplane("XY")
    for i in range(13):
        link = cq.Workplane("XY").box(16, 22, 10).translate((i * 15, 0, 0))
        link = link.cut(cq.Workplane("XY").box(8, 14, 12).translate((i * 15, 0, 0)))
        chain = chain.union(link)
    return safe_chamfer(chain, 0.5)


def limit_switch():
    body = cq.Workplane("XY").box(28, 12, 16)
    lever = cq.Workplane("XY").box(38, 3, 2).translate((10, 0, 10)).rotate((0, 0, 0), (0, 1, 0), -14)
    button = cq.Workplane("XY").box(4, 8, 3).translate((-11, 0, 9))
    return safe_chamfer(body.union(lever).union(button), 0.4)


def sensor_module():
    body = cq.Workplane("XY").box(35, 28, 22)
    lens = cq.Workplane("XY").circle(7).extrude(2).translate((0, -15, 2))
    cable = cq.Workplane("XY").circle(3).extrude(22).rotate((0, 0, 0), (1, 0, 0), 90).translate((0, 18, 4))
    return safe_chamfer(body.union(lens).union(cable), 0.6)


def emergency_stop():
    base = cq.Workplane("XY").circle(14).extrude(8)
    stem = cq.Workplane("XY").circle(8).extrude(8).translate((0, 0, 8))
    mushroom = cq.Workplane("XY").circle(18).extrude(10).translate((0, 0, 16))
    return safe_fillet(base.union(stem).union(mushroom), 1.0)


def control_box():
    box = cq.Workplane("XY").box(140, 90, 55)
    lid = cq.Workplane("XY").box(146, 96, 4).translate((0, 0, 29))
    vents = cq.Workplane("XY")
    for i in range(5):
        vents = vents.union(cq.Workplane("XY").box(52, 2, 2).translate((0, -47, -15 + i * 7)))
    return safe_chamfer(box.union(lid).union(vents), 1.5)


def parallel_gripper():
    body = cq.Workplane("XY").box(60, 34, 26)
    palm = cq.Workplane("XY").box(48, 12, 10).translate((0, -23, 0))
    left = cq.Workplane("XY").box(C.gripper_finger_width, C.gripper_finger_length, 12).translate((-C.gripper_opening / 2, -52, 0))
    right = cq.Workplane("XY").box(C.gripper_finger_width, C.gripper_finger_length, 12).translate((C.gripper_opening / 2, -52, 0))
    pads = cq.Workplane("XY").box(8, 12, 14).translate((-C.gripper_opening / 2, -76, 0)).union(cq.Workplane("XY").box(8, 12, 14).translate((C.gripper_opening / 2, -76, 0)))
    return safe_chamfer(body.union(palm).union(left).union(right).union(pads), 0.8)


def fasteners():
    asm = cq.Workplane("XY")
    for i, x in enumerate(range(-36, 37, 18)):
        screw = cq.Workplane("XY").circle(3).extrude(12).union(cq.Workplane("XY").circle(5).extrude(3).translate((0, 0, 12)))
        washer = cq.Workplane("XY").circle(6).extrude(1).cut(cq.Workplane("XY").circle(3.2).extrude(2)).translate((0, 16, 0))
        asm = asm.union(screw.translate((x, 0, 0))).union(washer.translate((x, 0, 0)))
    return asm


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    parts = {
        "fallback_nema17_motor.step": (nema17_motor(), (0.08, 0.08, 0.09, 1)),
        "fallback_mgn12_rail.step": (mgn12_rail(), (0.72, 0.72, 0.74, 1)),
        "fallback_mgn12_slider.step": (mgn12_slider(), (0.32, 0.32, 0.34, 1)),
        "fallback_t8_lead_screw.step": (t8_lead_screw(), (0.65, 0.65, 0.68, 1)),
        "fallback_gt2_belt.step": (gt2_belt(), (0.03, 0.03, 0.03, 1)),
        "fallback_coupling.step": (coupling(), (0.9, 0.55, 0.18, 1)),
        "fallback_bearing_block.step": (bearing_block(), (0.25, 0.25, 0.25, 1)),
        "fallback_2020_profile.step": (profile_2020(), (0.78, 0.78, 0.74, 1)),
        "fallback_cable_chain.step": (cable_chain(), (0.04, 0.04, 0.04, 1)),
        "fallback_limit_switch.step": (limit_switch(), (0.08, 0.08, 0.08, 1)),
        "fallback_sensor_module.step": (sensor_module(), (0.05, 0.12, 0.42, 1)),
        "fallback_emergency_stop.step": (emergency_stop(), (0.9, 0.02, 0.02, 1)),
        "fallback_control_box.step": (control_box(), (0.78, 0.78, 0.72, 1)),
        "fallback_parallel_gripper.step": (parallel_gripper(), (0.22, 0.22, 0.24, 1)),
        "fallback_fasteners.step": (fasteners(), (0.6, 0.6, 0.62, 1)),
    }
    for filename, (obj, color) in parts.items():
        export_colored(obj, OUT / filename, color=color, name=filename[:-5])
    print(f"Generated fallback standard STEP parts in {OUT}")


if __name__ == "__main__":
    main()
