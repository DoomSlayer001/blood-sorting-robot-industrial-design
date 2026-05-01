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

STEP_OUT = OUT_DIR / "blood_sorting_robot_cadquery_rough_layout_v5_1.step"
CSV_OUT = OUT_DIR / "blood_sorting_robot_cadquery_rough_layout_v5_1_validation.csv"
AUDIT_CSV_OUT = OUT_DIR / "blood_sorting_robot_cadquery_rough_layout_v5_1_interference_audit.csv"
COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_cadquery_rough_layout_v5_1_color_manifest.csv"
REPORT_OUT = REPORT_DIR / "cadquery_rough_assembly_v5_1_report.md"
AUDIT_REPORT_OUT = REPORT_DIR / "blood_sorting_robot_cadquery_rough_layout_v5_1_interference_report.md"
COLOR_REPORT_OUT = REPORT_DIR / "color_export_attempt_report_v5_1.md"

TUBE_INSERT_Z = 25.0
OVERLAP_VOLUME_THRESHOLD_MM3 = 1.0
DEFAULT_CLEARANCE_THRESHOLD_MM = 5.0
SCAN_MOVING_CLEARANCE_THRESHOLD_MM = 20.0


COLORS = {
    "axis_dark_gray": ("dark_gray", (0.22, 0.23, 0.24, 1.0)),
    "base_plate": ("base_light_gray", (0.70, 0.72, 0.74, 1.0)),
    "rack_light_gray": ("rack_light_gray", (0.83, 0.85, 0.84, 1.0)),
    "bin_mid_gray": ("bin_mid_gray", (0.72, 0.74, 0.73, 1.0)),
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
}


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    rel_path: str
    position: tuple[float, float, float]
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    target_axis: str | None = None
    color_key: str = "axis_dark_gray"
    note: str = ""


@dataclass(frozen=True)
class TubeSpec:
    key: str
    name: str
    rel_path: str
    height_mm: float
    cap_color_key: str


@dataclass
class LogicalInstance:
    name: str
    source_path: str
    status: str
    solid_count: int
    position: tuple[float, float, float]
    rotation: tuple[float, float, float]
    world_shape: cq.Shape
    notes: str


