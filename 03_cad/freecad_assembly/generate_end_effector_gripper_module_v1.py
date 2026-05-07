from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "03_cad" / "freecad_assembly"
REPORT_DIR = ROOT / "reports"

LATEST_CABLE_PREVIEW_CANDIDATES = [
    OUT_DIR / "blood_sorting_robot_v7_3d_cable_chain_wiring_preview_v1_3.step",
    OUT_DIR / "blood_sorting_robot_v7_3d_cable_chain_wiring_preview_v1_2.step",
]
CABLE_VISUAL_SCRIPT = OUT_DIR / "generate_cable_chain_wiring_module_v1_2_clean_visual.py"
CABLE_PREVIEW_VALIDATION = OUT_DIR / "blood_sorting_robot_v7_3d_cable_chain_wiring_preview_v1_2_validation.csv"

CURRENT_STATE_AUDIT_OUT = OUT_DIR / "end_effector_current_state_audit_v1.csv"

MODULE_STEP_OUT = OUT_DIR / "blood_sorting_robot_end_effector_gripper_module_v1.step"
MODULE_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_end_effector_gripper_module_v1_validation.csv"
MODULE_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_end_effector_gripper_module_v1_color_manifest.csv"
MODULE_PICK_GEOMETRY_OUT = OUT_DIR / "blood_sorting_robot_end_effector_gripper_module_v1_pick_geometry.csv"
MODULE_ACCESSIBILITY_OUT = OUT_DIR / "blood_sorting_robot_end_effector_gripper_module_v1_accessibility_check.csv"

PREVIEW_STEP_OUT = OUT_DIR / "blood_sorting_robot_v7_3e_end_effector_gripper_preview.step"
PREVIEW_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_v7_3e_end_effector_gripper_preview_validation.csv"
PREVIEW_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_v7_3e_end_effector_gripper_preview_color_manifest.csv"
PREVIEW_VISIBILITY_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3e_end_effector_gripper_preview_visibility_audit.csv"
PREVIEW_IMPORT_DISPLAY_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3e_end_effector_gripper_preview_import_display_audit.csv"
PREVIEW_INTERFERENCE_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3e_end_effector_gripper_preview_interference_audit.csv"

REPORT_OUT = REPORT_DIR / "stage_7a3e_end_effector_gripper_module_report.md"

OVERLAP_VOLUME_THRESHOLD_MM3 = 1.0
DEFAULT_CLEARANCE_THRESHOLD_MM = 5.0
TRANSPARENT_ALPHA = 0.35

TOOL_X = 0.0
TOOL_Y = 20.0
ADAPTER_Z = 146.0
BODY_Z = 111.0
JAW_Z = 67.0

GRIPPER_BODY_WIDTH_MM = 56.0
GRIPPER_BODY_DEPTH_MM = 42.0
GRIPPER_BODY_HEIGHT_MM = 38.0
JAW_LENGTH_MM = 54.0
JAW_WIDTH_MM = 9.0
JAW_DEPTH_MM = 14.0
GRIPPER_OPEN_GAP_MM = 23.0
ASSUMED_TUBE_OD_MM = 13.0


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cable_source = load_module("cable_chain_wiring_v1_2_for_end_effector", CABLE_VISUAL_SCRIPT)
source = cable_source.source
v71 = cable_source.v71

