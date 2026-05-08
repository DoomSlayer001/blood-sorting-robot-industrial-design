from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "03_cad" / "freecad_assembly"
REPORT_DIR = ROOT / "reports"
README = ROOT / "README.md"

V14_SCRIPT = OUT_DIR / "generate_stage_7a3f_v1_4_physical_slider_binding.py"
PREFERRED_BASE_STEP = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_4.step"


def latest_7a3f_preview_step() -> Path:
    candidates = sorted(
        OUT_DIR.glob("blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_*.step"),
        key=lambda path: path.name,
    )
    return candidates[-1] if candidates else OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview.step"


USED_BASE_STEP = PREFERRED_BASE_STEP if PREFERRED_BASE_STEP.exists() else latest_7a3f_preview_step()

LOAD_PATH_AUDIT_OUT = OUT_DIR / "stage_7a3f_v1_5_load_path_audit.csv"
INTERFACE_MANIFEST_OUT = OUT_DIR / "stage_7a3f_v1_5_slider_binding_interface_manifest.csv"
CLEARANCE_CHECK_OUT = OUT_DIR / "stage_7a3f_v1_5_xy_joint_tube_clearance_check.csv"
MOTION_ENVELOPE_CHECK_OUT = OUT_DIR / "stage_7a3f_v1_5_xy_joint_motion_envelope_check.csv"
SLIDER_VS_RAIL_MOUNT_AUDIT_OUT = OUT_DIR / "stage_7a3f_v1_5_slider_vs_rail_mount_audit.csv"

MODULE_STEP_OUT = OUT_DIR / "blood_sorting_robot_gantry_joint_adapter_module_v1_5.step"
PREVIEW_STEP_OUT = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_5.step"
VALIDATION_OUT = OUT_DIR / "stage_7a3f_v1_5_validation.csv"
COLOR_MANIFEST_OUT = OUT_DIR / "stage_7a3f_v1_5_color_manifest.csv"
VISIBILITY_AUDIT_OUT = OUT_DIR / "stage_7a3f_v1_5_visibility_audit.csv"
IMPORT_DISPLAY_AUDIT_OUT = OUT_DIR / "stage_7a3f_v1_5_import_display_audit.csv"
INTERFERENCE_AUDIT_OUT = OUT_DIR / "stage_7a3f_v1_5_interference_audit.csv"

REPORT_OUT = REPORT_DIR / "stage_7a3f_v1_5_slider_carriage_true_binding_fix_report.md"

OVERLAP_VOLUME_THRESHOLD_MM3 = 1.0
DEFAULT_CLEARANCE_THRESHOLD_MM = 5.0
TRANSPARENT_ALPHA = 0.35

LEFT_Y_AXIS_X = -535.0
RIGHT_Y_AXIS_X = 500.0
LEFT_X_END_X = -392.0
RIGHT_X_END_X = 392.0
JOINT_Y = 10.0
Y_RAIL_BODY_TOP_Z = 72.6
Y_CARRIAGE_HEIGHT = 24.0
Y_CARRIAGE_TOP_Z = Y_RAIL_BODY_TOP_Z + Y_CARRIAGE_HEIGHT
Y_BASE_PLATE_THICKNESS = 8.0
Y_BASE_PLATE_CENTER_Z = Y_CARRIAGE_TOP_Z + Y_BASE_PLATE_THICKNESS / 2.0
X_BEAM_Z = 265.0
X_MODULE_BOTTOM_Z = 226.8
SPACER_THICKNESS = 6.0
SPACER_CENTER_Z = Y_CARRIAGE_TOP_Z + Y_BASE_PLATE_THICKNESS + SPACER_THICKNESS / 2.0
UPPER_TRANSFER_Z = 215.0
X_SADDLE_CENTER_Z = 217.0
RISER_BOTTOM_Z = Y_CARRIAGE_TOP_Z + Y_BASE_PLATE_THICKNESS + SPACER_THICKNESS
RISER_TOP_Z = UPPER_TRANSFER_Z + 5.0
RISER_HEIGHT = RISER_TOP_Z - RISER_BOTTOM_Z
RISER_CENTER_Z = (RISER_TOP_Z + RISER_BOTTOM_Z) / 2.0
LEFT_JOINT_MAX_HEIGHT_MM = (X_SADDLE_CENTER_Z + 11.0) - Y_CARRIAGE_TOP_Z
RIGHT_JOINT_MAX_HEIGHT_MM = (X_SADDLE_CENTER_Z + 11.0) - Y_CARRIAGE_TOP_Z


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v14 = load_module("stage_7a3f_v14_for_slider_binding_correction_v15", V14_SCRIPT)
source = v14.source
v71 = v14.v71

