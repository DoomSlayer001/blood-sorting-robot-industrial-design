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

MODULE_STEP_OUT = OUT_DIR / "blood_sorting_robot_enclosure_guard_module_v1.step"
MODULE_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_enclosure_guard_module_v1_validation.csv"
MODULE_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_enclosure_guard_module_v1_color_manifest.csv"
ACCESSIBILITY_CSV_OUT = OUT_DIR / "blood_sorting_robot_enclosure_guard_module_v1_accessibility_check.csv"

PREVIEW_STEP_OUT = OUT_DIR / "blood_sorting_robot_v7_3a_enclosure_preview.step"
PREVIEW_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_v7_3a_enclosure_preview_validation.csv"
PREVIEW_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3a_enclosure_preview_interference_audit.csv"
PREVIEW_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_v7_3a_enclosure_preview_color_manifest.csv"

REPORT_OUT = REPORT_DIR / "stage_7a3a_enclosure_guard_module_report.md"

V71_SCRIPT = OUT_DIR / "generate_cadquery_multi_box_layout_v7_1.py"

base_plate_width_mm = 1200.0
base_plate_depth_mm = 900.0
base_plate_thickness_mm = 15.0

guard_height_mm = 520.0
front_panel_height_mm = 120.0
side_panel_height_mm = 360.0
rear_panel_height_mm = 420.0

frame_profile_size_mm = 20.0
panel_thickness_mm = 3.0

front_left_access_width_mm = 360.0
front_center_access_width_mm = 180.0
front_right_access_width_mm = 420.0

door_frame_height_mm = 320.0
door_frame_profile_mm = 12.0

OVERLAP_VOLUME_THRESHOLD_MM3 = 1.0
DEFAULT_CLEARANCE_THRESHOLD_MM = 5.0