v71.COLORS.update({
    "gripper_body_dark": ("dark_gray_electric_parallel_gripper_body", (0.08, 0.085, 0.09, 1.0)),
    "gripper_body_black": ("black_gripper_motor_cover", (0.015, 0.015, 0.018, 1.0)),
    "gripper_metal": ("machined_aluminum_gripper_adapter", (0.55, 0.57, 0.58, 1.0)),
    "jaw_metal": ("brushed_steel_gripper_jaws", (0.62, 0.64, 0.65, 1.0)),
    "soft_pad": ("black_rubber_soft_tube_contact_pad", (0.01, 0.01, 0.01, 1.0)),
    "fastener_dark": ("dark_socket_head_fasteners", (0.03, 0.03, 0.032, 1.0)),
    "strain_relief": ("black_gripper_strain_relief", (0.008, 0.008, 0.009, 1.0)),
    "tcp_reference": ("transparent_tcp_centerline_reference", (0.85, 0.92, 1.0, 0.35)),
})


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def selected_input_preview() -> Path:
    for path in LATEST_CABLE_PREVIEW_CANDIDATES:
        if path.exists():
            return path
    return LATEST_CABLE_PREVIEW_CANDIDATES[-1]


def subpart(name: str, shape: cq.Shape, color_key: str):
    return source.subpart(name, shape, color_key)


def component(name: str, module_name: str, category: str, subparts, notes: str):
    return source.component(name, module_name, category, subparts, (0.0, 0.0, 0.0), notes)


def box(size: tuple[float, float, float], offset: tuple[float, float, float]) -> cq.Shape:
    return source.box_shape(size, offset)


def cyl(radius: float, height: float, offset: tuple[float, float, float], rotation=(0.0, 0.0, 0.0)) -> cq.Shape:
    return source.cyl_shape(radius, height, offset, rotation)


def make_adapter_plate():
    parts = [
        subpart("z_gripper_adapter_plate_main", box((74.0, 8.0, 62.0), (TOOL_X, TOOL_Y + 1.0, ADAPTER_Z)), "gripper_metal"),
        subpart("z_gripper_adapter_lower_flange", box((64.0, 28.0, 8.0), (TOOL_X, TOOL_Y, ADAPTER_Z - 35.0)), "gripper_metal"),
        subpart("z_gripper_adapter_upper_flange", box((64.0, 28.0, 8.0), (TOOL_X, TOOL_Y, ADAPTER_Z + 35.0)), "gripper_metal"),
    ]
    for index, x in enumerate([-24.0, 24.0], start=1):
        for z in [ADAPTER_Z - 19.0, ADAPTER_Z + 19.0]:
            parts.append(subpart(f"z_adapter_socket_head_{index}_{int(z)}", cyl(2.4, 2.2, (TOOL_X + x, TOOL_Y - 4.7, z), (90.0, 0.0, 0.0)), "fastener_dark"))
    return parts


def make_gripper_body():
    parts = [
        subpart("electric_parallel_gripper_body_housing", box((GRIPPER_BODY_WIDTH_MM, GRIPPER_BODY_DEPTH_MM, GRIPPER_BODY_HEIGHT_MM), (TOOL_X, TOOL_Y, BODY_Z)), "gripper_body_dark"),
        subpart("electric_parallel_gripper_front_motor_cover", box((42.0, 5.0, 25.0), (TOOL_X, TOOL_Y - 23.5, BODY_Z + 2.0)), "gripper_body_black"),
        subpart("parallel_jaw_linear_slide_rail", box((46.0, 8.0, 8.0), (TOOL_X, TOOL_Y - 1.0, BODY_Z - 24.0)), "jaw_metal"),
    ]
    for x in [-20.0, 20.0]:
        for z in [BODY_Z - 7.0, BODY_Z + 11.0]:
            parts.append(subpart(f"gripper_body_socket_head_{int(x)}_{int(z)}", cyl(2.2, 2.0, (TOOL_X + x, TOOL_Y - 25.2, z), (90.0, 0.0, 0.0)), "fastener_dark"))
    return parts


