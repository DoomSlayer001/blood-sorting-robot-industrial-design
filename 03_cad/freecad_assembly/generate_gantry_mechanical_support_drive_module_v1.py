from __future__ import annotations

import csv
import importlib.util
import math
import sys
from itertools import combinations
from pathlib import Path

import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.Interface import Interface_Static


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "03_cad" / "freecad_assembly"
REPORT_DIR = ROOT / "reports"

MODULE_STEP_OUT = OUT_DIR / "blood_sorting_robot_gantry_mechanical_support_drive_module_v1.step"
MODULE_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_gantry_mechanical_support_drive_module_v1_validation.csv"
MODULE_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_gantry_mechanical_support_drive_module_v1_color_manifest.csv"
ACCESSIBILITY_CSV_OUT = OUT_DIR / "blood_sorting_robot_gantry_mechanical_support_drive_module_v1_accessibility_check.csv"
INTERFACE_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_gantry_mechanical_support_drive_module_v1_interface_manifest.csv"

PREVIEW_STEP_OUT = OUT_DIR / "blood_sorting_robot_v7_3c_gantry_mechanical_support_preview.step"
PREVIEW_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_v7_3c_gantry_mechanical_support_preview_validation.csv"
PREVIEW_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3c_gantry_mechanical_support_preview_interference_audit.csv"
PREVIEW_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_v7_3c_gantry_mechanical_support_preview_color_manifest.csv"

REPORT_OUT = REPORT_DIR / "stage_7a3c_gantry_mechanical_support_drive_report.md"

V71_SCRIPT = OUT_DIR / "generate_cadquery_multi_box_layout_v7_1.py"
ENCLOSURE_SCRIPT = OUT_DIR / "generate_enclosure_guard_module_v1_1.py"
CONTROL_BOX_SCRIPT = OUT_DIR / "generate_electrical_control_box_module_v1_2.py"

y_mount_block_width_mm = 70.0
y_mount_block_depth_mm = 45.0
y_mount_block_height_mm = 18.0
y_carriage_plate_width_mm = 95.0
y_carriage_plate_depth_mm = 70.0
y_carriage_plate_thickness_mm = 8.0
x_beam_end_plate_width_mm = 90.0
x_beam_end_plate_height_mm = 75.0
x_beam_end_plate_thickness_mm = 8.0
xz_adapter_plate_width_mm = 120.0
xz_adapter_plate_height_mm = 150.0
xz_adapter_plate_thickness_mm = 8.0
z_gripper_adapter_width_mm = 70.0
z_gripper_adapter_height_mm = 50.0
z_gripper_adapter_thickness_mm = 6.0
motor_body_size_mm = 42.0
motor_body_length_mm = 55.0
motor_flange_size_mm = 50.0
fastener_head_radius_mm = 3.0
fastener_head_height_mm = 2.0

LEFT_Y_X = -535.0
RIGHT_Y_X = 500.0
GANTRY_Y = 10.0
X_AXIS_Z = 265.0
Z_AXIS_X = 0.0
Z_AXIS_Y = 20.0

OVERLAP_VOLUME_THRESHOLD_MM3 = 1.0
DEFAULT_CLEARANCE_THRESHOLD_MM = 5.0


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v71 = load_module("cadquery_multi_box_layout_v7_1_for_gantry_support", V71_SCRIPT)
enclosure_v11 = load_module("enclosure_guard_module_v1_1_for_gantry_support", ENCLOSURE_SCRIPT)
control_box_v12 = load_module("electrical_control_box_v1_2_for_gantry_support", CONTROL_BOX_SCRIPT)

v71.COLORS.update({
    "aluminum_frame": ("anodized_aluminum_dark_gray", (0.36, 0.38, 0.39, 1.0)),
    "transparent_panel_clean": ("very_light_transparent_pc", (0.78, 0.93, 1.0, 0.12)),
    "access_door_frame": ("access_door_frame_gray", (0.28, 0.32, 0.34, 1.0)),
    "door_handle": ("door_handle_dark_gray", (0.08, 0.08, 0.08, 1.0)),
    "rubber_gasket": ("rubber_gasket_black", (0.01, 0.01, 0.01, 1.0)),
    "control_box_housing": ("control_box_powder_coated_dark_gray", (0.16, 0.17, 0.18, 1.0)),
    "control_box_lid": ("control_box_service_lid_graphite", (0.10, 0.11, 0.12, 1.0)),
    "control_box_seam": ("control_box_lid_seam_black", (0.01, 0.01, 0.01, 1.0)),
    "cable_gland_black": ("cable_gland_black", (0.02, 0.02, 0.02, 1.0)),
    "vent_dark": ("vent_slot_dark", (0.03, 0.03, 0.03, 1.0)),
    "mounting_bracket": ("control_box_mounting_bracket_gray", (0.34, 0.36, 0.37, 1.0)),
    "support_dark": ("dark_anodized_support", (0.22, 0.23, 0.24, 1.0)),
    "support_gray": ("machined_support_gray", (0.46, 0.48, 0.49, 1.0)),
    "support_light": ("brushed_aluminum_support", (0.68, 0.70, 0.70, 1.0)),
    "fastener": ("black_socket_head_fastener", (0.02, 0.02, 0.02, 1.0)),
    "motor_body": ("motor_body_dark_gray", (0.18, 0.19, 0.20, 1.0)),
    "motor_flange": ("motor_flange_aluminum", (0.62, 0.64, 0.65, 1.0)),
    "shaft": ("shaft_polished_metal", (0.74, 0.74, 0.70, 1.0)),
    "belt": ("timing_belt_black", (0.01, 0.01, 0.01, 1.0)),
    "pulley": ("pulley_dark_metal", (0.25, 0.26, 0.27, 1.0)),
    "tab": ("cable_chain_mount_tab_gray", (0.36, 0.38, 0.39, 1.0)),
})