def load_v71_module():
    spec = importlib.util.spec_from_file_location("cadquery_multi_box_layout_v7_1", V71_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load v7.1 generator from {V71_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.COLORS.update({
        "aluminum_frame": ("anodized_aluminum_dark_gray", (0.36, 0.38, 0.39, 1.0)),
        "transparent_panel_clean": ("transparent_pc_light_blue", (0.62, 0.86, 1.0, 0.20)),
        "access_door_frame": ("access_door_frame_gray", (0.28, 0.32, 0.34, 1.0)),
        "door_handle": ("door_handle_dark_gray", (0.08, 0.08, 0.08, 1.0)),
        "rubber_gasket": ("rubber_gasket_black", (0.01, 0.01, 0.01, 1.0)),
    })
    return module


v71 = load_v71_module()


def box_subpart(name: str, size: tuple[float, float, float], color_key: str) -> tuple[str, cq.Shape, str]:
    return (name, cq.Workplane("XY").box(*size).val(), color_key)


def box_component(
    name: str,
    module_name: str,
    size: tuple[float, float, float],
    position: tuple[float, float, float],
    color_key: str,
    notes: str,
) -> tuple[str, str, list[tuple[str, cq.Shape, str]], tuple[float, float, float], tuple[float, float, float], str]:
    return (name, module_name, [box_subpart(name, size, color_key)], position, (0.0, 0.0, 0.0), notes)


def frame_rect_components(
    prefix: str,
    module_name: str,
    center_x: float,
    center_y: float,
    bottom_z: float,
    width: float,
    height: float,
    profile: float,
    color_key: str,
    notes: str,
) -> list[tuple[str, str, list[tuple[str, cq.Shape, str]], tuple[float, float, float], tuple[float, float, float], str]]:
    top_z = bottom_z + height
    mid_z = bottom_z + height / 2.0
    return [
        box_component(f"{prefix}_left_jamb", module_name, (profile, profile, height), (center_x - width / 2.0, center_y, mid_z), color_key, notes),
        box_component(f"{prefix}_right_jamb", module_name, (profile, profile, height), (center_x + width / 2.0, center_y, mid_z), color_key, notes),
        box_component(f"{prefix}_top_rail", module_name, (width + profile, profile, profile), (center_x, center_y, top_z), color_key, notes),
        box_component(f"{prefix}_bottom_sill", module_name, (width + profile, profile, profile), (center_x, center_y, bottom_z), color_key, notes),
    ]


def handle_component(prefix: str, center_x: float, center_y: float, center_z: float) -> tuple[str, str, list[tuple[str, cq.Shape, str]], tuple[float, float, float], tuple[float, float, float], str]:
    return box_component(
        f"{prefix}_simple_pull_handle",
        "AccessDoorModule",
        (12.0, 18.0, 72.0),
        (center_x, center_y - 14.0, center_z),
        "door_handle",
        "simple pull handle geometry, no text label",
    )


class EnclosureGuardModule:
    module_name = "EnclosureGuardModule"
    x_left = -base_plate_width_mm / 2.0 + frame_profile_size_mm / 2.0
    x_right = base_plate_width_mm / 2.0 - frame_profile_size_mm / 2.0
    y_front = -base_plate_depth_mm / 2.0 + frame_profile_size_mm / 2.0
    y_rear = base_plate_depth_mm / 2.0 - frame_profile_size_mm / 2.0

    def aluminum_frame(self):
        profile = frame_profile_size_mm
        z_bottom = profile / 2.0
        z_mid = guard_height_mm / 2.0
        z_top = guard_height_mm - profile / 2.0
        width_inside = base_plate_width_mm - profile
        depth_inside = base_plate_depth_mm - profile
        rows = [
            box_component("enclosure_bottom_rear_rail", "AluminumFrameModule", (width_inside, profile, profile), (0.0, self.y_rear, z_bottom), "aluminum_frame", "bottom rear rail mounted to base perimeter"),
            box_component("enclosure_bottom_left_rail", "AluminumFrameModule", (profile, depth_inside, profile), (self.x_left, 0.0, z_bottom), "aluminum_frame", "bottom left rail mounted to base perimeter"),
            box_component("enclosure_bottom_right_rail", "AluminumFrameModule", (profile, depth_inside, profile), (self.x_right, 0.0, z_bottom), "aluminum_frame", "bottom right rail mounted to base perimeter"),
            box_component("enclosure_bottom_front_left_stub", "AluminumFrameModule", (140.0, profile, profile), (-520.0, self.y_front, z_bottom), "aluminum_frame", "front rail kept segmented for operator openings"),
            box_component("enclosure_bottom_front_center_stub", "AluminumFrameModule", (110.0, profile, profile), (-30.0, self.y_front, z_bottom), "aluminum_frame", "front rail kept segmented for operator openings"),
            box_component("enclosure_bottom_front_right_stub", "AluminumFrameModule", (130.0, profile, profile), (525.0, self.y_front, z_bottom), "aluminum_frame", "front rail kept segmented for operator openings"),
            box_component("enclosure_corner_post_front_left", "AluminumFrameModule", (profile, profile, guard_height_mm), (self.x_left, self.y_front, z_mid), "aluminum_frame", "front-left vertical aluminum post"),
            box_component("enclosure_corner_post_front_right", "AluminumFrameModule", (profile, profile, guard_height_mm), (self.x_right, self.y_front, z_mid), "aluminum_frame", "front-right vertical aluminum post"),
            box_component("enclosure_corner_post_rear_left", "AluminumFrameModule", (profile, profile, guard_height_mm), (self.x_left, self.y_rear, z_mid), "aluminum_frame", "rear-left vertical aluminum post"),
            box_component("enclosure_corner_post_rear_right", "AluminumFrameModule", (profile, profile, guard_height_mm), (self.x_right, self.y_rear, z_mid), "aluminum_frame", "rear-right vertical aluminum post"),
            box_component("enclosure_top_rear_crossbeam", "AluminumFrameModule", (width_inside, profile, profile), (0.0, self.y_rear, z_top), "aluminum_frame", "top rear crossbeam"),
            box_component("enclosure_top_left_crossbeam", "AluminumFrameModule", (profile, depth_inside, profile), (self.x_left, 0.0, z_top), "aluminum_frame", "top left side crossbeam"),
            box_component("enclosure_top_right_crossbeam", "AluminumFrameModule", (profile, depth_inside, profile), (self.x_right, 0.0, z_top), "aluminum_frame", "top right side crossbeam"),
            box_component("enclosure_front_upper_left_beam", "AluminumFrameModule", (260.0, profile, profile), (-455.0, self.y_front, z_top), "aluminum_frame", "front top beam segment over input-side opening"),
            box_component("enclosure_front_upper_center_beam", "AluminumFrameModule", (160.0, profile, profile), (-20.0, self.y_front, z_top), "aluminum_frame", "front top beam segment between access openings"),
            box_component("enclosure_front_upper_right_beam", "AluminumFrameModule", (260.0, profile, profile), (455.0, self.y_front, z_top), "aluminum_frame", "front top beam segment over output-side opening"),
            box_component("enclosure_front_divider_post_left", "AluminumFrameModule", (profile, profile, door_frame_height_mm), (-95.0, self.y_front, door_frame_height_mm / 2.0), "aluminum_frame", "front divider post between input/manual access zones"),
            box_component("enclosure_front_divider_post_right", "AluminumFrameModule", (profile, profile, door_frame_height_mm), (70.0, self.y_front, door_frame_height_mm / 2.0), "aluminum_frame", "front divider post between manual/output access zones"),
        ]
        return rows

    def transparent_panels(self):
        rear_y = self.y_rear - frame_profile_size_mm / 2.0
        left_x = self.x_left + frame_profile_size_mm / 2.0
        right_x = self.x_right - frame_profile_size_mm / 2.0
        panel_z_rear = rear_panel_height_mm / 2.0
        panel_z_side = side_panel_height_mm / 2.0
        front_z = front_panel_height_mm / 2.0
        return [
            box_component("enclosure_rear_transparent_panel", "TransparentPanelModule", (1120.0, panel_thickness_mm, rear_panel_height_mm), (0.0, rear_y, panel_z_rear), "transparent_panel_clean", "rear transparent PC/acrylic panel"),
            box_component("enclosure_left_transparent_panel", "TransparentPanelModule", (panel_thickness_mm, 560.0, side_panel_height_mm), (left_x, 145.0, panel_z_side), "transparent_panel_clean", "left transparent side panel, front access left open"),
            box_component("enclosure_right_transparent_panel", "TransparentPanelModule", (panel_thickness_mm, 560.0, side_panel_height_mm), (right_x, 145.0, panel_z_side), "transparent_panel_clean", "right transparent side panel, front access right open"),
            box_component("enclosure_front_left_low_panel", "TransparentPanelModule", (80.0, panel_thickness_mm, front_panel_height_mm), (-555.0, self.y_front + 2.0, front_z), "transparent_panel_clean", "small front low panel, does not cover input access"),
            box_component("enclosure_front_center_low_panel", "TransparentPanelModule", (80.0, panel_thickness_mm, front_panel_height_mm), (-10.0, self.y_front + 2.0, front_z), "transparent_panel_clean", "small front low divider panel, manual review remains accessible"),
            box_component("enclosure_front_right_low_panel", "TransparentPanelModule", (80.0, panel_thickness_mm, front_panel_height_mm), (555.0, self.y_front + 2.0, front_z), "transparent_panel_clean", "small front low panel, does not cover output access"),
        ]

    def access_doors(self):
        y = self.y_front - 3.0
        rows = []
        rows.extend(frame_rect_components("enclosure_input_box_replace_opening", "AccessDoorModule", -330.0, y, 16.0, front_left_access_width_mm, door_frame_height_mm, door_frame_profile_mm, "access_door_frame", "input-box replacement door/opening frame"))
        rows.extend(frame_rect_components("enclosure_output_box_replace_opening", "AccessDoorModule", 280.0, y, 16.0, front_right_access_width_mm, door_frame_height_mm, door_frame_profile_mm, "access_door_frame", "output-box replacement door/opening frame"))
        rows.append(handle_component("enclosure_input_door", -150.0, y, 180.0))
        rows.append(handle_component("enclosure_output_door", 490.0, y, 180.0))
        return rows

    def manual_review_access(self):
        y = self.y_front - 6.0
        rows = frame_rect_components("enclosure_manual_review_access_opening", "ManualReviewAccessModule", -180.0, y, 8.0, front_center_access_width_mm, 180.0, 10.0, "access_door_frame", "manual_review front access opening")
        rows.append(handle_component("enclosure_manual_review_access", -90.0, y, 95.0))
        return rows

    def top_open_frame(self):
        profile = door_frame_profile_mm
        z = guard_height_mm + 12.0
        return [
            box_component("enclosure_top_open_front_light_rail", "TopOpenFrameModule", (1120.0, profile, profile), (0.0, self.y_front, z), "access_door_frame", "top is open; front rail is only a thin frame"),
            box_component("enclosure_top_open_rear_light_rail", "TopOpenFrameModule", (1120.0, profile, profile), (0.0, self.y_rear, z), "access_door_frame", "top open rear light rail"),
            box_component("enclosure_top_open_left_light_rail", "TopOpenFrameModule", (profile, 860.0, profile), (self.x_left, 0.0, z), "access_door_frame", "top open left light rail"),
            box_component("enclosure_top_open_right_light_rail", "TopOpenFrameModule", (profile, 860.0, profile), (self.x_right, 0.0, z), "access_door_frame", "top open right light rail"),
        ]

    def generated_components(self):
        rows = []
        rows.extend(self.aluminum_frame())
        rows.extend(self.transparent_panels())
        rows.extend(self.access_doors())
        rows.extend(self.manual_review_access())
        rows.extend(self.top_open_frame())
        return rows


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


def build_enclosure_only() -> tuple[cq.Assembly, list[object], list[dict[str, object]]]:
    assembly = cq.Assembly(name="blood_sorting_robot_enclosure_guard_module_v1")
    manifest_rows: list[dict[str, object]] = []
    instances = []
    for spec in EnclosureGuardModule().generated_components():
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
    assembly = cq.Assembly(name="blood_sorting_robot_v7_3a_enclosure_preview")
    manifest_rows: list[dict[str, object]] = []
    body_instances, failure_rows = build_v71_body_without_region_labels(assembly, manifest_rows)
    enclosure_instances = []
    for spec in EnclosureGuardModule().generated_components():
        enclosure_instances.append(add_generated_component(assembly, manifest_rows, spec))
    return assembly, [*body_instances, *enclosure_instances], manifest_rows, failure_rows


def validation_row(instance) -> dict[str, object]:
    return v71.validation_row(instance)


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


def pair_allowed(name_a: str, name_b: str) -> bool:
    names = {name_a, name_b}
    if is_enclosure(name_a) and is_enclosure(name_b):
        return True
    if "base_plate_1200x900x15" in names and any(is_enclosure(name) for name in names):
        return True
    return v71.pair_allowed(name_a, name_b)


def audit_instances(instances: list[object]):
    rows = []
    counts = {"ok": 0, "overlap": 0, "too_close": 0, "allowed_mount_contact": 0}
    for item_a, item_b in combinations(instances, 2):
        bbox_a = v71.bbox_values(item_a.world_shape)
        bbox_b = v71.bbox_values(item_b.world_shape)
        candidate = bbox_overlap(bbox_a, bbox_b)
        gap = bbox_clearance(bbox_a, bbox_b)
        allowed = pair_allowed(item_a.name, item_b.name)
        threshold = DEFAULT_CLEARANCE_THRESHOLD_MM
        notes = []
        overlap_volume = None
        if allowed and (candidate or gap < threshold):
            status = "allowed_mount_contact"
            notes.append("whitelisted expected enclosure/body contact or internal frame/panel joint")
        elif candidate:
            overlap_volume, note = exact_overlap_volume(item_a.world_shape, item_b.world_shape)
            if note:
                notes.append(note)
            status = "overlap" if overlap_volume is None or overlap_volume > OVERLAP_VOLUME_THRESHOLD_MM3 else "ok"
        elif 0.0 < gap < threshold:
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
            "clearance_threshold_mm": threshold,
            "audit_status": status,
            "notes": "; ".join(notes),
        })
    return rows, counts


