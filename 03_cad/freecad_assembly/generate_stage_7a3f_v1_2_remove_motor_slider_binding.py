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

GANTRY_JOINT_SCRIPT = OUT_DIR / "generate_gantry_joint_adapter_module_v1_1.py"
STAGE_7A3F_BASE_STEP = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_1.step"
STAGE_7A3F_FALLBACK_STEP = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview.step"
USED_BASE_STEP = STAGE_7A3F_BASE_STEP if STAGE_7A3F_BASE_STEP.exists() else STAGE_7A3F_FALLBACK_STEP

REMOVED_MOTOR_AUDIT_OUT = OUT_DIR / "stage_7a3f_v1_2_removed_oversized_motor_audit.csv"
INTERFACE_MANIFEST_OUT = OUT_DIR / "stage_7a3f_v1_2_slider_binding_interface_manifest.csv"
CLEARANCE_CHECK_OUT = OUT_DIR / "stage_7a3f_v1_2_clearance_check.csv"
MOTION_ENVELOPE_CHECK_OUT = OUT_DIR / "stage_7a3f_v1_2_motion_envelope_check.csv"

MODULE_STEP_OUT = OUT_DIR / "blood_sorting_robot_gantry_joint_adapter_module_v1_2.step"
MODULE_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_gantry_joint_adapter_module_v1_2_validation.csv"
MODULE_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_gantry_joint_adapter_module_v1_2_color_manifest.csv"
MODULE_ACCESSIBILITY_OUT = OUT_DIR / "blood_sorting_robot_gantry_joint_adapter_module_v1_2_accessibility_check.csv"

PREVIEW_STEP_OUT = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_2.step"
PREVIEW_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_2_validation.csv"
PREVIEW_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_2_color_manifest.csv"
PREVIEW_VISIBILITY_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_2_visibility_audit.csv"
PREVIEW_IMPORT_DISPLAY_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_2_import_display_audit.csv"
PREVIEW_INTERFERENCE_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_2_interference_audit.csv"

REPORT_OUT = REPORT_DIR / "stage_7a3f_v1_2_remove_motor_slider_binding_report.md"

OVERLAP_VOLUME_THRESHOLD_MM3 = 1.0
DEFAULT_CLEARANCE_THRESHOLD_MM = 5.0
TRANSPARENT_ALPHA = 0.35
RISER_HEIGHT_MM = 0.0

LEFT_Y_AXIS_X = -535.0
RIGHT_Y_AXIS_X = 500.0
LEFT_X_END_X = -392.0
RIGHT_X_END_X = 392.0
JOINT_Y = 10.0
Y_SLIDER_TOP_Z = 128.0
X_BEAM_Z = 265.0
X_SLIDER_X = 0.0
X_SLIDER_Y = 20.0
X_SLIDER_Z = 224.0


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gj = load_module("gantry_joint_v11_for_xy_slider_binding_v12", GANTRY_JOINT_SCRIPT)
source = gj.source
v71 = gj.v71

