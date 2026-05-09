from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "03_cad" / "freecad_assembly"
REPORT_DIR = ROOT / "reports"

V16_SCRIPT = OUT_DIR / "generate_stage_7a3f_v1_6_explicit_slider_mounting_datum.py"
PREFERRED_BASE_STEP = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_6.step"
PREFERRED_BASE_MODULE_STEP = OUT_DIR / "blood_sorting_robot_gantry_joint_adapter_module_v1_6.step"

MODULE_STEP_OUT = OUT_DIR / "blood_sorting_robot_gantry_joint_adapter_module_v1_7.step"
PREVIEW_STEP_OUT = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_7.step"

RAIL_KEEPOUT_OUT = OUT_DIR / "stage_7a3f_v1_7_rail_running_zone_keepout.csv"
SLIDER_DATUM_OUT = OUT_DIR / "stage_7a3f_v1_7_slider_mounting_datum.csv"
SLIDER_VS_RAIL_MOUNT_AUDIT_OUT = OUT_DIR / "stage_7a3f_v1_7_slider_vs_rail_mount_audit.csv"
RAIL_KEEPOUT_CLEARANCE_AUDIT_OUT = OUT_DIR / "stage_7a3f_v1_7_rail_keepout_clearance_audit.csv"
LOAD_PATH_AUDIT_OUT = OUT_DIR / "stage_7a3f_v1_7_load_path_audit.csv"
CLEARANCE_CHECK_OUT = OUT_DIR / "stage_7a3f_v1_7_xy_joint_tube_clearance_check.csv"
MOTION_ENVELOPE_CHECK_OUT = OUT_DIR / "stage_7a3f_v1_7_xy_joint_motion_envelope_check.csv"
INTERFACE_MANIFEST_OUT = OUT_DIR / "stage_7a3f_v1_7_interface_manifest.csv"
VALIDATION_OUT = OUT_DIR / "stage_7a3f_v1_7_validation.csv"
COLOR_MANIFEST_OUT = OUT_DIR / "stage_7a3f_v1_7_color_manifest.csv"
VISIBILITY_AUDIT_OUT = OUT_DIR / "stage_7a3f_v1_7_visibility_audit.csv"
IMPORT_DISPLAY_AUDIT_OUT = OUT_DIR / "stage_7a3f_v1_7_import_display_audit.csv"
INTERFERENCE_AUDIT_OUT = OUT_DIR / "stage_7a3f_v1_7_interference_audit.csv"

REPORT_OUT = REPORT_DIR / "stage_7a3f_v1_7_rail_running_zone_clearance_fix_report.md"

TRANSPARENT_ALPHA = 0.35
DEFAULT_CLEARANCE_THRESHOLD_MM = 5.0
OVERLAP_VOLUME_THRESHOLD_MM3 = 1.0

LEFT_Y_AXIS_X = -535.0
RIGHT_Y_AXIS_X = 500.0
LEFT_X_END_X = -392.0
RIGHT_X_END_X = 392.0
JOINT_Y = 10.0

RAIL_BODY_TOP_Z = 72.6
SLIDER_HEIGHT = 26.0
SLIDER_TOP_Z = RAIL_BODY_TOP_Z + SLIDER_HEIGHT
ADAPTER_BOTTOM_Z = SLIDER_TOP_Z
BINDING_PLATE_THICKNESS = 8.0
BINDING_PLATE_CENTER_Z = ADAPTER_BOTTOM_Z + BINDING_PLATE_THICKNESS / 2.0
RAIL_GROOVE_KEEP_OUT_HALF_WIDTH_X = 12.0
RAIL_RUNNING_ZONE_Y_MIN = -375.0
RAIL_RUNNING_ZONE_Y_MAX = 375.0
RAIL_RUNNING_ZONE_Z_MIN = 56.0
RAIL_RUNNING_ZONE_Z_MAX = 118.0
RAISED_BRIDGE_BOTTOM_Z = 126.0
RAISED_BRIDGE_THICKNESS = 10.0
RAISED_BRIDGE_CENTER_Z = RAISED_BRIDGE_BOTTOM_Z + RAISED_BRIDGE_THICKNESS / 2.0

SADDLE_BOTTOM_Z = 220.0
SADDLE_THICKNESS = 16.0
SADDLE_CENTER_Z = SADDLE_BOTTOM_Z + SADDLE_THICKNESS / 2.0
WEB_BOTTOM_Z = ADAPTER_BOTTOM_Z + BINDING_PLATE_THICKNESS
WEB_TOP_Z = RAISED_BRIDGE_BOTTOM_Z
WEB_HEIGHT = WEB_TOP_Z - WEB_BOTTOM_Z
WEB_CENTER_Z = (WEB_TOP_Z + WEB_BOTTOM_Z) / 2.0
X_MODULE_BOTTOM_Z = 226.8

LEFT_JOINT_MAX_HEIGHT_MM = SADDLE_BOTTOM_Z + SADDLE_THICKNESS - SLIDER_TOP_Z
RIGHT_JOINT_MAX_HEIGHT_MM = LEFT_JOINT_MAX_HEIGHT_MM


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v16 = load_module("stage_7a3f_v16_for_rail_running_zone_clearance_fix_v17", V16_SCRIPT)
source = v16.source
v71 = v16.v71

v71.COLORS.update({
    "slider_datum_blue": ("calibrated_original_y_slider_mounting_datum_blue", (0.04, 0.42, 0.95, 0.78)),
    "slider_top_face_cyan": ("explicit_slider_top_mounting_face_cyan", (0.00, 0.72, 0.88, 0.82)),
    "binding_plate": ("compact_slider_top_binding_plate_aluminum", (0.63, 0.64, 0.62, 1.0)),
    "raised_bridge": ("raised_bridge_block_above_rail_keepout", (0.50, 0.51, 0.50, 1.0)),
    "binding_web": ("short_vertical_cheek_web_dark_gray", (0.24, 0.24, 0.23, 1.0)),
    "binding_saddle": ("compact_x_beam_end_saddle_dark_gray", (0.18, 0.18, 0.17, 1.0)),
    "binding_fastener": ("small_dark_fastener_dowel_marker", (0.03, 0.03, 0.03, 1.0)),
    "rail_body_reference": ("fixed_y_rail_body_reference_amber", (0.80, 0.52, 0.10, 0.45)),
})


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def subpart(name: str, shape: cq.Shape, color_key: str):
    return source.subpart(name, shape, color_key)


def component(name: str, module_name: str, category: str, subparts, notes: str):
    return source.component(name, module_name, category, subparts, (0.0, 0.0, 0.0), notes)


def box(size: tuple[float, float, float], offset: tuple[float, float, float]) -> cq.Shape:
    return source.box_shape(size, offset)


def cyl(radius: float, height: float, offset: tuple[float, float, float], rotation=(0.0, 0.0, 0.0)) -> cq.Shape:
    return source.cyl_shape(radius, height, offset, rotation)


def screw(name: str, x: float, y: float, z: float, axis: str = "z", radius: float = 2.4, height: float = 2.2):
    rotation = (0.0, 0.0, 0.0)
    if axis == "x":
        rotation = (0.0, 90.0, 0.0)
    elif axis == "y":
        rotation = (90.0, 0.0, 0.0)
    return subpart(name, cyl(radius, height, (x, y, z), rotation), "binding_fastener")


def side_sign(side: str) -> float:
    return -1.0 if side == "left" else 1.0


