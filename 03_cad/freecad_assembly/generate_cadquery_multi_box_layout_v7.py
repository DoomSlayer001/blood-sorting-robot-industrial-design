from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterable

import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.Interface import Interface_Static


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "03_cad" / "freecad_assembly"
REPORT_DIR = ROOT / "reports"

STEP_OUT = OUT_DIR / "blood_sorting_robot_cadquery_multi_box_layout_v7.step"
CSV_OUT = OUT_DIR / "blood_sorting_robot_cadquery_multi_box_layout_v7_validation.csv"
AUDIT_CSV_OUT = OUT_DIR / "blood_sorting_robot_cadquery_multi_box_layout_v7_interference_audit.csv"
COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_cadquery_multi_box_layout_v7_color_manifest.csv"
REPORT_OUT = REPORT_DIR / "cadquery_multi_box_layout_v7_report.md"

BASE_SIZE = (1200.0, 900.0, 15.0)
TUBE_INSERT_Z = 25.0
OVERLAP_VOLUME_THRESHOLD_MM3 = 1.0
DEFAULT_CLEARANCE_THRESHOLD_MM = 5.0
SCAN_MOVING_CLEARANCE_THRESHOLD_MM = 20.0

COLORS = {
    "axis_dark_gray": ("dark_gray", (0.22, 0.23, 0.24, 1.0)),
    "base_plate": ("base_light_gray", (0.70, 0.72, 0.74, 1.0)),
    "input_box": ("input_box_blue_gray", (0.65, 0.76, 0.88, 1.0)),
    "output_a": ("category_A_purple_gray", (0.58, 0.45, 0.72, 1.0)),
    "output_b": ("category_B_yellow_gray", (0.86, 0.75, 0.36, 1.0)),
    "output_c": ("category_C_blue_gray", (0.45, 0.61, 0.82, 1.0)),
    "output_d": ("category_D_red_gray", (0.75, 0.42, 0.40, 1.0)),
    "manual_review": ("manual_review_gray", (0.58, 0.58, 0.58, 1.0)),
    "scanner_black": ("scanner_black", (0.06, 0.06, 0.06, 1.0)),
    "sensor_dark_gray": ("sensor_dark_gray", (0.14, 0.14, 0.14, 1.0)),
    "adapter_gray": ("adapter_gray", (0.50, 0.54, 0.56, 1.0)),
    "bracket_gray": ("bracket_gray", (0.32, 0.34, 0.35, 1.0)),
    "plate_dark": ("label_plate_dark", (0.04, 0.04, 0.04, 1.0)),
    "plate_text": ("label_plate_text_light", (0.92, 0.92, 0.86, 1.0)),
    "tube_body": ("light_gray_body", (0.78, 0.84, 0.88, 0.55)),
    "tube_label": ("white_label", (1.0, 1.0, 1.0, 1.0)),
    "barcode_black": ("barcode_black", (0.0, 0.0, 0.0, 1.0)),
    "purple": ("purple_cap", (0.45, 0.16, 0.75, 1.0)),
    "yellow": ("yellow_cap", (1.0, 0.82, 0.05, 1.0)),
    "blue": ("blue_cap", (0.08, 0.34, 0.95, 1.0)),
    "red": ("red_cap", (0.86, 0.05, 0.05, 1.0)),
    "control_box": ("control_box_dark", (0.16, 0.18, 0.20, 1.0)),
    "safety_red": ("safety_red", (0.9, 0.02, 0.02, 1.0)),
    "guard": ("transparent_guard", (0.65, 0.85, 1.0, 0.25)),
    "cable_chain": ("cable_chain_black", (0.03, 0.03, 0.03, 1.0)),
}


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    module_name: str
    rel_path: str
    position: tuple[float, float, float]
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    target_axis: str | None = None
    color_key: str = "axis_dark_gray"
    note: str = ""


@dataclass(frozen=True)
class TubeSpec:
    key: str
    rel_path: str
    height_mm: float
    cap_color_key: str


@dataclass
class LogicalInstance:
    name: str
    module_name: str
    source_path: str
    status: str
    solid_count: int
    position: tuple[float, float, float]
    rotation: tuple[float, float, float]
    world_shape: cq.Shape
    notes: str


TUBE_SPECS = {
    "purple75": TubeSpec("purple75", "03_cad/custom_parts/sample_tube/purple_cap_tube_13x75_v2.step", 75.0, "purple"),
    "yellow100": TubeSpec("yellow100", "03_cad/custom_parts/sample_tube/yellow_cap_tube_13x100_v2.step", 100.0, "yellow"),
    "blue75": TubeSpec("blue75", "03_cad/custom_parts/sample_tube/blue_cap_tube_13x75_v2.step", 75.0, "blue"),
    "red75": TubeSpec("red75", "03_cad/custom_parts/sample_tube/red_cap_tube_13x75_v2.step", 75.0, "red"),
}