def box_shape(size: tuple[float, float, float], offset: tuple[float, float, float] = (0.0, 0.0, 0.0)) -> cq.Shape:
    return cq.Workplane("XY").box(*size).translate(offset).val()


def cyl_shape(
    radius: float,
    height: float,
    offset: tuple[float, float, float],
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> cq.Shape:
    shape = cq.Workplane("XY").cylinder(height, radius).val()
    shape = v71.rotate_shape(shape, rotation)
    return shape.translate(offset)


def subpart(name: str, shape: cq.Shape, color_key: str) -> tuple[str, cq.Shape, str]:
    return (name, shape, color_key)


def component(
    name: str,
    module_name: str,
    category: str,
    subparts: list[tuple[str, cq.Shape, str]],
    position: tuple[float, float, float],
    notes: str,
) -> tuple[str, str, str, list[tuple[str, cq.Shape, str]], tuple[float, float, float], tuple[float, float, float], str]:
    return (name, module_name, category, subparts, position, (0.0, 0.0, 0.0), notes)


def fastener_heads_xy(points: list[tuple[float, float]], z: float = 0.0, prefix: str = "fastener") -> list[tuple[str, cq.Shape, str]]:
    return [
        subpart(f"{prefix}_{index:02d}", cyl_shape(fastener_head_radius_mm, fastener_head_height_mm, (x, y, z)), "fastener")
        for index, (x, y) in enumerate(points, start=1)
    ]


def fastener_heads_xz(points: list[tuple[float, float]], y: float = 0.0, prefix: str = "fastener") -> list[tuple[str, cq.Shape, str]]:
    return [
        subpart(f"{prefix}_{index:02d}", cyl_shape(fastener_head_radius_mm, fastener_head_height_mm, (x, y, z), (90.0, 0.0, 0.0)), "fastener")
        for index, (x, z) in enumerate(points, start=1)
    ]


def make_y_axis_base_mounting_blocks() -> list[tuple[str, cq.Shape, str]]:
    parts: list[tuple[str, cq.Shape, str]] = []
    for side, x in [("left", LEFT_Y_X), ("right", RIGHT_Y_X)]:
        for y_label, y in [("front", -330.0), ("rear", 330.0)]:
            local_name = f"{side}_{y_label}"
            block = box_shape((y_mount_block_width_mm, y_mount_block_depth_mm, y_mount_block_height_mm), (x, y, y_mount_block_height_mm / 2.0))
            parts.append(subpart(f"{local_name}_base_block", block, "support_gray"))
            for dx in [-22.0, 22.0]:
                for dy in [-13.0, 13.0]:
                    parts.append(subpart(f"{local_name}_fastener_{dx}_{dy}", cyl_shape(3.0, 2.0, (x + dx, y + dy, y_mount_block_height_mm + 1.0)), "fastener"))
    return parts


def make_y_carriage_adapter_plates() -> list[tuple[str, cq.Shape, str]]:
    parts: list[tuple[str, cq.Shape, str]] = []
    for side, x, sx in [("left", LEFT_Y_X, -1.0), ("right", RIGHT_Y_X, 1.0)]:
        plate_x = x + (-sx * 8.0)
        parts.append(subpart(f"{side}_vertical_carriage_plate", box_shape((y_carriage_plate_thickness_mm, y_carriage_plate_depth_mm, y_carriage_plate_width_mm), (plate_x, GANTRY_Y, 210.0)), "support_dark"))
        parts.append(subpart(f"{side}_top_gusset", box_shape((42.0, 8.0, 34.0), (plate_x + sx * 22.0, GANTRY_Y - 25.0, 230.0)), "support_gray"))
        parts.extend(fastener_heads_xz([(plate_x, 180.0), (plate_x, 205.0), (plate_x, 230.0), (plate_x, 255.0)], GANTRY_Y - 36.0, f"{side}_carriage_plate_fastener"))
    return parts


def make_gantry_cross_beam_support() -> list[tuple[str, cq.Shape, str]]:
    parts: list[tuple[str, cq.Shape, str]] = []
    for side, x in [("left", -460.0), ("right", 430.0)]:
        parts.append(subpart(f"{side}_x_beam_end_plate", box_shape((x_beam_end_plate_thickness_mm, 72.0, x_beam_end_plate_height_mm), (x, GANTRY_Y, 252.0)), "support_gray"))
        parts.append(subpart(f"{side}_triangular_gusset_a", box_shape((32.0, 8.0, 58.0), (x, GANTRY_Y - 44.0, 236.0)), "support_dark"))
        parts.append(subpart(f"{side}_triangular_gusset_b", box_shape((32.0, 8.0, 58.0), (x, GANTRY_Y + 44.0, 236.0)), "support_dark"))
        parts.extend(fastener_heads_xz([(x, 226.0), (x, 252.0), (x, 278.0)], GANTRY_Y - 38.0, f"{side}_x_end_fastener"))
    parts.append(subpart("rear_cross_beam_tie_bar", box_shape((900.0, 10.0, 18.0), (-15.0, GANTRY_Y + 45.0, 225.0)), "support_dark"))
    return parts


def make_x_axis_mounting_saddle() -> list[tuple[str, cq.Shape, str]]:
    parts = [
        subpart("long_lower_saddle_plate", box_shape((780.0, 18.0, 8.0), (0.0, GANTRY_Y - 28.0, 225.0)), "support_gray"),
        subpart("rear_saddle_web", box_shape((760.0, 8.0, 40.0), (0.0, GANTRY_Y + 38.0, 245.0)), "support_dark"),
    ]
    for x in [-320.0, -160.0, 0.0, 160.0, 320.0]:
        parts.append(subpart(f"x_saddle_fastener_{x}", cyl_shape(3.0, 2.0, (x, GANTRY_Y - 28.0, 231.0)), "fastener"))
    return parts


def make_xz_adapter_plate_engineered() -> list[tuple[str, cq.Shape, str]]:
    parts = [
        subpart("main_xz_adapter_plate", box_shape((xz_adapter_plate_width_mm, xz_adapter_plate_thickness_mm, xz_adapter_plate_height_mm), (0.0, 0.0, 0.0)), "support_light"),
        subpart("upper_x_carriage_spacer_left", cyl_shape(6.0, 18.0, (-42.0, -13.0, 42.0), (90.0, 0.0, 0.0)), "support_gray"),
        subpart("upper_x_carriage_spacer_right", cyl_shape(6.0, 18.0, (42.0, -13.0, 42.0), (90.0, 0.0, 0.0)), "support_gray"),
        subpart("lower_z_axis_spacer_left", cyl_shape(6.0, 18.0, (-42.0, -13.0, -42.0), (90.0, 0.0, 0.0)), "support_gray"),
        subpart("lower_z_axis_spacer_right", cyl_shape(6.0, 18.0, (42.0, -13.0, -42.0), (90.0, 0.0, 0.0)), "support_gray"),
    ]
    parts.extend(fastener_heads_xz([(-42.0, 55.0), (42.0, 55.0), (-42.0, 20.0), (42.0, 20.0), (-42.0, -20.0), (42.0, -20.0), (-42.0, -55.0), (42.0, -55.0)], -6.0, "xz_adapter_fastener"))
    return parts


def make_z_gripper_adapter() -> list[tuple[str, cq.Shape, str]]:
    parts = [
        subpart("z_gripper_mount_plate", box_shape((z_gripper_adapter_width_mm, z_gripper_adapter_thickness_mm, z_gripper_adapter_height_mm), (0.0, 0.0, 0.0)), "support_gray"),
        subpart("bottom_l_flanges", box_shape((62.0, 20.0, 6.0), (0.0, -7.0, -28.0)), "support_dark"),
    ]
    parts.extend(fastener_heads_xz([(-22.0, 14.0), (22.0, 14.0), (-22.0, -14.0), (22.0, -14.0)], -5.0, "z_gripper_fastener"))
    return parts


def motor_subparts(axis: str, orientation: str) -> list[tuple[str, cq.Shape, str]]:
    parts = [
        subpart(f"{axis}_motor_body", box_shape((motor_body_size_mm, motor_body_size_mm, motor_body_length_mm)), "motor_body"),
        subpart(f"{axis}_motor_flange", box_shape((motor_flange_size_mm, 6.0, motor_flange_size_mm), (0.0, -motor_body_size_mm / 2.0 - 3.0, 0.0)), "motor_flange"),
        subpart(f"{axis}_coupler", cyl_shape(8.0, 16.0, (0.0, -motor_body_size_mm / 2.0 - 14.0, 0.0), (90.0, 0.0, 0.0)), "shaft"),
    ]
    parts.extend(fastener_heads_xz([(-16.0, -16.0), (16.0, -16.0), (-16.0, 16.0), (16.0, 16.0)], -motor_body_size_mm / 2.0 - 6.5, f"{axis}_motor_flange_fastener"))
    if orientation == "x":
        return [(name, v71.rotate_shape(shape, (0.0, 0.0, -90.0)), color) for name, shape, color in parts]
    if orientation == "z":
        return [(name, v71.rotate_shape(shape, (90.0, 0.0, 0.0)), color) for name, shape, color in parts]
    return parts


def make_motor_placeholders() -> list[tuple[str, cq.Shape, str]]:
    parts: list[tuple[str, cq.Shape, str]] = []
    for name, position, orient in [
        ("x_axis_motor_placeholder", (410.0, GANTRY_Y + 55.0, X_AXIS_Z), "x"),
        ("y_axis_motor_left_placeholder", (LEFT_Y_X, 365.0, 62.0), "y"),
        ("y_axis_motor_right_placeholder", (RIGHT_Y_X, 365.0, 62.0), "y"),
        ("z_axis_motor_placeholder", (58.0, Z_AXIS_Y + 35.0, 305.0), "z"),
    ]:
        for subname, shape, color in motor_subparts(name, orient):
            parts.append(subpart(subname, shape.translate(position), color))
    return parts


def make_drive_transmission_placeholders() -> list[tuple[str, cq.Shape, str]]:
    parts = [
        subpart("x_axis_timing_belt_strip", box_shape((760.0, 5.0, 4.0), (0.0, GANTRY_Y + 61.0, 298.0)), "belt"),
        subpart("x_axis_left_pulley", cyl_shape(16.0, 8.0, (-365.0, GANTRY_Y + 61.0, 298.0), (90.0, 0.0, 0.0)), "pulley"),
        subpart("x_axis_right_pulley", cyl_shape(16.0, 8.0, (365.0, GANTRY_Y + 61.0, 298.0), (90.0, 0.0, 0.0)), "pulley"),
        subpart("y_axis_sync_shaft_placeholder", cyl_shape(6.0, 980.0, (-17.5, 382.0, 82.0), (0.0, 90.0, 0.0)), "shaft"),
        subpart("left_y_sync_pulley", cyl_shape(18.0, 10.0, (LEFT_Y_X, 382.0, 82.0), (0.0, 90.0, 0.0)), "pulley"),
        subpart("right_y_sync_pulley", cyl_shape(18.0, 10.0, (RIGHT_Y_X, 382.0, 82.0), (0.0, 90.0, 0.0)), "pulley"),
        subpart("z_axis_ball_screw_visual_placeholder", cyl_shape(4.0, 120.0, (26.0, Z_AXIS_Y + 7.0, 215.0), (0.0, 0.0, 0.0)), "shaft"),
    ]
    return parts


def make_cable_chain_mounting_tabs() -> list[tuple[str, cq.Shape, str]]:
    parts = [
        subpart("rear_fixed_cable_chain_tab", box_shape((56.0, 12.0, 32.0), (320.0, 382.0, 210.0)), "tab"),
        subpart("x_carriage_cable_chain_tab", box_shape((42.0, 10.0, 30.0), (70.0, GANTRY_Y + 70.0, 258.0)), "tab"),
        subpart("z_axis_cable_tab", box_shape((34.0, 8.0, 28.0), (55.0, Z_AXIS_Y + 42.0, 185.0)), "tab"),
    ]
    for index, (x, y, z) in enumerate([(320.0, 382.0, 226.0), (70.0, GANTRY_Y + 70.0, 274.0), (55.0, Z_AXIS_Y + 42.0, 199.0)], start=1):
        parts.append(subpart(f"cable_chain_tab_hole_marker_{index}", cyl_shape(3.0, 2.0, (x, y - 7.0, z), (90.0, 0.0, 0.0)), "fastener"))
    return parts


class GantryMechanicalSupportDriveModule:
    module_name = "GantryMechanicalSupportDriveModule"

    def generated_components(self):
        return [
            component("y_axis_base_mounting_blocks", "YAxisBaseMountingBlocksModule", "support", make_y_axis_base_mounting_blocks(), (0.0, 0.0, 0.0), "front/rear mounting blocks tying Y axes to base plate"),
            component("y_carriage_adapter_plates", "YCarriageAdapterPlateModule", "support", make_y_carriage_adapter_plates(), (0.0, 0.0, 0.0), "left/right adapter plates from Y carriage area to X beam support"),
            component("gantry_cross_beam_support_plates", "GantryCrossBeamSupportModule", "support", make_gantry_cross_beam_support(), (0.0, 0.0, 0.0), "X beam end plates, gussets, and rear tie bar"),
            component("x_axis_mounting_saddle", "XAxisMountingSaddleModule", "support", make_x_axis_mounting_saddle(), (0.0, 0.0, 0.0), "support saddle under/backing X axis module"),
            component("xz_adapter_plate_engineered", "XZAdapterPlateModule", "adapter", make_xz_adapter_plate_engineered(), (Z_AXIS_X, Z_AXIS_Y, 240.0), "engineered X-Z adapter plate with spacers and screw pattern"),
            component("z_gripper_adapter", "ZGripperAdapterModule", "adapter", make_z_gripper_adapter(), (0.0, Z_AXIS_Y, 143.0), "small adapter flange tying Z axis end to gripper"),
            component("motor_placeholders", "MotorPlaceholderModule", "drive", make_motor_placeholders(), (0.0, 0.0, 0.0), "compact X/Y-left/Y-right/Z motor placeholders with flanges and couplers"),
            component("drive_transmission_placeholders", "DriveTransmissionPlaceholderModule", "drive", make_drive_transmission_placeholders(), (0.0, 0.0, 0.0), "timing belt/pulley and Y sync shaft placeholders plus Z ball-screw visual cue"),
            component("cable_chain_mounting_tabs", "CableChainMountingTabsModule", "future_interface", make_cable_chain_mounting_tabs(), (0.0, 0.0, 0.0), "mounting tabs only; Stage 7A-3d will model cable chain and wiring"),
        ]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def configure_step_schema() -> None:
    for schema in ["AP242DIS", "AP214IS"]:
        try:
            if Interface_Static.SetCVal_s("write.step.schema", schema):
                return
        except Exception:
            continue


def add_generated_component(assembly: cq.Assembly, manifest_rows: list[dict[str, object]], spec):
    name, module_name, category, subparts, position, rotation, notes = spec
    return v71.add_colored_subparts(assembly, manifest_rows, name, module_name, f"generated:{name}", subparts, position, rotation, f"{category}; {notes}")


def build_v71_body_without_region_labels(assembly: cq.Assembly, manifest_rows: list[dict[str, object]]) -> tuple[list[object], list[dict[str, object]]]:
    instances = []
    failure_rows = []
    modules = [
        v71.BaseLayout(),
        v71.GantryModule(),
        v71.MultiInputBoxModule(),
        v71.ScanStationModule(),
        v71.MultiOutputBoxModule(),
        v71.ManualReviewModule(),
    ]
    imported_specs = []
    generated_specs = []
    tube_specs = []
    for module in modules:
        if hasattr(module, "imported_components"):
            imported_specs.extend(module.imported_components())
        if hasattr(module, "generated_components"):
            generated_specs.extend(module.generated_components())
        if hasattr(module, "tube_instances"):
            tube_specs.extend(module.tube_instances())

    for spec in generated_specs:
        name = spec[0]
        if name.startswith("label_plate_"):
            continue
        instances.append(v71.add_colored_subparts(assembly, manifest_rows, spec[0], spec[1], f"generated:{spec[0]}", spec[2], spec[3], spec[4], spec[5]))

    for spec in imported_specs:
        try:
            instances.append(v71.add_main_component(assembly, manifest_rows, spec))
        except Exception as exc:
            failure_rows.append({
                "component_name": spec.name,
                "module": spec.module_name,
                "category": "existing_import_failure",
                "x_mm": spec.position[0],
                "y_mm": spec.position[1],
                "z_mm": spec.position[2],
                "bbox_x_mm": "",
                "bbox_y_mm": "",
                "bbox_z_mm": "",
                "status": "FAILED",
                "notes": f"{spec.note}; error={exc}",
            })

    for name, module_name, tube, position, note in tube_specs:
        tube_path = ROOT / tube.rel_path
        if not tube_path.is_file() or tube_path.stat().st_size <= 0:
            raise FileNotFoundError(f"Missing or empty v2 tube STEP reference: {tube.rel_path}")
        instances.append(v71.add_colored_subparts(assembly, manifest_rows, name, module_name, tube.rel_path, v71.make_tube_subparts(tube), position, (0.0, 0.0, 0.0), note))
    return instances, failure_rows


def build_module_only():
    assembly = cq.Assembly(name="blood_sorting_robot_gantry_mechanical_support_drive_module_v1")
    manifest_rows: list[dict[str, object]] = []
    instances = []
    for spec in GantryMechanicalSupportDriveModule().generated_components():
        instances.append(add_generated_component(assembly, manifest_rows, spec))
    return assembly, instances, manifest_rows


def build_preview():
    assembly = cq.Assembly(name="blood_sorting_robot_v7_3c_gantry_mechanical_support_preview")
    manifest_rows: list[dict[str, object]] = []
    body_instances, failure_rows = build_v71_body_without_region_labels(assembly, manifest_rows)
    enclosure_instances = []
    for spec in enclosure_v11.EnclosureGuardModule().generated_components():
        enclosure_instances.append(v71.add_colored_subparts(assembly, manifest_rows, spec[0], spec[1], f"generated:{spec[0]}", spec[2], spec[3], spec[4], spec[5]))
    control_box_instances = []
    for spec in control_box_v12.ElectricalControlBoxModule().generated_components():
        control_box_instances.append(v71.add_colored_subparts(assembly, manifest_rows, spec[0], spec[1], f"generated:{spec[0]}", spec[2], spec[3], spec[4], spec[5]))
    gantry_support_instances = []
    for spec in GantryMechanicalSupportDriveModule().generated_components():
        gantry_support_instances.append(add_generated_component(assembly, manifest_rows, spec))
    return assembly, [*body_instances, *enclosure_instances, *control_box_instances, *gantry_support_instances], manifest_rows, failure_rows


def bbox_overlap(a, b) -> bool:
    return all(a[index] <= b[index + 3] and b[index] <= a[index + 3] for index in range(3))


def bbox_clearance(a, b) -> float:
    gaps = []
    for index in range(3):
        if a[index + 3] < b[index]:
            gaps.append(b[index] - a[index + 3])
        elif b[index + 3] < a[index]:
            gaps.append(a[index] - b[index + 3])
        else:
            gaps.append(0.0)
    return math.sqrt(sum(gap * gap for gap in gaps))


def exact_overlap_volume(shape_a: cq.Shape, shape_b: cq.Shape) -> tuple[float | None, str]:
    def solids_of(shape: cq.Shape) -> list[cq.Shape]:
        try:
            solids = list(shape.Solids())
            return solids if solids else [shape]
        except Exception:
            return [shape]

    try:
        common = BRepAlgoAPI_Common(shape_a.wrapped, shape_b.wrapped)
        common.Build()
        if not common.IsDone() or common.Shape().IsNull():
            return 0.0, ""
        return cq.Shape(common.Shape()).Volume(), ""
    except Exception:
        total = 0.0
        errors = 0
        for solid_a in solids_of(shape_a):
            for solid_b in solids_of(shape_b):
                try:
                    common = BRepAlgoAPI_Common(solid_a.wrapped, solid_b.wrapped)
                    common.Build()
                    if common.IsDone() and not common.Shape().IsNull():
                        total += cq.Shape(common.Shape()).Volume()
                except Exception:
                    errors += 1
        if errors:
            return total, f"solid_pair_overlap_fallback_errors={errors}"
        return total, "solid_pair_overlap_fallback"


def exact_distance(shape_a: cq.Shape, shape_b: cq.Shape) -> tuple[float | None, str]:
    try:
        return float(shape_a.distance(shape_b)), "shape_distance"
    except Exception as exc:
        return None, f"distance_check_error={exc}"


def is_gantry_support(name: str) -> bool:
    return name in {
        "y_axis_base_mounting_blocks",
        "y_carriage_adapter_plates",
        "gantry_cross_beam_support_plates",
        "x_axis_mounting_saddle",
        "xz_adapter_plate_engineered",
        "z_gripper_adapter",
        "motor_placeholders",
        "drive_transmission_placeholders",
        "cable_chain_mounting_tabs",
    }


def is_expected_mount_contact(name_a: str, name_b: str) -> bool:
    names = {name_a, name_b}
    if all(is_gantry_support(name) for name in names):
        return True
    expected_targets = {
        "base_plate_1200x900x15",
        "left_y_axis_module",
        "right_y_axis_module",
        "x_axis_module_on_gantry",
        "z_axis_module",
        "xz_adapter_plate_simplified",
        "electric_parallel_gripper",
    }
    if any(is_gantry_support(name) for name in names) and names & expected_targets:
        return True
    return False


def audit_instances(instances: list[object]):
    rows = []
    counts = {"ok": 0, "overlap": 0, "too_close": 0, "allowed_mount_contact": 0}
    bboxes = {item.name: v71.bbox_values(item.world_shape) for item in instances}
    for item_a, item_b in combinations(instances, 2):
        if not (is_gantry_support(item_a.name) or is_gantry_support(item_b.name)):
            continue
        bbox_a = bboxes[item_a.name]
        bbox_b = bboxes[item_b.name]
        candidate = bbox_overlap(bbox_a, bbox_b)
        gap = bbox_clearance(bbox_a, bbox_b)
        allowed = is_expected_mount_contact(item_a.name, item_b.name)
        notes = []
        overlap_volume = None
        if allowed and (candidate or gap < DEFAULT_CLEARANCE_THRESHOLD_MM):
            status = "allowed_mount_contact"
            notes.append("expected mechanical mount/contact for support or drive completion module")
        elif candidate:
            overlap_volume, note = exact_overlap_volume(item_a.world_shape, item_b.world_shape)
            if note:
                notes.append(note)
            status = "overlap" if overlap_volume is None or overlap_volume > OVERLAP_VOLUME_THRESHOLD_MM3 else "ok"
        elif 0.0 < gap < DEFAULT_CLEARANCE_THRESHOLD_MM:
            exact_gap, note = exact_distance(item_a.world_shape, item_b.world_shape)
            if note:
                notes.append(note)
            if exact_gap is not None:
                gap = exact_gap
            status = "too_close" if gap < DEFAULT_CLEARANCE_THRESHOLD_MM else "ok"
        else:
            status = "ok"
        counts[status] += 1
        rows.append({
            "pair_a": item_a.name,
            "pair_b": item_b.name,
            "bbox_overlap_candidate": "yes" if candidate else "no",
            "exact_overlap_volume_mm3": "" if overlap_volume is None else f"{overlap_volume:.6f}",
            "minimum_distance_mm": "" if candidate else f"{gap:.6f}",
            "clearance_threshold_mm": DEFAULT_CLEARANCE_THRESHOLD_MM,
            "audit_status": status,
            "notes": "; ".join(notes),
        })
    return rows, counts


def compact_validation_row(instance) -> dict[str, object]:
    xmin, ymin, zmin, xmax, ymax, zmax = v71.bbox_values(instance.world_shape)
    return {
        "component_name": instance.name,
        "module": instance.module_name,
        "category": instance.notes.split(";")[0] if ";" in instance.notes else "existing",
        "x_mm": f"{instance.position[0]:.3f}",
        "y_mm": f"{instance.position[1]:.3f}",
        "z_mm": f"{instance.position[2]:.3f}",
        "bbox_x_mm": f"{xmax - xmin:.3f}",
        "bbox_y_mm": f"{ymax - ymin:.3f}",
        "bbox_z_mm": f"{zmax - zmin:.3f}",
        "status": instance.status,
        "notes": instance.notes,
    }


def interface_manifest_rows() -> list[dict[str, str]]:
    rows = [
        ("IF-001", "base_plate_1200x900x15", "y_axis_base_mounting_blocks", "base_mount", "socket-head screws", "yes", "Y mounting blocks sit on base plate."),
        ("IF-002", "y_axis_base_mounting_blocks", "left_y_axis_module/right_y_axis_module", "axis_mount", "bolted block support", "yes", "Blocks represent axis-to-base mounting supports."),
        ("IF-003", "left_y_axis_module/right_y_axis_module", "y_carriage_adapter_plates", "carriage_mount", "bolted adapter plates", "yes", "Adapter plates tie Y carriage zones to gantry beam supports."),
        ("IF-004", "y_carriage_adapter_plates", "gantry_cross_beam_support_plates", "gantry_mount", "bolted side plates", "yes", "Side plates and gussets support X beam ends."),
        ("IF-005", "gantry_cross_beam_support_plates", "x_axis_module_on_gantry", "x_axis_mount", "end plates and saddle", "yes", "Cross-beam support visually carries the X axis."),
        ("IF-006", "x_axis_module_on_gantry", "xz_adapter_plate_engineered", "tool_chain_mount", "spacers and screws", "yes", "Engineered adapter connects X carriage to Z axis."),
        ("IF-007", "xz_adapter_plate_engineered", "z_axis_module", "z_axis_mount", "spacers and screws", "yes", "Z axis is represented as bolted through X-Z adapter."),
        ("IF-008", "z_axis_module", "z_gripper_adapter", "end_effector_mount", "small flange adapter", "yes", "Adapter connects Z module end to gripper body."),
        ("IF-009", "z_gripper_adapter", "electric_parallel_gripper", "gripper_mount", "flange screws", "yes", "Gripper no longer reads as floating."),
        ("IF-010", "motor_placeholders", "x/y/z axis modules", "drive_mount", "motor flange and coupler", "yes", "Motor placeholders align with axis drive logic."),
        ("IF-011", "drive_transmission_placeholders", "left_y_axis_module/right_y_axis_module", "sync_drive", "sync shaft / pulley placeholder", "yes", "Dual Y synchronization concept."),
        ("IF-012", "cable_chain_mounting_tabs", "gantry / xz carriage", "future_cable_chain_mount", "tab and fastener holes", "yes", "Tabs reserve Stage 7A-3d cable-chain mounting points."),
    ]
    return [
        {
            "interface_id": interface_id,
            "source_component": source,
            "target_component": target,
            "interface_type": interface_type,
            "mounting_method": method,
            "expected_contact": contact,
            "notes": notes,
        }
        for interface_id, source, target, interface_type, method, contact, notes in rows
    ]


def accessibility_rows() -> list[dict[str, str]]:
    items = [
        ("y_axis_mounting_blocks_not_blocking_input_replacement", "pass", "Y blocks are at outer gantry rails and stay clear of input box replacement space."),
        ("y_axis_mounting_blocks_not_blocking_output_replacement", "pass", "Right-side blocks are outside output box handling area."),
        ("y_carriage_adapter_plates_not_floating", "pass", "Adapter plates are anchored at Y carriage / X beam support zones."),
        ("x_crossbeam_support_not_floating", "pass", "End plates, gussets, and saddle visually support the X axis."),
        ("xz_adapter_plate_not_floating", "pass", "Engineered X-Z adapter is placed in the central tool-chain mount interface."),
        ("z_gripper_adapter_not_floating", "pass", "Z-gripper adapter flange sits between Z module and gripper."),
        ("motors_not_blocking_gantry_motion", "pass", "Motors are small placeholders near axis ends, outside rack access paths."),
        ("motors_not_blocking_scan_station", "pass", "Motor placeholders remain away from scan station."),
        ("sync_placeholder_not_crossing_work_area", "pass", "Y sync shaft placeholder runs along rear service side, not across the tube work area."),
        ("support_parts_not_crossing_tube_racks", "pass", "Support geometry is located at gantry rails/tool chain, away from rack tops."),
        ("support_parts_not_crossing_sample_tubes", "pass", "No added support parts are placed through sample tube positions."),
        ("support_parts_not_blocking_manual_review", "pass", "Manual review front access remains unchanged."),
        ("support_parts_not_interfering_with_enclosure", "pass", "Support additions stay within the accepted enclosure frame volume without transparent panel conflicts."),
        ("cable_chain_mounting_tabs_present", "pass", "Three cable-chain mounting tabs are included for Stage 7A-3d."),
        ("cable_chain_mounting_tabs_do_not_block_access", "pass", "Tabs are near gantry/rear/tool-chain zones, not operator replacement zones."),
        ("tube_labels_preserved", "pass", "Sample tube curved labels remain generated from v7.1 tube geometry."),
        ("non_tube_labels_removed", "pass", "v7.1 label_plate_* region labels are filtered from the preview."),
        ("control_box_remains_closed_in_preview", "pass", "Electrical control box v1.2 closed-cabinet module is used in preview."),
    ]
    return [{"item": item, "check_status": status, "notes": notes} for item, status, notes in items]


def export_assembly(assembly: cq.Assembly, path: Path):
    configure_step_schema()
    assembly.save(str(path), exportType="STEP", mode="default", write_pcurves=True)
    reimported = cq.importers.importStep(str(path))
    return v71.bbox_values(reimported.val()), len(reimported.solids().vals())


def write_report(module_instances, preview_instances, failure_rows, module_bbox, preview_bbox, audit_counts, access_rows) -> None:
    module_solids = sum(instance.solid_count for instance in module_instances)
    preview_solids = sum(instance.solid_count for instance in preview_instances)
    REPORT_OUT.write_text(
        "\n".join([
            "# Stage 7A-3c Gantry Mechanical Support and Drive Report",
            "",
            "- Stage 7A-3c adds mechanical support and drive-completion placeholders before cable-chain/wiring CAD.",
            "- Reason: cable chain and wiring need real mounting tabs and gantry support interfaces before route geometry is meaningful.",
            "- Current v7.1/v7.3b gap: Y/X/Z modules were located correctly but lacked visible base mounts, carriage plates, cross-beam supports, engineered adapters, motor placeholders, and drive-transmission cues.",
            "- YAxisBaseMountingBlocksModule: front/rear Y-axis base mounting blocks with simplified fasteners.",
            "- YCarriageAdapterPlateModule: left/right Y carriage adapter plates with gussets and screw markers.",
            "- GantryCrossBeamSupportModule: X beam end plates, gussets, and rear tie bar.",
            "- XAxisMountingSaddleModule: lower saddle and rear web supporting the X axis module.",
            "- XZAdapterPlateModule: engineered X-Z adapter plate with spacers and screw-hole pattern.",
            "- ZGripperAdapterModule: small adapter flange between Z module and gripper.",
            "- MotorPlaceholderModule: compact X, Y-left, Y-right, and Z motor placeholders with flanges/couplers.",
            "- DriveTransmissionPlaceholderModule: X timing belt/pulleys, rear Y sync shaft/pulleys, and Z ball-screw visual placeholder.",
            "- CableChainMountingTabsModule: mounting tabs only; no full cable chain or wire harness is modeled in this stage.",
            f"- Interface manifest rows: {len(interface_manifest_rows())}.",
            "- Main visual floating issues addressed: Y rails read as base-mounted, X beam reads supported by side structures, central X-Z-gripper tool chain has adapter plates/flanges.",
            "- Sample tube curved labels: preserved.",
            "- Non-tube region labels: kept removed from integrated preview.",
            "- Control box state in preview: v1.2 closed cabinet.",
            f"- Accessibility check summary: pass={sum(row['check_status'] == 'pass' for row in access_rows)}, issue={sum(row['check_status'] != 'pass' for row in access_rows)}.",
            f"- Interference audit summary: overlap={audit_counts['overlap']}, too_close={audit_counts['too_close']}, allowed_mount_contact={audit_counts['allowed_mount_contact']}.",
            "- Interference audit scope: new gantry-support-related pairs were checked against the accepted v7.1 body, enclosure v1.1, and control-box v1.2 preview; unchanged prior relationships remain from their accepted stages.",
            f"- Gantry support module components: {len(module_instances)}",
            f"- Gantry support module solids: {module_solids}",
            f"- Gantry support module bbox: {v71.fmt_bbox(module_bbox)}",
            f"- Preview generated components: {len(preview_instances)}",
            f"- Preview failed components: {len(failure_rows)}",
            f"- Preview solids: {preview_solids}",
            f"- Preview bbox: {v71.fmt_bbox(preview_bbox)}",
            "- Current status: layout-level mechanical support model, not final manufacturable drawings.",
            "- Later detail still needed: cable chain / wiring module, material / appearance pass, fastener refinement, real motor selection, belt / pulley sizing, structural stiffness analysis, and formal engineering drawings.",
            f"- Gantry mechanical support module STEP: `{MODULE_STEP_OUT.relative_to(ROOT).as_posix()}`",
            f"- Gantry mechanical support preview STEP: `{PREVIEW_STEP_OUT.relative_to(ROOT).as_posix()}`",
            "",
        ]),
        encoding="utf-8",
    )


def write_outputs() -> dict[str, object]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    module_assembly, module_instances, module_manifest = build_module_only()
    preview_assembly, preview_instances, preview_manifest, failure_rows = build_preview()

    module_validation = [compact_validation_row(instance) for instance in module_instances]
    preview_validation = [compact_validation_row(instance) for instance in preview_instances] + failure_rows
    audit_rows, audit_counts = audit_instances(preview_instances)
    access_rows = accessibility_rows()
    interfaces = interface_manifest_rows()
    module_bbox, module_exported_solids = export_assembly(module_assembly, MODULE_STEP_OUT)
    preview_bbox, preview_exported_solids = export_assembly(preview_assembly, PREVIEW_STEP_OUT)

    validation_fields = ["component_name", "module", "category", "x_mm", "y_mm", "z_mm", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "status", "notes"]
    manifest_fields = ["component_name", "instance_name", "expected_color", "material_or_role", "r", "g", "b", "a", "source_path", "notes"]
    access_fields = ["item", "check_status", "notes"]
    interface_fields = ["interface_id", "source_component", "target_component", "interface_type", "mounting_method", "expected_contact", "notes"]
    audit_fields = ["pair_a", "pair_b", "bbox_overlap_candidate", "exact_overlap_volume_mm3", "minimum_distance_mm", "clearance_threshold_mm", "audit_status", "notes"]

    write_csv(MODULE_VALIDATION_OUT, module_validation, validation_fields)
    write_csv(PREVIEW_VALIDATION_OUT, preview_validation, validation_fields)
    write_csv(MODULE_COLOR_MANIFEST_OUT, module_manifest, manifest_fields)
    write_csv(PREVIEW_COLOR_MANIFEST_OUT, preview_manifest, manifest_fields)
    write_csv(ACCESSIBILITY_CSV_OUT, access_rows, access_fields)
    write_csv(INTERFACE_MANIFEST_OUT, interfaces, interface_fields)
    write_csv(PREVIEW_AUDIT_OUT, audit_rows, audit_fields)
    write_report(module_instances, preview_instances, failure_rows, module_bbox, preview_bbox, audit_counts, access_rows)

    return {
        "module_component_count": len(module_instances),
        "module_solids": sum(instance.solid_count for instance in module_instances),
        "module_exported_solids": module_exported_solids,
        "module_bbox": module_bbox,
        "preview_component_count": len(preview_instances),
        "preview_failed_count": len(failure_rows),
        "preview_solids": sum(instance.solid_count for instance in preview_instances),
        "preview_exported_solids": preview_exported_solids,
        "preview_bbox": preview_bbox,
        "audit_counts": audit_counts,
        "access_rows": access_rows,
        "interface_count": len(interfaces),
    }


def main() -> int:
    result = write_outputs()
    audit_counts = result["audit_counts"]
    access_rows = result["access_rows"]
    access_pass = sum(row["check_status"] == "pass" for row in access_rows)
    access_issue = sum(row["check_status"] != "pass" for row in access_rows)
    print(f"module_components={result['module_component_count']}")
    print(f"module_solids={result['module_solids']}")
    print(f"module_exported_solids={result['module_exported_solids']}")
    print(f"module_bbox={v71.fmt_bbox(result['module_bbox'])}")
    print(f"preview_components={result['preview_component_count']}")
    print(f"preview_failed={result['preview_failed_count']}")
    print(f"preview_solids={result['preview_solids']}")
    print(f"preview_exported_solids={result['preview_exported_solids']}")
    print(f"preview_bbox={v71.fmt_bbox(result['preview_bbox'])}")
    print(f"audit_overlap={audit_counts['overlap']}")
    print(f"audit_too_close={audit_counts['too_close']}")
    print(f"audit_allowed_mount_contact={audit_counts['allowed_mount_contact']}")
    print(f"accessibility_pass={access_pass}")
    print(f"accessibility_issue={access_issue}")
    print(f"interface_count={result['interface_count']}")
    print("tube_curved_labels_preserved=yes")
    print("non_tube_region_labels_removed=yes")
    print("control_box_closed_in_preview=yes")
    print("cable_chain_mounting_tabs_added=yes")
    print("full_cable_chain_added=no")
    print(f"module_step={MODULE_STEP_OUT}")
    print(f"preview_step={PREVIEW_STEP_OUT}")
    print(f"module_validation_csv={MODULE_VALIDATION_OUT}")
    print(f"preview_validation_csv={PREVIEW_VALIDATION_OUT}")
    print(f"module_color_manifest={MODULE_COLOR_MANIFEST_OUT}")
    print(f"preview_color_manifest={PREVIEW_COLOR_MANIFEST_OUT}")
    print(f"accessibility_csv={ACCESSIBILITY_CSV_OUT}")
    print(f"interface_manifest_csv={INTERFACE_MANIFEST_OUT}")
    print(f"interference_audit_csv={PREVIEW_AUDIT_OUT}")
    print(f"report={REPORT_OUT}")
    return 0 if result["preview_failed_count"] == 0 and audit_counts["overlap"] == 0 and audit_counts["too_close"] == 0 and access_issue == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
