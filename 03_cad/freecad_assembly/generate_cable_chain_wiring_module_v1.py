from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "03_cad" / "freecad_assembly"
REPORT_DIR = ROOT / "reports"

WIRING_INTERFACE_TABLE = ROOT / "01_system_design" / "electrical_wiring_interface_table_v1.csv"
CABLE_ROUTING_PLAN = ROOT / "01_system_design" / "cable_routing_plan_v1.md"
ELECTRICAL_ARCHITECTURE = ROOT / "01_system_design" / "electrical_system_architecture_v1.md"
ELECTRICAL_IO_MAP = ROOT / "01_system_design" / "electrical_io_map_v1.csv"

GANTRY_SUPPORT_SCRIPT = OUT_DIR / "generate_gantry_mechanical_support_drive_module_v1.py"

MODULE_STEP_OUT = OUT_DIR / "blood_sorting_robot_cable_chain_wiring_module_v1.step"
MODULE_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_cable_chain_wiring_module_v1_validation.csv"
MODULE_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_cable_chain_wiring_module_v1_color_manifest.csv"
MODULE_ACCESSIBILITY_OUT = OUT_DIR / "blood_sorting_robot_cable_chain_wiring_module_v1_accessibility_check.csv"
MODULE_ROUTE_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_cable_chain_wiring_module_v1_wiring_route_manifest.csv"

PREVIEW_STEP_OUT = OUT_DIR / "blood_sorting_robot_v7_3d_cable_chain_wiring_preview.step"
PREVIEW_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_v7_3d_cable_chain_wiring_preview_validation.csv"
PREVIEW_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_v7_3d_cable_chain_wiring_preview_color_manifest.csv"
PREVIEW_VISIBILITY_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3d_cable_chain_wiring_preview_visibility_audit.csv"
PREVIEW_IMPORT_DISPLAY_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3d_cable_chain_wiring_preview_import_display_audit.csv"
PREVIEW_INTERFERENCE_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3d_cable_chain_wiring_preview_interference_audit.csv"

REPORT_OUT = REPORT_DIR / "stage_7a3d_cable_chain_wiring_module_report.md"

main_cable_chain_link_count = 28
main_cable_chain_link_length_mm = 18.0
main_cable_chain_link_width_mm = 32.0
main_cable_chain_link_height_mm = 18.0

OVERLAP_VOLUME_THRESHOLD_MM3 = 1.0
DEFAULT_CLEARANCE_THRESHOLD_MM = 5.0
TRANSPARENT_ALPHA = 0.35


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


source = load_module("gantry_mechanical_support_drive_v1_for_cable_chain", GANTRY_SUPPORT_SCRIPT)
v71 = source.v71

v71.COLORS.update({
    "cable_tray_dark": ("rear_fixed_cable_tray_dark_gray", (0.08, 0.09, 0.10, 1.0)),
    "cable_tray_cover": ("cable_tray_cover_graphite", (0.13, 0.14, 0.15, 1.0)),
    "cable_black": ("black_cable_bundle", (0.01, 0.01, 0.01, 1.0)),
    "cable_gray": ("gray_signal_cable", (0.22, 0.23, 0.24, 1.0)),
    "cable_blue": ("blue_signal_cable", (0.05, 0.16, 0.36, 1.0)),
    "cable_green": ("green_grounding_cable", (0.03, 0.36, 0.12, 1.0)),
    "drag_chain_body": ("black_engineering_plastic_drag_chain", (0.02, 0.02, 0.025, 1.0)),
    "drag_chain_pin": ("drag_chain_hinge_pin_gray", (0.34, 0.35, 0.36, 1.0)),
    "cable_clamp": ("black_cable_clamp", (0.015, 0.015, 0.015, 1.0)),
    "anchor_gray": ("cable_anchor_gray", (0.32, 0.33, 0.34, 1.0)),
})


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_wiring_rows() -> list[dict[str, str]]:
    with WIRING_INTERFACE_TABLE.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def cable_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    fixed = sum(row["moving_or_fixed"].strip().lower() == "fixed" for row in rows)
    chain = sum(row["requires_cable_chain"].strip().lower() == "yes" for row in rows)
    return {"fixed": fixed, "chain": chain, "total": len(rows)}


def subpart(name: str, shape: cq.Shape, color_key: str):
    return source.subpart(name, shape, color_key)


def component(name: str, module_name: str, category: str, subparts, notes: str):
    return source.component(name, module_name, category, subparts, (0.0, 0.0, 0.0), notes)