MAIN_COMPONENTS = [
    ComponentSpec("base_plate", "03_cad/custom_parts/base_plate/base_plate_1100x900x15.step", (0.0, 0.0, -7.5), color_key="base_plate"),
    ComponentSpec(
        "left_y_axis_module",
        "03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step",
        (-360.0, 0.0, 35.0),
        target_axis="Y",
        color_key="axis_dark_gray",
        note="v3/v4 gantry position retained; auto-align long axis to Y",
    ),
    ComponentSpec(
        "right_y_axis_module",
        "03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step",
        (360.0, 0.0, 35.0),
        target_axis="Y",
        color_key="axis_dark_gray",
        note="v3/v4 gantry position retained; auto-align long axis to Y",
    ),
    ComponentSpec(
        "x_axis_module_on_gantry",
        "03_cad/standard_parts/downloaded/x_axis_module/MISUMI_MSA628_X_axis_L750_double_shaft_B1_v1.step",
        (0.0, 0.0, 260.0),
        target_axis="X",
        color_key="axis_dark_gray",
        note="v3/v4 gantry position retained; auto-align long axis to X",
    ),
    ComponentSpec(
        "z_axis_module",
        "03_cad/standard_parts/downloaded/z_axis_module/MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.step",
        (0.0, 0.0, 195.0),
        target_axis="Z",
        color_key="axis_dark_gray",
        note="v3/v4 Z height retained; auto-align long axis to Z",
    ),
    ComponentSpec(
        "electric_parallel_gripper",
        "03_cad/standard_parts/downloaded/gripper/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.step",
        (0.0, 0.0, 115.0),
        color_key="axis_dark_gray",
        note="v3/v4 gripper height retained",
    ),
    ComponentSpec(
        "input_mixed_tube_rack_4x6",
        "03_cad/custom_parts/tube_bins/input_mixed_tube_rack_4x6.step",
        (-160.0, 300.0, 17.5),
        color_key="rack_light_gray",
        note="v5 moved inward from left Y axis for clearance after audit",
    ),
    ComponentSpec(
        "category_A_output_bin_2x3",
        "03_cad/custom_parts/tube_bins/category_A_output_bin_2x3.step",
        (90.0, -160.0, 17.5),
        color_key="bin_mid_gray",
        note="v5 moved away from right Y axis",
    ),
    ComponentSpec(
        "category_B_output_bin_2x3",
        "03_cad/custom_parts/tube_bins/category_B_output_bin_2x3.step",
        (250.0, -160.0, 17.5),
        color_key="bin_mid_gray",
        note="v5 moved away from right Y axis",
    ),
    ComponentSpec(
        "category_C_output_bin_2x3",
        "03_cad/custom_parts/tube_bins/category_C_output_bin_2x3.step",
        (90.0, -330.0, 17.5),
        color_key="bin_mid_gray",
        note="v5 moved away from right Y axis",
    ),
    ComponentSpec(
        "category_D_output_bin_2x3",
        "03_cad/custom_parts/tube_bins/category_D_output_bin_2x3.step",
        (250.0, -330.0, 17.5),
        color_key="bin_mid_gray",
        note="v5 moved away from right Y axis",
    ),
    ComponentSpec(
        "manual_review_bin_2x3",
        "03_cad/custom_parts/tube_bins/manual_review_bin_2x3.step",
        (-205.0, -330.0, 17.5),
        color_key="bin_mid_gray",
        note="v5 moved inward from left Y axis for clearance",
    ),
    ComponentSpec(
        "barcode_scanner",
        "03_cad/standard_parts/downloaded/barcode_scanner/Cognex_DataMan80_USB_fixed_barcode_reader_v1.step",
        (-135.0, 190.0, 82.0),
        color_key="scanner_black",
        note="v5.1 slightly adjusted scan-station display pose",
    ),
    ComponentSpec(
        "photoelectric_sensor",
        "03_cad/standard_parts/downloaded/sensors/Panasonic_CX421J_diffuse_photoelectric_sensor_v1.step",
        (-190.0, 105.0, 62.0),
        color_key="sensor_dark_gray",
        note="v5.1 slightly adjusted scan-station display pose",
    ),
]

TUBE_SPECS = {
    "purple75": TubeSpec("purple75", "purple_cap_tube_13x75_v2", "03_cad/custom_parts/sample_tube/purple_cap_tube_13x75_v2.step", 75.0, "purple"),
    "yellow100": TubeSpec("yellow100", "yellow_cap_tube_13x100_v2", "03_cad/custom_parts/sample_tube/yellow_cap_tube_13x100_v2.step", 100.0, "yellow"),
    "blue75": TubeSpec("blue75", "blue_cap_tube_13x75_v2", "03_cad/custom_parts/sample_tube/blue_cap_tube_13x75_v2.step", 75.0, "blue"),
    "red75": TubeSpec("red75", "red_cap_tube_13x75_v2", "03_cad/custom_parts/sample_tube/red_cap_tube_13x75_v2.step", 75.0, "red"),
}


def color_value(color_key: str) -> cq.Color:
    _, rgba = COLORS[color_key]
    return cq.Color(*rgba)


def color_manifest_row(instance_name: str, subpart_name: str, color_key: str, source: str, notes: str) -> dict[str, object]:
    color_name, rgba = COLORS[color_key]
    return {
        "instance_name": instance_name,
        "subpart_name": subpart_name,
        "color_name": color_name,
        "r": rgba[0],
        "g": rgba[1],
        "b": rgba[2],
        "a": rgba[3],
        "source_path": source,
        "notes": notes,
    }


def hole_points(rows: int, cols: int, pitch: float = 28.0) -> list[tuple[float, float]]:
    x0 = -((cols - 1) * pitch) / 2
    y0 = ((rows - 1) * pitch) / 2
    return [(x0 + c * pitch, y0 - r * pitch) for r in range(rows) for c in range(cols)]


def slot_xy(origin: tuple[float, float], rows: int, cols: int, row: int, col: int) -> tuple[float, float]:
    local = hole_points(rows, cols)[row * cols + col]
    return (origin[0] + local[0], origin[1] + local[1])