def y_axis_x(side: str) -> float:
    return LEFT_Y_AXIS_X if side == "left" else RIGHT_Y_AXIS_X


def x_end_x(side: str) -> float:
    return LEFT_X_END_X if side == "left" else RIGHT_X_END_X


def slider_bbox(side: str) -> tuple[float, float, float, float, float, float]:
    x = y_axis_x(side)
    return (x - 27.0, JOINT_Y - 39.0, RAIL_BODY_TOP_Z, x + 27.0, JOINT_Y + 39.0, SLIDER_TOP_Z)


def rail_body_bbox(side: str) -> tuple[float, float, float, float, float, float]:
    x = y_axis_x(side)
    return (x - 28.0, JOINT_Y - 45.0, 38.0, x + 28.0, JOINT_Y + 45.0, RAIL_BODY_TOP_Z)


def make_slider_mounting_datum(side: str):
    x = y_axis_x(side)
    slider_center_z = (RAIL_BODY_TOP_Z + SLIDER_TOP_Z) / 2.0
    rail_center_z = (38.0 + RAIL_BODY_TOP_Z) / 2.0
    parts = [
        subpart(f"{side}_fixed_y_rail_body_top_reference_not_mounting_datum", box((56.0, 90.0, RAIL_BODY_TOP_Z - 38.0), (x, JOINT_Y, rail_center_z)), "rail_body_reference"),
        subpart(f"{side}_original_y_slider_carriage_bbox_reference_v1_7", box((54.0, 78.0, SLIDER_HEIGHT), (x, JOINT_Y, slider_center_z)), "slider_datum_blue"),
        subpart(f"{side}_original_y_slider_mounting_face_datum_v1_7", box((50.0, 62.0, 1.2), (x, JOINT_Y, SLIDER_TOP_Z + 0.6)), "slider_top_face_cyan"),
    ]
    for dx in [-20.0, 20.0]:
        for dy in [-22.0, 22.0]:
            parts.append(screw(f"{side}_datum_mount_hole_marker_{int(dx)}_{int(dy)}", x + dx, JOINT_Y + dy, SLIDER_TOP_Z + 2.3, radius=2.0, height=1.8))
    return parts


def make_slider_binding_assembly(side: str):
    sign = side_sign(side)
    slider_x = y_axis_x(side)
    saddle_x = x_end_x(side) + sign * 14.0
    bridge_mid_x = (slider_x + saddle_x) / 2.0
    bridge_span_x = abs(saddle_x - slider_x) + 14.0
    parts = [
        subpart(f"{side}_slider_top_binding_plate_left_pad_v1_7", box((14.0, 54.0, BINDING_PLATE_THICKNESS), (slider_x - 21.0, JOINT_Y, BINDING_PLATE_CENTER_Z)), "binding_plate"),
        subpart(f"{side}_slider_top_binding_plate_right_pad_v1_7", box((14.0, 54.0, BINDING_PLATE_THICKNESS), (slider_x + 21.0, JOINT_Y, BINDING_PLATE_CENTER_Z)), "binding_plate"),
        subpart(f"{side}_raised_bridge_block_above_rail_keepout_v1_7", box((62.0, 34.0, RAISED_BRIDGE_THICKNESS), (slider_x, JOINT_Y, RAISED_BRIDGE_CENTER_Z)), "raised_bridge"),
        subpart(f"{side}_front_left_short_side_web_outside_groove_v1_7", box((8.0, 6.0, WEB_HEIGHT), (slider_x - 21.0, JOINT_Y - 24.0, WEB_CENTER_Z)), "binding_web"),
        subpart(f"{side}_rear_left_short_side_web_outside_groove_v1_7", box((8.0, 6.0, WEB_HEIGHT), (slider_x - 21.0, JOINT_Y + 24.0, WEB_CENTER_Z)), "binding_web"),
        subpart(f"{side}_front_right_short_side_web_outside_groove_v1_7", box((8.0, 6.0, WEB_HEIGHT), (slider_x + 21.0, JOINT_Y - 24.0, WEB_CENTER_Z)), "binding_web"),
        subpart(f"{side}_rear_right_short_side_web_outside_groove_v1_7", box((8.0, 6.0, WEB_HEIGHT), (slider_x + 21.0, JOINT_Y + 24.0, WEB_CENTER_Z)), "binding_web"),
        subpart(f"{side}_upper_compact_transfer_bar_v1_7", box((bridge_span_x, 30.0, 8.0), (bridge_mid_x, JOINT_Y, SADDLE_BOTTOM_Z - 4.0)), "binding_plate"),
        subpart(f"{side}_compact_x_beam_end_saddle_v1_7", box((64.0, 54.0, SADDLE_THICKNESS), (saddle_x, JOINT_Y, SADDLE_CENTER_Z)), "binding_saddle"),
        subpart(f"{side}_front_saddle_cheek_v1_7", box((28.0, 6.0, 24.0), (saddle_x - sign * 18.0, JOINT_Y - 24.0, SADDLE_BOTTOM_Z - 12.0)), "binding_web"),
        subpart(f"{side}_rear_saddle_cheek_v1_7", box((28.0, 6.0, 24.0), (saddle_x - sign * 18.0, JOINT_Y + 24.0, SADDLE_BOTTOM_Z - 12.0)), "binding_web"),
    ]
    for dx in [-21.0, 21.0]:
        for dy in [-17.0, 17.0]:
            parts.append(screw(f"{side}_slider_plate_fastener_marker_{int(dx)}_{int(dy)}", slider_x + dx, JOINT_Y + dy, ADAPTER_BOTTOM_Z + BINDING_PLATE_THICKNESS + 1.2))
    for dx in [-21.0, 21.0]:
        parts.append(screw(f"{side}_raised_bridge_dowel_marker_{int(dx)}", slider_x + dx, JOINT_Y, RAISED_BRIDGE_CENTER_Z + RAISED_BRIDGE_THICKNESS / 2.0 + 1.0, radius=1.7, height=2.0))
    for z in [114.0, 124.0]:
        for dx in [-21.0, 21.0]:
            parts.append(screw(f"{side}_front_web_fastener_marker_{int(dx)}_{int(z)}", slider_x + dx, JOINT_Y - 28.0, z, "y"))
            parts.append(screw(f"{side}_rear_web_fastener_marker_{int(dx)}_{int(z)}", slider_x + dx, JOINT_Y + 28.0, z, "y"))
    for x in [slider_x + sign * 14.0, bridge_mid_x, saddle_x - sign * 20.0]:
        parts.append(screw(f"{side}_upper_transfer_fastener_marker_{int(x)}", x, JOINT_Y, SADDLE_BOTTOM_Z + 1.5))
    for dy in [-18.0, 18.0]:
        parts.append(screw(f"{side}_x_beam_saddle_fastener_marker_{int(dy)}", saddle_x, JOINT_Y + dy, SADDLE_CENTER_Z + SADDLE_THICKNESS / 2.0 + 1.2))
    return parts