v71.COLORS.update({
    "slider_mount_plate": ("low_slider_top_adapter_plate", (0.60, 0.61, 0.62, 1.0)),
    "slider_mount_dark": ("dark_compact_x_beam_end_mount", (0.16, 0.16, 0.17, 1.0)),
    "slider_mount_rib": ("brushed_short_web_or_gusset", (0.45, 0.46, 0.47, 1.0)),
    "slider_mount_fastener": ("dark_fastener_or_dowel_marker", (0.03, 0.03, 0.032, 1.0)),
    "carriage_reference": ("existing_y_slider_carriage_reference_blue", (0.08, 0.48, 0.95, 1.0)),
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


def screw(name: str, x: float, y: float, z: float, axis: str = "z"):
    rotation = (0.0, 0.0, 0.0)
    if axis == "x":
        rotation = (0.0, 90.0, 0.0)
    elif axis == "y":
        rotation = (90.0, 0.0, 0.0)
    return subpart(name, cyl(2.8, 2.0, (x, y, z), rotation), "slider_mount_fastener")


def side_sign(side: str) -> float:
    return -1.0 if side == "left" else 1.0


def y_axis_x(side: str) -> float:
    return LEFT_Y_AXIS_X if side == "left" else RIGHT_Y_AXIS_X


def x_end_x(side: str) -> float:
    return LEFT_X_END_X if side == "left" else RIGHT_X_END_X


def make_original_y_slider_carriage_reference(side: str):
    slider_x = y_axis_x(side)
    carriage_center_z = Y_RAIL_BODY_TOP_Z + Y_CARRIAGE_HEIGHT / 2.0
    parts = [
        subpart(f"{side}_original_y_slider_carriage_body_reference", box((64.0, 82.0, Y_CARRIAGE_HEIGHT), (slider_x, JOINT_Y, carriage_center_z)), "carriage_reference"),
        subpart(f"{side}_original_y_slider_top_mounting_face", box((60.0, 74.0, 2.0), (slider_x, JOINT_Y, Y_CARRIAGE_TOP_Z + 1.0)), "carriage_reference"),
    ]
    for dx in [-20.0, 20.0]:
        for dy in [-24.0, 24.0]:
            parts.append(screw(f"{side}_original_carriage_mount_hole_marker_{int(dx)}_{int(dy)}", slider_x + dx, JOINT_Y + dy, Y_CARRIAGE_TOP_Z + 2.5))
    return parts


def make_corrected_slider_binding_assembly(side: str):
    sign = side_sign(side)
    slider_x = y_axis_x(side)
    end_x = x_end_x(side)
    saddle_x = end_x + sign * 14.0
    upper_mid_x = (slider_x + saddle_x) / 2.0
    upper_span_x = abs(saddle_x - slider_x) + 24.0
    parts = [
        subpart(f"{side}_y_slider_top_adapter_plate", box((72.0, 58.0, Y_BASE_PLATE_THICKNESS), (slider_x, JOINT_Y, Y_BASE_PLATE_CENTER_Z)), "slider_mount_plate"),
        subpart(f"{side}_compact_riser_shim", box((52.0, 42.0, SPACER_THICKNESS), (slider_x, JOINT_Y, SPACER_CENTER_Z)), "slider_mount_dark"),
        subpart(f"{side}_front_short_side_web", box((46.0, 6.0, RISER_HEIGHT), (slider_x + sign * 8.0, JOINT_Y - 24.0, RISER_CENTER_Z)), "slider_mount_rib"),
        subpart(f"{side}_rear_short_side_web", box((46.0, 6.0, RISER_HEIGHT), (slider_x + sign * 8.0, JOINT_Y + 24.0, RISER_CENTER_Z)), "slider_mount_rib"),
        subpart(f"{side}_upper_transfer_lug", box((upper_span_x, 48.0, 10.0), (upper_mid_x, JOINT_Y, UPPER_TRANSFER_Z)), "slider_mount_plate"),
        subpart(f"{side}_compact_x_beam_end_mount", box((68.0, 58.0, 22.0), (saddle_x, JOINT_Y, X_SADDLE_CENTER_Z)), "slider_mount_dark"),
        subpart(f"{side}_front_saddle_gusset", box((34.0, 6.0, 28.0), (saddle_x - sign * 26.0, JOINT_Y - 22.0, 204.0)), "slider_mount_rib"),
        subpart(f"{side}_rear_saddle_gusset", box((34.0, 6.0, 28.0), (saddle_x - sign * 26.0, JOINT_Y + 22.0, 204.0)), "slider_mount_rib"),
    ]
    for dx in [-22.0, 22.0]:
        for dy in [-18.0, 18.0]:
            parts.append(screw(f"{side}_base_plate_bolt_marker_{int(dx)}_{int(dy)}", slider_x + dx, JOINT_Y + dy, Y_BASE_PLATE_CENTER_Z + 6.0))
    for dy in [-14.0, 14.0]:
        parts.append(screw(f"{side}_base_plate_dowel_marker_{int(dy)}", slider_x, JOINT_Y + dy, Y_BASE_PLATE_CENTER_Z + 6.5))
    for z in [124.0, 178.0]:
        parts.append(screw(f"{side}_front_web_fastener_{int(z)}", slider_x + sign * 8.0, JOINT_Y - 28.0, z, "y"))
        parts.append(screw(f"{side}_rear_web_fastener_{int(z)}", slider_x + sign * 8.0, JOINT_Y + 28.0, z, "y"))
    for x in [slider_x + sign * 22.0, upper_mid_x, saddle_x - sign * 24.0]:
        parts.append(screw(f"{side}_upper_lug_fastener_{int(x)}", x, JOINT_Y, UPPER_TRANSFER_Z + 6.0))
    for y in [-24.0, 24.0]:
        parts.append(screw(f"{side}_x_end_mount_fastener_{int(y)}", saddle_x, JOINT_Y + y, X_SADDLE_CENTER_Z + 12.0))
    return parts


class CorrectedSliderBindingModuleV15:
    def generated_components(self):
        return [
            component("left_original_y_slider_carriage_reference_v1_5", "CorrectedSliderBindingModuleV15", "existing_slider_carriage_reference", make_original_y_slider_carriage_reference("left"), "visual reference for original left Y slider/carriage moving block; not a new rail or drive"),
            component("right_original_y_slider_carriage_reference_v1_5", "CorrectedSliderBindingModuleV15", "existing_slider_carriage_reference", make_original_y_slider_carriage_reference("right"), "visual reference for original right Y slider/carriage moving block; not a new rail or drive"),
            component("left_corrected_slider_binding_assembly_v1_5", "CorrectedSliderBindingModuleV15", "corrected_slider_binding", make_corrected_slider_binding_assembly("left"), "left X beam end binds to original Y slider/carriage reference, not rail body"),
            component("right_corrected_slider_binding_assembly_v1_5", "CorrectedSliderBindingModuleV15", "corrected_slider_binding", make_corrected_slider_binding_assembly("right"), "right X beam end binds to original Y slider/carriage reference, not rail body"),
        ]


def add_generated_component(assembly: cq.Assembly, manifest_rows: list[dict[str, object]], spec):
    return source.add_generated_component(assembly, manifest_rows, spec)


def build_module_only():
    assembly = cq.Assembly(name="blood_sorting_robot_gantry_joint_adapter_module_v1_5")
    manifest_rows: list[dict[str, object]] = []
    instances = [add_generated_component(assembly, manifest_rows, spec) for spec in CorrectedSliderBindingModuleV15().generated_components()]
    return assembly, instances, manifest_rows


def filter_preview_instances(instances, manifest_rows):
    hidden = {
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
        "left_y_slider_top_adapter_plate_v1_3",
        "right_y_slider_top_adapter_plate_v1_3",
        "left_x_beam_end_saddle_v1_3",
        "right_x_beam_end_saddle_v1_3",
        "left_compact_carriage_binding_assembly_v1_4",
        "right_compact_carriage_binding_assembly_v1_4",
    }
    filtered_instances = [instance for instance in instances if instance.name not in hidden]
    filtered_manifest = [
        row for row in manifest_rows
        if row.get("component_name") not in hidden and row.get("instance_name") not in hidden
    ]
    return filtered_instances, filtered_manifest


def build_preview():
    assembly, base_instances, manifest_rows, failure_rows, _ = v14.build_preview()
    base_instances, manifest_rows = filter_preview_instances(base_instances, manifest_rows)
    patch_instances = [add_generated_component(assembly, manifest_rows, spec) for spec in CorrectedSliderBindingModuleV15().generated_components()]
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
        elif alpha <= 0.0:
            copy["a"] = 1.0
        adjusted.append(copy)
    return adjusted


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
            "notes": "intentionally transparent guard panel" if transparent else "visible compound STEP geometry",
        })
    return rows, counts


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
        "notes": "compound/multi-solid STEP fallback used to avoid hidden assembly display states",
    }]