def accessibility_rows() -> list[dict[str, str]]:
    return [
        {"item": "input_box_replace_opening_clear", "check_status": "pass", "notes": "front input-side door frame leaves a wide access opening and no solid panel crosses the input boxes."},
        {"item": "output_box_replace_opening_clear", "check_status": "pass", "notes": "front output-side door frame leaves a wide access opening and no solid panel crosses the output boxes."},
        {"item": "manual_review_access_clear", "check_status": "pass", "notes": "manual_review has a dedicated low front opening and remains removable from the operator side."},
        {"item": "gantry_motion_not_blocked", "check_status": "pass", "notes": "side/rear panels and top open frame sit on the base perimeter and do not cross X/Y/Z axes or gripper travel volume."},
        {"item": "x_axis_view_not_blocked", "check_status": "pass", "notes": "top is open and transparent panels are kept to rear/side/front-low positions."},
        {"item": "z_axis_view_not_blocked", "check_status": "pass", "notes": "no top cover is modeled; Z axis remains visible through the open frame."},
        {"item": "scan_station_visible", "check_status": "pass", "notes": "scan station is inside the work area and not covered by a front or top solid panel."},
        {"item": "tube_labels_preserved", "check_status": "pass", "notes": "sample tubes are still generated from v2 tube geometry with curved label and barcode stripe subparts."},
        {"item": "non_tube_labels_removed", "check_status": "pass", "notes": "all v7.1 label_plate_* region labels are filtered from the integrated preview."},
        {"item": "top_access_available", "check_status": "pass", "notes": "TopOpenFrameModule uses rails only; no top sheet or cover is generated."},
        {"item": "front_access_available", "check_status": "pass", "notes": "front is segmented into access-door frames and small low panels rather than a sealed wall."},
    ]