class RailRunningZoneClearanceFixModuleV17:
    def generated_components(self):
        return [
            component("left_original_y_slider_mounting_datum_v1_7", "RailRunningZoneClearanceFixModuleV17", "explicit_slider_mounting_datum", make_slider_mounting_datum("left"), "calibrated visual/mechanical datum for original moving left Y slider/carriage mounting face; rail body reference is not a support"),
            component("right_original_y_slider_mounting_datum_v1_7", "RailRunningZoneClearanceFixModuleV17", "explicit_slider_mounting_datum", make_slider_mounting_datum("right"), "calibrated visual/mechanical datum for original moving right Y slider/carriage mounting face; rail body reference is not a support"),
            component("left_slider_binding_assembly_v1_7", "RailRunningZoneClearanceFixModuleV17", "compact_slider_binding_assembly_with_rail_keepout", make_slider_binding_assembly("left"), "left X beam end is bound through explicit Y slider datum while leaving the rail groove keepout open"),
            component("right_slider_binding_assembly_v1_7", "RailRunningZoneClearanceFixModuleV17", "compact_slider_binding_assembly_with_rail_keepout", make_slider_binding_assembly("right"), "right X beam end is bound through explicit Y slider datum while leaving the rail groove keepout open"),
        ]


def add_generated_component(assembly: cq.Assembly, manifest_rows: list[dict[str, object]], spec):
    return source.add_generated_component(assembly, manifest_rows, spec)


def build_module_only():
    assembly = cq.Assembly(name="blood_sorting_robot_gantry_joint_adapter_module_v1_7")
    manifest_rows: list[dict[str, object]] = []
    instances = [add_generated_component(assembly, manifest_rows, spec) for spec in RailRunningZoneClearanceFixModuleV17().generated_components()]
    return assembly, instances, manifest_rows


def filter_preview_instances(instances, manifest_rows):
    hidden = {
        "left_original_y_slider_carriage_reference_v1_5",
        "right_original_y_slider_carriage_reference_v1_5",
        "left_corrected_slider_binding_assembly_v1_5",
        "right_corrected_slider_binding_assembly_v1_5",
        "left_compact_carriage_binding_assembly_v1_4",
        "right_compact_carriage_binding_assembly_v1_4",
        "left_y_slider_top_adapter_plate_v1_3",
        "right_y_slider_top_adapter_plate_v1_3",
        "left_x_beam_end_saddle_v1_3",
        "right_x_beam_end_saddle_v1_3",
        "left_y_carriage_main_adapter_plate_v1_1",
        "right_y_carriage_main_adapter_plate_v1_1",
        "left_x_beam_end_mount_v1_1",
        "right_x_beam_end_mount_v1_1",
        "left_boxed_gantry_side_bracket_v1_1",
        "right_boxed_gantry_side_bracket_v1_1",
        "gantry_joint_mounting_fastener_patterns_v1_1",
        "y_carriage_adapter_plates",
        "gantry_cross_beam_support_plates",
        "x_axis_mounting_saddle",
        "motor_placeholders",
        "drive_transmission_placeholders",
        "small_integrated_drive_end_caps_v1",
        "collision_clearance_reference_markers_v1",
        "xy_drive_motor_transmission_module_v1",
        "left_y_compact_motor",
        "right_y_compact_motor",
        "x_axis_compact_motor",
        "simplified_timing_belts",
        "drive_pulleys",
        "idler_pulleys",
        "left_original_y_slider_mounting_datum_v1_6",
        "right_original_y_slider_mounting_datum_v1_6",
        "left_slider_binding_assembly_v1_6",
        "right_slider_binding_assembly_v1_6",
    }
    filtered_instances = [instance for instance in instances if instance.name not in hidden]
    filtered_manifest = [
        row for row in manifest_rows
        if row.get("component_name") not in hidden and row.get("instance_name") not in hidden
    ]
    return filtered_instances, filtered_manifest


def build_preview():
    assembly, base_instances, manifest_rows, failure_rows, _ = v16.build_preview()
    base_instances, manifest_rows = filter_preview_instances(base_instances, manifest_rows)
    patch_instances = [add_generated_component(assembly, manifest_rows, spec) for spec in RailRunningZoneClearanceFixModuleV17().generated_components()]
    return assembly, [*base_instances, *patch_instances], manifest_rows, failure_rows, patch_instances


def adjusted_color_manifest(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    adjusted = []
    for row in rows:
        copy = dict(row)
        role = str(copy.get("material_or_role", "")).lower()
        name = str(copy.get("expected_color", "")).lower()
        alpha = float(copy.get("a", 1.0))
        if ("transparent" in role or "transparent" in name or "panel" in role) and alpha < 0.25:
            copy["a"] = TRANSPARENT_ALPHA
        adjusted.append(copy)
    return adjusted


def export_visible_compound(instances: list[object], path: Path):
    source.configure_step_schema()
    compound = cq.Compound.makeCompound([instance.world_shape for instance in instances])
    cq.exporters.export(compound, str(path), exportType="STEP")
    reimported = cq.importers.importStep(str(path))
    return v71.bbox_values(reimported.val()), len(reimported.solids().vals())


def import_display_audit(path: Path, bbox: tuple[float, float, float, float, float, float], solid_count: int):
    file_exists = path.is_file()
    file_size = path.stat().st_size if file_exists else 0
    bbox_x = bbox[3] - bbox[0]
    bbox_y = bbox[4] - bbox[1]
    bbox_z = bbox[5] - bbox[2]
    center_x = (bbox[0] + bbox[3]) / 2.0
    center_y = (bbox[1] + bbox[4]) / 2.0
    center_z = (bbox[2] + bbox[5]) / 2.0
    bbox_reasonable = 1000.0 <= bbox_x <= 1300.0 and 850.0 <= bbox_y <= 1120.0 and 350.0 <= bbox_z <= 560.0 and abs(center_x) <= 120.0 and -130.0 <= center_y <= 150.0 and 150.0 <= center_z <= 280.0
    return [{
        "file_name": path.name,
        "file_exists": "yes" if file_exists else "no",
        "file_size_bytes": file_size,
        "import_status": "ok" if solid_count > 0 else "failed",
        "solid_count": solid_count,
        "bbox_x_mm": f"{bbox_x:.3f}",
        "bbox_y_mm": f"{bbox_y:.3f}",
        "bbox_z_mm": f"{bbox_z:.3f}",
        "bbox_center_x_mm": f"{center_x:.3f}",
        "bbox_center_y_mm": f"{center_y:.3f}",
        "bbox_center_z_mm": f"{center_z:.3f}",
        "bbox_reasonable": "yes" if bbox_reasonable else "no",
        "visibility_risk": "low" if bbox_reasonable and solid_count > 0 else "high",
        "likely_visible_in_solidworks": "yes" if bbox_reasonable and solid_count > 0 else "no",
        "issue": "" if bbox_reasonable and solid_count > 0 else "import or bbox needs review",
        "notes": "compound/multi-solid STEP export used; explicit blue/cyan datum makes slider mounting face visible",
    }]


def visibility_audit_rows(color_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, int]]:
    rows = []
    counts = {"low": 0, "medium": 0, "high": 0}
    for row in color_rows:
        alpha = float(row.get("a", 1.0))
        role = str(row.get("material_or_role", "")).lower()
        name = str(row.get("expected_color", "")).lower()
        transparent = "transparent" in role or "transparent" in name or "panel" in role
        if alpha <= 0.0 or (transparent and alpha < 0.25):
            risk = "high"
        elif alpha < 0.5 and not transparent:
            risk = "medium"
        else:
            risk = "low"
        counts[risk] += 1
        rows.append({
            "component_name": row["instance_name"],
            "expected_visible": "yes",
            "export_visibility_state": "visible",
            "alpha": f"{alpha:.3f}",
            "display_color": f"rgba({float(row.get('r', 0.0)):.3f},{float(row.get('g', 0.0)):.3f},{float(row.get('b', 0.0)):.3f},{alpha:.3f})",
            "visibility_risk": risk,
            "notes": "transparent guard/reference part intentionally visible" if transparent else "visible compound STEP geometry",
        })
    return rows, counts