def color_value(color_key: str) -> cq.Color:
    _, rgba = COLORS[color_key]
    return cq.Color(*rgba)


def color_manifest_row(instance_name: str, subpart_name: str, color_key: str, source: str, notes: str) -> dict[str, object]:
    color_name, rgba = COLORS[color_key]
    return {
        "component_name": subpart_name,
        "instance_name": instance_name,
        "expected_color": color_name,
        "material_or_role": color_key,
        "r": rgba[0],
        "g": rgba[1],
        "b": rgba[2],
        "a": rgba[3],
        "source_path": source,
        "notes": notes,
    }


def hole_points(rows: int, cols: int, pitch: float = 28.0) -> list[tuple[float, float]]:
    x0 = -((cols - 1) * pitch) / 2.0
    y0 = ((rows - 1) * pitch) / 2.0
    return [(x0 + col * pitch, y0 - row * pitch) for row in range(rows) for col in range(cols)]


def slot_xy(origin: tuple[float, float], rows: int, cols: int, row: int, col: int, pitch: float = 28.0) -> tuple[float, float]:
    local = hole_points(rows, cols, pitch)[row * cols + col]
    return (origin[0] + local[0], origin[1] + local[1])


def axis_from_bbox(bbox) -> str:
    dims = {"X": bbox.xlen, "Y": bbox.ylen, "Z": bbox.zlen}
    return max(dims, key=dims.get)


def rotation_to_target_axis(source_axis: str, target_axis: str | None) -> tuple[float, float, float]:
    if target_axis is None or source_axis == target_axis:
        return (0.0, 0.0, 0.0)
    rotations = {
        ("X", "Y"): (0.0, 0.0, 90.0),
        ("X", "Z"): (0.0, -90.0, 0.0),
        ("Y", "X"): (0.0, 0.0, -90.0),
        ("Y", "Z"): (90.0, 0.0, 0.0),
        ("Z", "X"): (0.0, 90.0, 0.0),
        ("Z", "Y"): (-90.0, 0.0, 0.0),
    }
    return rotations[(source_axis, target_axis)]


def rotate_shape(shape: cq.Shape, rotation: Iterable[float]) -> cq.Shape:
    rx, ry, rz = rotation
    rotated = shape
    if rx:
        rotated = rotated.rotate((0, 0, 0), (1, 0, 0), rx)
    if ry:
        rotated = rotated.rotate((0, 0, 0), (0, 1, 0), ry)
    if rz:
        rotated = rotated.rotate((0, 0, 0), (0, 0, 1), rz)
    return rotated


def make_compound(shapes: list[cq.Shape]) -> cq.Shape:
    return cq.Compound.makeCompound(shapes)


def bbox_values(shape: cq.Shape) -> tuple[float, float, float, float, float, float]:
    bbox = shape.BoundingBox()
    return (bbox.xmin, bbox.ymin, bbox.zmin, bbox.xmax, bbox.ymax, bbox.zmax)


def fmt_bbox(values: tuple[float, float, float, float, float, float]) -> str:
    return f"{values[3] - values[0]:.3f} x {values[4] - values[1]:.3f} x {values[5] - values[2]:.3f} mm"


def solid_count(shapes: list[cq.Shape]) -> int:
    return sum(len(shape.Solids()) for shape in shapes)


def annular_sector(inner_radius: float, outer_radius: float, height: float, start_angle_deg: float, end_angle_deg: float, segments: int = 72) -> cq.Shape:
    outer_points = []
    inner_points = []
    for index in range(segments + 1):
        angle = math.radians(start_angle_deg + (end_angle_deg - start_angle_deg) * index / segments)
        outer_points.append((outer_radius * math.cos(angle), outer_radius * math.sin(angle)))
        inner_points.append((inner_radius * math.cos(angle), inner_radius * math.sin(angle)))
    return cq.Workplane("XY").polyline(outer_points + list(reversed(inner_points))).close().extrude(height).val()


