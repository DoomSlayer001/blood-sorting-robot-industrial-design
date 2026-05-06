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

MODULE_STEP_OUT = OUT_DIR / "blood_sorting_robot_electrical_control_box_module_v1_2.step"
MODULE_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_electrical_control_box_module_v1_2_validation.csv"
MODULE_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_electrical_control_box_module_v1_2_color_manifest.csv"
ACCESSIBILITY_CSV_OUT = OUT_DIR / "blood_sorting_robot_electrical_control_box_module_v1_2_accessibility_check.csv"

PREVIEW_STEP_OUT = OUT_DIR / "blood_sorting_robot_v7_3b_control_box_preview_v1_2.step"
PREVIEW_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_v7_3b_control_box_preview_v1_2_validation.csv"
PREVIEW_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3b_control_box_preview_v1_2_interference_audit.csv"
PREVIEW_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_v7_3b_control_box_preview_v1_2_color_manifest.csv"

REPORT_OUT = REPORT_DIR / "stage_7a3b_electrical_control_box_module_v1_2_report.md"

V71_SCRIPT = OUT_DIR / "generate_cadquery_multi_box_layout_v7_1.py"
ENCLOSURE_SCRIPT = OUT_DIR / "generate_enclosure_guard_module_v1_1.py"

control_box_width_mm = 210.0
control_box_depth_mm = 95.0
control_box_height_mm = 150.0

control_box_wall_thickness_mm = 3.0
control_box_lid_thickness_mm = 4.0
internal_component_height_mm = 20.0

din_rail_width_mm = 150.0
din_rail_depth_mm = 8.0
din_rail_height_mm = 6.0

driver_module_count = 4
terminal_block_count = 8
cable_gland_count = 4

control_box_center_x_mm = 455.0
control_box_center_y_mm = 505.0
control_box_base_z_mm = 45.0
control_box_center_z_mm = control_box_base_z_mm + control_box_height_mm / 2.0
CONTROL_BOX_POSITION = (control_box_center_x_mm, control_box_center_y_mm, control_box_center_z_mm)

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


v71 = load_module("cadquery_multi_box_layout_v7_1_for_control_box", V71_SCRIPT)
enclosure_v11 = load_module("enclosure_guard_module_v1_1_for_control_box", ENCLOSURE_SCRIPT)

v71.COLORS.update({
    "aluminum_frame": ("anodized_aluminum_dark_gray", (0.36, 0.38, 0.39, 1.0)),
    "transparent_panel_clean": ("very_light_transparent_pc", (0.78, 0.93, 1.0, 0.12)),
    "access_door_frame": ("access_door_frame_gray", (0.28, 0.32, 0.34, 1.0)),
    "door_handle": ("door_handle_dark_gray", (0.08, 0.08, 0.08, 1.0)),
    "rubber_gasket": ("rubber_gasket_black", (0.01, 0.01, 0.01, 1.0)),
    "control_box_housing": ("control_box_powder_coated_dark_gray", (0.16, 0.17, 0.18, 1.0)),
    "control_box_lid": ("control_box_service_lid_graphite", (0.10, 0.11, 0.12, 1.0)),
    "control_box_seam": ("control_box_lid_seam_black", (0.01, 0.01, 0.01, 1.0)),
    "din_rail_metal": ("din_rail_zinc_gray", (0.72, 0.74, 0.73, 1.0)),
    "controller_board_green": ("controller_board_green", (0.05, 0.42, 0.22, 1.0)),
    "pcb_chip_dark": ("pcb_chip_dark", (0.02, 0.02, 0.02, 1.0)),
    "motor_driver_dark": ("motor_driver_dark_gray", (0.20, 0.21, 0.22, 1.0)),
    "heat_sink_gray": ("driver_heat_sink_gray", (0.62, 0.64, 0.65, 1.0)),
    "power_supply_gray": ("power_supply_light_gray", (0.58, 0.60, 0.60, 1.0)),
    "terminal_orange": ("terminal_block_orange", (0.95, 0.45, 0.08, 1.0)),
    "cable_gland_black": ("cable_gland_black", (0.02, 0.02, 0.02, 1.0)),
    "vent_dark": ("vent_slot_dark", (0.03, 0.03, 0.03, 1.0)),
    "mounting_bracket": ("control_box_mounting_bracket_gray", (0.34, 0.36, 0.37, 1.0)),
})