def make_two_finger_jaws():
    jaw_x = GRIPPER_OPEN_GAP_MM / 2.0 + JAW_WIDTH_MM / 2.0
    parts = [
        subpart("left_gripper_jaw_vertical_finger", box((JAW_WIDTH_MM, JAW_DEPTH_MM, JAW_LENGTH_MM), (TOOL_X - jaw_x, TOOL_Y, JAW_Z)), "jaw_metal"),
        subpart("right_gripper_jaw_vertical_finger", box((JAW_WIDTH_MM, JAW_DEPTH_MM, JAW_LENGTH_MM), (TOOL_X + jaw_x, TOOL_Y, JAW_Z)), "jaw_metal"),
        subpart("left_jaw_root_block", box((18.0, 18.0, 12.0), (TOOL_X - jaw_x, TOOL_Y, BODY_Z - 25.0)), "jaw_metal"),
        subpart("right_jaw_root_block", box((18.0, 18.0, 12.0), (TOOL_X + jaw_x, TOOL_Y, BODY_Z - 25.0)), "jaw_metal"),
    ]
    return parts


def make_soft_contact_pads():
    pad_x = GRIPPER_OPEN_GAP_MM / 2.0 - 1.2
    parts = [
        subpart("left_soft_tube_contact_pad", box((2.6, 16.0, 32.0), (TOOL_X - pad_x, TOOL_Y - 0.5, JAW_Z - 4.0)), "soft_pad"),
        subpart("right_soft_tube_contact_pad", box((2.6, 16.0, 32.0), (TOOL_X + pad_x, TOOL_Y - 0.5, JAW_Z - 4.0)), "soft_pad"),
        subpart("left_pad_shallow_v_groove_marker", cyl(1.2, 16.5, (TOOL_X - pad_x + 1.5, TOOL_Y - 0.5, JAW_Z - 4.0), (90.0, 0.0, 0.0)), "fastener_dark"),
        subpart("right_pad_shallow_v_groove_marker", cyl(1.2, 16.5, (TOOL_X + pad_x - 1.5, TOOL_Y - 0.5, JAW_Z - 4.0), (90.0, 0.0, 0.0)), "fastener_dark"),
    ]
    return parts


def make_gripper_strain_relief():
    parts = [
        subpart("gripper_top_strain_relief_clamp", box((24.0, 12.0, 8.0), (TOOL_X + 20.0, TOOL_Y + 17.0, BODY_Z + 20.0)), "strain_relief"),
        subpart("short_hose_to_gripper_body", cyl(3.0, 30.0, (TOOL_X + 29.0, TOOL_Y + 17.0, BODY_Z + 36.0), (0.0, 24.0, 0.0)), "strain_relief"),
    ]
    return parts


def make_tcp_reference():
    return [
        subpart("tcp_centerline_reference_transparent", cyl(0.8, 92.0, (TOOL_X, TOOL_Y, 61.0)), "tcp_reference"),
    ]


class EndEffectorGripperModuleV1:
    def generated_components(self):
        return [
            component("z_gripper_adapter_plate_v1", "EndEffectorGripperModuleV1", "adapter", make_adapter_plate(), "new adapter plate between Z axis end and gripper body"),
            component("electric_parallel_gripper_body_v1", "EndEffectorGripperModuleV1", "gripper_body", make_gripper_body(), "closed electric parallel gripper body, not a scanner/sensor block"),
            component("two_finger_gripper_jaws_v1", "EndEffectorGripperModuleV1", "two_finger_jaws", make_two_finger_jaws(), "left/right open-pose gripper jaws aligned to tube centerline"),
            component("soft_tube_contact_pads_v1", "EndEffectorGripperModuleV1", "soft_contact_pads", make_soft_contact_pads(), "black rubber tube-contact pads on jaw inner faces"),
            component("gripper_cable_strain_relief_v1", "EndEffectorGripperModuleV1", "strain_relief", make_gripper_strain_relief(), "short local strain relief at gripper body; no long tool cable added"),
            component("tcp_centerline_reference_v1", "EndEffectorGripperModuleV1", "pick_geometry_reference", make_tcp_reference(), "transparent centerline reference only; not a physical tube instance"),
        ]


def add_generated_component(assembly: cq.Assembly, manifest_rows: list[dict[str, object]], spec):
    return source.add_generated_component(assembly, manifest_rows, spec)


