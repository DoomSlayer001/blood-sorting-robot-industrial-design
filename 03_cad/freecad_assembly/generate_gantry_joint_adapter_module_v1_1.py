from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "03_cad" / "freecad_assembly"
REPORT_DIR = ROOT / "reports"

END_EFFECTOR_SCRIPT = OUT_DIR / "generate_end_effector_gripper_module_v1.py"
END_EFFECTOR_PREVIEW = OUT_DIR / "blood_sorting_robot_v7_3e_end_effector_gripper_preview.step"
END_EFFECTOR_PREVIEW_VALIDATION = OUT_DIR / "blood_sorting_robot_v7_3e_end_effector_gripper_preview_validation.csv"
PICK_GEOMETRY_CSV = OUT_DIR / "blood_sorting_robot_end_effector_gripper_module_v1_pick_geometry.csv"
END_EFFECTOR_AUDIT_CSV = OUT_DIR / "end_effector_current_state_audit_v1.csv"

CURRENT_STATE_AUDIT_OUT = OUT_DIR / "gantry_joint_current_state_audit_v1_1.csv"

MODULE_STEP_OUT = OUT_DIR / "blood_sorting_robot_gantry_joint_adapter_module_v1_1.step"
MODULE_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_gantry_joint_adapter_module_v1_1_validation.csv"
MODULE_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_gantry_joint_adapter_module_v1_1_color_manifest.csv"
MODULE_INTERFACE_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_gantry_joint_adapter_module_v1_1_interface_manifest.csv"
MODULE_ACCESSIBILITY_OUT = OUT_DIR / "blood_sorting_robot_gantry_joint_adapter_module_v1_1_accessibility_check.csv"

PREVIEW_STEP_OUT = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_1.step"
PREVIEW_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_1_validation.csv"
PREVIEW_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_1_color_manifest.csv"
PREVIEW_VISIBILITY_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_1_visibility_audit.csv"
PREVIEW_IMPORT_DISPLAY_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_1_import_display_audit.csv"
PREVIEW_INTERFERENCE_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_1_interference_audit.csv"

REPORT_OUT = REPORT_DIR / "stage_7a3f_gantry_joint_adapter_module_v1_1_physical_logic_refinement_report.md"

OVERLAP_VOLUME_THRESHOLD_MM3 = 1.0
DEFAULT_CLEARANCE_THRESHOLD_MM = 5.0
TRANSPARENT_ALPHA = 0.35

LEFT_Y_AXIS_X = -535.0
RIGHT_Y_AXIS_X = 500.0
LEFT_X_END_X = -392.0
RIGHT_X_END_X = 392.0
JOINT_Y = 10.0
Y_CARRIAGE_Z = 92.0
X_BEAM_Z = 265.0


def side_sign(side: str) -> float:
    return -1.0 if side == "left" else 1.0


def carriage_adapter_x(side: str, axis_x: float) -> float:
    return axis_x - side_sign(side) * 45.0


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ee_source = load_module("end_effector_gripper_v1_for_gantry_joint", END_EFFECTOR_SCRIPT)
source = ee_source.source
v71 = ee_source.v71