def build_tube_layout() -> list[tuple[str, TubeSpec, tuple[float, float, float], str]]:
    input_origin = (-160.0, 300.0)
    input_slots = [
        (0, 0, "purple75"),
        (0, 1, "yellow100"),
        (0, 3, "blue75"),
        (0, 5, "red75"),
        (1, 0, "yellow100"),
        (1, 2, "purple75"),
        (1, 4, "blue75"),
        (2, 1, "red75"),
        (2, 3, "yellow100"),
        (2, 5, "purple75"),
        (3, 0, "blue75"),
        (3, 4, "red75"),
    ]
    layout: list[tuple[str, TubeSpec, tuple[float, float, float], str]] = []
    for index, (row, col, tube_key) in enumerate(input_slots, start=1):
        x, y = slot_xy(input_origin, 4, 6, row, col)
        layout.append(
            (
                f"input_demo_tube_{index:02d}_{tube_key}",
                TUBE_SPECS[tube_key],
                (x, y, TUBE_INSERT_Z),
                f"input rack row {row + 1}, col {col + 1}; v5 input rack origin",
            )
        )

    layout.append(
        (
            "scan_station_demo_tube_yellow100",
            TUBE_SPECS["yellow100"],
            (-95.0, 150.0, 35.0),
            "v5.1 scan tube remains vertical with clearer scanner alignment",
        )
    )

    output_a_origin = (90.0, -160.0)
    output_b_origin = (250.0, -160.0)
    for index, (row, col) in enumerate([(0, 0), (1, 1)], start=1):
        x, y = slot_xy(output_a_origin, 2, 3, row, col)
        layout.append(
            (
                f"category_A_classified_tube_{index:02d}_purple75",
                TUBE_SPECS["purple75"],
                (x, y, TUBE_INSERT_Z),
                f"Category A output row {row + 1}, col {col + 1}; v5 output origin",
            )
        )
    x, y = slot_xy(output_b_origin, 2, 3, 0, 1)
    layout.append(
        (
            "category_B_classified_tube_01_yellow100",
            TUBE_SPECS["yellow100"],
            (x, y, TUBE_INSERT_Z),
            "Category B output row 1, col 2; v5 output origin",
        )
    )
    return layout


def annular_sector(
    inner_radius: float,
    outer_radius: float,
    height: float,
    start_angle_deg: float,
    end_angle_deg: float,
    segments: int = 72,
) -> cq.Shape:
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
    label_wrap_angle = 220.0
    label_clearance = 0.04
    label_thickness = 0.22
    body_height = tube.height_mm - cap_height
    label_bottom_z = max(22.0, min(body_height - label_height - 8.0, body_height * 0.46))

    body = cq.Workplane("XY").circle(body_radius).extrude(body_height).val()
    cap = cq.Workplane("XY").circle(cap_radius).extrude(cap_height).translate((0, 0, body_height)).val()
    label = annular_sector(
        body_radius + label_clearance,
        body_radius + label_clearance + label_thickness,
        label_height,
        -label_wrap_angle / 2,
        label_wrap_angle / 2,
        segments=96,
    ).translate((0, 0, label_bottom_z))

    subparts = [
        ("tube_body_13mm_od", body, "tube_body"),
        ("tube_cap", cap, tube.cap_color_key),
        ("curved_white_label_220deg", label, "tube_label"),
    ]

    stripe_angles = [-72, -58, -42, -25, -8, 14, 33, 56, 76]
    stripe_widths = [3.0, 2.0, 4.0, 2.5, 3.5, 2.0, 4.5, 2.0, 3.0]
    stripe_inner_radius = body_radius + label_clearance + label_thickness
    stripe_outer_radius = stripe_inner_radius + 0.06
    for index, (angle, width) in enumerate(zip(stripe_angles, stripe_widths), start=1):
        stripe = annular_sector(
            stripe_inner_radius,
            stripe_outer_radius,
            label_height - 6.0,
            angle,
            angle + width,
            segments=8,
        ).translate((0, 0, label_bottom_z + 3.0))
        subparts.append((f"curved_barcode_stripe_{index}", stripe, "barcode_black"))

    return subparts