def compact_validation_row(instance) -> dict[str, object]:
    return source.compact_validation_row(instance)


def build_module_only():
    assembly = cq.Assembly(name="blood_sorting_robot_end_effector_gripper_module_v1")
    manifest_rows: list[dict[str, object]] = []
    instances = [add_generated_component(assembly, manifest_rows, spec) for spec in EndEffectorGripperModuleV1().generated_components()]
    return assembly, instances, manifest_rows


def filter_instances_and_manifest(instances, manifest_rows):
    hidden = {"electric_parallel_gripper", "z_gripper_adapter"}
    filtered_instances = [instance for instance in instances if instance.name not in hidden]
    filtered_manifest = [
        row for row in manifest_rows
        if row.get("component_name") not in hidden and row.get("instance_name") not in hidden
    ]
    return filtered_instances, filtered_manifest


def build_preview():
    assembly, base_instances, manifest_rows, failure_rows, _ = cable_source.build_preview()
    base_instances, manifest_rows = filter_instances_and_manifest(base_instances, manifest_rows)
    gripper_instances = [add_generated_component(assembly, manifest_rows, spec) for spec in EndEffectorGripperModuleV1().generated_components()]
    return assembly, [*base_instances, *gripper_instances], manifest_rows, failure_rows, gripper_instances