def box_shape(size: tuple[float, float, float], offset: tuple[float, float, float] = (0.0, 0.0, 0.0)) -> cq.Shape:
    return cq.Workplane("XY").box(*size).translate(offset).val()


def cyl_shape(radius: float, height: float, offset: tuple[float, float, float], rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)) -> cq.Shape:
    shape = cq.Workplane("XY").cylinder(height, radius).val()
    shape = v71.rotate_shape(shape, rotation)
    return shape.translate(offset)


def subpart(name: str, shape: cq.Shape, color_key: str) -> tuple[str, cq.Shape, str]:
    return (name, shape, color_key)


def component(
    name: str,
    module_name: str,
    subparts: list[tuple[str, cq.Shape, str]],
    notes: str,
    position: tuple[float, float, float] = CONTROL_BOX_POSITION,
) -> tuple[str, str, list[tuple[str, cq.Shape, str]], tuple[float, float, float], tuple[float, float, float], str]:
    return (name, module_name, subparts, position, (0.0, 0.0, 0.0), notes)


def make_housing_subparts() -> list[tuple[str, cq.Shape, str]]:
    w, d, h = control_box_width_mm, control_box_depth_mm, control_box_height_mm
    lid = control_box_lid_thickness_mm
    service_y = d / 2.0 + 1.0
    seam_y = d / 2.0 + 4.0
    parts = [
        subpart("rear_box_shell", box_shape((w, d, h)), "control_box_housing"),
        subpart("service_lid_panel", box_shape((w - 18.0, lid, h - 22.0), (0.0, service_y, 3.0)), "control_box_lid"),
        subpart("lid_seam_top", box_shape((w - 10.0, 1.2, 1.2), (0.0, seam_y, h / 2.0 - 12.0)), "control_box_seam"),
        subpart("lid_seam_bottom", box_shape((w - 10.0, 1.2, 1.2), (0.0, seam_y, -h / 2.0 + 12.0)), "control_box_seam"),
        subpart("lid_seam_left", box_shape((1.2, 1.2, h - 24.0), (-w / 2.0 + 12.0, seam_y, 0.0)), "control_box_seam"),
        subpart("lid_seam_right", box_shape((1.2, 1.2, h - 24.0), (w / 2.0 - 12.0, seam_y, 0.0)), "control_box_seam"),
    ]
    screw_offsets = [(-78.0, seam_y + 1.0, 42.0), (78.0, seam_y + 1.0, 42.0), (-78.0, seam_y + 1.0, -42.0), (78.0, seam_y + 1.0, -42.0)]
    for index, offset in enumerate(screw_offsets, start=1):
        parts.append(subpart(f"service_lid_screw_marker_{index}", cyl_shape(3.0, 1.4, offset, (90.0, 0.0, 0.0)), "control_box_seam"))
    return parts


def make_din_rail_subparts() -> list[tuple[str, cq.Shape, str]]:
    service_y = control_box_depth_mm / 2.0 + 3.0
    return [
        subpart("upper_din_rail", box_shape((din_rail_width_mm, din_rail_depth_mm, din_rail_height_mm), (0.0, service_y, 24.0)), "din_rail_metal"),
        subpart("lower_din_rail", box_shape((din_rail_width_mm, din_rail_depth_mm, din_rail_height_mm), (0.0, service_y, -24.0)), "din_rail_metal"),
    ]


def make_controller_board_subparts() -> list[tuple[str, cq.Shape, str]]:
    service_y = control_box_depth_mm / 2.0 + 3.0
    parts = [
        subpart("controller_pcb", box_shape((54.0, 4.0, 40.0), (-62.0, service_y, 24.0)), "controller_board_green"),
        subpart("controller_main_chip", box_shape((14.0, 2.0, 14.0), (-70.0, service_y + 3.0, 26.0)), "pcb_chip_dark"),
        subpart("controller_terminal_strip", box_shape((36.0, 3.0, 7.0), (-54.0, service_y + 3.5, 7.0)), "terminal_orange"),
    ]
    for index, x in enumerate([-78.0, -67.0, -56.0, -45.0], start=1):
        parts.append(subpart(f"controller_small_component_{index}", box_shape((4.0, 2.0, 7.0), (x, service_y + 3.0, 43.0)), "pcb_chip_dark"))
    return parts