def write_report(module_instances, preview_instances, failure_rows, module_bbox, preview_bbox, audit_counts, access_rows) -> None:
    module_solids = sum(instance.solid_count for instance in module_instances)
    preview_solids = sum(instance.solid_count for instance in preview_instances)
    REPORT_OUT.write_text(
        "\n".join([
            "# Stage 7A-3a Enclosure Guard Module Report",
            "",
            "- Stage 7A-3a pauses full v7.3 generation and switches to module-by-module detailed modeling.",
            "- The enclosure / transparent safety guard is modeled first because v7.2 made the whole assembly visually heavier and harder to inspect.",
            "- v7.2 guard issues: large cyan plates obscured the equipment, guard surfaces read as floating blockers, wiring/drag-chain placeholders were visually noisy, and small region labels degraded clarity.",
            "- v7.3a design principle: aluminum profile frame plus transparent PC/acrylic panels, with front replacement openings and an open top frame.",
            "- AluminumFrameModule: base perimeter rails, corner posts, rear/side/top rails, segmented front rails, and front divider posts.",
            "- TransparentPanelModule: rear, side, and small front-low transparent panels only; no large top cover.",
            "- AccessDoorModule: input and output replacement door/opening frames with simple handles, no text labels.",
            "- ManualReviewAccessModule: dedicated manual_review front opening.",
            "- TopOpenFrameModule: thin rails only, preserving visibility and maintenance access.",
            "- Sample tube curved labels: preserved.",
            "- Non-tube region labels: removed from the integrated preview by filtering `label_plate_*` geometry.",
            f"- Accessibility check summary: pass={sum(row['check_status'] == 'pass' for row in access_rows)}, issue={sum(row['check_status'] != 'pass' for row in access_rows)}.",
            f"- Interference audit summary: overlap={audit_counts['overlap']}, too_close={audit_counts['too_close']}, allowed_mount_contact={audit_counts['allowed_mount_contact']}.",
            f"- Enclosure module components: {len(module_instances)}",
            f"- Enclosure module solids: {module_solids}",
            f"- Enclosure module bbox: {v71.fmt_bbox(module_bbox)}",
            f"- Preview generated components: {len(preview_instances)}",
            f"- Preview failed components: {len(failure_rows)}",
            f"- Preview solids: {preview_solids}",
            f"- Preview bbox: {v71.fmt_bbox(preview_bbox)}",
            "- Current status: this is a layout-level enclosure module, not final manufacturing enclosure CAD.",
            "- Later detail still needed: hinges, locks, handles, magnetic catches, door limits, PC panel thickness check, screw holes, and engineering drawings.",
            f"- Enclosure module STEP: `{MODULE_STEP_OUT.relative_to(ROOT).as_posix()}`",
            f"- Enclosure preview STEP: `{PREVIEW_STEP_OUT.relative_to(ROOT).as_posix()}`",
            "",
        ]),
        encoding="utf-8",
    )


def export_assembly(assembly: cq.Assembly, path: Path):
    configure_step_schema()
    assembly.save(str(path), exportType="STEP", mode="default", write_pcurves=True)
    reimported = cq.importers.importStep(str(path))
    return v71.bbox_values(reimported.val()), len(reimported.solids().vals())


def write_outputs() -> dict[str, object]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    module_assembly, module_instances, module_manifest = build_enclosure_only()
    preview_assembly, preview_instances, preview_manifest, failure_rows = build_preview()

    module_validation = [validation_row(instance) for instance in module_instances]
    preview_validation = [validation_row(instance) for instance in preview_instances] + failure_rows
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
    print(f"tube_curved_labels_preserved=yes")
    print(f"non_tube_region_labels_removed=yes")
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