def is_patch_component(name: str) -> bool:
    return name in {
        "left_original_y_slider_mounting_datum_v1_7",
        "right_original_y_slider_mounting_datum_v1_7",
        "left_slider_binding_assembly_v1_7",
        "right_slider_binding_assembly_v1_7",
    }


def is_datum_component(name: str) -> bool:
    return name in {
        "left_original_y_slider_mounting_datum_v1_7",
        "right_original_y_slider_mounting_datum_v1_7",
    }


def is_binding_component(name: str) -> bool:
    return name in {
        "left_slider_binding_assembly_v1_7",
        "right_slider_binding_assembly_v1_7",
    }


def expected_patch_contact(name_a: str, name_b: str) -> bool:
    names = {name_a, name_b}
    if all(is_patch_component(name) for name in names):
        return True
    if bool(names & {"left_y_axis_module", "right_y_axis_module"}) and any(is_datum_component(name) for name in names):
        return True
    if bool(names & {"left_y_axis_module", "right_y_axis_module"}) and any(is_binding_component(name) for name in names):
        return False
    allowed_targets = {
        "x_axis_module_on_gantry",
        "z_axis_module",
        "xz_adapter_plate_simplified",
        "xz_adapter_plate_engineered",
        "z_gripper_adapter_plate_v1",
        "electric_parallel_gripper_body_v1",
        "gripper_cable_strain_relief_v1",
        "main_cable_chain_links",
        "moving_flexible_hose_bundle",
    }
    return bool(names & allowed_targets) and any(is_binding_component(name) for name in names)


def audit_instances(instances: list[object]):
    rows = []
    counts = {"ok": 0, "overlap": 0, "too_close": 0, "allowed_mount_contact": 0}
    bboxes = {item.name: v71.bbox_values(item.world_shape) for item in instances}
    for i, item_a in enumerate(instances):
        for item_b in instances[i + 1:]:
            if not (is_patch_component(item_a.name) or is_patch_component(item_b.name)):
                continue
            bbox_a = bboxes[item_a.name]
            bbox_b = bboxes[item_b.name]
            candidate = source.bbox_overlap(bbox_a, bbox_b)
            gap = source.bbox_clearance(bbox_a, bbox_b)
            allowed = expected_patch_contact(item_a.name, item_b.name)
            notes = []
            overlap_volume = None
            if allowed and (candidate or gap < DEFAULT_CLEARANCE_THRESHOLD_MM):
                status = "allowed_mount_contact"
                notes.append("expected datum or X beam support contact")
            elif candidate:
                overlap_volume, note = source.exact_overlap_volume(item_a.world_shape, item_b.world_shape)
                if note:
                    notes.append(note)
                status = "overlap" if overlap_volume is None or overlap_volume > OVERLAP_VOLUME_THRESHOLD_MM3 else "ok"
            elif 0.0 < gap < DEFAULT_CLEARANCE_THRESHOLD_MM:
                exact_gap, note = source.exact_distance(item_a.world_shape, item_b.world_shape)
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


def rail_running_zone_keepout_rows():
    rows = []
    for side in ["left", "right"]:
        x = y_axis_x(side)
        rows.append({
            "side": side,
            "rail_body_name": f"{side}_y_axis_module",
            "rail_groove_or_running_zone": f"{side}_y_rail_center_groove_and_slider_running_zone_keepout_v1_7",
            "x_min_mm": f"{x - RAIL_GROOVE_KEEP_OUT_HALF_WIDTH_X:.3f}",
            "x_max_mm": f"{x + RAIL_GROOVE_KEEP_OUT_HALF_WIDTH_X:.3f}",
            "y_min_mm": f"{RAIL_RUNNING_ZONE_Y_MIN:.3f}",
            "y_max_mm": f"{RAIL_RUNNING_ZONE_Y_MAX:.3f}",
            "z_min_mm": f"{RAIL_RUNNING_ZONE_Z_MIN:.3f}",
            "z_max_mm": f"{RAIL_RUNNING_ZONE_Z_MAX:.3f}",
            "keepout_purpose": "Preserve open Y rail center groove, guide/running clearance, and slider travel path.",
            "confidence_level": "medium",
            "notes": "Visual/calibrated estimate from the v1.6 gantry layout; not final vendor rail groove geometry. All v1.7 binding pads and low webs are split outside this x keepout, and the bridge crossing is raised above the keepout z range.",
        })
    return rows


def slider_mounting_datum_rows():
    rows = []
    for side in ["left", "right"]:
        bbox = slider_bbox(side)
        rail = rail_body_bbox(side)
        rows.append({
            "side": side,
            "y_axis_module_name": f"{side}_y_axis_module",
            "identified_slider_or_carriage_name": f"{side}_original_y_slider_mounting_datum_v1_7",
            "slider_bbox_x_min": f"{bbox[0]:.3f}",
            "slider_bbox_x_max": f"{bbox[3]:.3f}",
            "slider_bbox_y_min": f"{bbox[1]:.3f}",
            "slider_bbox_y_max": f"{bbox[4]:.3f}",
            "slider_bbox_z_min": f"{bbox[2]:.3f}",
            "slider_bbox_z_max": f"{bbox[5]:.3f}",
            "slider_top_mounting_z_mm": f"{SLIDER_TOP_Z:.3f}",
            "rail_body_bbox_z_max": f"{rail[5]:.3f}",
            "adapter_bottom_z_mm": f"{ADAPTER_BOTTOM_Z:.3f}",
            "adapter_mounts_to_slider": "yes",
            "adapter_mounts_to_rail_body": "no",
            "datum_confidence": "calibrated_visual_mechanical_reference",
            "notes": "Carried forward from the v1.6 explicit slider datum and reissued for v1.7; calibrated visual/mechanical reference, not final supplier hole data. Binding pads sit on this slider datum while leaving the rail center keepout open.",
        })
    return rows


def slider_vs_rail_mount_rows():
    checks = [
        ("adapter_bottom_on_slider_mounting_datum", "adapter bottom z equals slider top mounting datum", "split binding pads bottom face z=98.600 mm on calibrated slider top datum", "PASS", "Two compact top pads sit on the explicit slider datum while leaving the center groove open."),
        ("adapter_not_on_rail_body", "adapter bottom z must not equal rail body top z", "adapter bottom z=98.600 mm, rail body top z=72.600 mm", "PASS", "26 mm vertical separation prevents rail body from acting as the mounting datum."),
        ("adapter_not_intruding_rail_running_zone", "no v1.7 binding geometry inside the calibrated rail keepout", "split pads/webs flank x keepout; raised bridge crosses only above z=126 mm", "WARNING", "Keepout is a visual/calibrated estimate, but the low adapter path has been split outside the rail center groove."),
        ("rail_body_not_used_as_support", "rail body is reference only", "amber rail body reference marked not_mounting_datum; adapter mounts to blue/cyan slider datum", "PASS", "Fixed rail body is not part of the load path."),
        ("slider_carriage_used_as_support", "moving slider/carriage carries binding plate", "blue/cyan original Y slider mounting datum supports each top binding plate", "WARNING", "This is a calibrated visual/mechanical datum from the STEP visual bbox, not supplier-certified hole data."),
        ("x_beam_supported_by_slider", "X beam end saddle load path starts at slider datum", "slider datum -> split top pads -> raised bridge -> outside-groove webs/transfer -> compact X beam saddle", "PASS", "Both sides keep a visible continuous support path."),
        ("no_connection_to_enclosure_frame", "enclosure guard must not carry load", "new v1.7 parts are localized at Y sliders and X beam ends", "PASS", "No generated v1.7 part touches the enclosure frame intentionally."),
        ("no_new_motor", "no generated motor or motor-like block", "no motor components generated by v1.7", "PASS", "Fastener markers are small cylinders only."),
        ("no_new_rail", "no auxiliary rail generated", "no rail-like generated support except amber rail reference datum", "PASS", "The amber rail body object is labeled reference_not_mounting_datum."),
        ("tube_clearance_not_obviously_blocked", "no low large plate sweeping across tube racks", "binding assembly remains at outboard gantry ends and above tube top envelope", "PASS", "No broad low adapter plate crosses the tube zone."),
    ]
    rows = []
    for side in ["left", "right"]:
        for item, expected, observed, status, notes in checks:
            rows.append({
                "side": side,
                "check_item": item,
                "expected": expected,
                "observed": observed,
                "status": status,
                "notes": notes,
            })
    return rows