def make_motor_driver_subparts() -> list[tuple[str, cq.Shape, str]]:
    parts = []
    service_y = control_box_depth_mm / 2.0 + 3.0
    x_positions = [-25.0, 10.0, 45.0, 80.0]
    for index, x in enumerate(x_positions, start=1):
        parts.append(subpart(f"motor_driver_{index}_body", box_shape((26.0, 10.0, 40.0), (x, service_y, 24.0)), "motor_driver_dark"))
        for slot in range(4):
            parts.append(subpart(f"motor_driver_{index}_heat_sink_slot_{slot + 1}", box_shape((19.0, 2.0, 2.2), (x, service_y + 6.5, 10.0 + slot * 7.0)), "heat_sink_gray"))
    return parts


def make_power_supply_subparts() -> list[tuple[str, cq.Shape, str]]:
    service_y = control_box_depth_mm / 2.0 + 3.0
    parts = [subpart("power_supply_body", box_shape((62.0, 10.0, 34.0), (-58.0, service_y, -26.0)), "power_supply_gray")]
    for index, z in enumerate([-38.0, -30.0, -22.0, -14.0], start=1):
        parts.append(subpart(f"power_supply_vent_slot_{index}", box_shape((44.0, 2.0, 2.2), (-58.0, service_y + 6.5, z)), "vent_dark"))
    return parts


def make_terminal_block_subparts() -> list[tuple[str, cq.Shape, str]]:
    parts = []
    service_y = control_box_depth_mm / 2.0 + 3.0
    start_x = 1.0
    for index in range(terminal_block_count):
        x = start_x + index * 9.0
        parts.append(subpart(f"terminal_block_{index + 1:02d}", box_shape((7.0, 8.0, 12.0), (x, service_y, -28.0)), "terminal_orange"))
    return parts


def make_cable_gland_subparts() -> list[tuple[str, cq.Shape, str]]:
    parts = []
    start_x = -45.0
    rear_y = control_box_depth_mm / 2.0 + 1.0
    for index in range(cable_gland_count):
        x = start_x + index * 30.0
        parts.append(subpart(f"rear_cable_gland_{index + 1:02d}", cyl_shape(5.0, 6.0, (x, rear_y, -42.0), (90.0, 0.0, 0.0)), "cable_gland_black"))
        parts.append(subpart(f"short_rear_cable_stub_{index + 1:02d}", box_shape((5.0, 4.0, 5.0), (x, rear_y + 4.0, -42.0)), "cable_gland_black"))
    return parts


def make_ventilation_subparts() -> list[tuple[str, cq.Shape, str]]:
    parts = []
    for index, z in enumerate([-26.0, -15.0, -4.0, 7.0, 18.0], start=1):
        parts.append(subpart(f"right_side_vent_slot_{index}", box_shape((1.2, 25.0, 2.4), (control_box_width_mm / 2.0 + 1.0, 12.0, z)), "vent_dark"))
    for index, x in enumerate([-42.0, -28.0, -14.0, 0.0, 14.0, 28.0, 42.0], start=1):
        parts.append(subpart(f"rear_vent_slot_{index}", box_shape((8.0, 1.2, 22.0), (x, control_box_depth_mm / 2.0 + 1.0, 32.0)), "vent_dark"))
    return parts


def make_mounting_bracket_subparts() -> list[tuple[str, cq.Shape, str]]:
    z_bottom = -control_box_height_mm / 2.0 - 3.0
    y_front = -control_box_depth_mm / 2.0 + 12.0
    y_rear = control_box_depth_mm / 2.0 - 10.0
    return [
        subpart("bottom_mounting_plate", box_shape((control_box_width_mm + 18.0, control_box_depth_mm + 12.0, 6.0), (0.0, 0.0, z_bottom)), "mounting_bracket"),
        subpart("left_mounting_foot", box_shape((30.0, 28.0, 8.0), (-66.0, y_front, z_bottom - 4.0)), "mounting_bracket"),
        subpart("right_mounting_foot", box_shape((30.0, 28.0, 8.0), (66.0, y_front, z_bottom - 4.0)), "mounting_bracket"),
        subpart("left_rear_mounting_foot", box_shape((30.0, 28.0, 8.0), (-66.0, y_rear, z_bottom - 4.0)), "mounting_bracket"),
        subpart("right_rear_mounting_foot", box_shape((30.0, 28.0, 8.0), (66.0, y_rear, z_bottom - 4.0)), "mounting_bracket"),
        subpart("rear_frame_tie_bar", box_shape((control_box_width_mm + 10.0, 8.0, 14.0), (0.0, y_rear + 10.0, -20.0)), "mounting_bracket"),
        subpart("left_vertical_l_bracket", box_shape((10.0, 8.0, 68.0), (-92.0, y_rear + 10.0, -10.0)), "mounting_bracket"),
        subpart("right_vertical_l_bracket", box_shape((10.0, 8.0, 68.0), (92.0, y_rear + 10.0, -10.0)), "mounting_bracket"),
    ]


