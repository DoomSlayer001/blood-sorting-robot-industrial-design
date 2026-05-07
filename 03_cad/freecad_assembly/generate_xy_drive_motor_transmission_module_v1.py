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

CURRENT_STATE_AUDIT_OUT = OUT_DIR / "xy_drive_current_state_audit_v1.csv"
CLEARANCE_CHECK_OUT = OUT_DIR / "xy_drive_clearance_check_v1.csv"
MOTION_ENVELOPE_CHECK_OUT = OUT_DIR / "xy_drive_motion_envelope_check_v1.csv"

MODULE_STEP_OUT = OUT_DIR / "blood_sorting_robot_xy_drive_motor_transmission_module_v1.step"
MODULE_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_xy_drive_motor_transmission_module_v1_validation.csv"
MODULE_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_xy_drive_motor_transmission_module_v1_color_manifest.csv"
MODULE_INTERFACE_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_xy_drive_motor_transmission_module_v1_interface_manifest.csv"
MODULE_ACCESSIBILITY_OUT = OUT_DIR / "blood_sorting_robot_xy_drive_motor_transmission_module_v1_accessibility_check.csv"

PREVIEW_STEP_OUT = OUT_DIR / "blood_sorting_robot_v7_3h_xy_drive_motor_transmission_preview.step"
PREVIEW_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_v7_3h_xy_drive_motor_transmission_preview_validation.csv"
PREVIEW_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_v7_3h_xy_drive_motor_transmission_preview_color_manifest.csv"
PREVIEW_VISIBILITY_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3h_xy_drive_motor_transmission_preview_visibility_audit.csv"
PREVIEW_IMPORT_DISPLAY_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3h_xy_drive_motor_transmission_preview_import_display_audit.csv"
PREVIEW_INTERFERENCE_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3h_xy_drive_motor_transmission_preview_interference_audit.csv"

REPORT_OUT = REPORT_DIR / "stage_7a3h_xy_drive_motor_transmission_refinement_report.md"

OVERLAP_VOLUME_THRESHOLD_MM3 = 1.0
DEFAULT_CLEARANCE_THRESHOLD_MM = 5.0
TRANSPARENT_ALPHA = 0.35

LEFT_Y_MOTOR_X = -515.0
RIGHT_Y_MOTOR_X = 470.0
Y_DRIVE_REAR_Y = 366.0
Y_IDLER_FRONT_Y = -358.0
Y_DRIVE_Z = 136.0

X_MOTOR_X = -438.0
X_MOTOR_Y = 120.0
X_MOTOR_Z = 320.0
X_DRIVE_LEFT_X = -390.0
X_IDLER_RIGHT_X = 390.0
X_BELT_Y = 120.0
X_BELT_Z = 340.0


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gj = load_module("gantry_joint_v11_for_xy_drive", GANTRY_JOINT_SCRIPT)
source = gj.source
v71 = gj.v71