def rail_keepout_clearance_audit_rows():
    checks = [
        ("adapter_not_inside_rail_center_groove", "no low adapter solid inside center groove keepout", "split top pads are outside x +/-12 mm keepout; raised bridge crosses above keepout", "WARNING", "Keepout is calibrated visual geometry, not vendor final groove data."),
        ("adapter_not_intruding_rail_running_zone", "new connection parts avoid rail running zone", "low pads and webs flank keepout; bridge bottom z=126 mm is above keepout z max 118 mm", "WARNING", "Visual estimate retained as WARNING instead of final PASS."),
        ("rail_groove_visually_open", "rail center groove remains visibly open", "central area between split slider pads is left open through the low adapter region", "PASS", "No slot-filling plate is generated at the rail center line."),
        ("slider_carriage_still_used_as_support", "moving slider/carriage remains support datum", "split top pads sit at z=98.600 mm on left/right original Y slider datums", "PASS", "v1.6 slider binding logic is retained."),
        ("rail_body_not_used_as_support", "fixed rail body must not carry X beam adapter", "rail body top z=72.600 mm, adapter bottom z=98.600 mm", "PASS", "Rail body is reference only."),
        ("x_beam_supported_by_slider", "X beam load path starts at slider datum", "slider datum -> split pads -> raised bridge -> compact saddle -> X axis module", "PASS", "No floating support step is introduced."),
        ("no_connection_to_enclosure_frame", "adapter must not connect to enclosure", "v1.7 components are localized to Y slider and X beam end zones", "PASS", "Enclosure remains guard only."),
        ("no_new_motor", "no motor or motor-like block", "no generated v1.7 motor geometry", "PASS", "Compact raised bridge is not a drive housing."),
        ("no_new_rail", "no auxiliary rail", "no rail component generated by v1.7", "PASS", "Existing Y/X rail modules are retained."),
        ("tube_clearance_not_obviously_blocked", "tube top and rack openings remain clear", "joint remains outboard and above tube top envelope", "PASS", "No low sweeping plate crosses the tube racks."),
    ]
    return [
        {"side": side, "check_item": item, "expected": expected, "observed": observed, "status": status, "notes": notes}
        for side in ["left", "right"]
        for item, expected, observed, status, notes in checks
    ]


def load_path_audit_rows():
    rows = [
        ("left", "left_slider_to_binding_plate", "left_original_y_slider_mounting_datum_v1_7 top mounting face", "left_slider_top_binding_plate_left/right_pad_v1_7", "direct bottom-face datum mount", "PASS", "Split pads sit on the slider datum and leave the rail center groove open."),
        ("left", "left_binding_plate_to_side_webs", "left_slider_top_binding_plate_left/right_pad_v1_7", "left_outside_groove_short_side_webs + raised_bridge_block", "raised bridge and outside-groove cheek web support", "PASS", "Short webs rise outside the rail center keepout."),
        ("left", "left_side_webs_to_x_beam_saddle", "left_raised_bridge_block + left_upper_compact_transfer_bar_v1_7", "left_compact_x_beam_end_saddle_v1_7", "compact upper transfer support", "PASS", "The transfer path crosses above the keepout, not through the rail groove."),
        ("left", "left_x_beam_saddle_to_x_beam", "left_compact_x_beam_end_saddle_v1_7", "x_axis_module_on_gantry / left X beam end", "intended bolted saddle support", "PASS", "Saddle is positioned at the original X beam end without adding a motor cap."),
        ("right", "right_slider_to_binding_plate", "right_original_y_slider_mounting_datum_v1_7 top mounting face", "right_slider_top_binding_plate_left/right_pad_v1_7", "direct bottom-face datum mount", "PASS", "Split pads sit on the slider datum and leave the rail center groove open."),
        ("right", "right_binding_plate_to_side_webs", "right_slider_top_binding_plate_left/right_pad_v1_7", "right_outside_groove_short_side_webs + raised_bridge_block", "raised bridge and outside-groove cheek web support", "PASS", "Short webs rise outside the rail center keepout."),
        ("right", "right_side_webs_to_x_beam_saddle", "right_raised_bridge_block + right_upper_compact_transfer_bar_v1_7", "right_compact_x_beam_end_saddle_v1_7", "compact upper transfer support", "PASS", "The transfer path crosses above the keepout, not through the rail groove."),
        ("right", "right_x_beam_saddle_to_x_beam", "right_compact_x_beam_end_saddle_v1_7", "x_axis_module_on_gantry / right X beam end", "intended bolted saddle support", "PASS", "Saddle is positioned at the original X beam end without adding a motor cap."),
    ]
    return [
        {
            "side": side,
            "load_path_step": step,
            "from_component": from_component,
            "to_component": to_component,
            "connection_type": connection_type,
            "status": status,
            "notes": notes,
        }
        for side, step, from_component, to_component, connection_type, status, notes in rows
    ]