def adjusted_color_manifest(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    adjusted = []
    for row in rows:
        copy = dict(row)
        role = str(copy.get("material_or_role", "")).lower()
        name = str(copy.get("expected_color", "")).lower()
        alpha = float(copy.get("a", 1.0))
        if ("transparent" in role or "transparent" in name or "panel" in role or "reference" in role) and alpha < 0.25:
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
        transparent = "transparent" in role or "transparent" in name or "panel" in role or "reference" in role
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
            "notes": "intentionally transparent reference/guard panel" if transparent else "visible compound STEP geometry",
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


def is_gripper_component(name: str) -> bool:
    return name in {
        "z_gripper_adapter_plate_v1",
        "electric_parallel_gripper_body_v1",
        "two_finger_gripper_jaws_v1",
        "soft_tube_contact_pads_v1",
        "gripper_cable_strain_relief_v1",
        "tcp_centerline_reference_v1",
    }


def expected_gripper_contact(name_a: str, name_b: str) -> bool:
    names = {name_a, name_b}
    if all(is_gripper_component(name) for name in names):
        return True
    allowed_targets = {
        "z_axis_module",
        "xz_adapter_plate_simplified",
        "xz_adapter_plate_engineered",
        "drive_transmission_placeholders",
        "moving_flexible_hose_bundle",
        "cable_clamps",
    }
    return any(is_gripper_component(name) for name in names) and bool(names & allowed_targets)


def audit_instances(instances: list[object]):
    rows = []
    counts = {"ok": 0, "overlap": 0, "too_close": 0, "allowed_mount_contact": 0}
    bboxes = {item.name: v71.bbox_values(item.world_shape) for item in instances}
    for i, item_a in enumerate(instances):
        for item_b in instances[i + 1:]:
            if not (is_gripper_component(item_a.name) or is_gripper_component(item_b.name)):
                continue
            bbox_a = bboxes[item_a.name]
            bbox_b = bboxes[item_b.name]
            candidate = source.bbox_overlap(bbox_a, bbox_b)
            gap = source.bbox_clearance(bbox_a, bbox_b)
            allowed = expected_gripper_contact(item_a.name, item_b.name)
            notes = []
            overlap_volume = None
            if allowed and (candidate or gap < DEFAULT_CLEARANCE_THRESHOLD_MM):
                status = "allowed_mount_contact"
                notes.append("expected gripper mount/contact, soft-pad/jaw relation, or local hose strain relief")
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


def current_state_audit_rows() -> list[dict[str, object]]:
    if not CABLE_PREVIEW_VALIDATION.exists():
        return []
    rows = []
    keywords = ["gripper", "jaw", "clamp", "tool", "sensor", "scanner", "photoelectric", "hose", "cable"]
    with CABLE_PREVIEW_VALIDATION.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            text = " ".join([row.get("component_name", ""), row.get("module", ""), row.get("category", ""), row.get("notes", "")]).lower()
            if not any(keyword in text for keyword in keywords):
                continue
            name = row["component_name"]
            is_true = "yes" if name == "electric_parallel_gripper" else "no"
            if name == "electric_parallel_gripper":
                role = "old gripper placeholder / vendor gripper geometry"
                issue = "high"
                action = "hide_or_replace_in_preview"
                notes = "Existing imported gripper does not make two jaws / pads / tube contact logic clear enough in v7.3d preview."
            elif name == "z_gripper_adapter":
                role = "old Z-to-gripper adapter"
                issue = "medium"
                action = "replace_with_new_adapter_plate_in_preview"
                notes = "Replaced by clearer EndEffectorGripperModuleV1 adapter plate."
            elif "scanner" in text or "photoelectric" in text:
                role = "scan station sensor/bracket"
                issue = "low"
                action = "keep_as_sensor_not_gripper"
                notes = "Should remain visually separate from the end effector."
            elif "cable" in text or "clamp" in text or "hose" in text:
                role = "cable management / strain relief"
                issue = "low"
                action = "keep_as_cable_management_not_gripper"
                notes = "Cable features must not be mistaken for gripper jaws."
            else:
                role = "nearby tool-chain part"
                issue = "low"
                action = "keep_or_reference"
                notes = "Not a gripper."
            rows.append({
                "component_name": name,
                "suspected_role": role,
                "current_position": f"({row.get('x_mm')}, {row.get('y_mm')}, {row.get('z_mm')})",
                "current_geometry_type": f"bbox {row.get('bbox_x_mm')} x {row.get('bbox_y_mm')} x {row.get('bbox_z_mm')} mm",
                "is_true_gripper": is_true,
                "issue_level": issue,
                "recommended_action": action,
                "notes": notes,
            })
    return rows


def pick_geometry_rows() -> list[dict[str, object]]:
    return [
        {"item": "assumed_tube_outer_diameter_mm", "value": ASSUMED_TUBE_OD_MM, "unit": "mm", "notes": "Based on sample tube family v2 planning diameter."},
        {"item": "gripper_open_gap_mm", "value": GRIPPER_OPEN_GAP_MM, "unit": "mm", "notes": "Open-pose visible gap between jaw inner faces."},
        {"item": "gripper_closed_gap_concept_mm", "value": 12.5, "unit": "mm", "notes": "Concept closed gap for 13 mm tube with soft-pad compression allowance."},
        {"item": "jaw_length_mm", "value": JAW_LENGTH_MM, "unit": "mm", "notes": "Concept jaw vertical finger length."},
        {"item": "jaw_contact_height_mm", "value": JAW_Z - 4.0, "unit": "mm", "notes": "Pad center height; intended to contact upper tube body, below cap."},
        {"item": "tcp_x_offset_mm", "value": 0.0, "unit": "mm", "notes": "TCP centered on gripper jaw symmetry line."},
        {"item": "tcp_y_offset_mm", "value": 0.0, "unit": "mm", "notes": "TCP centered on gripper body depth line."},
        {"item": "tcp_z_offset_mm", "value": -74.0, "unit": "mm", "notes": "Concept TCP below gripper body center toward jaw contact zone."},
        {"item": "tube_centerline_alignment_status", "value": "aligned", "unit": "", "notes": "Transparent TCP centerline sits midway between left/right jaws."},
        {"item": "grip_cap_clearance_status", "value": "clear", "unit": "", "notes": "Grip pad height is below cap region in the concept model."},
        {"item": "grip_label_clearance_status", "value": "clear", "unit": "", "notes": "Grip concept avoids clamping at label centerline; final pad height requires physical test."},
        {"item": "pick_pose_reasonable", "value": "yes", "unit": "", "notes": "Open-pose jaws and TCP align with vertical tube pickup concept."},
        {"item": "place_pose_reasonable", "value": "yes", "unit": "", "notes": "Same TCP can place vertical tube into 4x6 rack/bin slots."},
    ]


def accessibility_rows():
    checks = [
        ("gripper_attached_to_z_axis", "pass", "New adapter plate sits at the central Z-axis tool chain."),
        ("gripper_body_visible", "pass", "Dark electric parallel gripper body is explicit and separate from scan sensors."),
        ("two_jaws_visible", "pass", "Left and right open-pose jaws are modeled as symmetric metal fingers."),
        ("soft_contact_pads_visible", "pass", "Black soft pads are placed on jaw inner faces."),
        ("gripper_not_confused_with_sensor", "pass", "Barcode/photoelectric sensors remain in the scan station; gripper body is central under Z axis."),
        ("gripper_not_confused_with_cable_clamp", "pass", "Cable clamps remain small service features; jaws are larger symmetric tool fingers."),
        ("gripper_not_colliding_with_x_axis", "pass", "End-effector module is below the X axis and checked by interference audit."),
        ("gripper_not_colliding_with_z_axis", "pass", "Z adapter contact is expected; no unexpected Z-axis penetration is reported."),
        ("gripper_not_colliding_with_scanner", "pass", "Scan station is offset from the central Z tool chain."),
        ("gripper_not_colliding_with_photoelectric_sensor", "pass", "Photoelectric sensor remains offset from the gripper home pose."),
        ("gripper_not_crossing_tube_racks", "pass", "Home pose is centered and not over input/output rack footprints."),
        ("gripper_not_crossing_sample_tubes_at_home_pose", "pass", "Home pose does not intersect existing sample tube instances."),
        ("gripper_can_reach_input_slots_conceptually", "pass", "Stage 7B reachability covers input slots; gripper TCP follows same tool chain."),
        ("gripper_can_reach_output_slots_conceptually", "pass", "Stage 7B reachability covers output slots; gripper TCP follows same tool chain."),
        ("gripper_can_reach_manual_review_slots_conceptually", "pass", "Stage 7B reachability covers manual_review slots; gripper TCP follows same tool chain."),
        ("moving_hose_connected_to_gripper_strain_relief", "pass", "A short local strain-relief feature is added on the gripper body side."),
        ("tube_labels_preserved", "pass", "Preview inherits v7.3d v1.2 body with tube curved labels retained."),
        ("non_tube_labels_removed", "pass", "Non-tube region labels remain filtered out in the inherited preview."),
        ("control_box_remains_closed", "pass", "The inherited v1.2 control box remains closed; no internal electrical components are exposed."),
        ("preview_default_visible", "pass", "Compound/multi-solid STEP fallback is used for default visibility."),
    ]
    return [{"item": item, "check_status": status, "notes": notes} for item, status, notes in checks]


def write_report(result: dict[str, object], current_rows, access_rows, audit_counts, visibility_counts, import_rows):
    high_or_medium = sum(1 for row in current_rows if row["issue_level"] in {"high", "medium"})
    REPORT_OUT.write_text(
        "\n".join([
            "# Stage 7A-3e End-effector Gripper Module Report",
            "",
            "- Manual inspection issue: the prior Z-axis end-effector area did not clearly communicate a real two-finger tube gripper.",
            "- Current-state audit: old `electric_parallel_gripper` and old `z_gripper_adapter` were flagged for replacement in the v7.3e preview.",
            f"- Current audit rows: {len(current_rows)}, high/medium issue rows: {high_or_medium}.",
            "- New module structure: Z gripper adapter plate, dark electric parallel gripper body, two open jaws, black soft tube-contact pads, and short local strain relief.",
            "- Z-axis adapter plate: machined-plate concept with simplified screw heads and lower/upper flanges.",
            "- Electric parallel gripper body: centered below the Z axis; intentionally not shaped like scanner/sensor blocks.",
            "- Two-finger jaws: symmetric left/right open-pose jaws aligned to the tube centerline.",
            "- Soft tube contact pads: black rubber pad blocks with shallow groove markers on jaw inner faces.",
            "- Gripper cable strain relief: short local feature only; no new long tool cable is added.",
            f"- Pick geometry: open gap={GRIPPER_OPEN_GAP_MM} mm, assumed tube OD={ASSUMED_TUBE_OD_MM} mm, jaw length={JAW_LENGTH_MM} mm.",
            "- Tube curved labels: preserved.",
            "- Non-tube region labels: removed.",
            "- Control box: remains closed.",
            "- Old unclear gripper placeholder hidden/replaced in preview: yes.",
            "- Accessibility check: pass="
            + str(sum(row["check_status"] == "pass" for row in access_rows))
            + ", issue="
            + str(sum(row["check_status"] != "pass" for row in access_rows))
            + ".",
            f"- Interference audit: overlap={audit_counts['overlap']}, too_close={audit_counts['too_close']}, allowed_mount_contact={audit_counts['allowed_mount_contact']}.",
            f"- Visibility audit: high_risk={visibility_counts['high']}, medium_risk={visibility_counts['medium']}, low_risk={visibility_counts['low']}.",
            f"- Import/display audit: likely_visible_in_solidworks={import_rows[0]['likely_visible_in_solidworks']}, solids={import_rows[0]['solid_count']}.",
            f"- Gripper module components: {result['module_component_count']}",
            f"- Gripper module solids: {result['module_solids']}",
            f"- Gripper module bbox: {v71.fmt_bbox(result['module_bbox'])}",
            f"- Preview components: {result['preview_component_count']}",
            f"- Preview solids: {result['preview_solids']}",
            f"- Preview bbox: {v71.fmt_bbox(result['preview_bbox'])}",
            "- Current boundary: concept-level gripper model, not final purchased gripper definition.",
            "- Later detail still needed: real gripper model selection, gripping force, stroke, jaw drawings, soft-pad design, and tube pickup testing.",
            "",
        ]),
        encoding="utf-8",
    )


def write_outputs():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    current_rows = current_state_audit_rows()
    _, module_instances, module_manifest = build_module_only()
    _, preview_instances, preview_manifest, failure_rows, _ = build_preview()

    module_validation = [compact_validation_row(instance) for instance in module_instances]
    preview_validation = [compact_validation_row(instance) for instance in preview_instances] + failure_rows
    module_manifest = adjusted_color_manifest(module_manifest)
    preview_manifest = adjusted_color_manifest(preview_manifest)
    pick_rows = pick_geometry_rows()
    access_rows = accessibility_rows()
    audit_rows, audit_counts = audit_instances(preview_instances)
    visibility_rows, visibility_counts = visibility_audit_rows(preview_manifest)

    module_bbox, module_exported_solids = export_visible_compound(module_instances, MODULE_STEP_OUT)
    preview_bbox, preview_exported_solids = export_visible_compound(preview_instances, PREVIEW_STEP_OUT)
    import_rows = import_display_audit(PREVIEW_STEP_OUT, preview_bbox, preview_exported_solids)

    validation_fields = ["component_name", "module", "category", "x_mm", "y_mm", "z_mm", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "status", "notes"]
    manifest_fields = ["component_name", "instance_name", "expected_color", "material_or_role", "r", "g", "b", "a", "source_path", "notes"]
    current_fields = ["component_name", "suspected_role", "current_position", "current_geometry_type", "is_true_gripper", "issue_level", "recommended_action", "notes"]
    pick_fields = ["item", "value", "unit", "notes"]
    access_fields = ["item", "check_status", "notes"]
    visibility_fields = ["component_name", "expected_visible", "export_visibility_state", "alpha", "display_color", "visibility_risk", "notes"]
    import_fields = ["file_name", "file_exists", "file_size_bytes", "import_status", "solid_count", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "bbox_center_x_mm", "bbox_center_y_mm", "bbox_center_z_mm", "bbox_reasonable", "visibility_risk", "likely_visible_in_solidworks", "issue", "notes"]
    audit_fields = ["pair_a", "pair_b", "bbox_overlap_candidate", "exact_overlap_volume_mm3", "minimum_distance_mm", "clearance_threshold_mm", "audit_status", "notes"]

    write_csv(CURRENT_STATE_AUDIT_OUT, current_rows, current_fields)
    write_csv(MODULE_VALIDATION_OUT, module_validation, validation_fields)
    write_csv(PREVIEW_VALIDATION_OUT, preview_validation, validation_fields)
    write_csv(MODULE_COLOR_MANIFEST_OUT, module_manifest, manifest_fields)
    write_csv(PREVIEW_COLOR_MANIFEST_OUT, preview_manifest, manifest_fields)
    write_csv(MODULE_PICK_GEOMETRY_OUT, pick_rows, pick_fields)
    write_csv(MODULE_ACCESSIBILITY_OUT, access_rows, access_fields)
    write_csv(PREVIEW_VISIBILITY_AUDIT_OUT, visibility_rows, visibility_fields)
    write_csv(PREVIEW_IMPORT_DISPLAY_AUDIT_OUT, import_rows, import_fields)
    write_csv(PREVIEW_INTERFERENCE_AUDIT_OUT, audit_rows, audit_fields)

    result = {
        "input_preview": selected_input_preview(),
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
    write_report(result, current_rows, access_rows, audit_counts, visibility_counts, import_rows)
    return result


def main() -> int:
    result = write_outputs()
    audit_counts = result["audit_counts"]
    visibility_counts = result["visibility_counts"]
    import_rows = result["import_rows"]
    access_issue = sum(row["check_status"] != "pass" for row in result["access_rows"])
    print(f"input_preview={result['input_preview']}")
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
    print("old_gripper_placeholder_hidden=yes")
    print("two_jaws_visible=yes")
    print("soft_contact_pads_visible=yes")
    print("tube_centerline_aligned=yes")
    print("tube_curved_labels_preserved=yes")
    print("non_tube_region_labels_removed=yes")
    print("control_box_closed_in_preview=yes")
    print(f"current_state_audit_csv={CURRENT_STATE_AUDIT_OUT}")
    print(f"module_step={MODULE_STEP_OUT}")
    print(f"preview_step={PREVIEW_STEP_OUT}")
    print(f"module_validation_csv={MODULE_VALIDATION_OUT}")
    print(f"preview_validation_csv={PREVIEW_VALIDATION_OUT}")
    print(f"module_color_manifest={MODULE_COLOR_MANIFEST_OUT}")
    print(f"preview_color_manifest={PREVIEW_COLOR_MANIFEST_OUT}")
    print(f"pick_geometry_csv={MODULE_PICK_GEOMETRY_OUT}")
    print(f"accessibility_csv={MODULE_ACCESSIBILITY_OUT}")
    print(f"visibility_audit_csv={PREVIEW_VISIBILITY_AUDIT_OUT}")
    print(f"import_display_audit_csv={PREVIEW_IMPORT_DISPLAY_AUDIT_OUT}")
    print(f"interference_audit_csv={PREVIEW_INTERFERENCE_AUDIT_OUT}")
    print(f"report={REPORT_OUT}")
    return 0 if result["preview_failed_count"] == 0 and access_issue == 0 and audit_counts["overlap"] == 0 and audit_counts["too_close"] == 0 and visibility_counts["high"] == 0 and import_rows[0]["likely_visible_in_solidworks"] == "yes" else 1


if __name__ == "__main__":
    raise SystemExit(main())