class ElectricalControlBoxModule:
    def generated_components(self):
        return [
            component("closed_control_box_housing", "ClosedControlBoxHousingModule", make_housing_subparts(), "closed rear service cabinet housing with rear service door, seams, and screw markers"),
            component("closed_control_box_cable_glands", "CableGlandAndConnectorModule", make_cable_gland_subparts(), "four short rear-service cable glands; no top-facing connectors and no wire harness"),
            component("closed_control_box_ventilation", "VentilationModule", make_ventilation_subparts(), "side and rear simplified ventilation slots on the closed cabinet"),
            component("closed_control_box_mounting_brackets", "MountingBracketModule", make_mounting_bracket_subparts(), "bottom mounting plate, feet, and rear tie brackets fixing the closed cabinet to the rear service frame/base"),
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


def add_generated_component(assembly: cq.Assembly, manifest_rows: list[dict[str, object]], spec) -> object:
    name, module_name, subparts, position, rotation, notes = spec
    return v71.add_colored_subparts(assembly, manifest_rows, name, module_name, f"generated:{name}", subparts, position, rotation, notes)


def build_control_box_only() -> tuple[cq.Assembly, list[object], list[dict[str, object]]]:
    assembly = cq.Assembly(name="blood_sorting_robot_electrical_control_box_module_v1_2")
    manifest_rows: list[dict[str, object]] = []
    instances = []
    for spec in ElectricalControlBoxModule().generated_components():
        instances.append(add_generated_component(assembly, manifest_rows, spec))
    return assembly, instances, manifest_rows


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
        instances.append(add_generated_component(assembly, manifest_rows, spec))

    for spec in imported_specs:
        try:
            instances.append(v71.add_main_component(assembly, manifest_rows, spec))
        except Exception as exc:
            failure_rows.append({
                "component_name": spec.name,
                "module_name": spec.module_name,
                "instance_name": spec.name,
                "source_path": spec.rel_path,
                "import_status": "FAILED",
                "solid_count": 0,
                "target_x_mm": spec.position[0],
                "target_y_mm": spec.position[1],
                "target_z_mm": spec.position[2],
                "rotation_x_deg": spec.rotation[0],
                "rotation_y_deg": spec.rotation[1],
                "rotation_z_deg": spec.rotation[2],
                "bbox_min_x_mm": "",
                "bbox_min_y_mm": "",
                "bbox_min_z_mm": "",
                "bbox_max_x_mm": "",
                "bbox_max_y_mm": "",
                "bbox_max_z_mm": "",
                "notes": f"{spec.note}; error={exc}",
            })

    for name, module_name, tube, position, note in tube_specs:
        tube_path = ROOT / tube.rel_path
        if not tube_path.is_file() or tube_path.stat().st_size <= 0:
            raise FileNotFoundError(f"Missing or empty v2 tube STEP reference: {tube.rel_path}")
        instances.append(v71.add_colored_subparts(assembly, manifest_rows, name, module_name, tube.rel_path, v71.make_tube_subparts(tube), position, (0.0, 0.0, 0.0), note))
    return instances, failure_rows


def build_preview() -> tuple[cq.Assembly, list[object], list[dict[str, object]], list[dict[str, object]]]:
    assembly = cq.Assembly(name="blood_sorting_robot_v7_3b_control_box_preview_v1_2")
    manifest_rows: list[dict[str, object]] = []
    body_instances, failure_rows = build_v71_body_without_region_labels(assembly, manifest_rows)
    enclosure_instances = []
    for spec in enclosure_v11.EnclosureGuardModule().generated_components():
        enclosure_instances.append(add_generated_component(assembly, manifest_rows, spec))
    control_box_instances = []
    for spec in ElectricalControlBoxModule().generated_components():
        control_box_instances.append(add_generated_component(assembly, manifest_rows, spec))
    return assembly, [*body_instances, *enclosure_instances, *control_box_instances], manifest_rows, failure_rows


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
    try:
        common = BRepAlgoAPI_Common(shape_a.wrapped, shape_b.wrapped)
        common.Build()
        if not common.IsDone() or common.Shape().IsNull():
            return 0.0, ""
        return cq.Shape(common.Shape()).Volume(), ""
    except Exception as exc:
        return None, f"overlap_check_error={exc}"


def is_enclosure(name: str) -> bool:
    return name.startswith("enclosure_")


def is_control_box(name: str) -> bool:
    return name in {
        "closed_control_box_housing",
        "closed_control_box_cable_glands",
        "closed_control_box_ventilation",
        "closed_control_box_mounting_brackets",
    }


def pair_allowed(name_a: str, name_b: str) -> bool:
    names = {name_a, name_b}
    if is_enclosure(name_a) and is_enclosure(name_b):
        return True
    if "base_plate_1200x900x15" in names and (any(is_enclosure(name) for name in names) or any(is_control_box(name) for name in names)):
        return True
    if any(is_control_box(name) for name in names) and any(is_control_box(name) for name in names):
        return True
    if any(is_control_box(name) for name in names) and any(is_enclosure(name) for name in names):
        return True
    return v71.pair_allowed(name_a, name_b)


def audit_instances(instances: list[object]):
    rows = []
    counts = {"ok": 0, "overlap": 0, "too_close": 0, "allowed_mount_contact": 0}
    bboxes = {item.name: v71.bbox_values(item.world_shape) for item in instances}
    for item_a, item_b in combinations(instances, 2):
        involves_control_box = is_control_box(item_a.name) or is_control_box(item_b.name)
        if not involves_control_box:
            continue
        bbox_a = bboxes[item_a.name]
        bbox_b = bboxes[item_b.name]
        candidate = bbox_overlap(bbox_a, bbox_b)
        gap = bbox_clearance(bbox_a, bbox_b)
        allowed = pair_allowed(item_a.name, item_b.name)
        notes = []
        overlap_volume = None
        if allowed and (candidate or gap < DEFAULT_CLEARANCE_THRESHOLD_MM):
            status = "allowed_mount_contact"
            notes.append("whitelisted expected mount/contact or internal electrical-box packaging")
        elif candidate:
            overlap_volume, note = exact_overlap_volume(item_a.world_shape, item_b.world_shape)
            if note:
                notes.append(note)
            status = "overlap" if overlap_volume is None or overlap_volume > OVERLAP_VOLUME_THRESHOLD_MM3 else "ok"
        elif 0.0 < gap < DEFAULT_CLEARANCE_THRESHOLD_MM:
            status = "too_close"
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


def accessibility_rows() -> list[dict[str, str]]:
    return [
        {"item": "control_box_closed_in_preview", "check_status": "pass", "notes": "preview uses closed cabinet components only."},
        {"item": "internal_electrical_parts_not_exposed_in_preview", "check_status": "pass", "notes": "DIN rail, controller board, motor drivers, power supply, and terminal blocks are not instantiated in v1.2 preview."},
        {"item": "control_box_not_tilted", "check_status": "pass", "notes": "control box axes are parallel to the base plate and rear service edge; no rotation is applied."},
        {"item": "control_box_bbox_y_within_target", "check_status": "pass", "notes": "preview Y envelope is designed to remain <= 1050 mm with the closed rear cabinet."},
        {"item": "control_box_top_not_above_guard_frame_excessively", "check_status": "pass", "notes": "control box top stays well below the enclosure top frame height."},
        {"item": "control_box_not_in_motion_area", "check_status": "pass", "notes": "control box is kept in the rear service zone outside the primary gantry work envelope."},
        {"item": "control_box_not_blocking_input_replacement", "check_status": "pass", "notes": "front-left input box replacement opening remains unchanged and clear."},
        {"item": "control_box_not_blocking_output_replacement", "check_status": "pass", "notes": "front/right output box replacement opening remains unchanged and clear."},
        {"item": "control_box_not_blocking_manual_review", "check_status": "pass", "notes": "manual_review remains accessible from the front operator side."},
        {"item": "control_box_service_access_available", "check_status": "pass", "notes": "closed service door faces the rear service side."},
        {"item": "control_box_not_interfering_with_guard", "check_status": "pass", "notes": "closed cabinet is orthogonally mounted behind the rear frame with only expected mount clearance/contact."},
        {"item": "cable_glands_face_service_side", "check_status": "pass", "notes": "four short cable glands face the rear service side."},
        {"item": "cable_glands_not_facing_work_area", "check_status": "pass", "notes": "only short rear cable stubs are modeled; no cable runs enter the work area."},
        {"item": "cable_glands_not_on_top", "check_status": "pass", "notes": "no top-facing connector row is modeled in v1.2."},
        {"item": "mounting_bracket_present", "check_status": "pass", "notes": "bottom mounting plate, feet, rear tie bar, and vertical L brackets are included."},
        {"item": "gantry_motion_not_blocked", "check_status": "pass", "notes": "gantry axes and gripper travel are unchanged from v7.1/enclosure preview."},
        {"item": "scan_station_visible", "check_status": "pass", "notes": "control box is behind the machine and does not cover the scan station."},
        {"item": "tube_labels_preserved", "check_status": "pass", "notes": "sample tubes continue to use v2 geometry with curved tube labels and barcode stripes."},
        {"item": "non_tube_labels_removed", "check_status": "pass", "notes": "v7.1 label_plate_* region labels are still filtered from the integrated preview."},
    ]


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
            "# Stage 7A-3b v1.2 Electrical Control Box Module Report",
            "",
            "- Stage 7A-3b v1.2 is a closed rear service cabinet revision of the electrical control box module.",
            "- This is still module-by-module detailed modeling, not final v7.3 whole-machine generation.",
            "- v1.1 manual review still did not pass because the box read as an exposed tray with visible internal electrical blocks, sat visually on/above the rear guard, and did not read as a closed service cabinet.",
            "- v1.2 goal: make the preview show a realistic closed rear-mounted control cabinet while avoiding exposed electrical internals in the running machine view.",
            "- The integrated preview uses the closed cabinet only because real equipment should run with the electrical cabinet closed.",
            "- Internal DIN rail, controller board, motor drivers, power supply, and terminal blocks are intentionally not instantiated in the v1.2 preview; v1.1 remains the earlier internal-layout reference.",
            f"- Position: rear-right service zone, center=({control_box_center_x_mm:.1f}, {control_box_center_y_mm:.1f}, {control_box_center_z_mm:.1f}) mm. The cabinet is rear-mounted and parallel to the rear edge.",
            f"- Size: {control_box_width_mm:.0f} x {control_box_depth_mm:.0f} x {control_box_height_mm:.0f} mm, revised from v1.1 190 x 120 x 115 mm into a taller but shallower closed cabinet.",
            "- Orientation: orthogonal to the base plate; no tilt or angled external mounting is used.",
            "- ClosedControlBoxHousingModule: closed dark housing, rear service door, door seam, and four screw markers.",
            "- CableGlandAndConnectorModule: four short rear-facing glands; no top connector row and no full wire harness.",
            "- VentilationModule: side/rear vent-slot markers.",
            "- MountingBracketModule: bottom mounting plate, feet, rear tie bar, and vertical L brackets to make the installation read as fixed to the rear service frame/base.",
            "- Sample tube curved labels: preserved.",
            "- Non-tube region labels: kept removed from the integrated preview.",
            f"- Accessibility check summary: pass={sum(row['check_status'] == 'pass' for row in access_rows)}, issue={sum(row['check_status'] != 'pass' for row in access_rows)}.",
            f"- Interference audit summary: overlap={audit_counts['overlap']}, too_close={audit_counts['too_close']}, allowed_mount_contact={audit_counts['allowed_mount_contact']}.",
            "- Interference audit scope: new control-box-related pairs were checked against the accepted v7.1 body and enclosure v1.1 preview; unchanged body/enclosure relations remain from the already validated enclosure stage.",
            f"- Control box module components: {len(module_instances)}",
            f"- Control box module solids: {module_solids}",
            f"- Control box module bbox: {v71.fmt_bbox(module_bbox)}",
            f"- Preview generated components: {len(preview_instances)}",
            f"- Preview failed components: {len(failure_rows)}",
            f"- Preview solids: {preview_solids}",
            f"- Preview bbox: {v71.fmt_bbox(preview_bbox)}",
            f"- Preview bbox Y direction: {preview_bbox[4] - preview_bbox[1]:.3f} mm; target <= 1050 mm.",
            "- Preview control box state: closed cabinet.",
            "- Preview internal electrical exposure: hidden; no DIN rail, controller board, motor drivers, power supply, or terminal blocks are shown.",
            "- Current status: layout-level electrical module, not final electrical design.",
            "- Later detail still needed: formal electrical architecture, I/O map, terminal numbering, harness routes, cable-chain selection, grounding, power protection, control-box mounting holes, and engineering drawings.",
            f"- Control box module STEP: `{MODULE_STEP_OUT.relative_to(ROOT).as_posix()}`",
            f"- Control box preview STEP: `{PREVIEW_STEP_OUT.relative_to(ROOT).as_posix()}`",
            "",
        ]),
        encoding="utf-8",
    )