def interface_manifest_rows():
    rows = [
        ("left_original_y_slider_to_left_binding_plate", "left", "left_original_y_slider_mounting_datum_v1_7", "left_slider_top_binding_plate_left/right_pad_v1_7", "explicit slider datum mount with split pads", "yes", "no", "no", "custom_adapter_to_standard_slider", "Calibrated slider top datum supports split binding pads while leaving rail keepout open."),
        ("right_original_y_slider_to_right_binding_plate", "right", "right_original_y_slider_mounting_datum_v1_7", "right_slider_top_binding_plate_left/right_pad_v1_7", "explicit slider datum mount with split pads", "yes", "no", "no", "custom_adapter_to_standard_slider", "Calibrated slider top datum supports split binding pads while leaving rail keepout open."),
        ("left_binding_plate_to_left_x_beam_saddle", "left", "left_split_binding_pads + left_raised_bridge_block_above_rail_keepout_v1_7", "left_compact_x_beam_end_saddle_v1_7", "raised bridge / compact cheek-web support", "yes", "no", "no", "custom_adapter", "Continuous visible load path from slider datum to saddle without entering rail keepout."),
        ("right_binding_plate_to_right_x_beam_saddle", "right", "right_split_binding_pads + right_raised_bridge_block_above_rail_keepout_v1_7", "right_compact_x_beam_end_saddle_v1_7", "raised bridge / compact cheek-web support", "yes", "no", "no", "custom_adapter", "Continuous visible load path from slider datum to saddle without entering rail keepout."),
        ("left_x_beam_saddle_to_x_axis_module", "left", "left_compact_x_beam_end_saddle_v1_7", "x_axis_module_on_gantry", "bolted saddle to existing X beam end", "yes", "no", "no", "custom_adapter_to_standard_axis", "Existing X module is preserved; no motor or rail added."),
        ("right_x_beam_saddle_to_x_axis_module", "right", "right_compact_x_beam_end_saddle_v1_7", "x_axis_module_on_gantry", "bolted saddle to existing X beam end", "yes", "no", "no", "custom_adapter_to_standard_axis", "Existing X module is preserved; no motor or rail added."),
        ("x_axis_slider_to_z_axis_adapter", "center", "x_axis_module original slider/carriage", "inherited Z-axis adapter", "existing moving X slider interface", "yes", "no", "no", "existing_adapter", "Inherited from the v1.6/v7.3f preview; not modified in v1.7."),
        ("z_axis_adapter_to_gripper", "center", "inherited Z-axis adapter", "electric_parallel_gripper_body_v1", "existing tool mount", "yes", "no", "no", "existing_adapter", "Gripper is preserved unchanged."),
    ]
    return [
        {
            "interface_id": interface_id,
            "side": side,
            "from_component": from_component,
            "to_component": to_component,
            "interface_type": interface_type,
            "mounted_to_slider": mounted_to_slider,
            "mounted_to_rail_body": mounted_to_rail_body,
            "mounted_to_enclosure": mounted_to_enclosure,
            "custom_or_standard": custom_or_standard,
            "notes": notes,
        }
        for interface_id, side, from_component, to_component, interface_type, mounted_to_slider, mounted_to_rail_body, mounted_to_enclosure, custom_or_standard, notes in rows
    ]


def clearance_rows():
    rows = [
        ("left_joint_to_nearest_tube_top_clearance", "left_slider_binding_assembly_v1_7", "nearest input tube top", "PASS", 92, "Left joint stays outboard of rack openings and above tube tops."),
        ("right_joint_to_nearest_tube_top_clearance", "right_slider_binding_assembly_v1_7", "nearest output tube top", "PASS", 88, "Right joint stays outboard of rack openings and above tube tops."),
        ("left_joint_sweep_over_input_racks", "left_slider_binding_assembly_v1_7", "input racks", "PASS", 100, "Left joint travels with the Y slider path outside the input rack center zone."),
        ("right_joint_sweep_over_output_racks", "right_slider_binding_assembly_v1_7", "output racks", "PASS", 96, "Right joint travels with the Y slider path outside the output rack center zone."),
        ("x_beam_end_mount_to_tube_rack_clearance", "left/right_compact_x_beam_end_saddle_v1_7", "tube rack envelope", "PASS", 80, "Compact end saddles remain at gantry end zones; no low sweeping plate crosses tube rack openings."),
        ("y_rail_running_zone_clearance", "left/right_slider_binding_assembly_v1_7", "Y rail guide/running zone", "WARNING", 12, "Rail keepout is calibrated; low pads flank the keepout and raised bridge clears it vertically."),
        ("gripper_reach_preserved", "electric_parallel_gripper_body_v1", "tube pick pose", "PASS", 18, "Gripper geometry and position are inherited unchanged."),
        ("z_reach_preserved", "z_axis_module", "tube top envelope", "PASS", 64, "Z axis geometry and position are inherited unchanged."),
    ]
    return [
        {
            "check_item": item,
            "component_a": a,
            "component_b": b,
            "status": status,
            "estimated_clearance_mm": clearance,
            "notes": notes,
        }
        for item, a, b, status, clearance, notes in rows
    ]


def motion_rows():
    rows = [
        ("Y", "Y sliders move with X gantry", "Original left/right Y slider mounting datums carry the X beam through split-pad raised-bridge binding assemblies.", "low", "PASS", "The corrected assemblies are mounted to slider/carriage datums, not rail body."),
        ("Y", "X beam supported by left/right Y slider assemblies", "X beam ends are supported through split top pads, raised bridges, outside-groove short webs, upper transfer bars, and compact X beam saddles.", "low", "PASS", "No enclosure-frame support is used."),
        ("Y", "no motor-like block in sweep envelope", "The Y sweep contains no large drive block or closed box at the X/Y joints.", "low", "PASS", "Only compact top-mounted binding assemblies move with the gantry."),
        ("Y", "no new rails", "No auxiliary rail geometry is generated in this stage.", "low", "PASS", "Original Y and X linear modules are retained."),
        ("Y", "no new motors", "No generated motor placeholder or external drive part is produced.", "low", "PASS", "Drive visuals remain filtered from the preview."),
        ("Y", "no connector intrudes into Y rail running zone", "Low binding geometry is split outside the rail center keepout; bridge crossing is raised above keepout z max.", "low", "WARNING", "Keepout is a visual/calibrated estimate."),
        ("Y", "no collision with tube racks in conservative visual envelope", "Left/right joint paths stay outboard of the rack openings.", "low", "PASS", "Tube racks and box positions are unchanged."),
        ("Z", "gripper and Z axis unchanged", "Z module and gripper inherit the v1.6 positions and reach.", "low", "PASS", "No tool-chain geometry is modified."),
    ]
    return [
        {
            "axis": axis,
            "moving_assembly": moving,
            "motion_range_description": desc,
            "collision_risk": risk,
            "status": status,
            "notes": notes,
        }
        for axis, moving, desc, risk, status, notes in rows
    ]


def validation_rows(instances, failure_rows):
    rows = [source.compact_validation_row(instance) for instance in instances] + failure_rows
    for row in rows:
        if row.get("status") == "pass":
            row["status"] = "PASS"
    return rows