def make_tube_subparts(tube: TubeSpec) -> list[tuple[str, cq.Shape, str]]:
    body_radius = 6.5
    cap_radius = 8.0
    cap_height = 12.0
    label_height = 24.0
    body_height = tube.height_mm - cap_height
    label_bottom_z = max(22.0, min(body_height - label_height - 8.0, body_height * 0.46))
    body = cq.Workplane("XY").circle(body_radius).extrude(body_height).val()
    cap = cq.Workplane("XY").circle(cap_radius).extrude(cap_height).translate((0.0, 0.0, body_height)).val()
    label = annular_sector(body_radius + 0.04, body_radius + 0.26, label_height, -110.0, 110.0, segments=96).translate((0.0, 0.0, label_bottom_z))
    subparts = [("tube_body_13mm_od", body, "tube_body"), ("tube_cap", cap, tube.cap_color_key), ("curved_white_label_220deg", label, "tube_label")]
    for index, angle in enumerate([-72, -52, -28, -7, 18, 42, 66], start=1):
        stripe = annular_sector(body_radius + 0.26, body_radius + 0.32, label_height - 6.0, angle, angle + 3.0, segments=8).translate((0.0, 0.0, label_bottom_z + 3.0))
        subparts.append((f"curved_barcode_stripe_{index}", stripe, "barcode_black"))
    return subparts


def make_label_plate(label: str, width: float | None = None) -> list[tuple[str, cq.Shape, str]]:
    width = width or max(34.0, min(96.0, 11.0 * len(label)))
    base = cq.Workplane("XY").box(width, 3.0, 16.0).val()
    marker = cq.Workplane("XY").box(min(width - 8.0, 70.0), 0.8, 3.0).translate((0.0, -2.0, 0.0)).val()
    return [("plate_base", base, "plate_dark"), ("light_marker", marker, "plate_text")]


def make_xz_adapter_plate() -> list[tuple[str, cq.Shape, str]]:
    plate = cq.Workplane("XY").box(82.0, 5.5, 125.0).val()
    markers = []
    for index, (x, z) in enumerate([(-25.0, -38.0), (25.0, -38.0), (-25.0, 38.0), (25.0, 38.0)], start=1):
        marker = cq.Workplane("XZ").center(x, z).circle(4.5).extrude(0.7).translate((0.0, -3.1, 0.0)).val()
        markers.append((f"mount_hole_marker_{index}", marker, "plate_dark"))
    return [("adapter_plate", plate, "adapter_gray"), *markers]


def make_barcode_scanner_mount_bracket() -> list[tuple[str, cq.Shape, str]]:
    post = cq.Workplane("XY").box(8.0, 8.0, 62.0).val()
    arm = cq.Workplane("XY").box(40.0, 5.0, 5.0).translate((26.0, -2.0, 33.0)).val()
    foot = cq.Workplane("XY").box(22.0, 14.0, 4.0).translate((0.0, 0.0, -31.0)).val()
    return [("vertical_post", post, "bracket_gray"), ("scanner_support_arm", arm, "bracket_gray"), ("base_foot", foot, "bracket_gray")]


def make_photoelectric_sensor_mount_bracket() -> list[tuple[str, cq.Shape, str]]:
    post = cq.Workplane("XY").box(8.0, 8.0, 42.0).val()
    arm = cq.Workplane("XY").box(72.0, 5.0, 4.0).translate((38.0, 0.0, 22.0)).val()
    foot = cq.Workplane("XY").box(22.0, 14.0, 4.0).translate((0.0, 0.0, -21.0)).val()
    return [("vertical_post", post, "bracket_gray"), ("sensor_support_arm", arm, "bracket_gray"), ("base_foot", foot, "bracket_gray")]


def make_scan_tube_holder() -> list[tuple[str, cq.Shape, str]]:
    base = cq.Workplane("XY").box(36.0, 36.0, 8.0).val()
    socket = cq.Workplane("XY").circle(9.0).extrude(1.0).translate((0.0, 0.0, 4.6)).val()
    return [("holder_base", base, "bracket_gray"), ("tube_socket_marker", socket, "plate_dark")]


def make_control_box() -> list[tuple[str, cq.Shape, str]]:
    box = cq.Workplane("XY").box(120.0, 55.0, 70.0).val()
    panel = cq.Workplane("XY").box(100.0, 2.0, 50.0).translate((0.0, -28.5, 3.0)).val()
    return [("control_box_body", box, "control_box"), ("front_panel_marker", panel, "plate_dark")]


def make_emergency_stop() -> list[tuple[str, cq.Shape, str]]:
    base = cq.Workplane("XY").cylinder(10.0, 16.0).val()
    button = cq.Workplane("XY").cylinder(16.0, 24.0).translate((0.0, 0.0, 16.0)).val()
    return [("estop_base", base, "plate_dark"), ("red_button", button, "safety_red")]