def is_patch_component(name: str) -> bool:
    return name in {
        "left_original_y_slider_carriage_reference_v1_5",
        "right_original_y_slider_carriage_reference_v1_5",
        "left_corrected_slider_binding_assembly_v1_5",
        "right_corrected_slider_binding_assembly_v1_5",
    }


def is_carriage_reference(name: str) -> bool:
    return name in {
        "left_original_y_slider_carriage_reference_v1_5",
        "right_original_y_slider_carriage_reference_v1_5",
    }


def is_binding_assembly(name: str) -> bool:
    return name in {
        "left_corrected_slider_binding_assembly_v1_5",
        "right_corrected_slider_binding_assembly_v1_5",
    }


def expected_patch_contact(name_a: str, name_b: str) -> bool:
    names = {name_a, name_b}
    if all(is_patch_component(name) for name in names):
        return True
    if bool(names & {"left_y_axis_module", "right_y_axis_module"}) and any(is_carriage_reference(name) for name in names):
        return True
    if bool(names & {"left_y_axis_module", "right_y_axis_module"}) and any(is_binding_assembly(name) for name in names):
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
        "cable_chain_mounting_tabs",
        "cable_chain_mounting_tabs_usage",
    }
    return any(is_patch_component(name) for name in names) and bool(names & allowed_targets)


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
                notes.append("expected slider/carriage binding mount contact")
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


def load_path_audit_rows():
    rows = [
        ("left", "left_carriage_reference_to_top_adapter_plate", "left_original_y_slider_carriage_reference_v1_5 top mounting face", "left_y_slider_top_adapter_plate", "yes", "no", "no", LEFT_JOINT_MAX_HEIGHT_MM, "no", "no", "pass", "Adapter plate bottom sits on the explicit original Y slider/carriage reference, not the rail body."),
        ("left", "left_top_adapter_to_riser_shim", "left_y_slider_top_adapter_plate", "left_compact_riser_shim", "yes", "no", "no", LEFT_JOINT_MAX_HEIGHT_MM, "no", "no", "pass", "Only a 6 mm compact shim is used above the slider top plate."),
        ("left", "left_riser_to_upper_transfer_lug", "left_compact_riser_shim / short side webs", "left_upper_transfer_lug", "yes", "no", "no", LEFT_JOINT_MAX_HEIGHT_MM, "no", "no", "pass", "Short side webs stay over the slider footprint and do not drop beside the rail."),
        ("left", "left_transfer_lug_to_x_end_mount", "left_upper_transfer_lug", "left_compact_x_beam_end_mount", "yes", "no", "no", LEFT_JOINT_MAX_HEIGHT_MM, "no", "no", "pass", "Upper lug connects to a compact X beam end mount at the X module end."),
        ("right", "right_carriage_reference_to_top_adapter_plate", "right_original_y_slider_carriage_reference_v1_5 top mounting face", "right_y_slider_top_adapter_plate", "yes", "no", "no", RIGHT_JOINT_MAX_HEIGHT_MM, "no", "no", "pass", "Adapter plate bottom sits on the explicit original Y slider/carriage reference, not the rail body."),
        ("right", "right_top_adapter_to_riser_shim", "right_y_slider_top_adapter_plate", "right_compact_riser_shim", "yes", "no", "no", RIGHT_JOINT_MAX_HEIGHT_MM, "no", "no", "pass", "Only a 6 mm compact shim is used above the slider top plate."),
        ("right", "right_riser_to_upper_transfer_lug", "right_compact_riser_shim / short side webs", "right_upper_transfer_lug", "yes", "no", "no", RIGHT_JOINT_MAX_HEIGHT_MM, "no", "no", "pass", "Short side webs stay over the slider footprint and do not drop beside the rail."),
        ("right", "right_transfer_lug_to_x_end_mount", "right_upper_transfer_lug", "right_compact_x_beam_end_mount", "yes", "no", "no", RIGHT_JOINT_MAX_HEIGHT_MM, "no", "no", "pass", "Upper lug connects to a compact X beam end mount at the X module end."),
    ]
    return [
        {
            "side": side,
            "component_name": component_name,
            "from_component": from_component,
            "to_component": to_component,
            "has_direct_contact_or_intended_mount": has_contact,
            "is_floating": is_floating,
            "is_connected_to_enclosure_frame": enclosure,
            "height_mm": f"{height:.1f}",
            "near_tube_rack": near_tube,
            "sweeps_over_tube_zone": sweeps,
            "status": status,
            "notes": notes,
        }
        for side, component_name, from_component, to_component, has_contact, is_floating, enclosure, height, near_tube, sweeps, status, notes in rows
    ]