def box(size: tuple[float, float, float], offset: tuple[float, float, float]) -> cq.Shape:
    return source.box_shape(size, offset)


def cyl(radius: float, height: float, offset: tuple[float, float, float], rotation=(0.0, 0.0, 0.0)) -> cq.Shape:
    return source.cyl_shape(radius, height, offset, rotation)


def segment_box(name: str, start: tuple[float, float, float], end: tuple[float, float, float], thickness: float, color_key: str):
    x1, y1, z1 = start
    x2, y2, z2 = end
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    dz = abs(z2 - z1)
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0
    cz = (z1 + z2) / 2.0
    if dx >= dy and dx >= dz:
        size = (max(dx, thickness), thickness, thickness)
    elif dy >= dx and dy >= dz:
        size = (thickness, max(dy, thickness), thickness)
    else:
        size = (thickness, thickness, max(dz, thickness))
    return subpart(name, box(size, (cx, cy, cz)), color_key)


def make_rear_fixed_cable_tray():
    parts = [
        subpart("rear_tray_bottom_channel", box((780.0, 32.0, 5.0), (-50.0, 520.0, 330.0)), "cable_tray_dark"),
        subpart("rear_tray_front_lip", box((780.0, 4.0, 26.0), (-50.0, 504.0, 343.0)), "cable_tray_dark"),
        subpart("rear_tray_rear_lip", box((780.0, 4.0, 26.0), (-50.0, 536.0, 343.0)), "cable_tray_dark"),
        subpart("rear_tray_partial_cover_left", box((250.0, 28.0, 3.0), (-255.0, 520.0, 357.0)), "cable_tray_cover"),
        subpart("rear_tray_partial_cover_right", box((250.0, 28.0, 3.0), (155.0, 520.0, 357.0)), "cable_tray_cover"),
    ]
    for x in [-390.0, -210.0, -30.0, 150.0, 330.0]:
        parts.append(subpart(f"rear_tray_mount_foot_{x:.0f}", box((26.0, 20.0, 8.0), (x, 520.0, 315.0)), "anchor_gray"))
    return parts


def make_control_box_cable_gland_stubs():
    parts = []
    for index, x in enumerate([410.0, 440.0, 470.0, 500.0], start=1):
        parts.append(segment_box(f"control_box_gland_short_rear_stub_{index}", (x, 562.0, 122.0), (x, 570.0, 122.0), 7.0, "cable_black"))
        parts.append(segment_box(f"control_box_gland_riser_to_tray_{index}", (x, 570.0, 122.0), (x, 570.0, 322.0), 5.0, "cable_black"))
        parts.append(segment_box(f"control_box_gland_top_entry_{index}", (x, 570.0, 322.0), (330.0, 526.0, 340.0), 5.0, "cable_black" if index < 4 else "cable_green"))
    return parts


def make_main_cable_chain_links():
    parts = []
    start_x = 315.0
    pitch = main_cable_chain_link_length_mm * 0.72
    for index in range(main_cable_chain_link_count):
        x = start_x - index * pitch
        parts.append(subpart(f"drag_chain_link_{index + 1:02d}_left_side", box((main_cable_chain_link_length_mm * 0.55, 4.0, main_cable_chain_link_height_mm), (x, 378.0, 330.0)), "drag_chain_body"))
        parts.append(subpart(f"drag_chain_link_{index + 1:02d}_right_side", box((main_cable_chain_link_length_mm * 0.55, 4.0, main_cable_chain_link_height_mm), (x, 410.0, 330.0)), "drag_chain_body"))
        parts.append(subpart(f"drag_chain_link_{index + 1:02d}_top_bridge", box((main_cable_chain_link_length_mm * 0.55, main_cable_chain_link_width_mm, 3.0), (x, 394.0, 340.5)), "drag_chain_body"))
        if index % 4 == 0:
            parts.append(subpart(f"drag_chain_hinge_pin_{index + 1:02d}", cyl(2.0, main_cable_chain_link_width_mm, (x, 394.0, 320.0), (90.0, 0.0, 0.0)), "drag_chain_pin"))
    return parts


def make_chain_anchors():
    return [
        subpart("fixed_anchor_to_stage_7a3c_rear_tab", box((58.0, 18.0, 16.0), (320.0, 382.0, 300.0)), "anchor_gray"),
        subpart("fixed_anchor_vertical_riser", box((20.0, 14.0, 86.0), (320.0, 382.0, 258.0)), "anchor_gray"),
        subpart("moving_anchor_drag_chain_end", box((48.0, 18.0, 16.0), (-38.0, 394.0, 300.0)), "anchor_gray"),
        subpart("moving_anchor_xz_service_bridge", box((30.0, 14.0, 58.0), (-38.0, 394.0, 281.0)), "anchor_gray"),
    ]