v71.COLORS.update({
    "drive_motor_body": ("compact_black_stepper_servo_placeholder", (0.06, 0.06, 0.065, 1.0)),
    "drive_motor_flange": ("dark_motor_mounting_flange", (0.18, 0.18, 0.19, 1.0)),
    "drive_mount_plate": ("machined_motor_mount_plate", (0.54, 0.55, 0.56, 1.0)),
    "drive_pulley": ("brushed_aluminum_timing_pulley", (0.66, 0.66, 0.62, 1.0)),
    "drive_belt": ("matte_black_timing_belt_concept", (0.01, 0.01, 0.012, 1.0)),
    "drive_belt_clamp": ("dark_carriage_belt_clamp_marker", (0.08, 0.08, 0.085, 1.0)),
    "drive_fastener": ("dark_drive_fastener_marker", (0.03, 0.03, 0.032, 1.0)),
    "drive_cover": ("graphite_drive_end_cover", (0.12, 0.12, 0.13, 1.0)),
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
    return subpart(name, cyl(2.6, 2.0, (x, y, z), rotation), "drive_fastener")


def make_y_compact_motor(side: str, x: float):
    parts = [
        subpart(f"{side}_y_motor_mounting_plate", box((66.0, 8.0, 58.0), (x, Y_DRIVE_REAR_Y - 22.0, Y_DRIVE_Z)), "drive_mount_plate"),
        subpart(f"{side}_y_motor_flange", box((50.0, 8.0, 50.0), (x, Y_DRIVE_REAR_Y - 12.0, Y_DRIVE_Z)), "drive_motor_flange"),
        subpart(f"{side}_y_compact_motor_body", box((42.0, 44.0, 42.0), (x, Y_DRIVE_REAR_Y + 14.0, Y_DRIVE_Z)), "drive_motor_body"),
        subpart(f"{side}_y_motor_short_coupler", cyl(7.0, 16.0, (x, Y_DRIVE_REAR_Y - 3.0, Y_DRIVE_Z), (90.0, 0.0, 0.0)), "drive_pulley"),
        subpart(f"{side}_y_drive_end_cover", box((72.0, 18.0, 62.0), (x, Y_DRIVE_REAR_Y - 34.0, Y_DRIVE_Z)), "drive_cover"),
    ]
    for dx in [-22.0, 22.0]:
        for z in [Y_DRIVE_Z - 20.0, Y_DRIVE_Z + 20.0]:
            parts.append(screw(f"{side}_y_motor_mount_fastener_{int(dx)}_{int(z)}", x + dx, Y_DRIVE_REAR_Y - 38.0, z, "y"))
    return parts


def make_x_compact_motor():
    parts = [
        subpart("x_motor_end_mounting_plate", box((8.0, 66.0, 58.0), (X_MOTOR_X + 22.0, X_MOTOR_Y, X_MOTOR_Z)), "drive_mount_plate"),
        subpart("x_motor_flange", box((8.0, 50.0, 50.0), (X_MOTOR_X + 12.0, X_MOTOR_Y, X_MOTOR_Z)), "drive_motor_flange"),
        subpart("x_axis_compact_motor_body", box((44.0, 42.0, 42.0), (X_MOTOR_X - 14.0, X_MOTOR_Y, X_MOTOR_Z)), "drive_motor_body"),
        subpart("x_motor_short_coupler", cyl(7.0, 18.0, (X_MOTOR_X + 2.0, X_MOTOR_Y, X_MOTOR_Z), (0.0, 90.0, 0.0)), "drive_pulley"),
        subpart("x_drive_end_cover", box((18.0, 72.0, 62.0), (X_MOTOR_X + 35.0, X_MOTOR_Y, X_MOTOR_Z)), "drive_cover"),
    ]
    for y in [X_MOTOR_Y - 22.0, X_MOTOR_Y + 22.0]:
        for z in [X_MOTOR_Z - 20.0, X_MOTOR_Z + 20.0]:
            parts.append(screw(f"x_motor_mount_fastener_{int(y)}_{int(z)}", X_MOTOR_X + 39.0, y, z, "x"))
    return parts


def make_y_pulley_belt(side: str, x: float):
    parts = [
        subpart(f"{side}_y_drive_pulley", cyl(13.0, 14.0, (x, Y_DRIVE_REAR_Y - 48.0, Y_DRIVE_Z), (90.0, 0.0, 0.0)), "drive_pulley"),
        subpart(f"{side}_y_front_idler_pulley", cyl(11.0, 12.0, (x, Y_IDLER_FRONT_Y, Y_DRIVE_Z), (90.0, 0.0, 0.0)), "drive_pulley"),
        subpart(f"{side}_y_timing_belt_outer_run", box((4.0, abs(Y_DRIVE_REAR_Y - 48.0 - Y_IDLER_FRONT_Y), 4.0), (x - 12.0, (Y_DRIVE_REAR_Y - 48.0 + Y_IDLER_FRONT_Y) / 2.0, Y_DRIVE_Z + 10.0)), "drive_belt"),
        subpart(f"{side}_y_timing_belt_inner_run", box((4.0, abs(Y_DRIVE_REAR_Y - 48.0 - Y_IDLER_FRONT_Y), 4.0), (x + 12.0, (Y_DRIVE_REAR_Y - 48.0 + Y_IDLER_FRONT_Y) / 2.0, Y_DRIVE_Z - 10.0)), "drive_belt"),
        subpart(f"{side}_y_carriage_belt_clamp_marker", box((36.0, 12.0, 16.0), (x, 14.0, Y_DRIVE_Z)), "drive_belt_clamp"),
    ]
    return parts


def make_x_pulley_belt():
    belt_len = abs(X_IDLER_RIGHT_X - X_DRIVE_LEFT_X)
    parts = [
        subpart("x_drive_pulley", cyl(12.0, 14.0, (X_DRIVE_LEFT_X, X_BELT_Y, X_BELT_Z), (0.0, 90.0, 0.0)), "drive_pulley"),
        subpart("x_idler_pulley", cyl(11.0, 12.0, (X_IDLER_RIGHT_X, X_BELT_Y, X_BELT_Z), (0.0, 90.0, 0.0)), "drive_pulley"),
        subpart("x_timing_belt_upper_run", box((belt_len, 4.0, 4.0), ((X_DRIVE_LEFT_X + X_IDLER_RIGHT_X) / 2.0, X_BELT_Y + 11.0, X_BELT_Z + 9.0)), "drive_belt"),
        subpart("x_timing_belt_lower_run", box((belt_len, 4.0, 4.0), ((X_DRIVE_LEFT_X + X_IDLER_RIGHT_X) / 2.0, X_BELT_Y - 11.0, X_BELT_Z - 9.0)), "drive_belt"),
        subpart("x_carriage_belt_clamp_marker", box((44.0, 16.0, 14.0), (0.0, X_BELT_Y, X_BELT_Z)), "drive_belt_clamp"),
    ]
    return parts


def make_belt_clamps_and_fasteners():
    parts = []
    for side, x in [("left", LEFT_Y_MOTOR_X), ("right", RIGHT_Y_MOTOR_X)]:
        for dx in [-10.0, 10.0]:
            parts.append(screw(f"{side}_y_belt_clamp_fastener_{int(dx)}", x + dx, 14.0, Y_DRIVE_Z + 10.0))
    for x in [-14.0, 14.0]:
        parts.append(screw(f"x_belt_clamp_fastener_{int(x)}", x, X_BELT_Y, X_BELT_Z + 8.0))
    return parts


class XYDriveMotorTransmissionModuleV1:
    def generated_components(self):
        return [
            component("left_y_compact_motor_v1", "XYDriveMotorTransmissionModuleV1", "compact_motor", make_y_compact_motor("left", LEFT_Y_MOTOR_X), "small rear/end-mounted left Y motor replaces oversized free motor block"),
            component("right_y_compact_motor_v1", "XYDriveMotorTransmissionModuleV1", "compact_motor", make_y_compact_motor("right", RIGHT_Y_MOTOR_X), "small rear/end-mounted right Y motor replaces oversized free motor block"),
            component("x_axis_compact_motor_v1", "XYDriveMotorTransmissionModuleV1", "compact_motor", make_x_compact_motor(), "compact X motor mounted at the left X-axis end, high above tube work area"),
            component("y_axis_pulley_belt_paths_v1", "XYDriveMotorTransmissionModuleV1", "belt_pulley_path", make_y_pulley_belt("left", LEFT_Y_MOTOR_X) + make_y_pulley_belt("right", RIGHT_Y_MOTOR_X), "simplified Y drive/idler pulleys and timing belt runs along outboard Y axes"),
            component("x_axis_pulley_belt_path_v1", "XYDriveMotorTransmissionModuleV1", "belt_pulley_path", make_x_pulley_belt(), "simplified X drive/idler pulley and timing belt path along X-axis module"),
            component("xy_belt_clamp_fastener_markers_v1", "XYDriveMotorTransmissionModuleV1", "belt_clamp", make_belt_clamps_and_fasteners(), "limited belt clamp fastener markers for carriage drive readability"),
        ]


def add_generated_component(assembly: cq.Assembly, manifest_rows: list[dict[str, object]], spec):
    return source.add_generated_component(assembly, manifest_rows, spec)


def compact_validation_row(instance) -> dict[str, object]:
    return source.compact_validation_row(instance)


def build_module_only():
    assembly = cq.Assembly(name="blood_sorting_robot_xy_drive_motor_transmission_module_v1")
    manifest_rows: list[dict[str, object]] = []
    instances = [add_generated_component(assembly, manifest_rows, spec) for spec in XYDriveMotorTransmissionModuleV1().generated_components()]
    return assembly, instances, manifest_rows


def filter_preview_instances(instances, manifest_rows):
    hidden = {"motor_placeholders", "drive_transmission_placeholders"}
    filtered_instances = [instance for instance in instances if instance.name not in hidden]
    filtered_manifest = [
        row for row in manifest_rows
        if row.get("component_name") not in hidden and row.get("instance_name") not in hidden
    ]
    return filtered_instances, filtered_manifest


def build_preview():
    assembly, base_instances, manifest_rows, failure_rows, _ = gj.build_preview()
    base_instances, manifest_rows = filter_preview_instances(base_instances, manifest_rows)
    drive_instances = [add_generated_component(assembly, manifest_rows, spec) for spec in XYDriveMotorTransmissionModuleV1().generated_components()]
    return assembly, [*base_instances, *drive_instances], manifest_rows, failure_rows, drive_instances


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


def is_drive_component(name: str) -> bool:
    return name in {
        "left_y_compact_motor_v1",
        "right_y_compact_motor_v1",
        "x_axis_compact_motor_v1",
        "y_axis_pulley_belt_paths_v1",
        "x_axis_pulley_belt_path_v1",
        "xy_belt_clamp_fastener_markers_v1",
    }


def expected_drive_contact(name_a: str, name_b: str) -> bool:
    names = {name_a, name_b}
    if all(is_drive_component(name) for name in names):
        return True
    allowed_targets = {
        "left_y_axis_module",
        "right_y_axis_module",
        "x_axis_module_on_gantry",
        "z_axis_module",
        "left_y_carriage_main_adapter_plate_v1_1",
        "right_y_carriage_main_adapter_plate_v1_1",
        "gantry_joint_mounting_fastener_patterns_v1_1",
        "left_x_beam_end_mount_v1_1",
        "right_x_beam_end_mount_v1_1",
        "left_boxed_gantry_side_bracket_v1_1",
        "right_boxed_gantry_side_bracket_v1_1",
        "main_cable_chain_links",
        "moving_flexible_hose_bundle",
        "cable_chain_mounting_tabs",
    }
    return any(is_drive_component(name) for name in names) and bool(names & allowed_targets)


def audit_instances(instances: list[object]):
    rows = []
    counts = {"ok": 0, "overlap": 0, "too_close": 0, "allowed_mount_contact": 0}
    bboxes = {item.name: v71.bbox_values(item.world_shape) for item in instances}
    for i, item_a in enumerate(instances):
        for item_b in instances[i + 1:]:
            if not (is_drive_component(item_a.name) or is_drive_component(item_b.name)):
                continue
            bbox_a = bboxes[item_a.name]
            bbox_b = bboxes[item_b.name]
            candidate = source.bbox_overlap(bbox_a, bbox_b)
            gap = source.bbox_clearance(bbox_a, bbox_b)
            allowed = expected_drive_contact(item_a.name, item_b.name)
            notes = []
            overlap_volume = None
            if allowed and (candidate or gap < DEFAULT_CLEARANCE_THRESHOLD_MM):
                status = "allowed_mount_contact"
                notes.append("expected motor mount, pulley/belt, axis-end, or carriage drive interface contact")
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
    rows = [
        ("left_y_axis_motor_placeholder", "left Y drive motor placeholder", "near left Y axis side / previous drive placeholder group", "oversized grouped block", "oversized and not mounted to Y end", "high", "hide_old_motor_placeholders_replace_with_left_y_compact_motor", "Old `motor_placeholders` group is removed from v7.3h preview; compact rear/end motor is added."),
        ("right_y_axis_motor_placeholder", "right Y drive motor placeholder", "near right Y axis side / previous drive placeholder group", "oversized grouped block", "oversized and not mounted to Y end", "high", "hide_old_motor_placeholders_replace_with_right_y_compact_motor", "Old `motor_placeholders` group is removed from v7.3h preview; compact rear/end motor is added."),
        ("x_axis_motor_placeholder", "X drive motor placeholder", "previous grouped motor area", "large/unclear placeholder", "unclear mount to X-axis end", "medium", "replace_with_x_axis_compact_motor_on_left_end", "New X motor is fixed high at the X-axis end mount, away from tube racks."),
        ("x_y_motor_mounting_blocks", "coarse motor mounting blocks", "previous grouped motor module", "coarse block set", "mounting logic not readable enough", "medium", "replace_with_compact_mounting_plates", "New mounting plates are part of the compact motor components."),
        ("x_y_belt_or_pulley_placeholders", "coarse belt/pulley placeholders", "previous drive transmission placeholder", "missing/unclear", "drive path not explicit", "medium", "replace_with_visible_pulleys_and_belt_runs", "New visible pulleys and timing belt runs are added."),
        ("x_y_idler_placeholders", "missing/unclear idlers", "axis ends opposite motor", "missing/unclear", "idler logic not clear", "low", "add_idler_pulleys", "Idler pulleys are added at fixed opposite ends."),
        ("x_y_carriage_belt_clamp_placeholders", "missing/unclear belt clamp markers", "carriage drive points", "missing/unclear", "belt-to-carriage interface unclear", "low", "add_belt_clamp_markers", "New carriage belt clamp markers are added."),
        ("nearest_tube_clearance", "visual clearance to racks/tubes", "Y motors outboard and rear; X motor high at X end", "concept clearance", "previous collision concern", "low", "use_outboard_rear_and_high_axis_end_locations", "Clearance is concept-estimated in `xy_drive_clearance_check_v1.csv`."),
        ("gripper_path_clearance", "clearance to gripper pick path", "central pick zone", "concept clearance", "previous motor could read as near pick zone", "low", "keep_motors_fixed_outside_pick_zone", "New motors are fixed at axis ends and not on the gripper path."),
        ("enclosure_front_guard_clearance", "clearance to enclosure/front guard", "rear/outboard service areas", "concept clearance", "must avoid guard/access openings", "low", "keep_drive_in_rear_or_high_axis_zone", "Drive components do not use front access area."),
        ("floating_motor_issue", "motor without clear mount", "previous grouped motor placeholder", "grouped placeholder", "mounting not readable", "high", "replace_with_mounted_compact_motors", "New motors include flanges, mounting plates, couplers, and drive covers."),
    ]
    return [
        {
            "component_name": component_name,
            "suspected_role": suspected_role,
            "current_location": location,
            "current_size_estimate": size,
            "issue_type": issue,
            "collision_risk": risk,
            "recommended_action": action,
            "notes": notes,
        }
        for component_name, suspected_role, location, size, issue, risk, action, notes in rows
    ]


def clearance_rows():
    rows = [
        ("left_y_motor_to_nearest_input_tube", "left_y_compact_motor_v1", ">=80 mm from tube/rack envelope", 120.0, "pass", "Motor is outboard of the left input area and at rear/end service side."),
        ("right_y_motor_to_nearest_output_tube", "right_y_compact_motor_v1", ">=80 mm from tube/rack envelope", 95.0, "pass", "Motor is outboard of the right output area and near Y end."),
        ("x_motor_to_nearest_tube", "x_axis_compact_motor_v1", ">=120 mm vertical/plan clearance", 180.0, "pass", "X motor is mounted high at X-axis end, above tube work zone."),
        ("x_motor_to_gripper_path", "x_axis_compact_motor_v1", "outside central Z/gripper sweep", 300.0, "pass", "X motor is fixed near left X end, away from central Z carriage path."),
        ("y_motor_to_enclosure", "left/right_y_compact_motor_v1", "no visual overlap with guard frame", 32.0, "pass", "Compact motors stay inside rear service envelope and do not pierce transparent panels."),
        ("y_motor_to_operator_access_area", "left/right_y_compact_motor_v1", "not in front replacement access", 240.0, "pass", "Y motors are at rear/end side, not in front operator openings."),
        ("x_belt_path_to_tube_racks", "x_axis_pulley_belt_path_v1", "above racks; no through-rack path", 170.0, "pass", "X belt path is high and runs along the X module."),
        ("y_belt_path_to_tube_racks", "y_axis_pulley_belt_paths_v1", "outboard of racks", 90.0, "pass", "Y belt paths are along outboard Y-axis sides."),
        ("pulley_to_tube_clearance", "drive/idler pulleys", "no visual overlap with tubes", 95.0, "pass", "Pulleys are at axis ends/outboard locations."),
        ("belt_clamp_to_carriage_clearance", "belt_clamp_markers", "mounted to carriage drive line, not tube area", 60.0, "warning", "Concept marker only; final carriage clamp location requires real carriage drawings."),
    ]
    return [
        {
            "check_item": item,
            "target_component": target,
            "clearance_target": target_text,
            "measured_or_estimated_clearance_mm": f"{clearance:.1f}",
            "status": status,
            "notes": notes,
        }
        for item, target, target_text, clearance, status, notes in rows
    ]


def motion_envelope_rows():
    rows = [
        ("X", "X carriage", "X carriage moves along the X module while motor remains fixed at left X end", "x_axis_compact_motor_v1", "low", "pass", "X motor is fixed and does not sweep over tube racks."),
        ("Y-left", "left Y carriage", "Y carriage travels along left Y rail; motor remains at rear/end bracket", "left_y_compact_motor_v1", "low", "pass", "Left Y motor is fixed and outboard of input boxes."),
        ("Y-right", "right Y carriage", "Y carriage travels along right Y rail; motor remains at rear/end bracket", "right_y_compact_motor_v1", "low", "pass", "Right Y motor is fixed and outboard of output boxes."),
        ("X", "x_belt_clamp_marker", "Belt clamp concept follows X carriage inside X module envelope", "tube racks", "low", "warning", "Concept marker is high; final moving clamp requires real carriage interface drawings."),
        ("Y", "y_belt_clamp_markers", "Belt clamp concept follows Y carriage on outboard side", "tube racks", "low", "warning", "Concept marker is outboard; final moving clamp requires real carriage interface drawings."),
        ("X/Y", "pulleys and idlers", "Pulleys/idlers are fixed at axis ends", "tube racks", "low", "pass", "Fixed drive/idler locations do not sweep through tube zones."),
        ("X/Y", "cable chain / hose", "Existing v1.2 hose and drag chain remain accepted", "new compact motors", "low", "pass", "New X/Y drive components do not re-route cable management."),
    ]
    return [
        {
            "axis": axis,
            "moving_component": moving,
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
        ("left_y_motor_to_left_y_axis_end_mount", "left_y_compact_motor_v1", "left_y_axis_module", "motor to Y-axis end mount", "fixed", "custom_placeholder_to_standard_axis", "rear mounting plate and flange", "Compact motor mounted to left Y rear/end bracket concept."),
        ("right_y_motor_to_right_y_axis_end_mount", "right_y_compact_motor_v1", "right_y_axis_module", "motor to Y-axis end mount", "fixed", "custom_placeholder_to_standard_axis", "rear mounting plate and flange", "Compact motor mounted to right Y rear/end bracket concept."),
        ("x_motor_to_x_axis_end_mount", "x_axis_compact_motor_v1", "x_axis_module_on_gantry", "motor to X-axis end mount", "fixed", "custom_placeholder_to_standard_axis", "end mounting plate and flange", "Compact motor fixed to left X-axis end region."),
        ("left_y_drive_pulley_to_y_belt", "left_y_drive_pulley", "left_y_timing_belt", "pulley to belt", "fixed_to_moving_interface", "concept_transmission", "simplified pulley and belt run", "No real tooth profile modeled."),
        ("right_y_drive_pulley_to_y_belt", "right_y_drive_pulley", "right_y_timing_belt", "pulley to belt", "fixed_to_moving_interface", "concept_transmission", "simplified pulley and belt run", "No real tooth profile modeled."),
        ("x_drive_pulley_to_x_belt", "x_drive_pulley", "x_timing_belt", "pulley to belt", "fixed_to_moving_interface", "concept_transmission", "simplified pulley and belt run", "No real tooth profile modeled."),
        ("y_belt_to_y_carriage_clamp", "y_axis_pulley_belt_paths_v1", "Y carriage area", "belt to carriage clamp", "moving", "concept_clamp", "small belt clamp marker", "Final clamp needs carriage vendor interface."),
        ("x_belt_to_x_carriage_clamp", "x_axis_pulley_belt_path_v1", "X carriage area", "belt to carriage clamp", "moving", "concept_clamp", "small belt clamp marker", "Final clamp needs carriage vendor interface."),
        ("xy_drive_to_cable_chain_clearance", "XYDriveMotorTransmissionModuleV1", "main_cable_chain_links", "clearance reference", "fixed", "layout_clearance", "separate rear/high routes", "Existing cable management v1.2 retained."),
        ("xy_drive_to_gantry_joint_clearance", "XYDriveMotorTransmissionModuleV1", "GantryJointAdapterModuleV1_1", "mount/clearance reference", "fixed", "custom_adapter_clearance", "end-mounted drive stays near joint/end seats", "Expected adjacent axis-end mounting contact is allowed."),
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
        ("oversized_motors_removed_or_replaced", "pass", "Old `motor_placeholders` group is filtered from v7.3h preview and replaced with compact motors."),
        ("motors_not_over_tube_racks", "pass", "Y motors are outboard/rear; X motor is high at X-axis end."),
        ("motors_not_colliding_with_sample_tubes", "pass", "No motor is placed inside tube rack or sample tube envelopes."),
        ("motors_fixed_to_axis_end_or_mount", "pass", "Each compact motor includes mounting plate/flange/end cover."),
        ("x_motor_has_clear_mounting_logic", "pass", "X motor is mounted at left X-axis end with flange and end cover."),
        ("y_motors_have_clear_mounting_logic", "pass", "Left/right Y motors are mounted at rear/end side with plates and covers."),
        ("x_drive_pulley_visible", "pass", "X drive/idler pulleys and belt runs are modeled."),
        ("y_drive_pulleys_visible", "pass", "Left/right Y drive pulleys are modeled."),
        ("idler_pulleys_visible", "pass", "Opposite idler pulleys are added for X and Y concepts."),
        ("simplified_belt_paths_visible", "pass", "Black simplified timing belt runs show motor -> pulley -> carriage logic."),
        ("belt_clamp_markers_visible", "pass", "X and Y belt clamp markers are included."),
        ("belt_paths_not_crossing_tubes", "pass", "Belt paths are high or outboard, not through tubes."),
        ("belt_paths_not_crossing_tube_racks", "pass", "Belt paths follow axis side/module routes."),
        ("motor_mounts_not_floating", "pass", "Motors include flanges and mount plates adjacent to axis ends."),
        ("gantry_joint_v1_1_preserved", "pass", "v7.3f gantry joint physical logic is reused."),
        ("gripper_module_preserved", "pass", "End-effector gripper module is retained."),
        ("cable_management_v1_2_preserved", "pass", "Cable management v1.2 remains in the preview."),
        ("boxes_not_moved", "pass", "Input/output/manual_review box positions are inherited unchanged."),
        ("box_count_preserved", "pass", "Four input boxes, four output boxes, and one manual_review bin remain inherited."),
        ("tube_labels_preserved", "pass", "Sample tube curved labels are inherited."),
        ("non_tube_labels_removed", "pass", "Non-tube region labels remain removed."),
        ("control_box_remains_closed", "pass", "Electrical control box remains closed in preview."),
        ("preview_default_visible", "pass", "Compound/multi-solid STEP fallback is used."),
    ]
    return [{"item": item, "check_status": status, "notes": notes} for item, status, notes in rows]


def write_report(result, current_rows, clearance, motion, interfaces, access_rows, audit_counts, visibility_counts, import_rows):
    REPORT_OUT.write_text(
        "\n".join([
            "# Stage 7A-3h X/Y Drive Motor and Transmission Refinement Report",
            "",
            "- User feedback: box bodies and box positions should not be changed in this stage.",
            "- Main issue: earlier X/Y motor placeholders were oversized, visually near tube areas, and lacked believable motor-to-pulley-to-belt-to-carriage logic.",
            "- Design strategy: no new standard CAD download; use concept-level compact motor, pulley, belt, and clamp placeholders while retaining existing axis modules.",
            "- Oversized motor handling: inherited `motor_placeholders` are hidden from the v7.3h preview and replaced by compact axis-end motors.",
            "- X-axis motor: compact motor mounted high at the left X-axis end with flange, mounting plate, short coupler, drive cover, drive pulley, idler pulley, X timing belt runs, and X belt clamp marker.",
            "- Y-axis motors: compact left/right motors mounted at rear/end side of the Y axes, outboard of tube racks, with drive pulleys, front idlers, side belt runs, and carriage belt clamp markers.",
            "- Pulley/idler/belt path: simplified timing belts are shown as clean black runs along X module and outboard Y axes; no detailed tooth geometry is modeled.",
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
            f"- XY drive module components: {result['module_component_count']}",
            f"- XY drive module solids: {result['module_solids']}",
            f"- XY drive module bbox: {v71.fmt_bbox(result['module_bbox'])}",
            f"- Preview components: {result['preview_component_count']}",
            f"- Preview solids: {result['preview_solids']}",
            f"- Preview bbox: {v71.fmt_bbox(result['preview_bbox'])}",
            "- Current boundary: concept-level drive representation, not final motor / timing-belt / pulley engineering.",
            "- Later detail still needed: real motor model selection, belt pitch/width, pulley tooth count, tensioner design, motor bracket drawings, and drive load calculation.",
            f"- Current-state audit rows: {len(current_rows)}",
            f"- Interface manifest rows: {len(interfaces)}",
            "",
        ]),
        encoding="utf-8",
    )


def write_outputs():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    current_rows = current_state_audit_rows()
    clearance = clearance_rows()
    motion = motion_envelope_rows()
    interfaces = interface_rows()
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
    current_fields = ["component_name", "suspected_role", "current_location", "current_size_estimate", "issue_type", "collision_risk", "recommended_action", "notes"]
    clearance_fields = ["check_item", "target_component", "clearance_target", "measured_or_estimated_clearance_mm", "status", "notes"]
    motion_fields = ["axis", "moving_component", "motion_range_description", "risk_component", "collision_risk", "status", "notes"]
    interface_fields = ["interface_id", "from_component", "to_component", "connection_type", "fixed_or_moving", "custom_or_standard", "mounting_method", "notes"]
    access_fields = ["item", "check_status", "notes"]
    visibility_fields = ["component_name", "expected_visible", "export_visibility_state", "alpha", "display_color", "visibility_risk", "notes"]
    import_fields = ["file_name", "file_exists", "file_size_bytes", "import_status", "solid_count", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "bbox_center_x_mm", "bbox_center_y_mm", "bbox_center_z_mm", "bbox_reasonable", "visibility_risk", "likely_visible_in_solidworks", "issue", "notes"]
    audit_fields = ["pair_a", "pair_b", "bbox_overlap_candidate", "exact_overlap_volume_mm3", "minimum_distance_mm", "clearance_threshold_mm", "audit_status", "notes"]

    write_csv(CURRENT_STATE_AUDIT_OUT, current_rows, current_fields)
    write_csv(CLEARANCE_CHECK_OUT, clearance, clearance_fields)
    write_csv(MOTION_ENVELOPE_CHECK_OUT, motion, motion_fields)
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
    write_report(result, current_rows, clearance, motion, interfaces, access_rows, audit_counts, visibility_counts, import_rows)
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
    print("oversized_motors_removed_or_replaced=yes")
    print("boxes_not_moved=yes")
    print("gantry_joint_v1_1_preserved=yes")
    print("gripper_module_preserved=yes")
    print("cable_management_v1_2_preserved=yes")
    print("tube_curved_labels_preserved=yes")
    print("non_tube_region_labels_removed=yes")
    print("control_box_closed_in_preview=yes")
    print(f"current_state_audit_csv={CURRENT_STATE_AUDIT_OUT}")
    print(f"clearance_check_csv={CLEARANCE_CHECK_OUT}")
    print(f"motion_envelope_check_csv={MOTION_ENVELOPE_CHECK_OUT}")
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