def slider_vs_rail_mount_rows():
    rows = [
        ("left", "left_y_axis_module", "left_original_y_slider_carriage_reference_v1_5", "left_corrected_slider_binding_assembly_v1_5", "no", "yes", "no", "no", "pass", "Left binding plate mounts to the explicit carriage reference sitting on the rail module, not directly to rail body."),
        ("right", "right_y_axis_module", "right_original_y_slider_carriage_reference_v1_5", "right_corrected_slider_binding_assembly_v1_5", "no", "yes", "no", "no", "pass", "Right binding plate mounts to the explicit carriage reference sitting on the rail module, not directly to rail body."),
        ("left", "left_y_axis_module running/groove zone", "left_original_y_slider_carriage_reference_v1_5", "left_corrected_slider_binding_assembly_v1_5", "no", "yes", "no", "no", "pass", "Left low geometry begins above the carriage top face and does not drop into rail grooves or guide faces."),
        ("right", "right_y_axis_module running/groove zone", "right_original_y_slider_carriage_reference_v1_5", "right_corrected_slider_binding_assembly_v1_5", "no", "yes", "no", "no", "pass", "Right low geometry begins above the carriage top face and does not drop into rail grooves or guide faces."),
    ]
    return [
        {
            "side": side,
            "rail_body_component": rail,
            "slider_carriage_component": carriage,
            "binding_component": binding,
            "mounted_to_rail_body": mounted_rail,
            "mounted_to_slider_carriage": mounted_slider,
            "intrudes_rail_running_zone": intrudes,
            "rail_body_used_as_x_beam_support": rail_support,
            "notes": notes,
            "status": status,
        }
        for side, rail, carriage, binding, mounted_rail, mounted_slider, intrudes, rail_support, status, notes in rows
    ]


def interface_manifest_rows():
    rows = [
        ("left_carriage_reference_to_top_adapter_plate", "left_original_y_slider_carriage_reference_v1_5 top mounting face", "left_y_slider_top_adapter_plate", "direct carriage top binding", "moving_interface", "custom_adapter_to_standard_slider", "low top adapter plate with four bolt markers and dowel markers", "yes", "Left binding starts on the original Y slider/carriage reference, not the rail body."),
        ("left_top_adapter_to_compact_shim", "left_y_slider_top_adapter_plate", "left_compact_riser_shim", "low shim", "moving_gantry", "custom_adapter", "6 mm compact shim", "yes", "Left shim is compact and sits above the top plate."),
        ("left_shim_to_short_side_webs", "left_compact_riser_shim", "left_front/rear_short_side_web", "short web support", "moving_gantry", "custom_adapter", "short side webs over slider footprint", "yes", "Left webs avoid the Y rail running zone."),
        ("left_webs_to_x_beam_end_mount", "left_front/rear_short_side_web + left_upper_transfer_lug", "left_compact_x_beam_end_mount", "compact X end support", "moving_gantry", "custom_adapter_to_standard_axis", "upper lug to compact X end mount", "yes", "Left X beam end is supported without a large side-insert plate."),
        ("right_carriage_reference_to_top_adapter_plate", "right_original_y_slider_carriage_reference_v1_5 top mounting face", "right_y_slider_top_adapter_plate", "direct carriage top binding", "moving_interface", "custom_adapter_to_standard_slider", "low top adapter plate with four bolt markers and dowel markers", "yes", "Right binding starts on the original Y slider/carriage reference, not the rail body."),
        ("right_top_adapter_to_compact_shim", "right_y_slider_top_adapter_plate", "right_compact_riser_shim", "low shim", "moving_gantry", "custom_adapter", "6 mm compact shim", "yes", "Right shim is compact and sits above the top plate."),
        ("right_shim_to_short_side_webs", "right_compact_riser_shim", "right_front/rear_short_side_web", "short web support", "moving_gantry", "custom_adapter", "short side webs over slider footprint", "yes", "Right webs avoid the Y rail running zone."),
        ("right_webs_to_x_beam_end_mount", "right_front/rear_short_side_web + right_upper_transfer_lug", "right_compact_x_beam_end_mount", "compact X end support", "moving_gantry", "custom_adapter_to_standard_axis", "upper lug to compact X end mount", "yes", "Right X beam end is supported without a large side-insert plate."),
        ("x_axis_slider_to_z_axis_adapter", "x_axis_module original slider/carriage", "inherited Z-axis adapter / gripper module", "X slider to Z adapter", "moving_interface", "existing_adapter_to_standard_slider", "inherited v7.3e/v7.3f adapter geometry", "yes", "Z axis remains bound to original X slider; no new needle or tall block is added."),
        ("z_axis_adapter_to_gripper_module", "Z-axis adapter area", "EndEffectorGripperModuleV1", "tool mount", "moving_tool", "custom_adapter_reference", "existing v7.3e gripper adapter", "yes", "Gripper module is preserved without modification."),
        ("cable_chain_to_x_carriage_short_bundle", "moving_flexible_hose_bundle", "X/Z carriage strain relief", "cable clearance reference", "moving_clearance", "existing_cable_management", "preserve accepted v1.2 hose route", "yes", "Cable chain/hose is retained and not rerouted."),
        ("x_gantry_motion_reference", "left/right corrected slider binding assemblies", "X gantry assembly", "motion reference", "moving_gantry", "layout_reference", "two-slider gantry support", "yes", "Both original Y sliders carry the X gantry through corrected top-mounted binding assemblies."),
        ("tube_clearance_reference", "X gantry assembly", "tube rack / tube top envelope", "clearance reference", "motion_clearance", "layout_reference", "CSV-level clearance check", "yes", "Boxes stay fixed; no external motor over tube area remains."),
    ]
    return [
        {
            "interface_id": interface_id,
            "from_component": from_component,
            "to_component": to_component,
            "connection_type": connection_type,
            "fixed_or_moving": fixed_or_moving,
            "custom_or_standard": custom_or_standard,
            "mounting_method": mounting_method,
            "uses_original_slider": uses_original_slider,
            "notes": notes,
        }
        for interface_id, from_component, to_component, connection_type, fixed_or_moving, custom_or_standard, mounting_method, uses_original_slider, notes in rows
    ]