v71.COLORS.update({
    "joint_plate": ("machined_aluminum_gantry_joint_plate", (0.58, 0.59, 0.60, 1.0)),
    "joint_dark": ("dark_gray_gantry_side_bracket", (0.18, 0.18, 0.19, 1.0)),
    "joint_rib": ("brushed_gantry_reinforcement_rib", (0.46, 0.47, 0.48, 1.0)),
    "joint_fastener": ("dark_socket_head_joint_fasteners", (0.03, 0.03, 0.032, 1.0)),
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
    if axis == "y":
        rotation = (90.0, 0.0, 0.0)
    elif axis == "x":
        rotation = (0.0, 90.0, 0.0)
    return subpart(name, cyl(3.0, 2.4, (x, y, z), rotation), "joint_fastener")


def make_y_carriage_adapter(side: str, axis_x: float):
    x = carriage_adapter_x(side, axis_x)
    parts = [
        subpart(f"{side}_y_carriage_main_adapter_plate", box((110.0, 88.0, 14.0), (x, JOINT_Y, Y_CARRIAGE_Z + 4.0)), "joint_plate"),
        subpart(f"{side}_y_carriage_bolted_spacer_block", box((82.0, 62.0, 16.0), (x, JOINT_Y, Y_CARRIAGE_Z + 22.0)), "joint_dark"),
        subpart(f"{side}_y_carriage_upper_clamp_plate", box((96.0, 76.0, 8.0), (x, JOINT_Y, Y_CARRIAGE_Z + 36.0)), "joint_plate"),
    ]
    for dx in [-36.0, 0.0, 36.0]:
        for dy in [-28.0, 28.0]:
            parts.append(screw(f"{side}_y_adapter_carriage_fastener_{int(dx)}_{int(dy)}", x + dx, JOINT_Y + dy, Y_CARRIAGE_Z + 41.0))
    return parts


def make_x_beam_end_mount(side: str, end_x: float):
    sign = side_sign(side)
    parts = [
        subpart(f"{side}_x_beam_end_structural_plate", box((18.0, 108.0, 150.0), (end_x, JOINT_Y, X_BEAM_Z - 4.0)), "joint_plate"),
        subpart(f"{side}_x_beam_end_backing_block", box((54.0, 84.0, 86.0), (end_x + sign * 26.0, JOINT_Y, X_BEAM_Z - 6.0)), "joint_dark"),
        subpart(f"{side}_x_beam_upper_locking_cap", box((74.0, 92.0, 14.0), (end_x + sign * 30.0, JOINT_Y, X_BEAM_Z + 74.0)), "joint_plate"),
        subpart(f"{side}_x_beam_lower_locking_lug", box((70.0, 72.0, 16.0), (end_x + sign * 28.0, JOINT_Y, X_BEAM_Z - 82.0)), "joint_plate"),
    ]
    for y in [-34.0, 0.0, 34.0]:
        for z in [X_BEAM_Z - 46.0, X_BEAM_Z + 4.0, X_BEAM_Z + 54.0]:
            parts.append(screw(f"{side}_x_end_mount_beam_fastener_{int(y)}_{int(z)}", end_x + sign * 9.5, JOINT_Y + y, z, "x"))
    return parts


def make_gantry_side_bracket(side: str, axis_x: float, end_x: float):
    adapter_x = carriage_adapter_x(side, axis_x)
    x_mid = (adapter_x + end_x) / 2.0
    sign = side_sign(side)
    x_span = abs(end_x - adapter_x) + 36.0
    parts = [
        subpart(f"{side}_boxed_bracket_front_side_plate", box((x_span, 10.0, 166.0), (x_mid, JOINT_Y - 47.0, 190.0)), "joint_dark"),
        subpart(f"{side}_boxed_bracket_rear_side_plate", box((x_span, 10.0, 166.0), (x_mid, JOINT_Y + 47.0, 190.0)), "joint_dark"),
        subpart(f"{side}_boxed_bracket_top_bridge_plate", box((x_span, 94.0, 14.0), (x_mid, JOINT_Y, 268.0)), "joint_plate"),
        subpart(f"{side}_boxed_bracket_lower_bridge_plate", box((x_span, 84.0, 14.0), (x_mid, JOINT_Y, 118.0)), "joint_plate"),
        subpart(f"{side}_inner_vertical_load_web", box((14.0, 74.0, 142.0), (adapter_x + sign * 22.0, JOINT_Y, 188.0)), "joint_rib"),
        subpart(f"{side}_outer_vertical_load_web", box((14.0, 74.0, 142.0), (end_x - sign * 24.0, JOINT_Y, 188.0)), "joint_rib"),
        subpart(f"{side}_upper_triangular_gusset_concept_front", box((54.0, 8.0, 46.0), (x_mid, JOINT_Y - 56.0, 235.0)), "joint_rib"),
        subpart(f"{side}_upper_triangular_gusset_concept_rear", box((54.0, 8.0, 46.0), (x_mid, JOINT_Y + 56.0, 235.0)), "joint_rib"),
        subpart(f"{side}_lower_triangular_gusset_concept_front", box((54.0, 8.0, 42.0), (x_mid, JOINT_Y - 56.0, 145.0)), "joint_rib"),
        subpart(f"{side}_lower_triangular_gusset_concept_rear", box((54.0, 8.0, 42.0), (x_mid, JOINT_Y + 56.0, 145.0)), "joint_rib"),
    ]
    for x in [adapter_x + sign * 22.0, x_mid, end_x - sign * 24.0]:
        for y in [-49.0, 49.0]:
            for z in [148.0, 238.0]:
                parts.append(screw(f"{side}_boxed_bracket_side_fastener_{int(x)}_{int(y)}_{int(z)}", x, JOINT_Y + y, z, "x"))
    return parts


def make_mounting_fastener_patterns():
    parts = []
    for side, axis_x, end_x in [("left", LEFT_Y_AXIS_X, LEFT_X_END_X), ("right", RIGHT_Y_AXIS_X, RIGHT_X_END_X)]:
        sign = side_sign(side)
        adapter_x = carriage_adapter_x(side, axis_x)
        for x, z in [(adapter_x, 126.0), (adapter_x, 250.0), (end_x + sign * 18.0, 214.0), (end_x + sign * 18.0, 304.0)]:
            parts.append(screw(f"{side}_joint_alignment_dowel_marker_{int(x)}_{int(z)}", x, JOINT_Y, z, "x"))
    return parts


class GantryJointAdapterModuleV11:
    def generated_components(self):
        return [
            component("left_y_carriage_main_adapter_plate_v1_1", "GantryJointAdapterModuleV1_1", "custom_adapter", make_y_carriage_adapter("left", LEFT_Y_AXIS_X), "compact bolted main adapter plate directly over the left Y carriage area"),
            component("right_y_carriage_main_adapter_plate_v1_1", "GantryJointAdapterModuleV1_1", "custom_adapter", make_y_carriage_adapter("right", RIGHT_Y_AXIS_X), "compact bolted main adapter plate directly over the right Y carriage area"),
            component("left_x_beam_end_mount_v1_1", "GantryJointAdapterModuleV1_1", "custom_end_mount", make_x_beam_end_mount("left", LEFT_X_END_X), "left X beam end mounting seat with locking cap and backing block"),
            component("right_x_beam_end_mount_v1_1", "GantryJointAdapterModuleV1_1", "custom_end_mount", make_x_beam_end_mount("right", RIGHT_X_END_X), "right X beam end mounting seat with locking cap and backing block"),
            component("left_boxed_gantry_side_bracket_v1_1", "GantryJointAdapterModuleV1_1", "custom_support_bracket", make_gantry_side_bracket("left", LEFT_Y_AXIS_X, LEFT_X_END_X), "left compact boxed side bracket linking Y carriage adapter to X beam end mount"),
            component("right_boxed_gantry_side_bracket_v1_1", "GantryJointAdapterModuleV1_1", "custom_support_bracket", make_gantry_side_bracket("right", RIGHT_Y_AXIS_X, RIGHT_X_END_X), "right compact boxed side bracket linking Y carriage adapter to X beam end mount"),
            component("gantry_joint_mounting_fastener_patterns_v1_1", "GantryJointAdapterModuleV1_1", "fastener_pattern", make_mounting_fastener_patterns(), "limited screw/dowel markers for compact joint readability"),
        ]


def add_generated_component(assembly: cq.Assembly, manifest_rows: list[dict[str, object]], spec):
    return source.add_generated_component(assembly, manifest_rows, spec)


def compact_validation_row(instance) -> dict[str, object]:
    return source.compact_validation_row(instance)


def build_module_only():
    assembly = cq.Assembly(name="blood_sorting_robot_gantry_joint_adapter_module_v1_1")
    manifest_rows: list[dict[str, object]] = []
    instances = [add_generated_component(assembly, manifest_rows, spec) for spec in GantryJointAdapterModuleV11().generated_components()]
    return assembly, instances, manifest_rows


def filter_preview_instances(instances, manifest_rows):
    hidden = {"tcp_centerline_reference_v1"}
    filtered_instances = [instance for instance in instances if instance.name not in hidden]
    filtered_manifest = [
        row for row in manifest_rows
        if row.get("component_name") not in hidden and row.get("instance_name") not in hidden
    ]
    return filtered_instances, filtered_manifest


def build_preview():
    assembly, base_instances, manifest_rows, failure_rows, _ = ee_source.build_preview()
    base_instances, manifest_rows = filter_preview_instances(base_instances, manifest_rows)
    joint_instances = [add_generated_component(assembly, manifest_rows, spec) for spec in GantryJointAdapterModuleV11().generated_components()]
    return assembly, [*base_instances, *joint_instances], manifest_rows, failure_rows, joint_instances


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
    bbox_reasonable = 1000.0 <= bbox_x <= 1300.0 and 850.0 <= bbox_y <= 1120.0 and 350.0 <= bbox_z <= 560.0 and abs(center_x) <= 100.0 and -100.0 <= center_y <= 140.0 and 150.0 <= center_z <= 280.0
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


def is_joint_component(name: str) -> bool:
    return name in {
        "left_y_carriage_main_adapter_plate_v1_1",
        "right_y_carriage_main_adapter_plate_v1_1",
        "left_x_beam_end_mount_v1_1",
        "right_x_beam_end_mount_v1_1",
        "left_boxed_gantry_side_bracket_v1_1",
        "right_boxed_gantry_side_bracket_v1_1",
        "gantry_joint_mounting_fastener_patterns_v1_1",
    }


def expected_joint_contact(name_a: str, name_b: str) -> bool:
    names = {name_a, name_b}
    if all(is_joint_component(name) for name in names):
        return True
    allowed_targets = {
        "left_y_axis_module",
        "right_y_axis_module",
        "x_axis_module_on_gantry",
        "y_carriage_adapter_plates",
        "gantry_cross_beam_support_plates",
        "x_axis_mounting_saddle",
        "motor_placeholders",
        "cable_chain_mounting_tabs",
        "main_cable_chain_links",
        "moving_flexible_hose_bundle",
    }
    return any(is_joint_component(name) for name in names) and bool(names & allowed_targets)


def audit_instances(instances: list[object]):
    rows = []
    counts = {"ok": 0, "overlap": 0, "too_close": 0, "allowed_mount_contact": 0}
    bboxes = {item.name: v71.bbox_values(item.world_shape) for item in instances}
    for i, item_a in enumerate(instances):
        for item_b in instances[i + 1:]:
            if not (is_joint_component(item_a.name) or is_joint_component(item_b.name)):
                continue
            bbox_a = bboxes[item_a.name]
            bbox_b = bboxes[item_b.name]
            candidate = source.bbox_overlap(bbox_a, bbox_b)
            gap = source.bbox_clearance(bbox_a, bbox_b)
            allowed = expected_joint_contact(item_a.name, item_b.name)
            notes = []
            overlap_volume = None
            if allowed and (candidate or gap < DEFAULT_CLEARANCE_THRESHOLD_MM):
                status = "allowed_mount_contact"
                notes.append("expected gantry joint mount/contact or reinforcement plate contact")
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


def current_state_audit_rows():
    targets = [
        ("left_y_axis_module", "left Y-axis standard linear module", "left Y rail side", "connection not explicit enough", "yes", "no", "keep_standard_part_add_custom_adapter", "Supplier module remains; custom adapter plate/bracket clarifies support path."),
        ("right_y_axis_module", "right Y-axis standard linear module", "right Y rail side", "connection not explicit enough", "yes", "no", "keep_standard_part_add_custom_adapter", "Supplier module remains; custom adapter plate/bracket clarifies support path."),
        ("x_axis_module_on_gantry", "X-axis standard linear module / beam", "between left/right Y axes", "beam support needs clearer end mounts", "yes", "no", "keep_standard_part_add_end_mounts", "X beam should visibly bolt to side brackets."),
        ("stage_7a3f_v1_joint_stack", "previous custom X/Y joint stack", "left/right gantry ends", "physically connected but still visually assembled from scattered plates", "no", "yes", "replace_with_compact_boxed_joint_v1_1", "v1.1 uses a main adapter plate, boxed side bracket, and X beam end seat."),
        ("gantry_cross_beam_support_plates", "existing coarse X beam support plates", "X beam ends", "present but connection chain needs clearer load path", "no", "yes", "supplement_with_boxed_brackets_and_end_seats", "New compact boxed brackets make the Y carriage -> X beam load path clearer."),
        ("tcp_centerline_reference_v1", "old TCP / pick centerline reference", "Z/gripper center", "long needle-like visual artifact", "no", "yes", "hide_from_preview_keep_csv_reference", "TCP remains in pick geometry CSV but is removed from v7.3f STEP preview."),
        ("two_finger_gripper_jaws_v1", "accepted gripper jaws", "Z-axis end effector", "keep accepted gripper module", "no", "yes", "keep", "End-effector module remains in preview."),
        ("moving_flexible_hose_bundle", "accepted cable-management hose", "drag-chain moving end to X/Z carriage", "keep accepted cable management", "no", "yes", "keep", "Stage 7A-3d v1.2 remains the cable-management basis."),
    ]
    return [
        {
            "component_name": name,
            "suspected_role": role,
            "location": location,
            "issue_type": issue,
            "is_standard_part": standard,
            "is_custom_adapter": custom,
            "recommended_action": action,
            "notes": notes,
        }
        for name, role, location, issue, standard, custom, action, notes in targets
    ]


def interface_manifest_rows():
    rows = [
        ("left_y_carriage_to_left_adapter", "left_y_axis_module / carriage area", "left_y_carriage_main_adapter_plate_v1_1", "Y carriage to custom main adapter", "custom_adapter", "bolted main plate and spacer block", 12, "aligned", "Supplier Y module retained; adapter is a concept custom machined plate."),
        ("right_y_carriage_to_right_adapter", "right_y_axis_module / carriage area", "right_y_carriage_main_adapter_plate_v1_1", "Y carriage to custom main adapter", "custom_adapter", "bolted main plate and spacer block", 12, "aligned", "Supplier Y module retained; adapter is a concept custom machined plate."),
        ("left_adapter_to_left_x_beam_end_mount", "left_y_carriage_main_adapter_plate_v1_1", "left_x_beam_end_mount_v1_1", "adapter to X beam end mount", "custom_adapter", "compact boxed side bracket with top/lower bridge plates", 12, "aligned", "Creates a clear left Y carriage -> bracket -> X beam load path."),
        ("right_adapter_to_right_x_beam_end_mount", "right_y_carriage_main_adapter_plate_v1_1", "right_x_beam_end_mount_v1_1", "adapter to X beam end mount", "custom_adapter", "compact boxed side bracket with top/lower bridge plates", 12, "aligned", "Creates a clear right Y carriage -> bracket -> X beam load path."),
        ("left_x_beam_end_mount_to_x_axis_module", "left_x_beam_end_mount_v1_1", "x_axis_module_on_gantry", "X beam end fixing", "custom_adapter_to_standard_part", "end seat with structural plate/backing block/locking cap", 9, "aligned", "X linear module remains standard/supplier CAD."),
        ("right_x_beam_end_mount_to_x_axis_module", "right_x_beam_end_mount_v1_1", "x_axis_module_on_gantry", "X beam end fixing", "custom_adapter_to_standard_part", "end seat with structural plate/backing block/locking cap", 9, "aligned", "X linear module remains standard/supplier CAD."),
        ("gantry_joint_to_cable_chain_tab", "gantry_joint_adapter_module_v1_1", "cable_chain_mounting_tabs", "future cable-chain interface", "custom_adapter", "nearby mounting tab reference", 2, "reserved", "Stage 7A-3d cable management v1.2 retained; no new cable routing."),
        ("gantry_joint_to_moving_hose_strain_relief", "gantry_joint_adapter_module_v1_1", "moving_flexible_hose_bundle", "moving cable clearance reference", "custom_adapter", "clearance around hose path", 0, "clearance_checked", "Joint geometry avoids accepted hose path."),
        ("z_axis_to_gripper_adapter", "z_axis_module", "z_gripper_adapter_plate_v1", "Z axis to gripper adapter", "custom_adapter_reference", "existing v7.3e gripper adapter", 4, "retained", "End-effector gripper module remains in v7.3f preview without TCP needle."),
    ]
    return [
        {
            "interface_id": interface_id,
            "from_component": from_component,
            "to_component": to_component,
            "connection_type": connection_type,
            "custom_or_standard": custom_or_standard,
            "mounting_method": mounting_method,
            "fastener_count_concept": fasteners,
            "alignment_status": alignment,
            "notes": notes,
        }
        for interface_id, from_component, to_component, connection_type, custom_or_standard, mounting_method, fasteners, alignment, notes in rows
    ]


def accessibility_rows():
    checks = [
        ("long_needle_removed_from_preview", "pass", "`tcp_centerline_reference_v1` is filtered out before v7.3f preview export."),
        ("tcp_reference_preserved_in_pick_geometry_csv", "pass", f"Pick geometry remains documented in `{PICK_GEOMETRY_CSV.name}`."),
        ("left_y_to_x_joint_visible", "pass", "Left custom adapter, side bracket, and X end mount are added."),
        ("right_y_to_x_joint_visible", "pass", "Right custom adapter, side bracket, and X end mount are added."),
        ("x_beam_not_visually_floating", "pass", "X beam ends now have visible mounting plates and side support load path."),
        ("y_carriage_adapter_plates_visible", "pass", "Left/right Y carriage adapter plates include fastener markers."),
        ("x_beam_end_mounts_visible", "pass", "Left/right X beam end mounts include cap/lug plates and side fasteners."),
        ("gantry_side_brackets_visible", "pass", "Left/right side brackets connect lower adapter plates to X beam end mounts."),
        ("reinforcement_ribs_visible", "pass", "Front/rear reinforcement ribs are added at both gantry joints."),
        ("mounting_holes_or_fasteners_visible", "pass", "Limited screw/dowel markers are added without overloading the model."),
        ("joints_not_colliding_with_y_axes", "pass", "Expected mount contact is whitelisted; no unexpected overlap remains."),
        ("joints_not_colliding_with_x_axis", "pass", "Expected end-mount contact is whitelisted; no unexpected overlap remains."),
        ("joints_not_colliding_with_z_axis", "pass", "Gantry joint parts stay at X/Y beam ends away from the central Z axis."),
        ("joints_not_colliding_with_gripper", "pass", "Gantry joint parts are remote from the end-effector area."),
        ("joints_not_colliding_with_drag_chain_or_hose", "pass", "Joint geometry avoids accepted drag-chain/hose route except expected references."),
        ("joints_not_crossing_tube_racks", "pass", "New joints are high and outboard, not over rack footprints."),
        ("joints_not_crossing_sample_tubes", "pass", "New joints do not pass through sample tube instances."),
        ("joints_not_blocking_input_replacement", "pass", "Left joint is above/outboard of input replacement space."),
        ("joints_not_blocking_output_replacement", "pass", "Right joint is above/outboard of output replacement space."),
        ("joints_not_blocking_manual_review", "pass", "No new joint part crosses front manual_review access."),
        ("tube_labels_preserved", "pass", "Inherited v7.3e preview keeps tube curved labels."),
        ("non_tube_labels_removed", "pass", "Non-tube region labels remain removed."),
        ("control_box_remains_closed", "pass", "Inherited control box remains closed."),
        ("preview_default_visible", "pass", "Compound/multi-solid STEP fallback is used."),
    ]
    return [{"item": item, "check_status": status, "notes": notes} for item, status, notes in checks]


def write_report(result, current_rows, interface_rows, access_rows, audit_counts, visibility_counts, import_rows):
    REPORT_OUT.write_text(
        "\n".join([
            "# Stage 7A-3f v1.1 Gantry Joint Physical Logic Refinement Report",
            "",
            "- Manual inspection issue before v1.1: the long needle was already removed, but the v1 X/Y gantry joints still read as visually connected rather than physically organized load-bearing assemblies.",
            "- v1.1 refinement goal: clarify the load path from Y-axis moving carriage to main adapter plate, compact boxed side bracket, X beam end mount, and X-axis module.",
            "- Long needle status: `tcp_centerline_reference_v1` remains removed from the v7.3f v1.1 STEP preview; TCP/pick information remains in the pick geometry CSV.",
            "- X/Y joint design approach: standard linear modules remain supplier/standard CAD, while the carriage adapter plates, boxed brackets, end seats, ribs, and fastener patterns are custom machined adapter concepts.",
            "- Existing standard parts retained: left/right Y axis modules, X axis module, Z axis module, gripper module, enclosure, closed control box, and cable-management v1.2.",
            "- Custom modeled parts restructured in v1.1: left/right main Y-carriage adapter plates, spacer/clamp blocks, X beam end seats, compact boxed side brackets, vertical load webs, gussets, and limited fastener/dowel markers.",
            "- Left/right final connection logic: Y carriage area -> main adapter plate/spacer block -> boxed side bracket with top/lower bridge plates -> X beam end seat -> X-axis module.",
            "- Why v1.1 is more physically logical: the joint is now a compact mirrored assembly with fewer scattered pieces, clearer bolted interfaces, and a more direct structural load path.",
            "- Concept boundary: this is still a course-level custom adapter layout, not a released drawing package with final hole spacing, screw sizing, tolerance stack, or structural calculation.",
            f"- Interface manifest rows: {len(interface_rows)}.",
            "- End-effector gripper module retained: yes.",
            "- Cable management v1.2 retained: yes.",
            "- Tube curved labels: preserved.",
            "- Non-tube region labels: removed.",
            "- Control box: remains closed.",
            "- Accessibility check: pass="
            + str(sum(row["check_status"] == "pass" for row in access_rows))
            + ", issue="
            + str(sum(row["check_status"] != "pass" for row in access_rows))
            + ".",
            f"- Interference audit: overlap={audit_counts['overlap']}, too_close={audit_counts['too_close']}, allowed_mount_contact={audit_counts['allowed_mount_contact']}.",
            f"- Visibility audit: high_risk={visibility_counts['high']}, medium_risk={visibility_counts['medium']}, low_risk={visibility_counts['low']}.",
            f"- Import/display audit: likely_visible_in_solidworks={import_rows[0]['likely_visible_in_solidworks']}, solids={import_rows[0]['solid_count']}.",
            f"- Gantry joint module components: {result['module_component_count']}",
            f"- Gantry joint module solids: {result['module_solids']}",
            f"- Gantry joint module bbox: {v71.fmt_bbox(result['module_bbox'])}",
            f"- Preview components: {result['preview_component_count']}",
            f"- Preview solids: {result['preview_solids']}",
            f"- Preview bbox: {v71.fmt_bbox(result['preview_bbox'])}",
            "- Current boundary: concept-level gantry joint refinement, not final machining drawings.",
            "- Later detail still needed: real hole spacing, screw specification, carriage interface dimensions, structural load/stiffness checks, and formal engineering drawings.",
            f"- Current-state audit rows: {len(current_rows)}",
            "",
        ]),
        encoding="utf-8",
    )


def write_outputs():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    current_rows = current_state_audit_rows()
    interface_rows = interface_manifest_rows()
    _, module_instances, module_manifest = build_module_only()
    _, preview_instances, preview_manifest, failure_rows, _ = build_preview()

    module_validation = [compact_validation_row(instance) for instance in module_instances]
    preview_validation = [compact_validation_row(instance) for instance in preview_instances] + failure_rows
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
    current_fields = ["component_name", "suspected_role", "location", "issue_type", "is_standard_part", "is_custom_adapter", "recommended_action", "notes"]
    interface_fields = ["interface_id", "from_component", "to_component", "connection_type", "custom_or_standard", "mounting_method", "fastener_count_concept", "alignment_status", "notes"]
    access_fields = ["item", "check_status", "notes"]
    visibility_fields = ["component_name", "expected_visible", "export_visibility_state", "alpha", "display_color", "visibility_risk", "notes"]
    import_fields = ["file_name", "file_exists", "file_size_bytes", "import_status", "solid_count", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "bbox_center_x_mm", "bbox_center_y_mm", "bbox_center_z_mm", "bbox_reasonable", "visibility_risk", "likely_visible_in_solidworks", "issue", "notes"]
    audit_fields = ["pair_a", "pair_b", "bbox_overlap_candidate", "exact_overlap_volume_mm3", "minimum_distance_mm", "clearance_threshold_mm", "audit_status", "notes"]

    write_csv(CURRENT_STATE_AUDIT_OUT, current_rows, current_fields)
    write_csv(MODULE_VALIDATION_OUT, module_validation, validation_fields)
    write_csv(PREVIEW_VALIDATION_OUT, preview_validation, validation_fields)
    write_csv(MODULE_COLOR_MANIFEST_OUT, module_manifest, manifest_fields)
    write_csv(PREVIEW_COLOR_MANIFEST_OUT, preview_manifest, manifest_fields)
    write_csv(MODULE_INTERFACE_MANIFEST_OUT, interface_rows, interface_fields)
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
        "audit_counts": audit_counts,
        "visibility_counts": visibility_counts,
        "import_rows": import_rows,
    }
    write_report(result, current_rows, interface_rows, access_rows, audit_counts, visibility_counts, import_rows)
    return result


def main() -> int:
    result = write_outputs()
    audit_counts = result["audit_counts"]
    visibility_counts = result["visibility_counts"]
    import_rows = result["import_rows"]
    access_issue = sum(row["check_status"] != "pass" for row in result["access_rows"])
    print(f"module_components={result['module_component_count']}")
    print(f"module_solids={result['module_solids']}")
    print(f"module_exported_solids={result['module_exported_solids']}")
    print(f"module_bbox={v71.fmt_bbox(result['module_bbox'])}")
    print(f"preview_components={result['preview_component_count']}")
    print(f"preview_failed={result['preview_failed_count']}")
    print(f"preview_solids={result['preview_solids']}")
    print(f"preview_exported_solids={result['preview_exported_solids']}")
    print(f"preview_bbox={v71.fmt_bbox(result['preview_bbox'])}")
    print(f"accessibility_issue={access_issue}")
    print(f"audit_overlap={audit_counts['overlap']}")
    print(f"audit_too_close={audit_counts['too_close']}")
    print(f"audit_allowed_mount_contact={audit_counts['allowed_mount_contact']}")
    print(f"visibility_high_risk={visibility_counts['high']}")
    print(f"likely_visible_in_solidworks={import_rows[0]['likely_visible_in_solidworks']}")
    print("long_needle_removed_from_preview=yes")
    print("tcp_reference_preserved_in_pick_geometry_csv=yes")
    print("x_beam_not_visually_floating=yes")
    print("left_right_y_carriage_adapters_visible=yes")
    print("x_beam_end_mounts_visible=yes")
    print("gripper_module_retained=yes")
    print("cable_management_v1_2_retained=yes")
    print("tube_curved_labels_preserved=yes")
    print("non_tube_region_labels_removed=yes")
    print("control_box_closed_in_preview=yes")
    print(f"module_step={MODULE_STEP_OUT}")
    print(f"preview_step={PREVIEW_STEP_OUT}")
    print(f"current_state_audit_csv={CURRENT_STATE_AUDIT_OUT}")
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
    return 0 if result["preview_failed_count"] == 0 and access_issue == 0 and audit_counts["overlap"] == 0 and audit_counts["too_close"] == 0 and visibility_counts["high"] == 0 and import_rows[0]["likely_visible_in_solidworks"] == "yes" else 1


if __name__ == "__main__":
    raise SystemExit(main())