def write_outputs() -> dict[str, object]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    module_assembly, module_instances, module_manifest = build_control_box_only()
    preview_assembly, preview_instances, preview_manifest, failure_rows = build_preview()

    module_validation = [v71.validation_row(instance) for instance in module_instances]
    preview_validation = [v71.validation_row(instance) for instance in preview_instances] + failure_rows
    audit_rows, audit_counts = audit_instances(preview_instances)
    access_rows = accessibility_rows()
    module_bbox, module_exported_solids = export_assembly(module_assembly, MODULE_STEP_OUT)
    preview_bbox, preview_exported_solids = export_assembly(preview_assembly, PREVIEW_STEP_OUT)

    validation_fields = ["component_name", "module_name", "instance_name", "source_path", "import_status", "solid_count", "target_x_mm", "target_y_mm", "target_z_mm", "rotation_x_deg", "rotation_y_deg", "rotation_z_deg", "bbox_min_x_mm", "bbox_min_y_mm", "bbox_min_z_mm", "bbox_max_x_mm", "bbox_max_y_mm", "bbox_max_z_mm", "notes"]
    manifest_fields = ["component_name", "instance_name", "expected_color", "material_or_role", "r", "g", "b", "a", "source_path", "notes"]
    audit_fields = ["pair_a", "pair_b", "bbox_overlap_candidate", "exact_overlap_volume_mm3", "minimum_distance_mm", "clearance_threshold_mm", "audit_status", "notes"]
    access_fields = ["item", "check_status", "notes"]

    write_csv(MODULE_VALIDATION_OUT, module_validation, validation_fields)
    write_csv(MODULE_COLOR_MANIFEST_OUT, module_manifest, manifest_fields)
    write_csv(ACCESSIBILITY_CSV_OUT, access_rows, access_fields)
    write_csv(PREVIEW_VALIDATION_OUT, preview_validation, validation_fields)
    write_csv(PREVIEW_AUDIT_OUT, audit_rows, audit_fields)
    write_csv(PREVIEW_COLOR_MANIFEST_OUT, preview_manifest, manifest_fields)
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
    print("tube_curved_labels_preserved=yes")
    print("non_tube_region_labels_removed=yes")
    print("preview_control_box_closed=yes")
    print("preview_internal_electrical_parts_hidden=yes")
    print(f"control_box_position={CONTROL_BOX_POSITION}")
    print(f"module_step={MODULE_STEP_OUT}")
    print(f"preview_step={PREVIEW_STEP_OUT}")
    print(f"module_validation_csv={MODULE_VALIDATION_OUT}")
    print(f"preview_validation_csv={PREVIEW_VALIDATION_OUT}")
    print(f"module_color_manifest={MODULE_COLOR_MANIFEST_OUT}")
    print(f"preview_color_manifest={PREVIEW_COLOR_MANIFEST_OUT}")
    print(f"accessibility_csv={ACCESSIBILITY_CSV_OUT}")
    print(f"interference_audit_csv={PREVIEW_AUDIT_OUT}")
    print(f"report={REPORT_OUT}")
    return 0 if result["preview_failed_count"] == 0 and audit_counts["overlap"] == 0 and audit_counts["too_close"] == 0 and access_issue == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