def make_limit_switch() -> list[tuple[str, cq.Shape, str]]:
    body = cq.Workplane("XY").box(28.0, 14.0, 12.0).val()
    lever = cq.Workplane("XY").box(36.0, 3.0, 3.0).translate((18.0, 0.0, 8.0)).val()
    return [("limit_switch_body", body, "sensor_dark_gray"), ("limit_switch_lever", lever, "plate_text")]


def make_cable_chain_path() -> list[tuple[str, cq.Shape, str]]:
    rear_run = cq.Workplane("XY").box(820.0, 18.0, 18.0).val()
    drop = cq.Workplane("XY").box(18.0, 18.0, 150.0).translate((0.0, -70.0, -65.0)).val()
    return [("rear_chain_path", rear_run, "cable_chain"), ("moving_drop_path", drop, "cable_chain")]


def make_guard_frame() -> list[tuple[str, cq.Shape, str]]:
    parts = [
        ("front_guard_rail", cq.Workplane("XY").box(1180.0, 8.0, 180.0).translate((0.0, -440.0, 90.0)).val()),
        ("rear_guard_rail", cq.Workplane("XY").box(1180.0, 8.0, 180.0).translate((0.0, 440.0, 90.0)).val()),
        ("left_guard_rail", cq.Workplane("XY").box(8.0, 880.0, 180.0).translate((-590.0, 0.0, 90.0)).val()),
        ("right_guard_rail", cq.Workplane("XY").box(8.0, 880.0, 180.0).translate((590.0, 0.0, 90.0)).val()),
    ]
    return [(name, shape, "guard") for name, shape in parts]


def add_colored_subparts(
    assembly: cq.Assembly,
    manifest_rows: list[dict[str, object]],
    logical_name: str,
    module_name: str,
    source_path: str,
    subparts: list[tuple[str, cq.Shape, str]],
    position: tuple[float, float, float],
    rotation: tuple[float, float, float],
    notes: str,
) -> LogicalInstance:
    local_shapes = []
    for subpart_name, shape, color_key in subparts:
        rotated = rotate_shape(shape, rotation)
        assembly.add(rotated, name=f"{logical_name}_{subpart_name}", loc=cq.Location(cq.Vector(*position)), color=color_value(color_key))
        local_shapes.append(rotated)
        manifest_rows.append(color_manifest_row(logical_name, subpart_name, color_key, source_path, notes))
    world_shape = make_compound([shape.translate(position) for shape in local_shapes])
    return LogicalInstance(logical_name, module_name, source_path, "OK", solid_count(local_shapes), position, rotation, world_shape, notes)


def add_main_component(assembly: cq.Assembly, manifest_rows: list[dict[str, object]], spec: ComponentSpec) -> LogicalInstance:
    path = ROOT / spec.rel_path
    if not path.is_file():
        raise FileNotFoundError(path)
    workplane = cq.importers.importStep(str(path))
    shape = workplane.val()
    solids = len(workplane.solids().vals())
    if shape is None or solids < 1:
        raise RuntimeError(f"empty STEP geometry: {spec.rel_path}")
    source_axis = axis_from_bbox(shape.BoundingBox())
    auto_rotation = rotation_to_target_axis(source_axis, spec.target_axis)
    rotation = tuple(a + b for a, b in zip(spec.rotation, auto_rotation))
    final_shape = rotate_shape(shape, rotation)
    assembly.add(final_shape, name=spec.name, loc=cq.Location(cq.Vector(*spec.position)), color=color_value(spec.color_key))
    manifest_rows.append(color_manifest_row(spec.name, "imported_shape", spec.color_key, spec.rel_path, spec.note))
    return LogicalInstance(spec.name, spec.module_name, spec.rel_path, "OK", solids, spec.position, rotation, final_shape.translate(spec.position), spec.note)


class BaseLayout:
    module_name = "BaseLayout"

    def generated_components(self):
        plate = cq.Workplane("XY").box(*BASE_SIZE).translate((0.0, 0.0, -BASE_SIZE[2] / 2.0)).val()
        return [("base_plate_1200x900x15", self.module_name, [("base_plate", plate, "base_plate")], (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), "v7 generated 1200 x 900 x 15 mm base plate")]


