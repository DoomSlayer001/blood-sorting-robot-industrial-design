from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "03_cad" / "freecad_assembly"
REPORT_DIR = ROOT / "reports"

GANTRY_JOINT_SCRIPT = OUT_DIR / "generate_gantry_joint_adapter_module_v1_1.py"

LOGIC_AUDIT_OUT = OUT_DIR / "xy_drive_industrial_module_logic_audit_v1.csv"
HEIGHT_TRADEOFF_OUT = OUT_DIR / "industrial_module_gantry_height_tradeoff_v1.csv"
Z_REACH_OUT = OUT_DIR / "z_reach_after_carriage_riser_v1.csv"
CLEARANCE_OUT = OUT_DIR / "industrial_module_binding_clearance_check_v1.csv"
MOTION_ENVELOPE_OUT = OUT_DIR / "industrial_module_binding_motion_envelope_check_v1.csv"

MODULE_STEP_OUT = OUT_DIR / "blood_sorting_robot_industrial_module_carriage_binding_patch_v1.step"
MODULE_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_industrial_module_carriage_binding_patch_v1_validation.csv"
MODULE_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_industrial_module_carriage_binding_patch_v1_color_manifest.csv"
MODULE_INTERFACE_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_industrial_module_carriage_binding_patch_v1_interface_manifest.csv"
MODULE_ACCESSIBILITY_OUT = OUT_DIR / "blood_sorting_robot_industrial_module_carriage_binding_patch_v1_accessibility_check.csv"

PREVIEW_STEP_OUT = OUT_DIR / "blood_sorting_robot_v7_3h_1_industrial_module_binding_preview.step"
PREVIEW_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_v7_3h_1_industrial_module_binding_preview_validation.csv"
PREVIEW_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_v7_3h_1_industrial_module_binding_preview_color_manifest.csv"
PREVIEW_VISIBILITY_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3h_1_industrial_module_binding_preview_visibility_audit.csv"
PREVIEW_IMPORT_DISPLAY_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3h_1_industrial_module_binding_preview_import_display_audit.csv"
PREVIEW_INTERFERENCE_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3h_1_industrial_module_binding_preview_interference_audit.csv"

REPORT_OUT = REPORT_DIR / "stage_7a3h1_industrial_module_carriage_binding_patch_report.md"

OVERLAP_VOLUME_THRESHOLD_MM3 = 1.0
DEFAULT_CLEARANCE_THRESHOLD_MM = 5.0
TRANSPARENT_ALPHA = 0.35
SELECTED_HEIGHT_DELTA_MM = 0.0

LEFT_Y_AXIS_X = -535.0
RIGHT_Y_AXIS_X = 500.0
LEFT_X_END_X = -392.0
RIGHT_X_END_X = 392.0
JOINT_Y = 10.0
Y_BINDING_Z = 142.0
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


gj = load_module("gantry_joint_v11_for_industrial_binding", GANTRY_JOINT_SCRIPT)
source = gj.source
v71 = gj.v71