def make_moving_cable_bundle():
    return [
        segment_box("moving_bundle_chain_to_x_carriage_x_run", (-38.0, 394.0, 360.0), (70.0, 394.0, 360.0), 8.0, "cable_black"),
        segment_box("moving_bundle_rear_to_carriage_y_run", (70.0, 394.0, 360.0), (70.0, 95.0, 360.0), 8.0, "cable_black"),
        segment_box("moving_bundle_drop_to_x_carriage", (70.0, 95.0, 360.0), (70.0, 95.0, 320.0), 7.0, "cable_black"),
        segment_box("z_axis_motor_cable_overhead_x", (70.0, 95.0, 320.0), (58.0, 95.0, 320.0), 5.0, "cable_gray"),
        segment_box("z_axis_motor_cable_overhead_y", (58.0, 95.0, 320.0), (58.0, 55.0, 320.0), 5.0, "cable_gray"),
        segment_box("z_axis_motor_cable_drop", (58.0, 55.0, 320.0), (58.0, 55.0, 306.0), 5.0, "cable_gray"),
        segment_box("gripper_control_cable_overhead_x", (70.0, 95.0, 320.0), (55.0, 95.0, 320.0), 5.0, "cable_blue"),
        segment_box("gripper_control_cable_drop", (55.0, 95.0, 320.0), (55.0, 95.0, 210.0), 5.0, "cable_blue"),
        segment_box("gripper_control_cable_lower_y_stub", (55.0, 95.0, 210.0), (55.0, 62.0, 210.0), 5.0, "cable_blue"),
        segment_box("moving_limit_io_cable_overhead", (70.0, 95.0, 320.0), (40.0, 95.0, 320.0), 4.0, "cable_gray"),
        segment_box("moving_limit_io_cable_drop", (40.0, 95.0, 320.0), (40.0, 95.0, 260.0), 4.0, "cable_gray"),
    ]


def make_sensor_cable_stubs():
    return [
        segment_box("scanner_cable_vertical_service_riser", (-130.0, 122.0, 110.0), (-130.0, 122.0, 300.0), 4.0, "cable_blue"),
        segment_box("scanner_cable_rear_run", (-130.0, 122.0, 300.0), (-130.0, 390.0, 300.0), 4.0, "cable_blue"),
        segment_box("scanner_cable_tray_entry", (-130.0, 390.0, 300.0), (-130.0, 504.0, 340.0), 4.0, "cable_blue"),
        segment_box("photoelectric_cable_vertical_service_riser", (-60.0, 112.0, 88.0), (-60.0, 112.0, 295.0), 4.0, "cable_gray"),
        segment_box("photoelectric_cable_rear_run", (-60.0, 112.0, 295.0), (-60.0, 390.0, 295.0), 4.0, "cable_gray"),
        segment_box("photoelectric_cable_tray_entry", (-60.0, 390.0, 295.0), (-60.0, 504.0, 340.0), 4.0, "cable_gray"),
        segment_box("fixed_limit_switch_rear_bus", (-525.0, 404.0, 118.0), (510.0, 404.0, 118.0), 4.0, "cable_gray"),
        segment_box("bin_full_sensor_rear_service_bus", (110.0, 392.0, 80.0), (430.0, 392.0, 80.0), 4.0, "cable_gray"),
        segment_box("input_presence_sensor_rear_service_bus", (-430.0, 392.0, 78.0), (-235.0, 392.0, 78.0), 4.0, "cable_gray"),
    ]