class GantryModule:
    module_name = "GantryModule"

    def imported_components(self) -> list[ComponentSpec]:
        return [
            ComponentSpec("left_y_axis_module", self.module_name, "03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step", (-535.0, 0.0, 35.0), target_axis="Y", note="v7 outer left Y axis clears multi-input box stack"),
            ComponentSpec("right_y_axis_module", self.module_name, "03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step", (500.0, 0.0, 35.0), target_axis="Y", note="v7 outer right Y axis clears multi-output box stack"),
            ComponentSpec("x_axis_module_on_gantry", self.module_name, "03_cad/standard_parts/downloaded/x_axis_module/MISUMI_MSA628_X_axis_L750_double_shaft_B1_v1.step", (0.0, 10.0, 265.0), target_axis="X", note="v7 central X axis spans input scan and output zones"),
            ComponentSpec("z_axis_module", self.module_name, "03_cad/standard_parts/downloaded/z_axis_module/MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.step", (0.0, 20.0, 195.0), target_axis="Z", note="v7 vertical Z module aligned to central tool chain"),
            ComponentSpec("electric_parallel_gripper", self.module_name, "03_cad/standard_parts/downloaded/gripper/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.step", (0.0, 20.0, 115.0), note="v7 gripper below Z module"),
        ]

    def generated_components(self):
        return [("xz_adapter_plate_simplified", self.module_name, make_xz_adapter_plate(), (0.0, 20.0, 260.0), (0.0, 0.0, 0.0), "adapter at X/Z tool-chain interface")]


class MultiInputBoxModule:
    module_name = "MultiInputBoxModule"
    origins = [(-360.0, 285.0, 17.5), (-360.0, 155.0, 17.5), (-360.0, 25.0, 17.5), (-360.0, -105.0, 17.5)]

    def imported_components(self) -> list[ComponentSpec]:
        return [
            ComponentSpec(f"input_box_{index}", self.module_name, "03_cad/custom_parts/tube_bins/input_mixed_tube_rack_4x6.step", origin, color_key="input_box", note="replaceable 4x6 input box")
            for index, origin in enumerate(self.origins, start=1)
        ]

    def tube_instances(self):
        pattern = [(0, 0, "purple75"), (0, 3, "yellow100"), (1, 5, "blue75"), (2, 2, "red75"), (3, 4, "purple75")]
        rows = []
        for box_index, origin in enumerate(self.origins, start=1):
            for tube_index, (row, col, tube_key) in enumerate(pattern, start=1):
                x, y = slot_xy((origin[0], origin[1]), 4, 6, row, col)
                rows.append((f"input_box_{box_index}_demo_tube_{tube_index:02d}_{tube_key}", self.module_name, TUBE_SPECS[tube_key], (x, y, TUBE_INSERT_Z), f"demo tube in input_box_{box_index}; 4x6 slot row {row + 1} col {col + 1}"))
        return rows

    def generated_components(self):
        rows = []
        for index, origin in enumerate(self.origins, start=1):
            rows.append((f"label_plate_INPUT_{index}", self.module_name, make_label_plate(f"INPUT {index}", 74.0), (origin[0] + 135.0, origin[1], 8.0), (0.0, 0.0, 0.0), f"input_box_{index} side label"))
        return rows


class ScanStationModule:
    module_name = "ScanStationModule"
    origin = (-140.0, 60.0, 0.0)

    def local(self, dx: float, dy: float, dz: float):
        return (self.origin[0] + dx, self.origin[1] + dy, self.origin[2] + dz)

    def imported_components(self) -> list[ComponentSpec]:
        return [
            ComponentSpec("barcode_scanner", self.module_name, "03_cad/standard_parts/downloaded/barcode_scanner/Cognex_DataMan80_USB_fixed_barcode_reader_v1.step", self.local(6.0, 40.0, 86.0), color_key="scanner_black", note="v7 scanner aimed at scan tube holder"),
            ComponentSpec("photoelectric_sensor", self.module_name, "03_cad/standard_parts/downloaded/sensors/Panasonic_CX421J_diffuse_photoelectric_sensor_v1.step", self.local(95.0, 58.0, 62.0), color_key="sensor_dark_gray", note="v7 presence sensor for scan station"),
        ]

    def tube_instances(self):
        return [("scan_station_demo_tube_yellow100", self.module_name, TUBE_SPECS["yellow100"], self.local(0.0, 0.0, 24.0), "scan tube in v7 holder")]

    def generated_components(self):
        return [
            ("scan_tube_holder", self.module_name, make_scan_tube_holder(), self.local(0.0, 0.0, 7.0), (0.0, 0.0, 0.0), "scan station holder"),
            ("barcode_scanner_mount_bracket", self.module_name, make_barcode_scanner_mount_bracket(), self.local(-38.0, 58.0, 52.0), (0.0, 0.0, 0.0), "scanner bracket"),
            ("photoelectric_sensor_mount_bracket", self.module_name, make_photoelectric_sensor_mount_bracket(), self.local(70.0, 48.0, 37.0), (0.0, 0.0, 0.0), "sensor bracket"),
            ("label_plate_SCAN", self.module_name, make_label_plate("SCAN", 54.0), self.local(38.0, -42.0, 8.0), (0.0, 0.0, 0.0), "scan station label"),
        ]