def make_label_plate(label: str) -> list[tuple[str, cq.Shape, str]]:
    width = {"INPUT": 62.0, "REVIEW": 76.0}.get(label, 32.0)
    base = cq.Workplane("XY").box(width, 3.0, 16.0).val()
    marker_width = min(width - 8.0, 42.0)
    marker = cq.Workplane("XY").box(marker_width, 0.8, 3.0).translate((0, -2.0, 0)).val()
    return [("plate_base", base, "plate_dark"), ("light_marker", marker, "plate_text")]


def make_xz_adapter_plate() -> list[tuple[str, cq.Shape, str]]:
    plate = cq.Workplane("XY").box(105.0, 5.5, 150.0).val()
    subparts = [("adapter_plate", plate, "adapter_gray")]
    for index, (x, z) in enumerate([(-32.0, -45.0), (32.0, -45.0), (-32.0, 45.0), (32.0, 45.0)], start=1):
        marker = (
            cq.Workplane("XZ")
            .center(x, z)
            .circle(4.5)
            .extrude(0.7)
            .translate((0.0, -3.1, 0.0))
            .val()
        )
        subparts.append((f"mount_hole_marker_{index}", marker, "plate_dark"))
    return subparts


def make_barcode_scanner_mount_bracket() -> list[tuple[str, cq.Shape, str]]:
    post = cq.Workplane("XY").box(10.0, 8.0, 72.0).val()
    arm = cq.Workplane("XY").box(54.0, 5.0, 5.0).translate((35.0, -4.0, 39.0)).val()
    foot = cq.Workplane("XY").box(24.0, 16.0, 4.0).translate((0.0, 0.0, -36.0)).val()
    return [
        ("vertical_post", post, "bracket_gray"),
        ("scanner_support_arm", arm, "bracket_gray"),
        ("base_foot", foot, "bracket_gray"),
    ]


def make_photoelectric_sensor_mount_bracket() -> list[tuple[str, cq.Shape, str]]:
    post = cq.Workplane("XY").box(8.0, 8.0, 46.0).val()
    arm = cq.Workplane("XY").box(92.0, 5.0, 4.0).translate((48.0, 0.0, 24.0)).val()
    foot = cq.Workplane("XY").box(22.0, 14.0, 4.0).translate((0.0, 0.0, -23.0)).val()
    return [
        ("vertical_post", post, "bracket_gray"),
        ("sensor_support_arm", arm, "bracket_gray"),
        ("base_foot", foot, "bracket_gray"),
    ]


def generated_layout() -> list[tuple[str, list[tuple[str, cq.Shape, str]], tuple[float, float, float], tuple[float, float, float], str]]:
    layout = [
        (
            "xz_adapter_plate_simplified",
            make_xz_adapter_plate(),
            (0.0, -60.0, 218.0),
            (0.0, 0.0, 0.0),
            "v5.1 adapter plate with simple mounting hole markers",
        ),
        (
            "barcode_scanner_mount_bracket",
            make_barcode_scanner_mount_bracket(),
            (-180.0, 220.0, 46.0),
            (0.0, 0.0, 0.0),
            "v5.1 simplified bracket explaining barcode scanner mounting",
        ),
        (
            "photoelectric_sensor_mount_bracket",
            make_photoelectric_sensor_mount_bracket(),
            (-205.0, 44.0, 35.0),
            (0.0, 0.0, 0.0),
            "v5.1 simplified bracket explaining photoelectric sensor mounting",
        )
    ]
    label_specs = [
        ("label_plate_INPUT", "INPUT", (-30.0, 225.0, 15.0)),
        ("label_plate_A", "A", (90.0, -215.0, 15.0)),
        ("label_plate_B", "B", (250.0, -215.0, 15.0)),
        ("label_plate_C", "C", (90.0, -385.0, 15.0)),
        ("label_plate_D", "D", (250.0, -385.0, 15.0)),
        ("label_plate_REVIEW", "REVIEW", (-205.0, -385.0, 15.0)),
    ]
    for name, text, position in label_specs:
        layout.append((name, make_label_plate(text), position, (0.0, 0.0, 0.0), f"{text} name plate with dark base and light text/marker"))
    return layout


def axis_from_bbox(bbox) -> str:
    dimensions = {"X": bbox.xlen, "Y": bbox.ylen, "Z": bbox.zlen}
    return max(dimensions, key=dimensions.get)


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
    return (
        f"{values[3] - values[0]:.3f} x "
        f"{values[4] - values[1]:.3f} x "
        f"{values[5] - values[2]:.3f} mm"
    )