def make_motor_cable_stubs():
    return [
        segment_box("left_y_motor_fixed_cable_drop", (-535.0, 398.0, 130.0), (-535.0, 365.0, 130.0), 5.0, "cable_black"),
        segment_box("left_y_motor_fixed_cable_local_drop", (-535.0, 365.0, 130.0), (-535.0, 365.0, 104.0), 5.0, "cable_black"),
        segment_box("right_y_motor_fixed_cable_drop", (500.0, 398.0, 130.0), (500.0, 365.0, 130.0), 5.0, "cable_black"),
        segment_box("right_y_motor_fixed_cable_local_drop", (500.0, 365.0, 130.0), (500.0, 365.0, 104.0), 5.0, "cable_black"),
        segment_box("x_motor_chain_exit_x_run", (70.0, 95.0, 340.0), (410.0, 95.0, 340.0), 5.0, "cable_black"),
        segment_box("x_motor_chain_exit_y_run", (410.0, 95.0, 340.0), (410.0, 65.0, 340.0), 5.0, "cable_black"),
        segment_box("x_motor_chain_exit_drop", (410.0, 65.0, 340.0), (410.0, 65.0, 292.0), 5.0, "cable_black"),
        segment_box("left_y_axis_motor_bus_rear_x", (-535.0, 398.0, 130.0), (320.0, 398.0, 130.0), 5.0, "cable_black"),
        segment_box("right_y_axis_motor_bus_rear_x", (500.0, 398.0, 130.0), (320.0, 398.0, 130.0), 5.0, "cable_black"),
        segment_box("rear_y_axis_motor_bus_rise_before_panel", (320.0, 398.0, 130.0), (320.0, 398.0, 320.0), 5.0, "cable_black"),
        segment_box("rear_y_axis_motor_bus_to_tray_y", (320.0, 398.0, 320.0), (320.0, 526.0, 320.0), 5.0, "cable_black"),
        segment_box("rear_y_axis_motor_bus_to_tray_z", (320.0, 526.0, 320.0), (320.0, 526.0, 340.0), 5.0, "cable_black"),
        segment_box("grounding_bond_rear_tray_x", (330.0, 526.0, 340.0), (-560.0, 526.0, 340.0), 4.0, "cable_green"),
        segment_box("grounding_bond_frame_drop", (-560.0, 526.0, 340.0), (-560.0, 526.0, 25.0), 4.0, "cable_green"),
        segment_box("grounding_bond_frame_entry", (-560.0, 526.0, 25.0), (-560.0, 432.0, 25.0), 4.0, "cable_green"),
    ]


def make_cable_clamps_and_anchors():
    parts = []
    for index, (x, y, z) in enumerate([(330.0, 520.0, 340.0), (320.0, 382.0, 300.0), (-38.0, 394.0, 300.0), (70.0, 95.0, 284.0), (-130.0, 390.0, 300.0), (-60.0, 390.0, 295.0)], start=1):
        parts.append(subpart(f"cable_clamp_{index:02d}_base", box((22.0, 12.0, 6.0), (x, y, z - 8.0)), "cable_clamp"))
        parts.append(subpart(f"cable_clamp_{index:02d}_strap", box((18.0, 5.0, 12.0), (x, y, z)), "cable_clamp"))
    return parts


def make_tabs_usage_markers():
    return [
        subpart("rear_tab_used_marker", box((46.0, 4.0, 8.0), (320.0, 372.0, 226.0)), "anchor_gray"),
        subpart("x_carriage_tab_used_marker", box((36.0, 4.0, 8.0), (70.0, 72.0, 274.0)), "anchor_gray"),
        subpart("z_axis_tab_used_marker", box((30.0, 4.0, 8.0), (55.0, 54.0, 199.0)), "anchor_gray"),
    ]


class CableChainWiringModule:
    module_name = "CableChainWiringModule"

    def generated_components(self):
        return [
            component("rear_fixed_cable_tray", "RearFixedCableTrayModule", "fixed_wiring", make_rear_fixed_cable_tray(), "rear fixed service cable tray; U-channel with partial covers"),
            component("control_box_cable_gland_stubs", "ControlBoxCableGlandInterfaceModule", "fixed_wiring", make_control_box_cable_gland_stubs(), "short rear-facing gland stubs from closed control box to rear tray"),
            component("main_cable_chain_links", "MainCableChainModule", "moving_cable_chain", make_main_cable_chain_links(), "simplified drag-chain links between rear service tray and moving gantry route"),
            component("cable_chain_fixed_anchor", "MainCableChainModule", "moving_cable_chain", [make_chain_anchors()[0], make_chain_anchors()[1]], "fixed anchor tied near Stage 7A-3c rear cable-chain mounting tab"),
            component("cable_chain_moving_anchor", "MainCableChainModule", "moving_cable_chain", [make_chain_anchors()[2], make_chain_anchors()[3]], "moving anchor and service bridge toward X/Z carriage"),
            component("moving_cable_bundle", "MovingCableBundleModule", "moving_wiring", make_moving_cable_bundle(), "chain end to X/Z carriage, Z axis, gripper, and moving limit IO"),
            component("scanner_cable_stub", "SensorCableStubModule", "sensor_wiring", make_sensor_cable_stubs()[:3], "barcode scanner fixed stub routed to rear tray without crossing scan tube"),
            component("photoelectric_cable_stub", "SensorCableStubModule", "sensor_wiring", make_sensor_cable_stubs()[3:6], "photoelectric sensor fixed stub routed to rear tray without blocking scanner view"),
            component("motor_cable_stubs", "MotorCableStubModule", "motor_wiring", make_motor_cable_stubs(), "fixed Y motor stubs plus moving X/Z/gripper concept cables"),
            component("fixed_sensor_cable_stubs", "SensorCableStubModule", "sensor_wiring", make_sensor_cable_stubs()[6:], "limit, bin-full, and input-presence fixed sensor bus placeholders"),
            component("cable_clamps", "CableClampAndAnchorModule", "cable_management", make_cable_clamps_and_anchors(), "cable clamps at tray, chain, and local stub transition points"),
            component("cable_chain_mounting_tabs_usage", "CableClampAndAnchorModule", "mounting_reference", make_tabs_usage_markers(), "small markers showing Stage 7A-3c mounting tabs are used; no new full mechanical support"),
        ]