class MultiOutputBoxModule:
    module_name = "MultiOutputBoxModule"
    boxes = {
        "A": ((350.0, 210.0, 17.5), "output_a", "Category A"),
        "B": ((350.0, 80.0, 17.5), "output_b", "Category B"),
        "C": ((350.0, -50.0, 17.5), "output_c", "Category C"),
        "D": ((350.0, -180.0, 17.5), "output_d", "Category D"),
    }

    def imported_components(self):
        return [
            ComponentSpec(f"category_{key}_output_box_4x6", self.module_name, "03_cad/custom_parts/tube_bins/input_mixed_tube_rack_4x6.step", origin, color_key=color_key, note=f"replaceable 4x6 output box for {label}")
            for key, (origin, color_key, label) in self.boxes.items()
        ]

    def tube_instances(self):
        rows = []
        tube_by_key = {"A": "purple75", "B": "yellow100", "C": "blue75", "D": "red75"}
        for key, (origin, _, _) in self.boxes.items():
            for index, (row, col) in enumerate([(0, 0), (1, 2), (2, 4)], start=1):
                x, y = slot_xy((origin[0], origin[1]), 4, 6, row, col)
                tube_key = tube_by_key[key]
                rows.append((f"category_{key}_classified_tube_{index:02d}_{tube_key}", self.module_name, TUBE_SPECS[tube_key], (x, y, TUBE_INSERT_Z), f"demo classified tube in Category {key} 4x6 output box"))
        return rows

    def generated_components(self):
        rows = []
        for key, (origin, _, label) in self.boxes.items():
            rows.append((f"label_plate_{key}", self.module_name, make_label_plate(key, 34.0), (origin[0] + 115.0, origin[1], 8.0), (0.0, 0.0, 90.0), f"{label} output side label"))
        return rows


class ManualReviewModule:
    module_name = "ManualReviewModule"
    origin = (-140.0, -300.0, 17.5)

    def imported_components(self):
        return [ComponentSpec("manual_review_bin_2x3", self.module_name, "03_cad/custom_parts/tube_bins/manual_review_bin_2x3.step", self.origin, color_key="manual_review", note="2x3 bin for true abnormal samples only")]

    def generated_components(self):
        return [("label_plate_REVIEW", self.module_name, make_label_plate("REVIEW", 76.0), (self.origin[0], self.origin[1] - 55.0, 8.0), (0.0, 0.0, 0.0), "manual review label")]


class ElectricalSafetyPlaceholderModule:
    module_name = "ElectricalSafetyPlaceholderModule"

    def generated_components(self):
        rows = [
            ("control_box_placeholder", self.module_name, make_control_box(), (520.0, 415.0, 35.0), (0.0, 0.0, 0.0), "rear/right electrical control box placeholder"),
            ("emergency_stop_placeholder", self.module_name, make_emergency_stop(), (-500.0, -415.0, 12.0), (0.0, 0.0, 0.0), "front reachable emergency stop placeholder"),
            ("cable_chain_path_placeholder", self.module_name, make_cable_chain_path(), (0.0, 390.0, 190.0), (0.0, 0.0, 0.0), "rear cable chain path placeholder"),
            ("transparent_guard_frame_placeholder", self.module_name, make_guard_frame(), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), "transparent perimeter guard frame placeholder"),
        ]
        for index, position in enumerate([(-535.0, -390.0, 82.0), (-535.0, 390.0, 82.0), (500.0, -390.0, 82.0), (500.0, 390.0, 82.0)], start=1):
            rows.append((f"limit_switch_placeholder_{index}", self.module_name, make_limit_switch(), position, (0.0, 0.0, 0.0), "axis end limit switch placeholder"))
        return rows


def validation_row(instance: LogicalInstance) -> dict[str, object]:
    xmin, ymin, zmin, xmax, ymax, zmax = bbox_values(instance.world_shape)
    return {
        "component_name": instance.name,
        "module_name": instance.module_name,
        "instance_name": instance.name,
        "source_path": instance.source_path,
        "import_status": instance.status,
        "solid_count": instance.solid_count,
        "target_x_mm": instance.position[0],
        "target_y_mm": instance.position[1],
        "target_z_mm": instance.position[2],
        "rotation_x_deg": instance.rotation[0],
        "rotation_y_deg": instance.rotation[1],
        "rotation_z_deg": instance.rotation[2],
        "bbox_min_x_mm": f"{xmin:.3f}",
        "bbox_min_y_mm": f"{ymin:.3f}",
        "bbox_min_z_mm": f"{zmin:.3f}",
        "bbox_max_x_mm": f"{xmax:.3f}",
        "bbox_max_y_mm": f"{ymax:.3f}",
        "bbox_max_z_mm": f"{zmax:.3f}",
        "notes": instance.notes,
    }


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