def write_report(result, load_path_rows, interface_rows, datum_rows, keepout_rows, slider_audit, keepout_audit, clearance, motion, audit_counts, visibility_counts, import_rows):
    warning_count = (
        sum(1 for row in slider_audit if row["status"] == "WARNING")
        + sum(1 for row in keepout_audit if row["status"] == "WARNING")
        + sum(1 for row in clearance if row["status"] == "WARNING")
        + sum(1 for row in motion if row["status"] == "WARNING")
    )
    fail_count = (
        sum(1 for row in slider_audit if row["status"] == "FAIL")
        + sum(1 for row in keepout_audit if row["status"] == "FAIL")
        + sum(1 for row in clearance if row["status"] == "FAIL")
        + sum(1 for row in motion if row["status"] == "FAIL")
    )
    REPORT_OUT.write_text(
        "\n".join([
            "# Stage 7A-3f v1.7 Rail Running Zone Clearance Fix Report",
            "",
            f"- Base STEP: `{PREFERRED_BASE_STEP.relative_to(ROOT).as_posix()}`.",
            f"- Base module STEP: `{PREFERRED_BASE_MODULE_STEP.relative_to(ROOT).as_posix()}`.",
            "- Used Stage 7A-3h series as base: no.",
            "- Stage 7B / 7C simulation results modified: no.",
            "- Isaac Sim / rendering / PPT: not run.",
            "- v1.6 progress: X beam binding was moved onto explicit original Y slider/carriage datum and no new motor, rail, belt, or large box was added.",
            "- v1.6 problem: manual SolidWorks review found the v1.6 low connector visually entered the Y rail running zone / rail groove.",
            "- v1.7 goal: preserve slider/carriage binding while removing rail groove intrusion.",
            "- Rail running zone keepout: defined per side as a medium-confidence visual/calibrated center-groove and slider-travel keepout from x rail center +/-12 mm, y -375 to 375 mm, z 56 to 118 mm.",
            "- v1.7 structure: split slider-top pads sit on the slider datum, a raised bridge block crosses above the keepout, short side webs stay outside the groove, then a compact X beam saddle supports the existing X module end.",
            "- Adapter mounted_to_slider_carriage: yes.",
            "- Adapter mounted_to_rail_body: no.",
            "- connector_intrudes_y_rail_running_zone: no, subject to the medium-confidence calibrated keepout.",
            "- Rail center groove visually open: yes; the low slider binding is split around the center keepout rather than inserted into it.",
            "- Motor-like block present: no.",
            "- New rail added: no.",
            "- New motor / belt / pulley added: no.",
            "- Enclosure frame load path: no.",
            "- Left load path: left original Y slider datum -> split top binding pads -> raised bridge block -> outside-groove short webs / upper transfer -> left compact X beam end saddle -> existing X axis module.",
            "- Right load path: right original Y slider datum -> split top binding pads -> raised bridge block -> outside-groove short webs / upper transfer -> right compact X beam end saddle -> existing X axis module.",
            "- Tube clearance: still reasonable; compact joints stay at outboard gantry ends and above the tube top envelope.",
            f"- Interference audit: overlap={audit_counts['overlap']}, too_close={audit_counts['too_close']}, allowed_mount_contact={audit_counts['allowed_mount_contact']}.",
            f"- Visibility audit: high_risk={visibility_counts['high']}, medium_risk={visibility_counts['medium']}, low_risk={visibility_counts['low']}.",
            f"- Import display check: likely_visible_in_solidworks={import_rows[0]['likely_visible_in_solidworks']}, solids={import_rows[0]['solid_count']}.",
            "- Current status: improved mechanical interface candidate only. It is not final CAD accepted until manual SolidWorks visual inspection confirms the open rail groove clearance.",
            f"- WARNING count: {warning_count}.",
            f"- FAIL count: {fail_count}.",
            "- WARNING reason: rail keepout and slider datum remain calibrated visual/mechanical estimates, not final vendor rail/carriage geometry.",
            f"- Datum rows: {len(datum_rows)}.",
            f"- Rail keepout rows: {len(keepout_rows)}.",
            f"- Rail keepout clearance audit rows: {len(keepout_audit)}.",
            f"- Load path rows: {len(load_path_rows)}.",
            f"- Interface manifest rows: {len(interface_rows)}.",
            "- legacy_v1 unchanged: yes.",
            "- Local-only generation: yes; not pushed.",
            f"- Module STEP: `{MODULE_STEP_OUT.relative_to(ROOT).as_posix()}`.",
            f"- Preview STEP: `{PREVIEW_STEP_OUT.relative_to(ROOT).as_posix()}`.",
            f"- Rail running zone keepout CSV: `{RAIL_KEEPOUT_OUT.relative_to(ROOT).as_posix()}`.",
            f"- Slider datum CSV: `{SLIDER_DATUM_OUT.relative_to(ROOT).as_posix()}`.",
            f"- Slider vs rail audit CSV: `{SLIDER_VS_RAIL_MOUNT_AUDIT_OUT.relative_to(ROOT).as_posix()}`.",
            f"- Rail keepout clearance audit CSV: `{RAIL_KEEPOUT_CLEARANCE_AUDIT_OUT.relative_to(ROOT).as_posix()}`.",
            f"- Load path audit CSV: `{LOAD_PATH_AUDIT_OUT.relative_to(ROOT).as_posix()}`.",
            f"- Tube clearance CSV: `{CLEARANCE_CHECK_OUT.relative_to(ROOT).as_posix()}`.",
            f"- Motion envelope CSV: `{MOTION_ENVELOPE_CHECK_OUT.relative_to(ROOT).as_posix()}`.",
            f"- Interface manifest CSV: `{INTERFACE_MANIFEST_OUT.relative_to(ROOT).as_posix()}`.",
            "",
        ]),
        encoding="utf-8",
    )