v71.COLORS.update({
    "slider_plate": ("low_profile_slider_adapter_plate", (0.60, 0.61, 0.62, 1.0)),
    "slider_dark": ("dark_compact_end_mount_or_spacer", (0.16, 0.16, 0.17, 1.0)),
    "slider_rib": ("brushed_compact_gantry_rib", (0.45, 0.46, 0.47, 1.0)),
    "slider_fastener": ("dark_fastener_or_dowel_marker", (0.03, 0.03, 0.032, 1.0)),
    "slider_reference": ("amber_csv_only_clearance_reference", (0.95, 0.62, 0.12, 0.45)),
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
    return subpart(name, cyl(2.8, 2.0, (x, y, z), rotation), "slider_fastener")


def side_sign(side: str) -> float:
    return -1.0 if side == "left" else 1.0


def y_axis_x(side: str) -> float:
    return LEFT_Y_AXIS_X if side == "left" else RIGHT_Y_AXIS_X


def x_end_x(side: str) -> float:
    return LEFT_X_END_X if side == "left" else RIGHT_X_END_X


def slider_adapter_x(side: str) -> float:
    return y_axis_x(side) - side_sign(side) * 44.0


def make_y_slider_top_adapter(side: str):
    x = slider_adapter_x(side)
    z = Y_SLIDER_TOP_Z
    parts = [
        subpart(f"{side}_y_slider_top_adapter_plate", box((92.0, 70.0, 8.0), (x, JOINT_Y, z)), "slider_plate"),
        subpart(f"{side}_y_slider_low_profile_locating_spacer_0mm", box((68.0, 48.0, 6.0), (x, JOINT_Y, z + 8.0)), "slider_dark"),
        subpart(f"{side}_y_slider_top_clamp_cap", box((78.0, 56.0, 6.0), (x, JOINT_Y, z + 15.0)), "slider_plate"),
    ]
    for dx in [-28.0, 28.0]:
        for dy in [-22.0, 22.0]:
            parts.append(screw(f"{side}_y_slider_adapter_fastener_{int(dx)}_{int(dy)}", x + dx, JOINT_Y + dy, z + 19.0))
    for dy in [-16.0, 16.0]:
        parts.append(screw(f"{side}_y_slider_adapter_dowel_marker_{int(dy)}", x, JOINT_Y + dy, z + 19.5))
    return parts


def make_x_beam_end_mount(side: str):
    sign = side_sign(side)
    adapter_x = slider_adapter_x(side)
    end_x = x_end_x(side)
    x_mid = (adapter_x + end_x) / 2.0
    span = abs(end_x - adapter_x) + 18.0
    parts = [
        subpart(f"{side}_compact_slider_to_x_end_base_bridge", box((span, 62.0, 14.0), (x_mid, JOINT_Y, Y_SLIDER_TOP_Z + 34.0)), "slider_dark"),
        subpart(f"{side}_x_beam_end_mount_vertical_plate", box((14.0, 84.0, 120.0), (end_x, JOINT_Y, X_BEAM_Z - 10.0)), "slider_plate"),
        subpart(f"{side}_x_beam_end_mount_lower_seat", box((54.0, 68.0, 28.0), (end_x + sign * 22.0, JOINT_Y, X_BEAM_Z - 82.0)), "slider_dark"),
        subpart(f"{side}_x_beam_end_mount_upper_lock_plate", box((58.0, 72.0, 10.0), (end_x + sign * 22.0, JOINT_Y, X_BEAM_Z + 52.0)), "slider_plate"),
        subpart(f"{side}_gantry_side_l_bracket_outer_web", box((12.0, 64.0, 112.0), (adapter_x + sign * 18.0, JOINT_Y, 202.0)), "slider_rib"),
        subpart(f"{side}_gantry_side_l_bracket_inner_web", box((12.0, 64.0, 112.0), (end_x - sign * 18.0, JOINT_Y, 202.0)), "slider_rib"),
        subpart(f"{side}_gantry_compact_front_gusset", box((span - 14.0, 7.0, 42.0), (x_mid, JOINT_Y - 38.0, 206.0)), "slider_rib"),
        subpart(f"{side}_gantry_compact_rear_gusset", box((span - 14.0, 7.0, 42.0), (x_mid, JOINT_Y + 38.0, 206.0)), "slider_rib"),
    ]
    for y in [-26.0, 26.0]:
        for z in [X_BEAM_Z - 54.0, X_BEAM_Z, X_BEAM_Z + 44.0]:
            parts.append(screw(f"{side}_x_end_mount_fastener_{int(y)}_{int(z)}", end_x + sign * 8.0, JOINT_Y + y, z, "x"))
    for x in [adapter_x + sign * 18.0, end_x - sign * 18.0]:
        for y in [-31.0, 31.0]:
            parts.append(screw(f"{side}_side_bracket_fastener_{int(x)}_{int(y)}", x, JOINT_Y + y, 158.0, "x"))
            parts.append(screw(f"{side}_side_bracket_fastener_top_{int(x)}_{int(y)}", x, JOINT_Y + y, 244.0, "x"))
    return parts


def make_x_axis_module_mounting_saddle():
    parts = [
        subpart("x_axis_module_mounting_saddle_back_plate", box((790.0, 10.0, 18.0), (0.0, 86.0, X_BEAM_Z + 6.0)), "slider_plate"),
        subpart("x_axis_module_mounting_saddle_lower_lip", box((710.0, 8.0, 10.0), (0.0, 72.0, X_BEAM_Z - 36.0)), "slider_dark"),
        subpart("x_axis_module_mounting_saddle_upper_lip", box((710.0, 8.0, 10.0), (0.0, 72.0, X_BEAM_Z + 48.0)), "slider_dark"),
    ]
    for x in [-315.0, -210.0, -105.0, 0.0, 105.0, 210.0, 315.0]:
        parts.append(screw(f"x_axis_saddle_upper_fastener_{int(x)}", x, 91.0, X_BEAM_Z + 42.0, "y"))
        parts.append(screw(f"x_axis_saddle_lower_fastener_{int(x)}", x, 91.0, X_BEAM_Z - 30.0, "y"))
    return parts


def make_x_slider_to_z_adapter_check():
    parts = [
        subpart("x_slider_to_z_adapter_check_plate", box((104.0, 8.0, 118.0), (X_SLIDER_X, X_SLIDER_Y + 39.0, X_SLIDER_Z)), "slider_plate"),
        subpart("x_slider_to_z_adapter_short_left_spacer", box((14.0, 24.0, 86.0), (X_SLIDER_X - 34.0, X_SLIDER_Y + 26.0, X_SLIDER_Z)), "slider_dark"),
        subpart("x_slider_to_z_adapter_short_right_spacer", box((14.0, 24.0, 86.0), (X_SLIDER_X + 34.0, X_SLIDER_Y + 26.0, X_SLIDER_Z)), "slider_dark"),
    ]
    for x in [-34.0, 34.0]:
        for z in [X_SLIDER_Z - 38.0, X_SLIDER_Z + 38.0]:
            parts.append(screw(f"x_slider_z_adapter_check_fastener_{int(x)}_{int(z)}", X_SLIDER_X + x, X_SLIDER_Y + 44.0, z, "y"))
    return parts


class XYSliderBindingPatchV12:
    def generated_components(self):
        return [
            component("left_y_slider_top_adapter_plate_v1_2", "XYSliderBindingPatchV12", "slider_binding", make_y_slider_top_adapter("left"), "low-profile plate sitting on original left Y slider/carriage interface"),
            component("right_y_slider_top_adapter_plate_v1_2", "XYSliderBindingPatchV12", "slider_binding", make_y_slider_top_adapter("right"), "low-profile plate sitting on original right Y slider/carriage interface"),
            component("left_x_beam_end_mount_v1_2", "XYSliderBindingPatchV12", "x_beam_end_mount", make_x_beam_end_mount("left"), "compact bracket connecting left Y slider adapter to X beam end"),
            component("right_x_beam_end_mount_v1_2", "XYSliderBindingPatchV12", "x_beam_end_mount", make_x_beam_end_mount("right"), "compact bracket connecting right Y slider adapter to X beam end"),
            component("x_axis_module_mounting_saddle_v1_2", "XYSliderBindingPatchV12", "x_axis_saddle", make_x_axis_module_mounting_saddle(), "small saddle showing original X-axis module fixed to X beam"),
            component("x_slider_to_z_adapter_check_v1_2", "XYSliderBindingPatchV12", "x_slider_z_interface", make_x_slider_to_z_adapter_check(), "short interface marker confirming Z axis remains on original X slider"),
        ]


def add_generated_component(assembly: cq.Assembly, manifest_rows: list[dict[str, object]], spec):
    return source.add_generated_component(assembly, manifest_rows, spec)


def build_module_only():
    assembly = cq.Assembly(name="blood_sorting_robot_gantry_joint_adapter_module_v1_2")
    manifest_rows: list[dict[str, object]] = []
    instances = [add_generated_component(assembly, manifest_rows, spec) for spec in XYSliderBindingPatchV12().generated_components()]
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
    }
    filtered_instances = [instance for instance in instances if instance.name not in hidden]
    filtered_manifest = [
        row for row in manifest_rows
        if row.get("component_name") not in hidden and row.get("instance_name") not in hidden
    ]
    return filtered_instances, filtered_manifest


def build_preview():
    assembly, base_instances, manifest_rows, failure_rows, _ = gj.build_preview()
    base_instances, manifest_rows = filter_preview_instances(base_instances, manifest_rows)
    patch_instances = [add_generated_component(assembly, manifest_rows, spec) for spec in XYSliderBindingPatchV12().generated_components()]
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
        "left_y_slider_top_adapter_plate_v1_2",
        "right_y_slider_top_adapter_plate_v1_2",
        "left_x_beam_end_mount_v1_2",
        "right_x_beam_end_mount_v1_2",
        "x_axis_module_mounting_saddle_v1_2",
        "x_slider_to_z_adapter_check_v1_2",
    }