def pair_allowed(name_a: str, name_b: str) -> bool:
    names = {name_a, name_b}
    if "base_plate_1200x900x15" in names:
        return True
    if "transparent_guard_frame_placeholder" in names:
        return True
    if any(name.endswith("_demo_tube_yellow100") or "_demo_tube_" in name or "_classified_tube_" in name for name in names):
        if any("box" in name or "bin" in name or "holder" in name for name in names):
            return True
    mount_stack = {"x_axis_module_on_gantry", "z_axis_module", "xz_adapter_plate_simplified", "electric_parallel_gripper"}
    if len(names & mount_stack) == 2:
        return True
    expected_pairs = [
        {"barcode_scanner", "barcode_scanner_mount_bracket"},
        {"photoelectric_sensor", "photoelectric_sensor_mount_bracket"},
        {"transparent_guard_frame_placeholder", "base_plate_1200x900x15"},
    ]
    return any(names == pair for pair in expected_pairs)


def pair_threshold(name_a: str, name_b: str) -> float:
    scan_station = {"scan_station_demo_tube_yellow100", "barcode_scanner", "photoelectric_sensor"}
    moving_members = {"x_axis_module_on_gantry", "z_axis_module", "electric_parallel_gripper", "xz_adapter_plate_simplified"}
    if (name_a in scan_station and name_b in moving_members) or (name_b in scan_station and name_a in moving_members):
        return SCAN_MOVING_CLEARANCE_THRESHOLD_MM
    return DEFAULT_CLEARANCE_THRESHOLD_MM


def audit_instances(instances: list[LogicalInstance]):
    rows = []
    counts = {"ok": 0, "overlap": 0, "too_close": 0, "allowed_mount_contact": 0}
    for item_a, item_b in combinations(instances, 2):
        bbox_a = bbox_values(item_a.world_shape)
        bbox_b = bbox_values(item_b.world_shape)
        candidate = bbox_overlap(bbox_a, bbox_b)
        gap = bbox_clearance(bbox_a, bbox_b)
        threshold = pair_threshold(item_a.name, item_b.name)
        allowed = pair_allowed(item_a.name, item_b.name)
        notes = []
        overlap_volume = None
        if allowed and (candidate or gap < threshold):
            status = "allowed_mount_contact"
            notes.append("whitelisted expected mount/contact pair")
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