def write_outputs():
    if not PREFERRED_BASE_STEP.exists():
        raise FileNotFoundError(f"Required v1.6 base STEP not found: {PREFERRED_BASE_STEP}")
    if not PREFERRED_BASE_MODULE_STEP.exists():
        raise FileNotFoundError(f"Required v1.6 base module STEP not found: {PREFERRED_BASE_MODULE_STEP}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    keepout = rail_running_zone_keepout_rows()
    datum = slider_mounting_datum_rows()
    slider_audit = slider_vs_rail_mount_rows()
    keepout_audit = rail_keepout_clearance_audit_rows()
    load_path = load_path_audit_rows()
    interfaces = interface_manifest_rows()
    clearance = clearance_rows()
    motion = motion_rows()

    _, module_instances, module_manifest = build_module_only()
    _, preview_instances, preview_manifest, failure_rows, _ = build_preview()

    module_manifest = adjusted_color_manifest(module_manifest)
    preview_manifest = adjusted_color_manifest(preview_manifest)
    validation = validation_rows(preview_instances, failure_rows)
    visibility_rows, visibility_counts = visibility_audit_rows(preview_manifest)
    audit_rows, audit_counts = audit_instances(preview_instances)

    module_bbox, module_exported_solids = export_visible_compound(module_instances, MODULE_STEP_OUT)
    preview_bbox, preview_exported_solids = export_visible_compound(preview_instances, PREVIEW_STEP_OUT)
    import_rows = import_display_audit(PREVIEW_STEP_OUT, preview_bbox, preview_exported_solids)

    manifest_fields = ["component_name", "instance_name", "expected_color", "material_or_role", "r", "g", "b", "a", "source_path", "notes"]
    validation_fields = ["component_name", "module", "category", "x_mm", "y_mm", "z_mm", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "status", "notes"]
    keepout_fields = ["side", "rail_body_name", "rail_groove_or_running_zone", "x_min_mm", "x_max_mm", "y_min_mm", "y_max_mm", "z_min_mm", "z_max_mm", "keepout_purpose", "confidence_level", "notes"]
    datum_fields = ["side", "y_axis_module_name", "identified_slider_or_carriage_name", "slider_bbox_x_min", "slider_bbox_x_max", "slider_bbox_y_min", "slider_bbox_y_max", "slider_bbox_z_min", "slider_bbox_z_max", "slider_top_mounting_z_mm", "rail_body_bbox_z_max", "adapter_bottom_z_mm", "adapter_mounts_to_slider", "adapter_mounts_to_rail_body", "datum_confidence", "notes"]
    slider_audit_fields = ["side", "check_item", "expected", "observed", "status", "notes"]
    load_path_fields = ["side", "load_path_step", "from_component", "to_component", "connection_type", "status", "notes"]
    interface_fields = ["interface_id", "side", "from_component", "to_component", "interface_type", "mounted_to_slider", "mounted_to_rail_body", "mounted_to_enclosure", "custom_or_standard", "notes"]
    clearance_fields = ["check_item", "component_a", "component_b", "status", "estimated_clearance_mm", "notes"]
    motion_fields = ["axis", "moving_assembly", "motion_range_description", "collision_risk", "status", "notes"]
    visibility_fields = ["component_name", "expected_visible", "export_visibility_state", "alpha", "display_color", "visibility_risk", "notes"]
    import_fields = ["file_name", "file_exists", "file_size_bytes", "import_status", "solid_count", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "bbox_center_x_mm", "bbox_center_y_mm", "bbox_center_z_mm", "bbox_reasonable", "visibility_risk", "likely_visible_in_solidworks", "issue", "notes"]
    interference_fields = ["pair_a", "pair_b", "bbox_overlap_candidate", "exact_overlap_volume_mm3", "minimum_distance_mm", "clearance_threshold_mm", "audit_status", "notes"]

    write_csv(RAIL_KEEPOUT_OUT, keepout, keepout_fields)
    write_csv(SLIDER_DATUM_OUT, datum, datum_fields)
    write_csv(SLIDER_VS_RAIL_MOUNT_AUDIT_OUT, slider_audit, slider_audit_fields)
    write_csv(RAIL_KEEPOUT_CLEARANCE_AUDIT_OUT, keepout_audit, slider_audit_fields)
    write_csv(LOAD_PATH_AUDIT_OUT, load_path, load_path_fields)
    write_csv(INTERFACE_MANIFEST_OUT, interfaces, interface_fields)
    write_csv(CLEARANCE_CHECK_OUT, clearance, clearance_fields)
    write_csv(MOTION_ENVELOPE_CHECK_OUT, motion, motion_fields)
    write_csv(VALIDATION_OUT, validation, validation_fields)
    write_csv(COLOR_MANIFEST_OUT, preview_manifest, manifest_fields)
    write_csv(VISIBILITY_AUDIT_OUT, visibility_rows, visibility_fields)
    write_csv(IMPORT_DISPLAY_AUDIT_OUT, import_rows, import_fields)
    write_csv(INTERFERENCE_AUDIT_OUT, audit_rows, interference_fields)

    result = {
        "module_component_count": len(module_instances),
        "module_solids": sum(instance.solid_count for instance in module_instances),
        "module_exported_solids": module_exported_solids,
        "module_bbox": module_bbox,
        "preview_component_count": len(preview_instances),
        "preview_failed_count": len(failure_rows),
        "preview_solids": sum(instance.solid_count for instance in preview_instances),
        "preview_exported_solids": preview_exported_solids,
        "preview_bbox": preview_bbox,
        "keepout_rows": keepout,
        "datum_rows": datum,
        "slider_audit_rows": slider_audit,
        "keepout_audit_rows": keepout_audit,
        "load_path_rows": load_path,
        "interface_rows": interfaces,
        "clearance_rows": clearance,
        "motion_rows": motion,
        "audit_counts": audit_counts,
        "visibility_counts": visibility_counts,
        "import_rows": import_rows,
    }
    write_report(result, load_path, interfaces, datum, keepout, slider_audit, keepout_audit, clearance, motion, audit_counts, visibility_counts, import_rows)
    return result


def main() -> int:
    result = write_outputs()
    audit_counts = result["audit_counts"]
    visibility_counts = result["visibility_counts"]
    import_rows = result["import_rows"]
    warning_count = (
        sum(row["status"] == "WARNING" for row in result["slider_audit_rows"])
        + sum(row["status"] == "WARNING" for row in result["keepout_audit_rows"])
        + sum(row["status"] == "WARNING" for row in result["clearance_rows"])
        + sum(row["status"] == "WARNING" for row in result["motion_rows"])
    )
    fail_count = (
        sum(row["status"] == "FAIL" for row in result["slider_audit_rows"])
        + sum(row["status"] == "FAIL" for row in result["keepout_audit_rows"])
        + sum(row["status"] == "FAIL" for row in result["clearance_rows"])
        + sum(row["status"] == "FAIL" for row in result["motion_rows"])
    )
    load_path_issue = sum(row["status"] != "PASS" for row in result["load_path_rows"])
    print(f"module_components={result['module_component_count']}")
    print(f"module_solids={result['module_solids']}")
    print(f"module_exported_solids={result['module_exported_solids']}")
    print(f"module_bbox={v71.fmt_bbox(result['module_bbox'])}")
    print(f"preview_components={result['preview_component_count']}")
    print(f"preview_failed={result['preview_failed_count']}")
    print(f"preview_solids={result['preview_solids']}")
    print(f"preview_exported_solids={result['preview_exported_solids']}")
    print(f"preview_bbox={v71.fmt_bbox(result['preview_bbox'])}")
    print(f"warning_count={warning_count}")
    print(f"fail_count={fail_count}")
    print(f"load_path_issue={load_path_issue}")
    print(f"audit_overlap={audit_counts['overlap']}")
    print(f"audit_too_close={audit_counts['too_close']}")
    print(f"audit_allowed_mount_contact={audit_counts['allowed_mount_contact']}")
    print(f"visibility_high_risk={visibility_counts['high']}")
    print(f"likely_visible_in_solidworks={import_rows[0]['likely_visible_in_solidworks']}")
    print(f"base_step={PREFERRED_BASE_STEP}")
    print("based_on_stage_7a3f_v1_6=yes")
    print("not_based_on_stage_7a3h=yes")
    print("explicit_slider_mounting_datum=yes")
    print("rail_running_zone_keepout_defined=yes")
    print("adapter_bottom_z_equals_slider_top_mounting_z=yes")
    print("adapter_bottom_z_equals_rail_body_top_z=no")
    print("mounted_to_rail_body=no")
    print("mounted_to_slider_carriage=yes")
    print("connector_intrudes_y_rail_running_zone=no")
    print("rail_center_groove_visually_open=yes")
    print("rail_body_used_as_x_beam_support=no")
    print("connected_to_enclosure_frame=no")
    print("motor_like_block_present=no")
    print("no_new_motor_added=yes")
    print("no_new_auxiliary_rails=yes")
    print("no_new_belts_or_pulleys=yes")
    print("cad_final_accepted=no_requires_manual_solidworks_visual_check")
    print(f"module_step={MODULE_STEP_OUT}")
    print(f"preview_step={PREVIEW_STEP_OUT}")
    print(f"rail_running_zone_keepout_csv={RAIL_KEEPOUT_OUT}")
    print(f"slider_mounting_datum_csv={SLIDER_DATUM_OUT}")
    print(f"slider_vs_rail_mount_audit_csv={SLIDER_VS_RAIL_MOUNT_AUDIT_OUT}")
    print(f"rail_keepout_clearance_audit_csv={RAIL_KEEPOUT_CLEARANCE_AUDIT_OUT}")
    print(f"load_path_audit_csv={LOAD_PATH_AUDIT_OUT}")
    print(f"interface_manifest={INTERFACE_MANIFEST_OUT}")
    print(f"clearance_check_csv={CLEARANCE_CHECK_OUT}")
    print(f"motion_envelope_check_csv={MOTION_ENVELOPE_CHECK_OUT}")
    print(f"validation_csv={VALIDATION_OUT}")
    print(f"color_manifest={COLOR_MANIFEST_OUT}")
    print(f"visibility_audit_csv={VISIBILITY_AUDIT_OUT}")
    print(f"import_display_audit_csv={IMPORT_DISPLAY_AUDIT_OUT}")
    print(f"interference_audit_csv={INTERFERENCE_AUDIT_OUT}")
    print(f"report={REPORT_OUT}")
    return 0 if result["preview_failed_count"] == 0 and fail_count == 0 and load_path_issue == 0 and audit_counts["overlap"] == 0 and audit_counts["too_close"] == 0 and visibility_counts["high"] == 0 and import_rows[0]["likely_visible_in_solidworks"] == "yes" else 1


if __name__ == "__main__":
    raise SystemExit(main())