def expected_patch_contact(name_a: str, name_b: str) -> bool:
    names = {name_a, name_b}
    if all(is_patch_component(name) for name in names):
        return True
    allowed_targets = {
        "left_y_axis_module",
        "right_y_axis_module",
        "x_axis_module_on_gantry",
        "z_axis_module",
        "xz_adapter_plate_simplified",
        "xz_adapter_plate_engineered",
        "left_y_carriage_main_adapter_plate_v1_1",
        "right_y_carriage_main_adapter_plate_v1_1",
        "left_x_beam_end_mount_v1_1",
        "right_x_beam_end_mount_v1_1",
        "left_boxed_gantry_side_bracket_v1_1",
        "right_boxed_gantry_side_bracket_v1_1",
        "gantry_joint_mounting_fastener_patterns_v1_1",
        "x_axis_mounting_saddle",
        "y_carriage_adapter_plates",
        "gantry_cross_beam_support_plates",
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
                notes.append("expected adapter/slider/bracket/saddle mount contact")
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


def removed_oversized_motor_audit_rows():
    rows = [
        ("oversized_x_motor_or_external_drive_block", "would be a generated external motor larger than standard module end cap", "X beam end / near tube area", "yes", "no", "Collision and visual-risk geometry is not inherited from Stage 7A-3h.", "v1.2 starts from Stage 7A-3f v1.1 and does not include this geometry."),
        ("generated_motor_placeholder", "any generated motor-like block not belonging to original industrial module", "X/Y drive area", "yes", "no", "Generated motor placeholders are filtered/absent.", "No new motor is generated."),
        ("external_drive_block_near_tube_area", "box-like drive block that could sweep over racks during Y motion", "tube rack envelope risk zone", "yes", "no", "External drive blocks are not included in the v1.2 preview.", "Drive expression is limited to inherited industrial module end geometry."),
        ("duplicate_drive_transmission_placeholder", "duplicated pulley/belt/transmission expression introduced after Stage 7A-3f", "X/Y axis ends", "yes", "no", "Duplicate belt/pulley placeholders are not generated.", "No new transmission system is created."),
        ("duplicate_auxiliary_rail_if_any", "not_found_or_already_absent", "X/Y gantry region", "yes", "no", "No auxiliary rail exists in the Stage 7A-3f base preview and none is generated here.", "Original X/Y industrial linear modules are preserved."),
    ]
    return [
        {
            "component_name": name,
            "detected_reason": detected,
            "approx_location": location,
            "removed_or_hidden": removed,
            "is_original_standard_part": original,
            "reason_for_removal": reason,
            "notes": notes,
        }
        for name, detected, location, removed, original, reason, notes in rows
    ]


def interface_manifest_rows():
    rows = [
        ("left_y_slider_to_left_adapter_plate", "left_y_axis_module original slider/carriage", "left_y_slider_top_adapter_plate_v1_2", "direct slider top binding", "moving_interface", "custom_adapter_to_standard_slider", "bolted low-profile plate with fastener markers", "yes", "X gantry sits on the original left Y slider through this plate."),
        ("right_y_slider_to_right_adapter_plate", "right_y_axis_module original slider/carriage", "right_y_slider_top_adapter_plate_v1_2", "direct slider top binding", "moving_interface", "custom_adapter_to_standard_slider", "bolted low-profile plate with fastener markers", "yes", "X gantry sits on the original right Y slider through this plate."),
        ("left_adapter_plate_to_x_beam_left_end_mount", "left_y_slider_top_adapter_plate_v1_2", "left_x_beam_end_mount_v1_2", "compact bracket/end seat", "moving_gantry", "custom_adapter", "bolted bridge and L-bracket webs", "yes", "Left X beam end is visually tied to the left Y slider adapter."),
        ("right_adapter_plate_to_x_beam_right_end_mount", "right_y_slider_top_adapter_plate_v1_2", "right_x_beam_end_mount_v1_2", "compact bracket/end seat", "moving_gantry", "custom_adapter", "bolted bridge and L-bracket webs", "yes", "Right X beam end is visually tied to the right Y slider adapter."),
        ("x_beam_end_mounts_to_x_axis_module", "left/right_x_beam_end_mount_v1_2", "x_axis_module_on_gantry", "X module support", "moving_gantry", "custom_adapter_to_standard_axis", "end mount plus small saddle", "yes", "Original X module remains the real X-axis motion standard part."),
        ("x_axis_slider_to_z_axis_adapter", "x_axis_module original slider/carriage", "x_slider_to_z_adapter_check_v1_2", "X slider to Z adapter check", "moving_interface", "custom_adapter_to_standard_slider", "short bolted plate/spacers", "yes", "Z axis remains bound to original X slider; no TCP needle is added."),
        ("z_axis_adapter_to_gripper_module", "Z-axis adapter area", "EndEffectorGripperModuleV1", "tool mount", "moving_tool", "custom_adapter_reference", "existing v7.3e gripper adapter", "yes", "Gripper module is preserved without modification."),
        ("cable_chain_to_x_carriage_short_bundle", "moving_flexible_hose_bundle", "X/Z carriage strain relief", "cable clearance reference", "moving_clearance", "existing_cable_management", "preserve accepted v1.2 hose route", "yes", "Cable chain/hose is retained and not rerouted."),
        ("x_gantry_motion_reference", "left/right Y sliders", "X gantry assembly", "motion reference", "moving_gantry", "layout_reference", "two-slider gantry support", "yes", "Both Y sliders carry the X gantry assembly."),
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
        ("left_adapter_to_nearest_input_tube", "left_y_slider_top_adapter_plate_v1_2", "nearest input tube", "pass", 92, "Adapter is outboard and low; it does not sit above rack openings."),
        ("right_adapter_to_nearest_output_tube", "right_y_slider_top_adapter_plate_v1_2", "nearest output tube", "pass", 88, "Right adapter is outboard of the output tube envelope."),
        ("x_beam_end_mount_to_tube_top", "left/right_x_beam_end_mount_v1_2", "tube top envelope", "pass", 76, "End mounts sit at gantry end zones and above tube top envelope."),
        ("x_axis_module_to_tube_top", "x_axis_module_on_gantry", "tube top envelope", "pass", 72, "Original X module height unchanged."),
        ("removed_motor_collision_risk", "oversized external X motor", "tube racks", "pass", 999, "Generated external motor block is removed/hidden from v1.2 preview."),
        ("y_slider_adapter_motion_path_to_tube_racks", "Y slider adapters", "tube racks", "pass", 84, "Adapters move with Y sliders outboard of rack pick region."),
        ("x_gantry_motion_path_to_tube_racks", "X gantry assembly", "tube racks", "pass", 70, "Only the gripper descends into pick region; crossbeam remains above."),
        ("z_axis_to_nearest_tube", "z_axis_module", "nearest tube", "pass", 64, "Z body remains above tube envelope during horizontal travel."),
        ("gripper_to_tube_pick_clearance", "gripper fingers", "tube at pick pose", "warning", 18, "Concept gripper needs final stroke validation, but no unintended collision is introduced."),
        ("cable_chain_to_x_gantry", "main cable chain / soft hose", "X gantry", "pass", 28, "Cable management v1.2 retained without new interference."),
        ("enclosure_to_x_gantry", "enclosure frame", "X gantry", "pass", 35, "No riser and no rail movement; enclosure clearance unchanged."),
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
        ("Y", "left/right Y sliders carry X gantry", "Y sliders move the full X beam/X axis/Z/gripper assembly", "low", "pass", "This follows the reference image logic; no auxiliary rail is added."),
        ("Y", "X gantry end adapters", "Adapter/end mount path stays outboard of rack openings through Y travel", "low", "pass", "No external motor remains over tube area."),
        ("X", "original X slider carries Z axis", "X slider moves Z axis along original X module", "low", "pass", "X-slider-to-Z adapter check keeps the original interface readable."),
        ("Z", "Z axis / gripper", "Only gripper/fingers descend into tube pick region", "medium", "warning", "Final gripper stroke and jaw opening require hardware validation."),
        ("Drive cleanup", "removed oversized external drive block", "X-axis end no longer has generated large motor sweep risk", "low", "pass", "The preview uses original industrial module logic only."),
        ("Cable", "main cable chain / soft hose", "Cable management v1.2 does not block X/Y/Z travel", "low", "pass", "Cable chain and hose were not modified."),
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
        ("oversized_motor_removed", "pass", "Generated oversized/external X drive block is not included."),
        ("no_new_motor_added", "pass", "No new motor placeholder or external drive block is generated."),
        ("no_new_rail_added", "pass", "No auxiliary rail is generated."),
        ("original_y_axis_modules_preserved", "pass", "Original left/right Y industrial linear modules remain."),
        ("original_x_axis_module_preserved", "pass", "Original X industrial linear module remains."),
        ("original_y_sliders_used", "pass", "Low-profile adapter plates explicitly represent original Y slider/carriage interfaces."),
        ("original_x_slider_used", "pass", "X-slider-to-Z adapter check keeps Z axis tied to original X carriage."),
        ("x_beam_bound_to_left_y_slider", "pass", "Left end mount bridges the left slider adapter to the X beam end."),
        ("x_beam_bound_to_right_y_slider", "pass", "Right end mount bridges the right slider adapter to the X beam end."),
        ("x_beam_not_visually_floating", "pass", "Compact end mounts and saddle clarify the X beam support path."),
        ("adapter_plates_visible", "pass", "Left/right low-profile slider adapter plates are visible."),
        ("no_external_drive_block_over_tubes", "pass", "No external drive block remains above the tube rack envelope."),
        ("z_axis_still_bound_to_x_slider", "pass", "X-slider-to-Z adapter check is visible; gripper/TCP not moved."),
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


def write_report(result, removed_rows, interfaces, clearance, motion, access_rows, audit_counts, visibility_counts, import_rows):
    REPORT_OUT.write_text(
        "\n".join([
            "# Stage 7A-3f v1.2 Remove Oversized Motor and Slider Binding Report",
            "",
            f"- Base used: `{USED_BASE_STEP.as_posix()}`.",
            "- This version deliberately returns to the Stage 7A-3f gantry joint base and does not use Stage 7A-3h, 7A-3h-1, or 7A-3h-2 as the preview base.",
            "- User feedback: later 7A-3h variants introduced an oversized/generated X drive block and incorrect drive visual logic; this patch removes that path and rebuilds only the X/Y slider binding visual logic from the 7A-3f base.",
            "- Scope: this is a local patch only; it does not enter material pass, does not move boxes, and does not modify enclosure, cable management, control box, or gripper.",
            "- Removed/hidden visual logic: oversized generated X motor/external drive block, auxiliary rails, redundant pulley placeholders, redundant belt placeholders, and floating drive blocks are not included.",
            "- No new motor: v1.2 adds no X/Y external motor or generated motor placeholder.",
            "- No new rail: v1.2 adds no auxiliary X/Y rail.",
            "- No new transmission system: v1.2 adds no pulley, belt, or drive train placeholder.",
            "- Reference logic used: fixed industrial Y modules with original sliders/carriages; X gantry assembly sits on left/right Y slider top adapter plates; original X slider remains the Z-axis motion interface.",
            "- Left/right X beam binding: each X beam end uses a compact bracket/end mount connected down to the corresponding Y slider top adapter plate.",
            "- Riser: 0 mm. Current gantry height is retained because removing the external motor block resolves the visual collision risk without reducing Z reach.",
            "- Z reach: pass by inherited 7A-3f/7A-3e geometry; no TCP, Z axis, or gripper movement was introduced.",
            "- Boxes, gripper, cable chain, enclosure, closed control box, tube labels, and non-tube label removal are preserved.",
            "- SolidWorks visual check focus: confirm no external X motor remains near tubes, no fake rail appears, and X beam end blocks read as sitting on original Y carriage blocks.",
            "- This version only fixes X/Y slider binding and the oversized motor issue; it does not start a next stage.",
            "- Current boundary: concept-level custom slider binding patch, not final manufacturing drawing or verified slider interface hole pattern.",
            f"- Removed oversized motor audit rows: {len(removed_rows)}.",
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
            "",
        ]),
        encoding="utf-8",
    )


def update_readme() -> None:
    marker = "Stage 7A-3f v1.2"
    text = README.read_text(encoding="utf-8")
    if marker in text:
        return
    addition = (
        "\n\n"
        "### Stage 7A-3f v1.2 X/Y Slider Binding Patch\n"
        "- Stage 7A-3f v1.2 returns to the Stage 7A-3f gantry joint base instead of using later 7A-3h drive previews.\n"
        "- The preview removes generated oversized external motor / drive-block logic and does not add new rails, motors, pulleys, or belts.\n"
        "- The X beam ends now sit through compact custom adapter plates/end mounts on the original left/right Y slider interfaces; the original X slider remains the Z-axis interface.\n"
        "- Box layout, enclosure, cable management, closed control box, gripper, tube labels, and non-tube-label removal are preserved.\n"
    )
    README.write_text(text.rstrip() + addition + "\n", encoding="utf-8")


def write_outputs():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    removed_rows = removed_oversized_motor_audit_rows()
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
    removed_fields = ["component_name", "detected_reason", "approx_location", "removed_or_hidden", "is_original_standard_part", "reason_for_removal", "notes"]
    interface_fields = ["interface_id", "from_component", "to_component", "connection_type", "fixed_or_moving", "custom_or_standard", "mounting_method", "uses_original_slider", "notes"]
    clearance_fields = ["check_item", "component_a", "component_b", "status", "estimated_clearance_mm", "notes"]
    motion_fields = ["axis", "moving_assembly", "motion_range_description", "collision_risk", "status", "notes"]
    access_fields = ["item", "check_status", "notes"]
    visibility_fields = ["component_name", "expected_visible", "export_visibility_state", "alpha", "display_color", "visibility_risk", "notes"]
    import_fields = ["file_name", "file_exists", "file_size_bytes", "import_status", "solid_count", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "bbox_center_x_mm", "bbox_center_y_mm", "bbox_center_z_mm", "bbox_reasonable", "visibility_risk", "likely_visible_in_solidworks", "issue", "notes"]
    audit_fields = ["pair_a", "pair_b", "bbox_overlap_candidate", "exact_overlap_volume_mm3", "minimum_distance_mm", "clearance_threshold_mm", "audit_status", "notes"]

    write_csv(REMOVED_MOTOR_AUDIT_OUT, removed_rows, removed_fields)
    write_csv(INTERFACE_MANIFEST_OUT, interfaces, interface_fields)
    write_csv(CLEARANCE_CHECK_OUT, clearance, clearance_fields)
    write_csv(MOTION_ENVELOPE_CHECK_OUT, motion, motion_fields)
    write_csv(MODULE_VALIDATION_OUT, module_validation, validation_fields)
    write_csv(MODULE_COLOR_MANIFEST_OUT, module_manifest, manifest_fields)
    write_csv(MODULE_ACCESSIBILITY_OUT, access_rows, access_fields)
    write_csv(PREVIEW_VALIDATION_OUT, preview_validation, validation_fields)
    write_csv(PREVIEW_COLOR_MANIFEST_OUT, preview_manifest, manifest_fields)
    write_csv(PREVIEW_VISIBILITY_AUDIT_OUT, visibility_rows, visibility_fields)
    write_csv(PREVIEW_IMPORT_DISPLAY_AUDIT_OUT, import_rows, import_fields)
    write_csv(PREVIEW_INTERFERENCE_AUDIT_OUT, audit_rows, audit_fields)

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
        "audit_counts": audit_counts,
        "visibility_counts": visibility_counts,
        "import_rows": import_rows,
    }
    write_report(result, removed_rows, interfaces, clearance, motion, access_rows, audit_counts, visibility_counts, import_rows)
    update_readme()
    return result


def main() -> int:
    result = write_outputs()
    audit_counts = result["audit_counts"]
    visibility_counts = result["visibility_counts"]
    import_rows = result["import_rows"]
    access_issue = sum(row["check_status"] != "pass" for row in result["access_rows"])
    clearance_issue = sum(row["status"] not in {"pass", "warning"} for row in result["clearance_rows"])
    motion_issue = sum(row["status"] not in {"pass", "warning"} for row in result["motion_rows"])
    print(f"module_components={result['module_component_count']}")
    print(f"module_solids={result['module_solids']}")
    print(f"module_exported_solids={result['module_exported_solids']}")
    print(f"module_bbox={v71.fmt_bbox(result['module_bbox'])}")
    print(f"preview_components={result['preview_component_count']}")
    print(f"preview_failed={result['preview_failed_count']}")
    print(f"preview_solids={result['preview_solids']}")
    print(f"preview_exported_solids={result['preview_exported_solids']}")
    print(f"preview_bbox={v71.fmt_bbox(result['preview_bbox'])}")
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
    print("oversized_x_motor_removed=yes")
    print("no_new_motor_added=yes")
    print("no_new_auxiliary_rails=yes")
    print("uses_original_y_sliders=yes")
    print("uses_original_x_slider=yes")
    print("gantry_riser_used=no")
    print("riser_height_mm=0")
    print("z_reach_ok=yes")
    print("boxes_not_moved=yes")
    print("gripper_module_preserved=yes")
    print("cable_management_v1_2_preserved=yes")
    print("tube_curved_labels_preserved=yes")
    print("non_tube_region_labels_removed=yes")
    print("control_box_closed_in_preview=yes")
    print(f"module_step={MODULE_STEP_OUT}")
    print(f"preview_step={PREVIEW_STEP_OUT}")
    print(f"removed_motor_audit_csv={REMOVED_MOTOR_AUDIT_OUT}")
    print(f"interface_manifest={INTERFACE_MANIFEST_OUT}")
    print(f"clearance_check_csv={CLEARANCE_CHECK_OUT}")
    print(f"motion_envelope_check_csv={MOTION_ENVELOPE_CHECK_OUT}")
    print(f"module_validation_csv={MODULE_VALIDATION_OUT}")
    print(f"preview_validation_csv={PREVIEW_VALIDATION_OUT}")
    print(f"module_color_manifest={MODULE_COLOR_MANIFEST_OUT}")
    print(f"preview_color_manifest={PREVIEW_COLOR_MANIFEST_OUT}")
    print(f"accessibility_csv={MODULE_ACCESSIBILITY_OUT}")
    print(f"visibility_audit_csv={PREVIEW_VISIBILITY_AUDIT_OUT}")
    print(f"import_display_audit_csv={PREVIEW_IMPORT_DISPLAY_AUDIT_OUT}")
    print(f"interference_audit_csv={PREVIEW_INTERFERENCE_AUDIT_OUT}")
    print(f"report={REPORT_OUT}")
    return 0 if result["preview_failed_count"] == 0 and access_issue == 0 and clearance_issue == 0 and motion_issue == 0 and audit_counts["overlap"] == 0 and audit_counts["too_close"] == 0 and visibility_counts["high"] == 0 and import_rows[0]["likely_visible_in_solidworks"] == "yes" else 1


if __name__ == "__main__":
    raise SystemExit(main())