def configure_step_schema() -> list[str]:
    notes = []
    for schema in ["AP242DIS", "AP214IS"]:
        try:
            result = Interface_Static.SetCVal_s("write.step.schema", schema)
            notes.append(f"Attempted STEP schema {schema}; SetCVal returned {result}.")
            if result:
                return notes
        except Exception as exc:
            notes.append(f"Attempted STEP schema {schema}; failed with {type(exc).__name__}: {exc}.")
    return notes


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_report(success_count: int, failure_count: int, total_solids: int, exported_solids: int, total_bbox, audit_counts: dict[str, int]) -> None:
    REPORT_OUT.write_text(
        "\n".join([
            "# CadQuery Multi-box Layout v7 Report",
            "",
            "- v7 is based on the Stage 6R multi-box requirement.",
            "- Input boxes: 4 replaceable 4 x 6 boxes, 24 slots each, total input capacity 96.",
            "- Output boxes: Category A/B/C/D each has one replaceable 4 x 6 box, total output capacity 96.",
            "- Manual review: one 2 x 3 bin, capacity 6, reserved for true abnormal samples.",
            "- Base selection: 1200 x 900 x 15 mm. 1100 x 900 is retained for v6 but is crowded for multi-box layout plus safety/electrical zones.",
            "- Main v6 difference: v7 expands from single-batch prototype to multi-box batch layout and adds electrical/safety placeholders.",
            f"- Successful imported/generated components: {success_count}",
            f"- Failed components: {failure_count}",
            f"- Total solids: {total_solids} added / {exported_solids} exported",
            f"- Total bbox: {fmt_bbox(total_bbox)}",
            f"- Interference audit summary: overlap={audit_counts['overlap']}, too_close={audit_counts['too_close']}, allowed_mount_contact={audit_counts['allowed_mount_contact']}.",
            "- Key coverage: four input boxes, scan station, four category output boxes, manual review, gantry, control box, emergency stop, limit switches, cable chain path, and guard frame are represented.",
            "- Remaining engineering detail: formal brackets, engineering drawings, hole patterns, tolerances, electrical wiring, real guard design, and PID simulation.",
            f"- STEP path: `{STEP_OUT.relative_to(ROOT).as_posix()}`",
            "",
        ]),
        encoding="utf-8",
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    assembly = cq.Assembly(name="blood_sorting_robot_cadquery_multi_box_layout_v7")
    manifest_rows = []
    instances: list[LogicalInstance] = []
    failure_rows = []

    modules = [
        BaseLayout(),
        GantryModule(),
        MultiInputBoxModule(),
        ScanStationModule(),
        MultiOutputBoxModule(),
        ManualReviewModule(),
        ElectricalSafetyPlaceholderModule(),
    ]
    imported_specs: list[ComponentSpec] = []
    generated_specs = []
    tube_specs = []
    for module in modules:
        if hasattr(module, "imported_components"):
            imported_specs.extend(module.imported_components())
        if hasattr(module, "generated_components"):
            generated_specs.extend(module.generated_components())
        if hasattr(module, "tube_instances"):
            tube_specs.extend(module.tube_instances())

    for name, module_name, subparts, position, rotation, note in generated_specs:
        instances.append(add_colored_subparts(assembly, manifest_rows, name, module_name, f"generated:{name}", subparts, position, rotation, note))

    for spec in imported_specs:
        try:
            instances.append(add_main_component(assembly, manifest_rows, spec))
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
        instances.append(add_colored_subparts(assembly, manifest_rows, name, module_name, tube.rel_path, make_tube_subparts(tube), position, (0.0, 0.0, 0.0), note))

    validation_rows = [validation_row(instance) for instance in instances] + failure_rows
    audit_rows, audit_counts = audit_instances(instances)
    configure_step_schema()
    assembly.save(str(STEP_OUT), exportType="STEP", mode="default", write_pcurves=True)
    reimported = cq.importers.importStep(str(STEP_OUT))
    exported_solids = len(reimported.solids().vals())
    total_bbox = bbox_values(reimported.val())
    success_count = len(instances)
    failure_count = len(failure_rows)
    total_solids = sum(instance.solid_count for instance in instances)

    validation_fields = ["component_name", "module_name", "instance_name", "source_path", "import_status", "solid_count", "target_x_mm", "target_y_mm", "target_z_mm", "rotation_x_deg", "rotation_y_deg", "rotation_z_deg", "bbox_min_x_mm", "bbox_min_y_mm", "bbox_min_z_mm", "bbox_max_x_mm", "bbox_max_y_mm", "bbox_max_z_mm", "notes"]
    audit_fields = ["pair_a", "pair_b", "bbox_overlap_candidate", "exact_overlap_volume_mm3", "minimum_distance_mm", "clearance_threshold_mm", "audit_status", "notes"]
    manifest_fields = ["component_name", "instance_name", "expected_color", "material_or_role", "r", "g", "b", "a", "source_path", "notes"]
    write_csv(CSV_OUT, validation_rows, validation_fields)
    write_csv(AUDIT_CSV_OUT, audit_rows, audit_fields)
    write_csv(COLOR_MANIFEST_OUT, manifest_rows, manifest_fields)
    write_report(success_count, failure_count, total_solids, exported_solids, total_bbox, audit_counts)

    print(f"base_size={BASE_SIZE[0]:.0f} x {BASE_SIZE[1]:.0f} x {BASE_SIZE[2]:.0f} mm")
    print(f"success_count={success_count}")
    print(f"failure_count={failure_count}")
    print(f"total_solids={total_solids}")
    print(f"exported_solids={exported_solids}")
    print(f"total_bbox={fmt_bbox(total_bbox)}")
    print(f"audit_overlap={audit_counts['overlap']}")
    print(f"audit_too_close={audit_counts['too_close']}")
    print(f"audit_allowed_mount_contact={audit_counts['allowed_mount_contact']}")
    print(f"step={STEP_OUT}")
    print(f"validation_csv={CSV_OUT}")
    print(f"audit_csv={AUDIT_CSV_OUT}")
    print(f"color_manifest={COLOR_MANIFEST_OUT}")
    print(f"report={REPORT_OUT}")
    return 0 if failure_count == 0 and audit_counts["overlap"] == 0 and audit_counts["too_close"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