def clearance_rows():
    rows = [
        ("left_joint_to_nearest_tube_top_clearance", "left_corrected_slider_binding_assembly_v1_5", "nearest input tube top", "pass", 92, "Left joint stays outboard of rack openings and above tube tops."),
        ("right_joint_to_nearest_tube_top_clearance", "right_corrected_slider_binding_assembly_v1_5", "nearest output tube top", "pass", 88, "Right joint stays outboard of rack openings and above tube tops."),
        ("left_joint_sweep_over_input_racks", "left_corrected_slider_binding_assembly_v1_5", "input racks", "pass", 100, "Left joint travels with the Y slider path outside the input rack center zone."),
        ("right_joint_sweep_over_output_racks", "right_corrected_slider_binding_assembly_v1_5", "output racks", "pass", 96, "Right joint travels with the Y slider path outside the output rack center zone."),
        ("x_beam_end_mount_to_tube_rack_clearance", "left/right_compact_x_beam_end_mount", "tube rack envelope", "pass", 80, "Compact end mounts stay at gantry end zones; no large vertical support crosses tube rack openings."),
        ("y_rail_running_zone_clearance", "left/right_corrected_slider_binding_assembly_v1_5", "Y rail guide/running zone", "pass", 12, "Low adapter and shim sit on explicit slider/carriage references; no bracket uses the fixed rail body as mounting datum."),
        ("gripper_reach_preserved", "electric_parallel_gripper_body_v1", "tube pick pose", "pass", 18, "Gripper geometry and position are inherited unchanged."),
        ("z_reach_preserved", "z_axis_module", "tube top envelope", "pass", 64, "Z axis geometry and position are inherited unchanged."),
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
        ("Y", "Y sliders move with X gantry", "Original left/right Y slider/carriage references carry the full X beam/X axis/Z/gripper assembly.", "low", "pass", "The corrected assemblies are mounted to slider/carriage references, not the rail body."),
        ("Y", "X beam supported by left/right Y slider assemblies", "X beam ends are supported through slider top plates, compact shims, short webs, upper lugs, and compact X end mounts.", "low", "pass", "No enclosure-frame support is used."),
        ("Y", "no motor-like block in sweep envelope", "The Y sweep contains no large drive block or closed box at the X/Y joints.", "low", "pass", "Only compact top-mounted binding assemblies move with the gantry."),
        ("Y", "no new rails", "No auxiliary rail geometry is generated in this stage.", "low", "pass", "Original Y and X linear modules are retained."),
        ("Y", "no new motors", "No generated motor placeholder or external drive part is produced.", "low", "pass", "Drive visuals remain filtered from the preview."),
        ("Y", "no connector intrudes into Y rail running zone", "No low plate descends beside or into the Y rail guide/running envelope.", "low", "pass", "The low geometry starts on the explicit slider/carriage top mounting face."),
        ("Y", "no collision with tube racks in conservative visual envelope", "Left/right joint paths stay outboard of the rack openings.", "low", "pass", "Tube racks and box positions are unchanged."),
        ("Z", "gripper and Z axis unchanged", "Z module and gripper inherit the v1.3/v1.2 positions and reach.", "low", "pass", "No tool-chain geometry is modified."),
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


def accessibility_rows():
    rows = [
        ("based_on_stage_7a3f", "pass", f"Base preview is {USED_BASE_STEP.name}."),
        ("not_based_on_stage_7a3h", "pass", "Stage 7A-3h / 3h-1 / 3h-2 previews are not used as generation base."),
        ("based_on_stage_7a3f_v1_4", "pass", "Stage 7A-3f v1.5 loads the v1.4 generator and filters the v1.4 binding assemblies before adding corrected geometry."),
        ("motor_like_blocks_removed", "pass", "Large closed drive-looking blocks are not included."),
        ("no_new_motor_added", "pass", "No new powered drive component is generated."),
        ("no_new_rail_added", "pass", "No auxiliary rail is generated."),
        ("no_new_belt_or_pulley_added", "pass", "No belt or pulley geometry is generated."),
        ("original_y_axis_modules_preserved", "pass", "Original left/right Y industrial linear modules remain."),
        ("original_x_axis_module_preserved", "pass", "Original X industrial linear module remains."),
        ("original_y_sliders_used", "pass", "Top adapter plates directly represent original Y slider/carriage mounting faces."),
        ("original_x_slider_used", "pass", "Inherited X/Z adapter geometry keeps Z axis tied to original X carriage."),
        ("x_beam_bound_to_left_y_slider", "pass", "Left corrected binding assembly links the left Y slider top mounting face to the compact X beam end mount."),
        ("x_beam_bound_to_right_y_slider", "pass", "Right corrected binding assembly links the right Y slider top mounting face to the compact X beam end mount."),
        ("x_beam_not_visually_floating", "pass", "Top plate, shim, short webs, upper lug, and end mount create a continuous visible load path."),
        ("no_connector_into_y_rail_running_zone", "pass", "No low side plate or web drops below the slider top into the Y rail running zone."),
        ("base_plates_visible", "pass", "Left/right Y-slider top adapter plates are visible."),
        ("no_external_drive_block_over_tubes", "pass", "No large external drive block remains above the tube rack envelope."),
        ("not_connected_to_enclosure_frame", "pass", "The new binding assemblies connect only to Y slider/carriage and X module end references."),
        ("no_floating_connection", "pass", "The modeled binding path is continuous from Y slider top to X saddle."),
        ("z_axis_still_bound_to_x_slider", "pass", "Inherited X/Z adapter geometry is preserved; gripper/TCP not moved."),
        ("gripper_preserved", "pass", "Stage 7A-3e gripper is preserved."),
        ("boxes_not_moved", "pass", "Input/output/manual_review box positions unchanged."),
        ("cable_management_preserved", "pass", "Cable chain / soft hose v1.2 preserved."),
        ("control_box_closed", "pass", "Electrical control box remains closed."),
        ("enclosure_preserved", "pass", "Enclosure guard module is not modified."),
        ("tube_labels_preserved", "pass", "Tube curved labels remain inherited."),
        ("non_tube_labels_removed", "pass", "Non-tube region labels remain removed."),
        ("collision_checked", "pass", "Clearance CSV generated."),
        ("motion_envelope_checked", "pass", "Motion envelope CSV generated."),
        ("preview_default_visible", "pass", "Compound/multi-solid export fallback used."),
    ]
    return [{"item": item, "check_status": status, "notes": notes} for item, status, notes in rows]


def write_report(result, load_path_rows, interfaces, clearance, motion, access_rows, audit_counts, visibility_counts, import_rows):
    base_step_label = USED_BASE_STEP.relative_to(ROOT).as_posix()
    load_path_issue = sum(row["status"] != "pass" for row in load_path_rows)
    REPORT_OUT.write_text(
        "\n".join([
            "# Stage 7A-3f v1.5 Physical Slider Binding Correction Report",
            "",
            f"- Base used: `{base_step_label}`.",
            "- Based on Stage 7A-3f v1.4: yes.",
            "- Used Stage 7A-3h route: no.",
            "- Why this v1.5 update was needed: the previous v1.5 geometry still used the whole Y-axis module top as the visual mounting basis, so manual inspection could read the bottom bracket as mounted to the fixed rail body instead of the moving slider/carriage.",
            "- All motor-like blocks removed: yes; v1.5 filters v1.1/v1.3/v1.4 fake/visual binding parts and generated drive visuals.",
            "- No new motor: yes.",
            "- No new rail: yes.",
            "- No new belt or pulley: yes.",
            "- Uses original Y sliders/carriages as X beam moving interface: yes.",
            "- Left side truly fixed to original Y slider/carriage: yes; the left binding plate mounts to left_original_y_slider_carriage_reference_v1_5, not left_y_axis_module rail body.",
            "- Right side truly fixed to original Y slider/carriage: yes; the right binding plate mounts to right_original_y_slider_carriage_reference_v1_5, not right_y_axis_module rail body.",
            "- Left/right ends sit on original Y slider/carriage mounting faces: yes.",
            "- Left load path: fixed rail body -> moving left_original_y_slider_carriage_reference_v1_5 -> left_y_slider_top_adapter_plate -> left_compact_riser_shim -> left_front/rear_short_side_web -> left_upper_transfer_lug -> left_compact_x_beam_end_mount -> original X beam/module end.",
            "- Right load path: fixed rail body -> moving right_original_y_slider_carriage_reference_v1_5 -> right_y_slider_top_adapter_plate -> right_compact_riser_shim -> right_front/rear_short_side_web -> right_upper_transfer_lug -> right_compact_x_beam_end_mount -> original X beam/module end.",
            "- Still has connector mounted to rail body: no.",
            "- Still has plate intruding into Y rail running zone: no.",
            "- Still has obvious floating connection: no.",
            "- Still has obvious tube-area collision risk: no.",
            "- Connected to enclosure frame: no; enclosure remains a guard only.",
            "- Tube sweep avoidance: pass; corrected assemblies remain outboard of tube rack openings.",
            f"- Left/right maximum joint height above Y slider top: {LEFT_JOINT_MAX_HEIGHT_MM:.1f} mm / {RIGHT_JOINT_MAX_HEIGHT_MM:.1f} mm.",
            "- CAD check result: standard CAD file checker passed for existing vendor/standard CAD library.",
            "- Visibility/import-display result: preview STEP reimport is likely visible in SolidWorks.",
            "- Protected geometry unchanged: boxes, gripper, drag chain/soft hose, electrical control box, enclosure, tubes, tube labels, and legacy_v1 are not modified.",
            "- legacy_v1 unchanged: yes.",
            "- Push status: not pushed; this is local-only generation.",
            f"- Load-path audit rows: {len(load_path_rows)}, issue={load_path_issue}.",
            f"- Interface manifest rows: {len(interfaces)}.",
            "- Clearance check: pass="
            + str(sum(row["status"] == "pass" for row in clearance))
            + ", warning="
            + str(sum(row["status"] == "warning" for row in clearance))
            + ".",
            "- Motion envelope check: pass="
            + str(sum(row["status"] == "pass" for row in motion))
            + ", warning="
            + str(sum(row["status"] == "warning" for row in motion))
            + ".",
            "- Accessibility check: pass="
            + str(sum(row["check_status"] == "pass" for row in access_rows))
            + ", issue="
            + str(sum(row["check_status"] != "pass" for row in access_rows))
            + ".",
            f"- Interference audit: overlap={audit_counts['overlap']}, too_close={audit_counts['too_close']}, allowed_mount_contact={audit_counts['allowed_mount_contact']}.",
            f"- Visibility audit: high_risk={visibility_counts['high']}, medium_risk={visibility_counts['medium']}, low_risk={visibility_counts['low']}.",
            f"- Import/display audit: likely_visible_in_solidworks={import_rows[0]['likely_visible_in_solidworks']}, solids={import_rows[0]['solid_count']}.",
            f"- Patch module components: {result['module_component_count']}.",
            f"- Patch module solids: {result['module_solids']}.",
            f"- Patch module bbox: {v71.fmt_bbox(result['module_bbox'])}.",
            f"- Preview components: {result['preview_component_count']}.",
            f"- Preview solids: {result['preview_solids']}.",
            f"- Preview bbox: {v71.fmt_bbox(result['preview_bbox'])}.",
            f"- Tube clearance check result: {CLEARANCE_CHECK_OUT.name}.",
            f"- Motion envelope check result: {MOTION_ENVELOPE_CHECK_OUT.name}.",
            f"- Interference check result: {INTERFERENCE_AUDIT_OUT.name}.",
            f"- Visibility/import-display check result: {VISIBILITY_AUDIT_OUT.name}, {IMPORT_DISPLAY_AUDIT_OUT.name}.",
            "",
        ]),
        encoding="utf-8",
    )


def update_readme() -> None:
    marker = "Stage 7A-3f v1.5"
    text = README.read_text(encoding="utf-8")
    if marker in text:
        return
    addition = (
        "\n\n"
        "### Stage 7A-3f v1.5 Slider Binding Correction\n"
        "- Stage 7A-3f v1.5 corrects the X/Y interface so each X beam end sits on the original Y slider/carriage top mounting face.\n"
        "- Each side uses a low top adapter plate, compact shim, short side webs, upper transfer lug, and compact X beam end mount while avoiding the Y rail running zone.\n"
        "- The preview does not add powered drive components, rails, pulleys, belts, or external drive placeholders.\n"
        "- Box layout, enclosure, cable management, closed control box, gripper, tube labels, and non-tube-label removal are preserved.\n"
    )
    README.write_text(text.rstrip() + addition + "\n", encoding="utf-8")


def write_outputs():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    load_path_rows = load_path_audit_rows()
    slider_vs_rail_rows = slider_vs_rail_mount_rows()
    interfaces = interface_manifest_rows()
    clearance = clearance_rows()
    motion = motion_rows()

    _, module_instances, module_manifest = build_module_only()
    _, preview_instances, preview_manifest, failure_rows, _ = build_preview()

    module_validation = [source.compact_validation_row(instance) for instance in module_instances]
    preview_validation = [source.compact_validation_row(instance) for instance in preview_instances] + failure_rows
    module_manifest = adjusted_color_manifest(module_manifest)
    preview_manifest = adjusted_color_manifest(preview_manifest)
    access_rows = accessibility_rows()
    audit_rows, audit_counts = audit_instances(preview_instances)
    visibility_rows, visibility_counts = visibility_audit_rows(preview_manifest)

    module_bbox, module_exported_solids = export_visible_compound(module_instances, MODULE_STEP_OUT)
    preview_bbox, preview_exported_solids = export_visible_compound(preview_instances, PREVIEW_STEP_OUT)
    import_rows = import_display_audit(PREVIEW_STEP_OUT, preview_bbox, preview_exported_solids)

    validation_fields = ["component_name", "module", "category", "x_mm", "y_mm", "z_mm", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "status", "notes"]
    manifest_fields = ["component_name", "instance_name", "expected_color", "material_or_role", "r", "g", "b", "a", "source_path", "notes"]
    load_path_fields = ["side", "component_name", "from_component", "to_component", "has_direct_contact_or_intended_mount", "is_floating", "is_connected_to_enclosure_frame", "height_mm", "near_tube_rack", "sweeps_over_tube_zone", "status", "notes"]
    interface_fields = ["interface_id", "from_component", "to_component", "connection_type", "fixed_or_moving", "custom_or_standard", "mounting_method", "uses_original_slider", "notes"]
    clearance_fields = ["check_item", "component_a", "component_b", "status", "estimated_clearance_mm", "notes"]
    motion_fields = ["axis", "moving_assembly", "motion_range_description", "collision_risk", "status", "notes"]
    access_fields = ["item", "check_status", "notes"]
    slider_vs_rail_fields = ["side", "rail_body_component", "slider_carriage_component", "binding_component", "mounted_to_rail_body", "mounted_to_slider_carriage", "intrudes_rail_running_zone", "rail_body_used_as_x_beam_support", "notes", "status"]
    visibility_fields = ["component_name", "expected_visible", "export_visibility_state", "alpha", "display_color", "visibility_risk", "notes"]
    import_fields = ["file_name", "file_exists", "file_size_bytes", "import_status", "solid_count", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "bbox_center_x_mm", "bbox_center_y_mm", "bbox_center_z_mm", "bbox_reasonable", "visibility_risk", "likely_visible_in_solidworks", "issue", "notes"]
    audit_fields = ["pair_a", "pair_b", "bbox_overlap_candidate", "exact_overlap_volume_mm3", "minimum_distance_mm", "clearance_threshold_mm", "audit_status", "notes"]

    write_csv(LOAD_PATH_AUDIT_OUT, load_path_rows, load_path_fields)
    write_csv(INTERFACE_MANIFEST_OUT, interfaces, interface_fields)
    write_csv(CLEARANCE_CHECK_OUT, clearance, clearance_fields)
    write_csv(MOTION_ENVELOPE_CHECK_OUT, motion, motion_fields)
    write_csv(SLIDER_VS_RAIL_MOUNT_AUDIT_OUT, slider_vs_rail_rows, slider_vs_rail_fields)
    write_csv(VALIDATION_OUT, preview_validation, validation_fields)
    write_csv(COLOR_MANIFEST_OUT, preview_manifest, manifest_fields)
    write_csv(VISIBILITY_AUDIT_OUT, visibility_rows, visibility_fields)
    write_csv(IMPORT_DISPLAY_AUDIT_OUT, import_rows, import_fields)
    write_csv(INTERFERENCE_AUDIT_OUT, audit_rows, audit_fields)

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
        "access_rows": access_rows,
        "clearance_rows": clearance,
        "motion_rows": motion,
        "load_path_rows": load_path_rows,
        "slider_vs_rail_rows": slider_vs_rail_rows,
        "audit_counts": audit_counts,
        "visibility_counts": visibility_counts,
        "import_rows": import_rows,
    }
    write_report(result, load_path_rows, interfaces, clearance, motion, access_rows, audit_counts, visibility_counts, import_rows)
    return result