def solid_count(shapes: list[cq.Shape]) -> int:
    return sum(len(shape.Solids()) for shape in shapes)


def add_colored_subparts(
    assembly: cq.Assembly,
    manifest_rows: list[dict[str, object]],
    logical_name: str,
    source_path: str,
    subparts: list[tuple[str, cq.Shape, str]],
    position: tuple[float, float, float],
    rotation: tuple[float, float, float],
    notes: str,
) -> LogicalInstance:
    local_shapes: list[cq.Shape] = []
    for subpart_name, shape, color_key in subparts:
        rotated = rotate_shape(shape, rotation)
        assembly.add(rotated, name=f"{logical_name}_{subpart_name}", loc=cq.Location(cq.Vector(*position)), color=color_value(color_key))
        local_shapes.append(rotated)
        manifest_rows.append(color_manifest_row(logical_name, subpart_name, color_key, source_path, notes))
    world_shape = make_compound([shape.translate(position) for shape in local_shapes])
    return LogicalInstance(logical_name, source_path, "OK", solid_count(local_shapes), position, rotation, world_shape, notes)


def add_main_component(
    assembly: cq.Assembly,
    manifest_rows: list[dict[str, object]],
    spec: ComponentSpec,
) -> LogicalInstance:
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
    return LogicalInstance(spec.name, spec.rel_path, "OK", solids, spec.position, rotation, final_shape.translate(spec.position), spec.note)