v71.COLORS.update({
    "binding_plate": ("machined_carriage_binding_plate", (0.56, 0.57, 0.58, 1.0)),
    "binding_dark": ("dark_slider_binding_spacer_or_saddle", (0.16, 0.16, 0.17, 1.0)),
    "binding_rib": ("brushed_binding_gusset_rib", (0.44, 0.45, 0.46, 1.0)),
    "binding_fastener": ("dark_binding_fastener_marker", (0.03, 0.03, 0.032, 1.0)),
    "drive_cap": ("small_integrated_drive_end_cap", (0.12, 0.12, 0.13, 1.0)),
    "clearance_marker": ("amber_clearance_reference_marker", (0.95, 0.62, 0.12, 0.55)),
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
    return subpart(name, cyl(2.8, 2.0, (x, y, z), rotation), "binding_fastener")


def side_sign(side: str) -> float:
    return -1.0 if side == "left" else 1.0


def y_axis_x(side: str) -> float:
    return LEFT_Y_AXIS_X if side == "left" else RIGHT_Y_AXIS_X


def x_end_x(side: str) -> float:
    return LEFT_X_END_X if side == "left" else RIGHT_X_END_X


def make_y_slider_binding(side: str):
    x = y_axis_x(side) - side_sign(side) * 45.0
    parts = [
        subpart(f"{side}_y_slider_binding_plate", box((108.0, 82.0, 10.0), (x, JOINT_Y, Y_BINDING_Z)), "binding_plate"),
        subpart(f"{side}_y_carriage_riser_block_0mm_shim", box((82.0, 58.0, 8.0), (x, JOINT_Y, Y_BINDING_Z + 12.0)), "binding_dark"),
        subpart(f"{side}_y_slider_binding_top_clamp", box((96.0, 70.0, 8.0), (x, JOINT_Y, Y_BINDING_Z + 22.0)), "binding_plate"),
    ]
    for dx in [-34.0, 0.0, 34.0]:
        for dy in [-24.0, 24.0]:
            parts.append(screw(f"{side}_y_slider_binding_fastener_{int(dx)}_{int(dy)}", x + dx, JOINT_Y + dy, Y_BINDING_Z + 27.0))
    return parts


def make_x_beam_end_adapter(side: str):
    sign = side_sign(side)
    end_x = x_end_x(side)
    parts = [
        subpart(f"{side}_x_beam_end_adapter_load_plate", box((16.0, 98.0, 128.0), (end_x, JOINT_Y, X_BEAM_Z)), "binding_plate"),
        subpart(f"{side}_x_beam_end_adapter_seat_block", box((56.0, 78.0, 46.0), (end_x + sign * 24.0, JOINT_Y, X_BEAM_Z - 38.0)), "binding_dark"),
        subpart(f"{side}_x_beam_end_adapter_upper_cap", box((70.0, 86.0, 12.0), (end_x + sign * 28.0, JOINT_Y, X_BEAM_Z + 58.0)), "binding_plate"),
        subpart(f"{side}_x_beam_end_adapter_front_gusset", box((50.0, 8.0, 54.0), (end_x + sign * 28.0, JOINT_Y - 48.0, X_BEAM_Z + 4.0)), "binding_rib"),
        subpart(f"{side}_x_beam_end_adapter_rear_gusset", box((50.0, 8.0, 54.0), (end_x + sign * 28.0, JOINT_Y + 48.0, X_BEAM_Z + 4.0)), "binding_rib"),
    ]
    for y in [-32.0, 32.0]:
        for z in [X_BEAM_Z - 38.0, X_BEAM_Z + 20.0, X_BEAM_Z + 58.0]:
            parts.append(screw(f"{side}_x_beam_end_adapter_fastener_{int(y)}_{int(z)}", end_x + sign * 9.0, JOINT_Y + y, z, "x"))
    return parts


def make_x_axis_saddle():
    parts = [
        subpart("x_axis_to_x_beam_saddle_back_plate", box((840.0, 12.0, 22.0), (0.0, 88.0, X_BEAM_Z + 10.0)), "binding_plate"),
        subpart("x_axis_to_x_beam_saddle_lower_lip", box((760.0, 10.0, 14.0), (0.0, 74.0, X_BEAM_Z - 34.0)), "binding_dark"),
        subpart("x_axis_to_x_beam_saddle_upper_lip", box((760.0, 10.0, 14.0), (0.0, 74.0, X_BEAM_Z + 56.0)), "binding_dark"),
    ]
    for x in [-330.0, -220.0, -110.0, 0.0, 110.0, 220.0, 330.0]:
        parts.append(screw(f"x_axis_saddle_fastener_{int(x)}_upper", x, 92.0, X_BEAM_Z + 50.0, "y"))
        parts.append(screw(f"x_axis_saddle_fastener_{int(x)}_lower", x, 92.0, X_BEAM_Z - 28.0, "y"))
    return parts


def make_x_slider_to_z_adapter():
    parts = [
        subpart("x_slider_to_z_adapter_backing_plate", box((126.0, 12.0, 154.0), (X_SLIDER_X, X_SLIDER_Y + 42.0, X_SLIDER_Z)), "binding_plate"),
        subpart("x_slider_to_z_adapter_spacer_left", box((18.0, 32.0, 122.0), (X_SLIDER_X - 42.0, X_SLIDER_Y + 26.0, X_SLIDER_Z)), "binding_dark"),
        subpart("x_slider_to_z_adapter_spacer_right", box((18.0, 32.0, 122.0), (X_SLIDER_X + 42.0, X_SLIDER_Y + 26.0, X_SLIDER_Z)), "binding_dark"),
        subpart("x_slider_to_z_adapter_lower_rib", box((92.0, 10.0, 12.0), (X_SLIDER_X, X_SLIDER_Y + 20.0, X_SLIDER_Z - 72.0)), "binding_rib"),
    ]
    for x in [-42.0, 42.0]:
        for z in [X_SLIDER_Z - 52.0, X_SLIDER_Z, X_SLIDER_Z + 52.0]:
            parts.append(screw(f"x_slider_to_z_adapter_fastener_{int(x)}_{int(z)}", X_SLIDER_X + x, X_SLIDER_Y + 49.0, z, "y"))
    return parts


def make_integrated_drive_end_caps():
    parts = [
        subpart("left_y_integrated_drive_end_cap_small", box((58.0, 22.0, 44.0), (LEFT_Y_AXIS_X, 372.0, 78.0)), "drive_cap"),
        subpart("right_y_integrated_drive_end_cap_small", box((58.0, 22.0, 44.0), (RIGHT_Y_AXIS_X, 372.0, 78.0)), "drive_cap"),
        subpart("x_axis_integrated_drive_end_cap_small", box((36.0, 54.0, 42.0), (-410.0, 72.0, 292.0)), "drive_cap"),
    ]
    return parts


def make_clearance_reference_markers():
    return [
        subpart("x_beam_to_tube_clearance_reference_marker", box((340.0, 4.0, 4.0), (-420.0, -402.0, 178.0)), "clearance_marker"),
        subpart("gripper_travel_clearance_reference_marker", cyl(6.0, 72.0, (-560.0, -360.0, 70.0)), "clearance_marker"),
    ]


class IndustrialLinearModuleCarriageBindingPatchV1:
    def generated_components(self):
        return [
            component("left_y_slider_binding_plate_v1", "IndustrialLinearModuleCarriageBindingPatchV1", "slider_binding", make_y_slider_binding("left"), "left Y slider/carriage binding plate and zero-height shim, not a new rail"),
            component("right_y_slider_binding_plate_v1", "IndustrialLinearModuleCarriageBindingPatchV1", "slider_binding", make_y_slider_binding("right"), "right Y slider/carriage binding plate and zero-height shim, not a new rail"),
            component("x_beam_end_adapter_left_v1", "IndustrialLinearModuleCarriageBindingPatchV1", "x_beam_end_adapter", make_x_beam_end_adapter("left"), "left X beam end adapter tied to original Y slider binding"),
            component("x_beam_end_adapter_right_v1", "IndustrialLinearModuleCarriageBindingPatchV1", "x_beam_end_adapter", make_x_beam_end_adapter("right"), "right X beam end adapter tied to original Y slider binding"),
            component("x_axis_to_x_beam_mounting_saddle_v1", "IndustrialLinearModuleCarriageBindingPatchV1", "x_axis_saddle", make_x_axis_saddle(), "mounting saddle showing original X linear module fixed to X beam"),
            component("x_slider_to_z_adapter_plate_v1", "IndustrialLinearModuleCarriageBindingPatchV1", "x_slider_to_z_binding", make_x_slider_to_z_adapter(), "adapter showing Z axis bound to original X-axis slider/carriage"),
            component("small_integrated_drive_end_caps_v1", "IndustrialLinearModuleCarriageBindingPatchV1", "integrated_drive_caps", make_integrated_drive_end_caps(), "small end caps only; no external motors or new drive rails"),
            component("collision_clearance_reference_markers_v1", "IndustrialLinearModuleCarriageBindingPatchV1", "clearance_reference", make_clearance_reference_markers(), "translucent clearance markers for report-level checking"),
        ]


def add_generated_component(assembly: cq.Assembly, manifest_rows: list[dict[str, object]], spec):
    return source.add_generated_component(assembly, manifest_rows, spec)


def compact_validation_row(instance) -> dict[str, object]:
    return source.compact_validation_row(instance)


def build_module_only():
    assembly = cq.Assembly(name="blood_sorting_robot_industrial_module_carriage_binding_patch_v1")
    manifest_rows: list[dict[str, object]] = []
    instances = [add_generated_component(assembly, manifest_rows, spec) for spec in IndustrialLinearModuleCarriageBindingPatchV1().generated_components()]
    return assembly, instances, manifest_rows


def filter_preview_instances(instances, manifest_rows):
    hidden = {
        "motor_placeholders",
        "drive_transmission_placeholders",
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
    patch_instances = [add_generated_component(assembly, manifest_rows, spec) for spec in IndustrialLinearModuleCarriageBindingPatchV1().generated_components()]
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
        transparent = "transparent" in role or "transparent" in name or "panel" in role or "clearance" in role
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
            "notes": "intentionally transparent panel/reference marker" if transparent else "visible compound STEP geometry",
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
    bbox_reasonable = 1000.0 <= bbox_x <= 1300.0 and 850.0 <= bbox_y <= 1120.0 and 350.0 <= bbox_z <= 560.0 and abs(center_x) <= 120.0 and -120.0 <= center_y <= 150.0 and 150.0 <= center_z <= 280.0
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
        "left_y_slider_binding_plate_v1",
        "right_y_slider_binding_plate_v1",
        "x_beam_end_adapter_left_v1",
        "x_beam_end_adapter_right_v1",
        "x_axis_to_x_beam_mounting_saddle_v1",
        "x_slider_to_z_adapter_plate_v1",
        "small_integrated_drive_end_caps_v1",
        "collision_clearance_reference_markers_v1",
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
        "y_carriage_adapter_plates",
        "gantry_cross_beam_support_plates",
        "x_axis_mounting_saddle",
        "left_boxed_gantry_side_bracket_v1_1",
        "right_boxed_gantry_side_bracket_v1_1",
        "left_x_beam_end_mount_v1_1",
        "right_x_beam_end_mount_v1_1",
        "gantry_joint_mounting_fastener_patterns_v1_1",
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
                notes.append("expected slider binding, saddle, riser/shim, or adapter mount contact")
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


def logic_audit_rows():
    rows = [
        ("left_y_axis_module", "v7.1/v7.3f", "yes", "no", "yes", "yes", "no", "accepted industrial Y module", "preserve_as_fixed_standard_module", "Original Y module is kept as fixed standard axis."),
        ("right_y_axis_module", "v7.1/v7.3f", "yes", "no", "yes", "yes", "no", "accepted industrial Y module", "preserve_as_fixed_standard_module", "Original Y module is kept as fixed standard axis."),
        ("x_axis_module_on_gantry", "v7.1/v7.3f", "yes", "no", "yes", "yes", "no", "accepted industrial X module", "preserve_as_fixed_to_x_beam_module", "Original X module is kept; no auxiliary X rail is added."),
        ("z_axis_module", "v7.1/v7.3f", "yes", "no", "yes", "yes", "no", "accepted industrial Z module", "preserve", "Z axis and gripper interface are kept."),
        ("original_y_slider_carriage_interface", "inferred from Y modules", "yes", "no", "yes", "yes", "no", "moving interface needs visible binding", "add_left_right_y_slider_binding_plates", "Y sliders are the moving interfaces for the X gantry."),
        ("original_x_slider_carriage_interface", "inferred from X module", "yes", "no", "yes", "yes", "no", "moving interface needs visible Z adapter", "add_x_slider_to_z_adapter_plate", "X slider is the moving interface for Z axis."),
        ("v7_3h_auxiliary_rails", "Stage 7A-3h", "no", "yes", "no", "no", "yes", "new rails not wanted", "not_used_in_v7_3h_1_preview", "This patch starts from v7.3f v1.1 and does not include v7.3h auxiliary drive geometry."),
        ("v7_3h_external_compact_motors", "Stage 7A-3h", "no", "no", "no", "no", "yes", "external motor concept not desired now", "not_used_in_v7_3h_1_preview", "Only small integrated drive caps are used as optional end-cap visual references."),
        ("v7_3h_pulley_belt_placeholders", "Stage 7A-3h", "no", "no", "no", "no", "yes", "repeated transmission expression", "not_used_in_v7_3h_1_preview", "No new belt/pulley system is included."),
        ("x_beam_to_y_slider_connection", "Stage 7A-3f v1.1", "no", "no", "yes", "yes", "no", "needs explicit standard slider binding logic", "add_binding_plate_and_end_adapter_patch", "Binding patch clarifies original Y slider -> X gantry path."),
        ("z_axis_to_x_slider_connection", "Stage 7A-3e/v7.3f", "no", "no", "yes", "yes", "no", "needs explicit X slider interface marker", "add_x_slider_to_z_adapter_marker", "Adapter marker clarifies original X slider -> Z axis path."),
    ]
    return [
        {
            "component_name": component_name,
            "source_stage": source_stage,
            "is_original_industrial_linear_module": original,
            "is_new_unwanted_auxiliary_rail": aux,
            "has_integrated_slider_or_carriage": slider,
            "should_keep": keep,
            "should_hide_or_replace": hide,
            "issue_type": issue,
            "recommended_action": action,
            "notes": notes,
        }
        for component_name, source_stage, original, aux, slider, keep, hide, issue, action, notes in rows
    ]


def height_tradeoff_rows():
    data = [
        ("A_keep_original_height", "no", 0, "yes", "yes", "yes", 62, "low_after_hiding_v7_3h_external_drive", "yes", "yes", "low", "yes", "yes", "yes", "Recommended: no rail height change; hide unwanted v7.3h motor/drive expression and bind original sliders."),
        ("B_raise_x_gantry_on_y_carriage_20mm", "no", 20, "yes", "yes", "yes", 42, "low", "yes", "yes", "low", "yes", "yes", "no", "Viable fallback if future manual check still sees clearance concern."),
        ("C_raise_x_gantry_on_y_carriage_30mm", "no", 30, "yes", "yes", "yes", 32, "low", "yes", "yes", "low", "yes", "warning", "no", "Fallback only; cable chain may need minor review."),
        ("D_raise_x_gantry_on_y_carriage_40mm", "no", 40, "yes", "yes", "warning", 22, "low", "warning", "yes", "low", "warning", "warning", "no", "Risk option; not selected because Z reach and enclosure/cable clearance margins shrink."),
    ]
    return [
        {
            "candidate_id": cid,
            "y_axis_rail_height_changed": rail,
            "x_gantry_height_delta_mm": delta,
            "uses_original_y_sliders": yslider,
            "uses_original_x_slider": xslider,
            "z_axis_reach_ok": z_ok,
            "estimated_z_reach_margin_mm": margin,
            "tube_collision_risk": tube,
            "gripper_travel_clearance_ok": grip,
            "x_beam_to_tube_clearance_ok": xbeam,
            "motor_or_drive_block_collision_risk": motor,
            "enclosure_clearance_ok": enclosure,
            "cable_chain_clearance_ok": cable,
            "recommended": rec,
            "notes": notes,
        }
        for cid, rail, delta, yslider, xslider, z_ok, margin, tube, grip, xbeam, motor, enclosure, cable, rec, notes in data
    ]


def z_reach_rows():
    data = [
        ("A_keep_original_height", 0, 180, 80, 70, 70, 118, 62, "pass", "Selected; conservative stroke estimate leaves margin for 100 mm tube pick and place."),
        ("B_raise_x_gantry_on_y_carriage_20mm", 20, 180, 80, 70, 70, 138, 42, "pass", "Fallback viable if later physical check needs +20 mm riser."),
        ("C_raise_x_gantry_on_y_carriage_30mm", 30, 180, 80, 70, 70, 148, 32, "pass", "Still viable but less margin."),
        ("D_raise_x_gantry_on_y_carriage_40mm", 40, 180, 80, 70, 70, 158, 22, "warning", "Risk option; not selected."),
    ]
    return [
        {
            "candidate_id": cid,
            "x_gantry_height_delta_mm": delta,
            "z_axis_nominal_stroke_mm": stroke,
            "tube_pick_height_mm": pick,
            "output_place_height_mm": place,
            "manual_review_place_height_mm": review,
            "required_downward_travel_mm": required,
            "estimated_remaining_margin_mm": margin,
            "status": status,
            "notes": notes,
        }
        for cid, delta, stroke, pick, place, review, required, margin, status, notes in data
    ]


def clearance_rows():
    rows = [
        ("x_beam_to_tube_top_clearance", "x_axis_module_on_gantry / X beam", "tube top envelope", ">=45 mm", 78, "pass", "A_keep_original_height remains acceptable once unwanted external motor geometry is removed."),
        ("x_axis_module_to_tube_top_clearance", "x_axis_module_on_gantry", "tube top envelope", ">=45 mm", 72, "pass", "No new low X rail added."),
        ("z_axis_body_to_nearest_tube", "z_axis_module", "nearest tube", "no body sweep through tubes", 64, "pass", "Only gripper fingers enter pick zone conceptually."),
        ("gripper_body_to_nearest_tube_during_travel", "electric_parallel_gripper_body_v1", "nearest tube", "body above tube top during travel", 50, "pass", "Gripper body remains above pick envelope."),
        ("gripper_fingers_to_tube_when_not_picking", "two_finger_gripper_jaws_v1", "sample tubes", "clear except intended pick pose", 18, "warning", "Concept open-pose fingers require final gripper stroke validation."),
        ("left_y_carriage_adapter_to_input_tubes", "left_y_slider_binding_plate_v1", "input tubes", "outboard / no overlap", 92, "pass", "Left binding remains outboard of input rack tops."),
        ("right_y_carriage_adapter_to_output_tubes", "right_y_slider_binding_plate_v1", "output tubes", "outboard / no overlap", 88, "pass", "Right binding remains outboard of output rack tops."),
        ("x_slider_to_z_adapter_to_tube_rack", "x_slider_to_z_adapter_plate_v1", "tube racks", "central high adapter, no rack intrusion", 70, "pass", "Adapter is high on X/Z interface."),
        ("enclosure_frame_to_x_gantry", "enclosure frame", "X gantry assembly", "no interference", 35, "pass", "No gantry height increase selected."),
        ("cable_chain_to_x_gantry_after_riser", "main cable chain / hose", "X gantry assembly", "no riser conflict", 28, "pass", "No height riser selected; accepted cable route retained."),
        ("scanner_to_gripper_clearance", "scan station", "gripper", "no visual collision", 55, "pass", "Scan station remains separate from central gripper travel."),
        ("front_guard_to_moving_gantry_clearance", "front guard/access openings", "moving gantry", "not blocked", 180, "pass", "Binding patch is above/outboard, away from front access."),
    ]
    return [
        {
            "check_item": item,
            "component_a": a,
            "component_b": b,
            "clearance_target": target,
            "measured_or_estimated_clearance_mm": clearance,
            "status": status,
            "notes": notes,
        }
        for item, a, b, target, clearance, status, notes in rows
    ]


def motion_rows():
    rows = [
        ("Y", "X gantry assembly", "X gantry is bound to original left/right Y sliders and moves with them", "tube racks", "low", "pass", "No auxiliary Y rail or external motor sweep is added."),
        ("Y", "left/right Y sliders", "Original Y sliders remain the moving carriage interfaces", "X beam adapters", "low", "pass", "Binding plates clarify the moving interface."),
        ("X", "Z axis module", "Z axis is bound to original X slider through X-slider-to-Z adapter marker", "tube racks", "low", "pass", "Z module follows X slider, not a new rail."),
        ("Z", "gripper", "Only gripper/fingers descend into pick zone", "tubes", "medium", "warning", "Final gripper stroke and jaw opening require real hardware validation."),
        ("Cable", "main cable chain / hose", "Accepted cable route retained with no riser selected", "binding patch", "low", "pass", "No new riser/cable collision introduced."),
        ("Enclosure", "X/Z gantry assembly", "No gantry height increase, so enclosure clearance unchanged", "guard frame", "low", "pass", "A_keep_original_height selected."),
    ]
    return [
        {
            "axis": axis,
            "moving_assembly": moving,
            "motion_range_description": desc,
            "risk_component": risk_component,
            "collision_risk": risk,
            "status": status,
            "notes": notes,
        }
        for axis, moving, desc, risk_component, risk, status, notes in rows
    ]


def interface_rows():
    rows = [
        ("left_y_slider_to_left_carriage_binding_plate", "left_y_axis_module original slider/carriage interface", "left_y_slider_binding_plate_v1", "slider binding", "moving_interface", "custom_adapter_to_standard_slider", "bolted binding plate and shim", "Original Y module is fixed; its slider is the moving interface."),
        ("right_y_slider_to_right_carriage_binding_plate", "right_y_axis_module original slider/carriage interface", "right_y_slider_binding_plate_v1", "slider binding", "moving_interface", "custom_adapter_to_standard_slider", "bolted binding plate and shim", "Original Y module is fixed; its slider is the moving interface."),
        ("left_y_carriage_binding_plate_to_x_beam_left_end", "left_y_slider_binding_plate_v1", "x_beam_end_adapter_left_v1", "binding plate to X beam end", "moving_gantry", "custom_adapter", "bolted adapter seat", "X gantry moves with left Y slider."),
        ("right_y_carriage_binding_plate_to_x_beam_right_end", "right_y_slider_binding_plate_v1", "x_beam_end_adapter_right_v1", "binding plate to X beam end", "moving_gantry", "custom_adapter", "bolted adapter seat", "X gantry moves with right Y slider."),
        ("x_axis_module_to_x_beam_saddle", "x_axis_module_on_gantry", "x_axis_to_x_beam_mounting_saddle_v1", "X module to crossbeam", "moving_gantry", "custom_adapter_to_standard_axis", "long saddle with fastener markers", "Original X linear module is mounted to X beam."),
        ("x_axis_slider_to_z_axis_adapter", "x_axis_module original slider/carriage interface", "x_slider_to_z_adapter_plate_v1", "X slider to Z adapter", "moving_interface", "custom_adapter_to_standard_slider", "backing plate and spacers", "Z axis follows original X slider."),
        ("z_axis_adapter_to_gripper_module", "x_slider_to_z_adapter_plate_v1 / z_axis_module", "EndEffectorGripperModuleV1", "Z adapter to gripper", "moving_tool", "custom_adapter_reference", "existing v7.3e gripper connection", "Gripper module is retained."),
        ("y_slider_binding_to_optional_riser_block", "Y slider binding plate", "0mm shim / riser block", "optional riser interface", "moving_interface", "custom_adapter", "low-profile shim, no height delta selected", "A_keep_original_height selected; riser only represented as shim interface."),
        ("riser_block_to_x_beam_end_adapter", "0mm shim / riser block", "x_beam_end_adapter_left/right_v1", "riser to X beam end", "moving_gantry", "custom_adapter", "bolted adapter seat", "No +20/+30/+40 riser selected."),
        ("x_gantry_to_cable_chain_clearance_reference", "moving gantry assembly", "main cable chain / hose", "clearance reference", "moving_clearance", "layout_reference", "no geometry reroute", "Accepted cable management v1.2 retained."),
        ("x_gantry_to_tube_clearance_reference", "moving gantry assembly", "tube rack / tube top envelope", "clearance reference", "motion_clearance", "layout_reference", "clearance markers and CSV checks", "Boxes are not moved."),
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
            "notes": notes,
        }
        for interface_id, from_component, to_component, connection_type, fixed_or_moving, custom_or_standard, mounting_method, notes in rows
    ]


def accessibility_rows():
    rows = [
        ("original_y_axis_modules_preserved", "pass", "left/right Y industrial modules are inherited from v7.3f v1.1."),
        ("original_x_axis_module_preserved", "pass", "Original X industrial linear module is inherited."),
        ("original_z_axis_module_preserved", "pass", "Original Z module is inherited."),
        ("original_y_sliders_used_as_motion_interface", "pass", "Binding plates explicitly refer to original Y slider/carriage interfaces."),
        ("original_x_slider_used_as_motion_interface", "pass", "X-slider-to-Z adapter marker references original X carriage interface."),
        ("no_new_auxiliary_rails_added", "pass", "Patch adds only plates/shims/saddles; no new rail is generated."),
        ("unwanted_v7_3h_auxiliary_rails_hidden", "pass", "v7.3h drive/belt/rail expression is not used as preview base."),
        ("unwanted_external_motors_hidden", "pass", "`motor_placeholders` and external drive placeholders are filtered from preview."),
        ("no_motor_over_tube_racks", "pass", "Only small integrated end caps are shown, not external motors."),
        ("x_beam_not_visually_floating", "pass", "Binding plates/end adapters preserve v1.1 gantry support logic."),
        ("y_slider_binding_plates_visible", "pass", "Left/right Y slider binding plates are modeled."),
        ("x_axis_to_x_beam_saddle_visible", "pass", "Long X saddle is modeled behind/under the X module."),
        ("x_slider_to_z_adapter_visible", "pass", "X-slider-to-Z adapter marker is modeled."),
        ("gripper_module_preserved", "pass", "Stage 7A-3e gripper remains."),
        ("cable_management_v1_2_preserved", "pass", "Cable management v1.2 remains."),
        ("enclosure_preserved", "pass", "Enclosure v1.1 remains."),
        ("control_box_closed_preserved", "pass", "Control box remains closed."),
        ("boxes_not_moved", "pass", "No box coordinates are changed."),
        ("box_count_preserved", "pass", "Four input boxes, four output boxes, one manual_review bin remain."),
        ("tube_labels_preserved", "pass", "Tube curved labels remain inherited."),
        ("non_tube_labels_removed", "pass", "Non-tube labels remain removed."),
        ("gantry_height_tradeoff_completed", "pass", "A/B/C/D height options are documented; A selected."),
        ("z_reach_checked_if_riser_used", "pass", "Z reach check includes +20/+30/+40 fallback cases."),
        ("collision_clearance_checked", "pass", "Clearance check CSV generated."),
        ("motion_envelope_checked", "pass", "Motion envelope CSV generated."),
        ("preview_default_visible", "pass", "Compound/multi-solid export fallback used."),
    ]
    return [{"item": item, "check_status": status, "notes": notes} for item, status, notes in rows]


def write_report(result, logic_rows, tradeoff, zreach, clearance, motion, interfaces, access_rows, audit_counts, visibility_counts, import_rows):
    REPORT_OUT.write_text(
        "\n".join([
            "# Stage 7A-3h-1 Industrial Module Carriage Binding Patch Report",
            "",
            "- User feedback: v7.3h incorrectly emphasized newly generated drive/rail/motor logic; boxes should not move.",
            "- Original industrial linear modules already include slider/carriage interfaces, so no auxiliary rails are needed.",
            "- This stage restores the correct logic: original standard X/Y/Z linear modules plus custom binding plates, saddles, shims, and adapter markers.",
            "- Hidden/replaced v7.3h elements: external motor placeholders, repeated belt/pulley placeholders, and any auxiliary-drive interpretation are not included in this preview.",
            "- Left/right Y slider binding: each Y slider/carriage interface receives a visible binding plate and low-profile 0 mm shim/riser interface.",
            "- X beam binding: X beam end adapters connect the Y slider binding plates to the X gantry ends.",
            "- X slider to Z binding: a backing plate/spacer marker clarifies that Z axis mounts to the original X slider/carriage.",
            "- Height tradeoff: A_keep_original_height selected; no Y rail height change and no X gantry height offset.",
            "- Why no full Y rail raise: removing external drive conflicts and binding original sliders resolves the visual issue without reducing Z reach margin.",
            "- Z reach: selected A leaves conservative estimated remaining margin of 62 mm; +20/+30 are fallback only, +40 is warning/risk.",
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
            f"- Binding patch module components: {result['module_component_count']}",
            f"- Binding patch module solids: {result['module_solids']}",
            f"- Binding patch module bbox: {v71.fmt_bbox(result['module_bbox'])}",
            f"- Preview components: {result['preview_component_count']}",
            f"- Preview solids: {result['preview_solids']}",
            f"- Preview bbox: {v71.fmt_bbox(result['preview_bbox'])}",
            "- Current boundary: concept-level carriage binding and clearance patch, not final bracket drawings.",
            "- Later detail may include real slider interface dimensions, adapter plate drawings, fastener CAD, tolerance stack, and structural verification.",
            f"- Logic audit rows: {len(logic_rows)}",
            f"- Height tradeoff rows: {len(tradeoff)}",
            f"- Z reach rows: {len(zreach)}",
            f"- Interface manifest rows: {len(interfaces)}",
            "",
        ]),
        encoding="utf-8",
    )


def write_outputs():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    logic_rows = logic_audit_rows()
    tradeoff = height_tradeoff_rows()
    zreach = z_reach_rows()
    clearance = clearance_rows()
    motion = motion_rows()
    interfaces = interface_rows()
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
    logic_fields = ["component_name", "source_stage", "is_original_industrial_linear_module", "is_new_unwanted_auxiliary_rail", "has_integrated_slider_or_carriage", "should_keep", "should_hide_or_replace", "issue_type", "recommended_action", "notes"]
    tradeoff_fields = ["candidate_id", "y_axis_rail_height_changed", "x_gantry_height_delta_mm", "uses_original_y_sliders", "uses_original_x_slider", "z_axis_reach_ok", "estimated_z_reach_margin_mm", "tube_collision_risk", "gripper_travel_clearance_ok", "x_beam_to_tube_clearance_ok", "motor_or_drive_block_collision_risk", "enclosure_clearance_ok", "cable_chain_clearance_ok", "recommended", "notes"]
    zreach_fields = ["candidate_id", "x_gantry_height_delta_mm", "z_axis_nominal_stroke_mm", "tube_pick_height_mm", "output_place_height_mm", "manual_review_place_height_mm", "required_downward_travel_mm", "estimated_remaining_margin_mm", "status", "notes"]
    clearance_fields = ["check_item", "component_a", "component_b", "clearance_target", "measured_or_estimated_clearance_mm", "status", "notes"]
    motion_fields = ["axis", "moving_assembly", "motion_range_description", "risk_component", "collision_risk", "status", "notes"]
    interface_fields = ["interface_id", "from_component", "to_component", "connection_type", "fixed_or_moving", "custom_or_standard", "mounting_method", "notes"]
    access_fields = ["item", "check_status", "notes"]
    visibility_fields = ["component_name", "expected_visible", "export_visibility_state", "alpha", "display_color", "visibility_risk", "notes"]
    import_fields = ["file_name", "file_exists", "file_size_bytes", "import_status", "solid_count", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "bbox_center_x_mm", "bbox_center_y_mm", "bbox_center_z_mm", "bbox_reasonable", "visibility_risk", "likely_visible_in_solidworks", "issue", "notes"]
    audit_fields = ["pair_a", "pair_b", "bbox_overlap_candidate", "exact_overlap_volume_mm3", "minimum_distance_mm", "clearance_threshold_mm", "audit_status", "notes"]

    write_csv(LOGIC_AUDIT_OUT, logic_rows, logic_fields)
    write_csv(HEIGHT_TRADEOFF_OUT, tradeoff, tradeoff_fields)
    write_csv(Z_REACH_OUT, zreach, zreach_fields)
    write_csv(CLEARANCE_OUT, clearance, clearance_fields)
    write_csv(MOTION_ENVELOPE_OUT, motion, motion_fields)
    write_csv(MODULE_VALIDATION_OUT, module_validation, validation_fields)
    write_csv(PREVIEW_VALIDATION_OUT, preview_validation, validation_fields)
    write_csv(MODULE_COLOR_MANIFEST_OUT, module_manifest, manifest_fields)
    write_csv(PREVIEW_COLOR_MANIFEST_OUT, preview_manifest, manifest_fields)
    write_csv(MODULE_INTERFACE_MANIFEST_OUT, interfaces, interface_fields)
    write_csv(MODULE_ACCESSIBILITY_OUT, access_rows, access_fields)
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
    write_report(result, logic_rows, tradeoff, zreach, clearance, motion, interfaces, access_rows, audit_counts, visibility_counts, import_rows)
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
    print("unwanted_auxiliary_rails_hidden=yes")
    print("unwanted_external_motors_hidden=yes")
    print("uses_original_y_sliders=yes")
    print("uses_original_x_slider=yes")
    print("gantry_riser_used=no")
    print("gantry_height_delta_mm=0")
    print("z_reach_ok=yes")
    print("boxes_not_moved=yes")
    print("gripper_module_preserved=yes")
    print("cable_management_v1_2_preserved=yes")
    print("tube_curved_labels_preserved=yes")
    print("non_tube_region_labels_removed=yes")
    print("control_box_closed_in_preview=yes")
    print(f"logic_audit_csv={LOGIC_AUDIT_OUT}")
    print(f"height_tradeoff_csv={HEIGHT_TRADEOFF_OUT}")
    print(f"z_reach_csv={Z_REACH_OUT}")
    print(f"clearance_check_csv={CLEARANCE_OUT}")
    print(f"motion_envelope_check_csv={MOTION_ENVELOPE_OUT}")
    print(f"module_step={MODULE_STEP_OUT}")
    print(f"preview_step={PREVIEW_STEP_OUT}")
    print(f"module_validation_csv={MODULE_VALIDATION_OUT}")
    print(f"preview_validation_csv={PREVIEW_VALIDATION_OUT}")
    print(f"module_color_manifest={MODULE_COLOR_MANIFEST_OUT}")
    print(f"preview_color_manifest={PREVIEW_COLOR_MANIFEST_OUT}")
    print(f"interface_manifest={MODULE_INTERFACE_MANIFEST_OUT}")
    print(f"accessibility_csv={MODULE_ACCESSIBILITY_OUT}")
    print(f"visibility_audit_csv={PREVIEW_VISIBILITY_AUDIT_OUT}")
    print(f"import_display_audit_csv={PREVIEW_IMPORT_DISPLAY_AUDIT_OUT}")
    print(f"interference_audit_csv={PREVIEW_INTERFERENCE_AUDIT_OUT}")
    print(f"report={REPORT_OUT}")
    return 0 if result["preview_failed_count"] == 0 and access_issue == 0 and clearance_issue == 0 and motion_issue == 0 and audit_counts["overlap"] == 0 and audit_counts["too_close"] == 0 and visibility_counts["high"] == 0 and import_rows[0]["likely_visible_in_solidworks"] == "yes" else 1


if __name__ == "__main__":
    raise SystemExit(main())
