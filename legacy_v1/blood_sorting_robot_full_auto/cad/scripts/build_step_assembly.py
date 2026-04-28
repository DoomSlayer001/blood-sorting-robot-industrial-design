from __future__ import annotations

import csv
from pathlib import Path

import cadquery as cq

from _cad_common import C, ROOT, rack_dimensions

CUSTOM = ROOT / "cad/custom_parts/step"
FALLBACK = ROOT / "cad/standard_parts/fallback_generated"
OUT = ROOT / "cad/assembly"


def step_path(filename):
    p = CUSTOM / filename
    if p.exists():
        return p
    return FALLBACK / filename


def import_shape(filename, rx=0, ry=0, rz=0):
    shape = cq.importers.importStep(str(step_path(filename)))
    if rx:
        shape = shape.rotate((0, 0, 0), (1, 0, 0), rx)
    if ry:
        shape = shape.rotate((0, 0, 0), (0, 1, 0), ry)
    if rz:
        shape = shape.rotate((0, 0, 0), (0, 0, 1), rz)
    return shape


def add(asm, rows, name, filename, x, y, z, rx=0, ry=0, rz=0, color=(0.7, 0.7, 0.7, 1), note=""):
    shape = import_shape(filename, rx=rx, ry=ry, rz=rz)
    asm.add(shape, name=name, loc=cq.Location(cq.Vector(x, y, z)), color=cq.Color(*color))
    rows.append([name, filename, round(x, 3), round(y, 3), round(z, 3), rx, ry, rz, note])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    asm = cq.Assembly(name="blood_sorting_robot_assembly")
    rows = []
    base_z = C.base_thickness / 2
    add(asm, rows, "base_plate", "base_plate.step", C.base_length / 2, C.base_width / 2, base_z, color=(0.68, 0.70, 0.72, 1), note="world datum: base lower face z=0")

    rack_l, rack_w = rack_dimensions()
    in_x = C.input_rack_origin[0] + rack_l / 2
    in_y = C.input_rack_origin[1] + rack_w / 2
    out_x = C.output_rack_origin[0] + rack_l / 2
    out_y = C.output_rack_origin[1] + rack_w / 2
    rack_z = C.base_thickness + C.rack_thickness / 2
    add(asm, rows, "input_tube_rack", "input_tube_rack.step", in_x, in_y, rack_z, color=(0.12, 0.42, 0.82, 1), note="3x4 input rack")
    add(asm, rows, "output_tube_rack", "output_tube_rack.step", out_x, out_y, rack_z, color=(0.12, 0.62, 0.42, 1), note="3x4 output rack")
    add(asm, rows, "input_test_tubes", "test_tube_set.step", in_x, in_y, C.base_thickness + C.rack_thickness, color=(0.8, 0.02, 0.02, 0.55), note="blood sample tubes in input rack")
    add(asm, rows, "output_reference_tubes", "test_tube_set.step", out_x, out_y, C.base_thickness + C.rack_thickness, color=(0.9, 0.08, 0.08, 0.35), note="visual capacity reference")

    y_left_x, y_right_x = 82, 418
    rail_z = C.base_thickness + 11
    for side, x in [("left", y_left_x), ("right", y_right_x)]:
        add(asm, rows, f"y_{side}_rail", "fallback_mgn12_rail.step", x, C.base_width / 2, rail_z, rz=90, color=(0.72, 0.72, 0.74, 1), note="Y axis rail")
        add(asm, rows, f"y_{side}_slider", "fallback_mgn12_slider.step", x, 190, rail_z + 6, rz=90, color=(0.28, 0.28, 0.30, 1), note="Y carriage block")

    add(asm, rows, "x_axis_beam", "x_axis_beam.step", C.base_length / 2, 190, 92, color=(0.84, 0.84, 0.78, 1), note="gantry bridge carried by Y sliders")
    add(asm, rows, "x_axis_rail", "fallback_mgn12_rail.step", C.base_length / 2, 190, 116, color=(0.72, 0.72, 0.74, 1), note="X axis guide rail")
    add(asm, rows, "x_axis_slider", "fallback_mgn12_slider.step", 250, 190, 127, color=(0.28, 0.28, 0.30, 1), note="X carriage carrying Z module")

    add(asm, rows, "z_mounting_plate", "z_axis_mounting_plate.step", 250, 177, 105, rx=90, color=(0.73, 0.73, 0.77, 1), note="vertical adapter plate")
    add(asm, rows, "z_axis_rail", "fallback_mgn12_rail.step", 250, 165, 80, ry=-90, color=(0.72, 0.72, 0.74, 1), note="Z axis short rail")
    add(asm, rows, "z_axis_slider", "fallback_mgn12_slider.step", 250, 153, 60, ry=-90, color=(0.28, 0.28, 0.30, 1), note="Z carriage block")
    add(asm, rows, "gripper_adapter", "gripper_adapter.step", 250, 148, 42, rx=90, color=(0.46, 0.46, 0.49, 1), note="adapter between Z slider and gripper")
    add(asm, rows, "parallel_gripper", "fallback_parallel_gripper.step", 250, 130, 24, rx=90, color=(0.22, 0.22, 0.24, 1), note="two-finger gripper near pick/place height")
    add(asm, rows, "sensor_bracket", "sensor_bracket.step", 288, 138, 45, rx=90, color=(0.1, 0.1, 0.1, 1), note="scanner/sensor bracket near gripper")
    add(asm, rows, "sensor_module", "fallback_sensor_module.step", 292, 122, 45, rx=90, color=(0.05, 0.12, 0.42, 1), note="barcode/photoelectric sensor appearance")

    for name, x, y, z, rz in [
        ("x_motor", 72, 190, 119, 90),
        ("y_motor", 45, 46, 34, 0),
        ("z_motor", 250, 166, 152, 0),
    ]:
        add(asm, rows, name, "fallback_nema17_motor.step", x, y, z, rz=rz, color=(0.08, 0.08, 0.09, 1), note="NEMA17 stepper motor")
    add(asm, rows, "x_gt2_belt", "fallback_gt2_belt.step", 250, 202, 124, color=(0.03, 0.03, 0.03, 1), note="simplified X belt drive")
    add(asm, rows, "y_gt2_belt", "fallback_gt2_belt.step", 82, 175, 32, rz=90, color=(0.03, 0.03, 0.03, 1), note="simplified Y belt drive")
    add(asm, rows, "z_t8_lead_screw", "fallback_t8_lead_screw.step", 262, 160, 92, ry=-90, color=(0.65, 0.65, 0.68, 1), note="simplified Z lead screw")

    add(asm, rows, "cable_chain", "fallback_cable_chain.step", 260, 325, 70, color=(0.04, 0.04, 0.04, 1), note="rear cable carrier")
    add(asm, rows, "control_box_mount", "control_box_mount.step", 380, 323, 18, color=(0.2, 0.2, 0.2, 1), note="rear mount")
    add(asm, rows, "control_box", "fallback_control_box.step", 380, 323, 62, color=(0.78, 0.78, 0.72, 1), note="controller enclosure")
    add(asm, rows, "emergency_stop", "fallback_emergency_stop.step", 330, 275, 100, rx=90, color=(0.9, 0.02, 0.02, 1), note="emergency stop button on control box")
    add(asm, rows, "limit_switches", "fallback_limit_switch.step", 70, 305, 28, color=(0.08, 0.08, 0.08, 1), note="representative limit switch")
    add(asm, rows, "fasteners", "fallback_fasteners.step", 250, 45, 18, color=(0.6, 0.6, 0.62, 1), note="sample fastener set")
    add(asm, rows, "bearing_block_a", "fallback_bearing_block.step", 92, 190, 124, rz=90, color=(0.25, 0.25, 0.25, 1), note="belt/screw support")
    add(asm, rows, "coupling_z", "fallback_coupling.step", 262, 160, 145, ry=-90, color=(0.9, 0.55, 0.18, 1), note="Z motor coupling")

    asm_path = OUT / "blood_sorting_robot_assembly.step"
    asm.save(str(asm_path), exportType="STEP")

    csv_path = OUT / "assembly_reference_coordinates.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["component_name", "step_file", "x_mm", "y_mm", "z_mm", "rx_deg", "ry_deg", "rz_deg", "note"])
        writer.writerows(rows)

    md = ["# Assembly Reference Coordinates", "", "Coordinate origin is the lower-left datum of the base plate. Units are mm.", "", "| Component | STEP | X | Y | Z | Rotation | Note |", "|---|---:|---:|---:|---:|---|---|"]
    for r in rows:
        md.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | ({r[5]}, {r[6]}, {r[7]}) | {r[8]} |")
    (OUT / "assembly_reference_coordinates.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Generated assembly STEP: {asm_path}")


if __name__ == "__main__":
    main()