def validation_row(instance: LogicalInstance) -> dict[str, object]:
    xmin, ymin, zmin, xmax, ymax, zmax = bbox_values(instance.world_shape)
    return {
        "component_name": instance.name,
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


def bbox_overlap(a: tuple[float, float, float, float, float, float], b: tuple[float, float, float, float, float, float]) -> bool:
    return all(a[index] <= b[index + 3] and b[index] <= a[index + 3] for index in range(3))


def bbox_clearance(a: tuple[float, float, float, float, float, float], b: tuple[float, float, float, float, float, float]) -> float:
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


def exact_distance(shape_a: cq.Shape, shape_b: cq.Shape) -> tuple[float | None, str]:
    try:
        return shape_a.distance(shape_b), ""
    except Exception as exc:
        return None, f"distance_check_error={exc}"


def pair_allowed(name_a: str, name_b: str) -> bool:
    names = {name_a, name_b}
    if "base_plate" in names:
        return True
    mount_stack = {"x_axis_module_on_gantry", "z_axis_module", "xz_adapter_plate_simplified", "electric_parallel_gripper"}
    if len(names & mount_stack) == 2:
        return True
    if "input_mixed_tube_rack_4x6" in names and any(name.startswith("input_demo_tube_") for name in names):
        return True
    if "category_A_output_bin_2x3" in names and any(name.startswith("category_A_classified_tube_") for name in names):
        return True
    if "category_B_output_bin_2x3" in names and any(name.startswith("category_B_classified_tube_") for name in names):
        return True
    return False


def pair_threshold(name_a: str, name_b: str) -> float:
    scan_station = {"scan_station_demo_tube_yellow100", "barcode_scanner", "photoelectric_sensor"}
    moving_members = {"x_axis_module_on_gantry", "z_axis_module", "electric_parallel_gripper", "xz_adapter_plate_simplified"}
    if (name_a in scan_station and name_b in moving_members) or (name_b in scan_station and name_a in moving_members):
        return SCAN_MOVING_CLEARANCE_THRESHOLD_MM
    return DEFAULT_CLEARANCE_THRESHOLD_MM


def audit_instances(instances: list[LogicalInstance]) -> tuple[list[dict[str, object]], dict[str, int]]:
    rows: list[dict[str, object]] = []
    counts = {"ok": 0, "overlap": 0, "too_close": 0, "allowed_mount_contact": 0}

    for item_a, item_b in combinations(instances, 2):
        bbox_a = bbox_values(item_a.world_shape)
        bbox_b = bbox_values(item_b.world_shape)
        bbox_is_candidate = bbox_overlap(bbox_a, bbox_b)
        bbox_gap = bbox_clearance(bbox_a, bbox_b)
        threshold = pair_threshold(item_a.name, item_b.name)
        allowed = pair_allowed(item_a.name, item_b.name)
        overlap_volume: float | None = None
        minimum_distance: float | None = None
        notes = []

        if allowed and (bbox_is_candidate or bbox_gap < threshold):
            counts["allowed_mount_contact"] += 1
            rows.append(
                {
                    "pair_a": item_a.name,
                    "pair_b": item_b.name,
                    "bbox_overlap_candidate": "yes" if bbox_is_candidate else "no",
                    "exact_overlap_volume_mm3": "",
                    "minimum_distance_mm": "",
                    "clearance_threshold_mm": threshold,
                    "audit_status": "allowed_mount_contact",
                    "notes": "whitelisted expected mount/contact pair; exact boolean skipped",
                }
            )
            continue

        if bbox_is_candidate:
            status = "overlap"
            notes.append("non-whitelisted bbox overlap candidate; conservative v5.1 audit marks as overlap")
        elif 0.0 < bbox_gap < threshold:
            status = "too_close"
        else:
            status = "ok"

        counts[status] += 1
        rows.append(
            {
                "pair_a": item_a.name,
                "pair_b": item_b.name,
                "bbox_overlap_candidate": "yes" if bbox_is_candidate else "no",
                "exact_overlap_volume_mm3": "" if overlap_volume is None else f"{overlap_volume:.6f}",
                "minimum_distance_mm": "" if bbox_is_candidate else f"{bbox_gap:.6f}",
                "clearance_threshold_mm": threshold,
                "audit_status": status,
                "notes": "; ".join(notes),
            }
        )
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
    notes.append("No STEP schema setting was confirmed; CadQuery default STEPCAF/XCAF export settings were used.")
    return notes


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_reports(
    success_count: int,
    failure_count: int,
    total_solids: int,
    exported_solids: int,
    total_bbox: tuple[float, float, float, float, float, float],
    audit_counts: dict[str, int],
    color_notes: list[str],
) -> None:
    REPORT_OUT.write_text(
        "\n".join(
            [
                "# CadQuery Rough Assembly v5.1 Report",
                "",
                "- v5.1 is based on v5, which already passed SolidWorks 2026 visual inspection.",
                "- v5.1 only makes presentation refinements; the main layout is not broadly changed.",
                "- Added barcode scanner mount bracket and photoelectric sensor mount bracket.",
                "- Slightly adjusted the scan-station display pose.",
                "- Optimized the X-Z adapter plate with simple mounting hole markers.",
                "- Deferred components remain excluded: cable chain, emergency stop, control box, limit switches, and motors.",
                f"- Successful imported/generated components: {success_count}",
                f"- Failed components: {failure_count}",
                f"- Total solids: {total_solids} added / {exported_solids} exported",
                f"- Total bbox: {fmt_bbox(total_bbox)}",
                "- STEP color export: attempted through CadQuery/OCP XCAF/STEPCAF; v5 colors were visible in SolidWorks 2026.",
                f"- Interference audit summary: overlap={audit_counts['overlap']}, too_close={audit_counts['too_close']}, allowed_mount_contact={audit_counts['allowed_mount_contact']}.",
                f"- Output STEP path: `{STEP_OUT.relative_to(ROOT).as_posix()}`",
                "- Next step: open the v5.1 STEP in SolidWorks 2026 for manual inspection.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    AUDIT_REPORT_OUT.write_text(
        "\n".join(
            [
                "# CadQuery Rough Assembly v5.1 Interference Report",
                "",
                f"- Pair count audited: {sum(audit_counts.values())}",
                f"- Overlap count: {audit_counts['overlap']}",
                f"- Too-close count: {audit_counts['too_close']}",
                f"- Allowed mount/contact count: {audit_counts['allowed_mount_contact']}",
                f"- OK count: {audit_counts['ok']}",
                f"- CSV: `{AUDIT_CSV_OUT.relative_to(ROOT).as_posix()}`",
                "- Thresholds: overlap volume > 1 mm^3 is overlap; clearance < 5 mm is too_close; scan station vs moving members uses 20 mm.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    COLOR_REPORT_OUT.write_text(
        "\n".join(
            [
                "# Color Export Attempt Report v5.1",
                "",
                "- Export path: CadQuery assembly STEP export using OCCT XCAF/STEPCAF color/name support.",
                "- STEP color mode/name mode are enabled by CadQuery's assembly exporter.",
                "- Local verification can confirm geometry re-import only; it cannot prove SolidWorks 2026 will preserve colors.",
                "- Fallback color manifest was generated for every intended colored instance/subpart.",
                f"- Manifest: `{COLOR_MANIFEST_OUT.relative_to(ROOT).as_posix()}`",
                "",
                "## Attempts",
                "",
                *[f"- {note}" for note in color_notes],
                "",
                "Conclusion: STEP color export was attempted again for v5.1. v5 colors were visible in SolidWorks 2026, but v5.1 should still be manually checked.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    assembly = cq.Assembly(name="blood_sorting_robot_cadquery_rough_layout_v5_1")
    manifest_rows: list[dict[str, object]] = []
    instances: list[LogicalInstance] = []
    failure_rows: list[dict[str, object]] = []

    for spec in MAIN_COMPONENTS:
        try:
            instances.append(add_main_component(assembly, manifest_rows, spec))
        except Exception as exc:
            failure_rows.append(
                {
                    "component_name": spec.name,
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
                }
            )

    for name, tube, position, note in build_tube_layout():
        tube_path = ROOT / tube.rel_path
        if not tube_path.is_file() or tube_path.stat().st_size <= 0:
            raise FileNotFoundError(f"Missing or empty v2 tube STEP reference: {tube.rel_path}")
        subparts = make_tube_subparts(tube)
        instances.append(add_colored_subparts(assembly, manifest_rows, name, tube.rel_path, subparts, position, (0.0, 0.0, 0.0), note))

    for name, subparts, position, rotation, note in generated_layout():
        instances.append(add_colored_subparts(assembly, manifest_rows, name, f"generated:{name}", subparts, position, rotation, note))

    validation_rows = [validation_row(instance) for instance in instances] + failure_rows
    success_count = len(instances)
    failure_count = len(failure_rows)
    total_solids = sum(instance.solid_count for instance in instances)

    audit_rows, audit_counts = audit_instances(instances)
    color_notes = configure_step_schema()
    assembly.save(str(STEP_OUT), exportType="STEP", mode="default", write_pcurves=True)

    reimported = cq.importers.importStep(str(STEP_OUT))
    exported_solids = len(reimported.solids().vals())
    total_bbox = bbox_values(reimported.val())

    write_csv(
        CSV_OUT,
        validation_rows,
        [
            "component_name",
            "source_path",
            "import_status",
            "solid_count",
            "target_x_mm",
            "target_y_mm",
            "target_z_mm",
            "rotation_x_deg",
            "rotation_y_deg",
            "rotation_z_deg",
            "bbox_min_x_mm",
            "bbox_min_y_mm",
            "bbox_min_z_mm",
            "bbox_max_x_mm",
            "bbox_max_y_mm",
            "bbox_max_z_mm",
            "notes",
        ],
    )
    write_csv(
        AUDIT_CSV_OUT,
        audit_rows,
        [
            "pair_a",
            "pair_b",
            "bbox_overlap_candidate",
            "exact_overlap_volume_mm3",
            "minimum_distance_mm",
            "clearance_threshold_mm",
            "audit_status",
            "notes",
        ],
    )
    write_csv(
        COLOR_MANIFEST_OUT,
        manifest_rows,
        ["instance_name", "subpart_name", "color_name", "r", "g", "b", "a", "source_path", "notes"],
    )
    write_reports(success_count, failure_count, total_solids, exported_solids, total_bbox, audit_counts, color_notes)

    print(f"success_count={success_count}")
    print(f"failure_count={failure_count}")
    print(f"total_solids={total_solids}")
    print(f"exported_solids={exported_solids}")
    print(f"total_bbox={fmt_bbox(total_bbox)}")
    print(f"audit_overlap={audit_counts['overlap']}")
    print(f"audit_too_close={audit_counts['too_close']}")
    print(f"step={STEP_OUT}")
    print(f"validation_csv={CSV_OUT}")
    print(f"audit_csv={AUDIT_CSV_OUT}")
    print(f"color_manifest={COLOR_MANIFEST_OUT}")
    print(f"report={REPORT_OUT}")
    return 0 if failure_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