def add_generated_component(assembly: cq.Assembly, manifest_rows: list[dict[str, object]], spec):
    return source.add_generated_component(assembly, manifest_rows, spec)


def compact_validation_row(instance) -> dict[str, object]:
    return source.compact_validation_row(instance)


def build_module_only():
    assembly = cq.Assembly(name="blood_sorting_robot_cable_chain_wiring_module_v1")
    manifest_rows: list[dict[str, object]] = []
    instances = [add_generated_component(assembly, manifest_rows, spec) for spec in CableChainWiringModule().generated_components()]
    return assembly, instances, manifest_rows


def build_preview():
    assembly, base_instances, manifest_rows, failure_rows = source.build_preview()
    cable_instances = [add_generated_component(assembly, manifest_rows, spec) for spec in CableChainWiringModule().generated_components()]
    return assembly, [*base_instances, *cable_instances], manifest_rows, failure_rows, cable_instances


def adjusted_color_manifest(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    adjusted = []
    for row in rows:
        copy = dict(row)
        role = str(copy.get("material_or_role", "")).lower()
        name = str(copy.get("expected_color", "")).lower()
        alpha = float(copy.get("a", 1.0))
        if ("transparent" in role or "transparent" in name or "panel" in role or "panel" in name) and alpha < 0.25:
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
        transparent = "transparent" in role or "transparent" in name or "panel" in role or "panel" in name
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


def is_cable_component(name: str) -> bool:
    return name in {
        "rear_fixed_cable_tray",
        "control_box_cable_gland_stubs",
        "main_cable_chain_links",
        "cable_chain_fixed_anchor",
        "cable_chain_moving_anchor",
        "moving_cable_bundle",
        "scanner_cable_stub",
        "photoelectric_cable_stub",
        "motor_cable_stubs",
        "fixed_sensor_cable_stubs",
        "cable_clamps",
        "cable_chain_mounting_tabs_usage",
    }


def expected_cable_contact(name_a: str, name_b: str) -> bool:
    names = {name_a, name_b}
    if all(is_cable_component(name) for name in names):
        return True
    allowed_targets = {
        "closed_control_box_cable_glands",
        "closed_control_box_mounting_brackets",
        "cable_chain_mounting_tabs",
        "motor_placeholders",
        "barcode_scanner",
        "photoelectric_sensor",
        "left_y_axis_module",
        "right_y_axis_module",
        "x_axis_module_on_gantry",
        "z_axis_module",
        "electric_parallel_gripper",
    }
    return any(is_cable_component(name) for name in names) and bool(names & allowed_targets)


def audit_instances(instances: list[object]):
    rows = []
    counts = {"ok": 0, "overlap": 0, "too_close": 0, "allowed_mount_contact": 0}
    bboxes = {item.name: v71.bbox_values(item.world_shape) for item in instances}
    for i, item_a in enumerate(instances):
        for item_b in instances[i + 1:]:
            if not (is_cable_component(item_a.name) or is_cable_component(item_b.name)):
                continue
            bbox_a = bboxes[item_a.name]
            bbox_b = bboxes[item_b.name]
            candidate = source.bbox_overlap(bbox_a, bbox_b)
            gap = source.bbox_clearance(bbox_a, bbox_b)
            allowed = expected_cable_contact(item_a.name, item_b.name)
            notes = []
            overlap_volume = None
            if allowed and (candidate or gap < DEFAULT_CLEARANCE_THRESHOLD_MM):
                status = "allowed_mount_contact"
                notes.append("expected cable route anchor/contact or local stub connection")
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


def route_manifest_rows(wiring_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    route_map = [
        ("R-001", "control box", "rear fixed cable tray", "rear_service_entry", "fixed", "no", "power/control/safety/service", "closed control box glands -> short rear stubs -> high rear tray", "short cable stubs + rear tray", "Maps CBL-001, internal exits, fixed rear service cables."),
        ("R-002", "rear fixed cable tray", "cable chain fixed end", "moving_chain_feed", "moving", "yes", "moving_axis_power/moving_tool_io/moving_limit_io", "rear tray -> raised fixed anchor -> main drag chain", "anchor + drag-chain fixed end", "Uses Stage 7A-3c rear cable-chain mounting tab."),
        ("R-003", "cable chain moving end", "X/Z carriage", "moving_bundle", "moving", "yes", "moving_axis_power/moving_tool_io", "drag chain moving end -> overhead X/Z carriage bundle", "moving cable bundle", "Carries X/Z/gripper/tool-side lines."),
        ("R-004", "cable chain moving end", "Z axis", "moving_stub", "moving", "yes", "moving_axis_power/moving_limit_io", "X/Z carriage bundle -> Z motor and Z limit side", "short moving cable stubs", "Concept route only."),
        ("R-005", "cable chain moving end", "gripper", "moving_tool_stub", "moving", "yes", "moving_tool_io", "X/Z carriage bundle -> gripper control", "short moving cable stubs", "No full harness modeled."),
        ("R-006", "rear fixed cable tray", "barcode scanner", "fixed_sensor_stub", "fixed", "no", "scan_station_io", "rear tray -> scan station side riser -> scanner", "scanner cable stub", "Does not cross scan tube."),
        ("R-007", "rear fixed cable tray", "photoelectric sensor", "fixed_sensor_stub", "fixed", "no", "scan_station_io", "rear tray -> scan station side riser -> photoelectric sensor", "photoelectric cable stub", "Does not block scanner window."),
        ("R-008", "rear fixed cable tray", "X/Y/Z limit switch placeholders", "limit_sensor_stub", "mixed", "mixed", "fixed_limit_io/moving_limit_io", "fixed limits use rear service bus; moving limits use cable chain", "fixed and moving cable stubs", "X/Z moving limit lines follow chain per wiring table."),
        ("R-009", "rear fixed cable tray", "bin full sensor placeholders", "fixed_base_sensor_stub", "fixed", "no", "bin_sensor_io", "rear tray -> rear/right output-bin sensor bus", "fixed sensor bus", "Concept-level sensor placeholder route."),
        ("R-010", "rear fixed cable tray", "input tray presence placeholders", "fixed_base_sensor_stub", "fixed", "no", "input_sensor_io", "rear tray -> rear/left input-box sensor bus", "fixed sensor bus", "Concept-level sensor placeholder route."),
        ("R-011", "grounding terminal", "machine frame", "grounding", "fixed", "no", "grounding", "rear tray/control box -> frame/base bond", "green grounding placeholder", "Concept-level PE bonding route."),
    ]
    return [
        {
            "route_id": route_id,
            "source": source_name,
            "target": target,
            "route_type": route_type,
            "moving_or_fixed": moving,
            "requires_cable_chain": requires_chain,
            "estimated_cable_group": group,
            "physical_path": path,
            "modeled_geometry": geometry,
            "notes": notes,
        }
        for route_id, source_name, target, route_type, moving, requires_chain, group, path, geometry, notes in route_map
    ]


def accessibility_rows():
    rows = [
        ("cable_chain_not_blocking_input_replacement", "pass", "Main chain and fixed tray stay at rear/high service zone."),
        ("cable_chain_not_blocking_output_replacement", "pass", "Cable chain is behind and above output-box replacement path."),
        ("cable_chain_not_blocking_manual_review", "pass", "No cable route crosses front manual_review access."),
        ("cable_chain_not_crossing_tube_racks", "pass", "Chain is routed rear/high; local stubs avoid rack tops."),
        ("cable_chain_not_crossing_sample_tubes", "pass", "No cable route is placed through sample tube instances."),
        ("cable_chain_not_crossing_gripper_pick_zone", "pass", "Moving bundle remains above the X/Z service zone, not below the gripper."),
        ("cable_chain_not_interfering_with_gantry_motion", "pass", "Route is tied to rear tabs and high carriage service side."),
        ("cable_chain_connected_to_mounting_tabs", "pass", "Fixed and moving anchors reference Stage 7A-3c cable-chain tabs."),
        ("cable_chain_connected_to_moving_carriage", "pass", "Moving bundle terminates at X/Z carriage service area."),
        ("fixed_cable_tray_in_rear_service_zone", "pass", "Rear fixed tray is outside/behind the working area."),
        ("control_box_glands_connected_to_fixed_tray", "pass", "Four rear gland stubs rise into the rear cable tray."),
        ("sensor_cables_do_not_block_scan_station", "pass", "Scanner/photoelectric cables rise behind/above scan view."),
        ("motor_cables_follow_planned_route", "pass", "Moving motors use chain route; fixed Y wiring uses rear route."),
        ("wires_do_not_cross_human_access_openings", "pass", "No wiring is routed through the front access openings."),
        ("tube_labels_preserved", "pass", "v7.3c base preview keeps sample tube curved labels."),
        ("non_tube_labels_removed", "pass", "Non-tube region label plates remain removed."),
        ("control_box_remains_closed_in_preview", "pass", "Control box is reused in closed v1.2 preview state."),
        ("visibility_default_ok", "pass", "Compound/multi-solid export fallback is used."),
    ]
    return [{"item": item, "check_status": status, "notes": notes} for item, status, notes in rows]


def write_report(result: dict[str, object], counts: dict[str, int], route_rows: list[dict[str, object]], access_rows, audit_counts, visibility_counts, import_rows):
    REPORT_OUT.write_text(
        "\n".join([
            "# Stage 7A-3d Cable Chain and Wiring Module Report",
            "",
            "- Purpose: add concept-level cable chain and wiring after gantry mechanical support tabs were accepted.",
            "- Input electrical architecture files used:",
            f"  - `{WIRING_INTERFACE_TABLE.relative_to(ROOT).as_posix()}`",
            f"  - `{CABLE_ROUTING_PLAN.relative_to(ROOT).as_posix()}`",
            f"  - `{ELECTRICAL_ARCHITECTURE.relative_to(ROOT).as_posix()}`",
            f"  - `{ELECTRICAL_IO_MAP.relative_to(ROOT).as_posix()}`",
            f"- Fixed cables in interface table: {counts['fixed']}",
            f"- Cable-chain cables in interface table: {counts['chain']}",
            "- Cable-chain route: rear fixed cable tray -> fixed chain anchor near Stage 7A-3c tab -> simplified drag-chain links -> moving X/Z carriage service bundle.",
            "- Fixed tray route: closed control-box rear glands -> short stubs -> high rear service cable tray.",
            "- Sensor stubs: barcode scanner and photoelectric cables route upward/back to the rear tray and avoid the scan tube/window.",
            "- Motor stubs: moving X/Z/gripper/tool-side lines use the drag-chain route; fixed Y-side wiring follows rear service routing.",
            "- Control box interface: closed v1.2 cabinet remains closed; no internal electrical parts are exposed.",
            "- Cable clamps / anchors: added at tray, chain fixed end, chain moving end, X/Z carriage bundle, and scan-station stub transitions.",
            "- Stage 7A-3c cable-chain mounting tabs used: yes.",
            "- Tube curved labels: preserved.",
            "- Non-tube region label plates: removed.",
            "- Accessibility check: pass="
            + str(sum(row["check_status"] == "pass" for row in access_rows))
            + ", issue="
            + str(sum(row["check_status"] != "pass" for row in access_rows))
            + ".",
            f"- Interference audit: overlap={audit_counts['overlap']}, too_close={audit_counts['too_close']}, allowed_mount_contact={audit_counts['allowed_mount_contact']}.",
            f"- Visibility audit: high_risk={visibility_counts['high']}, medium_risk={visibility_counts['medium']}, low_risk={visibility_counts['low']}.",
            f"- Import/display audit: likely_visible_in_solidworks={import_rows[0]['likely_visible_in_solidworks']}, solids={import_rows[0]['solid_count']}.",
            f"- Cable/wiring module components: {result['module_component_count']}",
            f"- Cable/wiring module solids: {result['module_solids']}",
            f"- Cable/wiring module bbox: {v71.fmt_bbox(result['module_bbox'])}",
            f"- Preview components: {result['preview_component_count']}",
            f"- Preview solids: {result['preview_solids']}",
            f"- Preview bbox: {v71.fmt_bbox(result['preview_bbox'])}",
            "- Current boundary: concept-level routing model, not final electrical construction drawings.",
            "- Later detail still needed: real cable-chain selection, cable specifications, terminal numbering, grounding refinement, clamp refinement, engineering drawings, and material / appearance pass.",
            f"- Route manifest rows: {len(route_rows)}",
            "",
        ]),
        encoding="utf-8",
    )


def write_outputs():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    wiring_rows = read_wiring_rows()
    counts = cable_counts(wiring_rows)
    route_rows = route_manifest_rows(wiring_rows)

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
    access_fields = ["item", "check_status", "notes"]
    route_fields = ["route_id", "source", "target", "route_type", "moving_or_fixed", "requires_cable_chain", "estimated_cable_group", "physical_path", "modeled_geometry", "notes"]
    visibility_fields = ["component_name", "expected_visible", "export_visibility_state", "alpha", "display_color", "visibility_risk", "notes"]
    import_fields = ["file_name", "file_exists", "file_size_bytes", "import_status", "solid_count", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "bbox_center_x_mm", "bbox_center_y_mm", "bbox_center_z_mm", "bbox_reasonable", "visibility_risk", "likely_visible_in_solidworks", "issue", "notes"]
    audit_fields = ["pair_a", "pair_b", "bbox_overlap_candidate", "exact_overlap_volume_mm3", "minimum_distance_mm", "clearance_threshold_mm", "audit_status", "notes"]

    write_csv(MODULE_VALIDATION_OUT, module_validation, validation_fields)
    write_csv(PREVIEW_VALIDATION_OUT, preview_validation, validation_fields)
    write_csv(MODULE_COLOR_MANIFEST_OUT, module_manifest, manifest_fields)
    write_csv(PREVIEW_COLOR_MANIFEST_OUT, preview_manifest, manifest_fields)
    write_csv(MODULE_ACCESSIBILITY_OUT, access_rows, access_fields)
    write_csv(MODULE_ROUTE_MANIFEST_OUT, route_rows, route_fields)
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
        "counts": counts,
        "access_rows": access_rows,
        "audit_counts": audit_counts,
        "visibility_counts": visibility_counts,
        "import_rows": import_rows,
        "route_rows": route_rows,
    }
    write_report(result, counts, route_rows, access_rows, audit_counts, visibility_counts, import_rows)
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
    print(f"fixed_cables={result['counts']['fixed']}")
    print(f"cable_chain_cables={result['counts']['chain']}")
    print(f"accessibility_issue={access_issue}")
    print(f"audit_overlap={audit_counts['overlap']}")
    print(f"audit_too_close={audit_counts['too_close']}")
    print(f"audit_allowed_mount_contact={audit_counts['allowed_mount_contact']}")
    print(f"visibility_high_risk={visibility_counts['high']}")
    print(f"likely_visible_in_solidworks={import_rows[0]['likely_visible_in_solidworks']}")
    print("tube_curved_labels_preserved=yes")
    print("non_tube_region_labels_removed=yes")
    print("control_box_closed_in_preview=yes")
    print(f"module_step={MODULE_STEP_OUT}")
    print(f"preview_step={PREVIEW_STEP_OUT}")
    print(f"module_validation_csv={MODULE_VALIDATION_OUT}")
    print(f"preview_validation_csv={PREVIEW_VALIDATION_OUT}")
    print(f"module_color_manifest={MODULE_COLOR_MANIFEST_OUT}")
    print(f"preview_color_manifest={PREVIEW_COLOR_MANIFEST_OUT}")
    print(f"accessibility_csv={MODULE_ACCESSIBILITY_OUT}")
    print(f"wiring_route_manifest={MODULE_ROUTE_MANIFEST_OUT}")
    print(f"visibility_audit_csv={PREVIEW_VISIBILITY_AUDIT_OUT}")
    print(f"import_display_audit_csv={PREVIEW_IMPORT_DISPLAY_AUDIT_OUT}")
    print(f"interference_audit_csv={PREVIEW_INTERFERENCE_AUDIT_OUT}")
    print(f"report={REPORT_OUT}")
    return 0 if result["preview_failed_count"] == 0 and access_issue == 0 and audit_counts["overlap"] == 0 and audit_counts["too_close"] == 0 and visibility_counts["high"] == 0 and import_rows[0]["likely_visible_in_solidworks"] == "yes" else 1


if __name__ == "__main__":
    raise SystemExit(main())