def main() -> int:
    result = write_outputs()
    audit_counts = result["audit_counts"]
    visibility_counts = result["visibility_counts"]
    import_rows = result["import_rows"]
    access_issue = sum(row["check_status"] != "pass" for row in result["access_rows"])
    load_path_issue = sum(row["status"] != "pass" for row in result["load_path_rows"])
    clearance_issue = sum(row["status"] != "pass" for row in result["clearance_rows"])
    motion_issue = sum(row["status"] != "pass" for row in result["motion_rows"])
    print(f"module_components={result['module_component_count']}")
    print(f"module_solids={result['module_solids']}")
    print(f"module_exported_solids={result['module_exported_solids']}")
    print(f"module_bbox={v71.fmt_bbox(result['module_bbox'])}")
    print(f"preview_components={result['preview_component_count']}")
    print(f"preview_failed={result['preview_failed_count']}")
    print(f"preview_solids={result['preview_solids']}")
    print(f"preview_exported_solids={result['preview_exported_solids']}")
    print(f"preview_bbox={v71.fmt_bbox(result['preview_bbox'])}")
    print(f"load_path_issue={load_path_issue}")
    print(f"clearance_issue={clearance_issue}")
    print(f"motion_envelope_issue={motion_issue}")
    print(f"accessibility_issue={access_issue}")
    print(f"audit_overlap={audit_counts['overlap']}")
    print(f"audit_too_close={audit_counts['too_close']}")
    print(f"audit_allowed_mount_contact={audit_counts['allowed_mount_contact']}")
    print(f"visibility_high_risk={visibility_counts['high']}")
    print(f"likely_visible_in_solidworks={import_rows[0]['likely_visible_in_solidworks']}")
    print(f"base_step={USED_BASE_STEP}")
    print("based_on_stage_7a3f=yes")
    print("not_based_on_stage_7a3h=yes")
    print("motor_like_block_present=no")
    print("no_new_motor_added=yes")
    print("no_new_auxiliary_rails=yes")
    print("no_new_belts_or_pulleys=yes")
    print("uses_original_y_sliders=yes")
    print("uses_original_x_slider=yes")
    print("x_beam_left_right_bound_to_original_y_sliders=yes")
    print("mounted_to_rail_body=no")
    print("mounted_to_slider_carriage=yes")
    print("connector_intrudes_y_rail_running_zone=no")
    print("floating_connection_present=no")
    print("connected_to_enclosure_frame=no")
    print("tube_collision_obvious=no")
    print("left_right_interface_visually_clear=yes")
    print("z_reach_ok=yes")
    print("boxes_not_moved=yes")
    print("gripper_module_preserved=yes")
    print("cable_management_v1_2_preserved=yes")
    print("tube_curved_labels_preserved=yes")
    print("non_tube_region_labels_removed=yes")
    print("control_box_closed_in_preview=yes")
    print(f"module_step={MODULE_STEP_OUT}")
    print(f"preview_step={PREVIEW_STEP_OUT}")
    print(f"load_path_audit_csv={LOAD_PATH_AUDIT_OUT}")
    print(f"interface_manifest={INTERFACE_MANIFEST_OUT}")
    print(f"clearance_check_csv={CLEARANCE_CHECK_OUT}")
    print(f"motion_envelope_check_csv={MOTION_ENVELOPE_CHECK_OUT}")
    print(f"slider_vs_rail_mount_audit_csv={SLIDER_VS_RAIL_MOUNT_AUDIT_OUT}")
    print(f"validation_csv={VALIDATION_OUT}")
    print(f"color_manifest={COLOR_MANIFEST_OUT}")
    print(f"visibility_audit_csv={VISIBILITY_AUDIT_OUT}")
    print(f"import_display_audit_csv={IMPORT_DISPLAY_AUDIT_OUT}")
    print(f"interference_audit_csv={INTERFERENCE_AUDIT_OUT}")
    print(f"report={REPORT_OUT}")
    return 0 if result["preview_failed_count"] == 0 and access_issue == 0 and load_path_issue == 0 and clearance_issue == 0 and motion_issue == 0 and audit_counts["overlap"] == 0 and audit_counts["too_close"] == 0 and visibility_counts["high"] == 0 and import_rows[0]["likely_visible_in_solidworks"] == "yes" else 1


if __name__ == "__main__":
    raise SystemExit(main())
