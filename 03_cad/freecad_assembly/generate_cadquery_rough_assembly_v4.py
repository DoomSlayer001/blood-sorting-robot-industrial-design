from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "03_cad" / "freecad_assembly"
STEP_OUT = OUT_DIR / "blood_sorting_robot_cadquery_rough_layout_v4.step"
CSV_OUT = OUT_DIR / "blood_sorting_robot_cadquery_rough_layout_v4_validation.csv"
REPORT_OUT = ROOT / "reports" / "cadquery_rough_assembly_v4_report.md"

TUBE_INSERT_Z = 25.0


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    rel_path: str
    position: tuple[float, float, float]
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    target_axis: str | None = None
    note: str = ""


MAIN_COMPONENTS = [
    ComponentSpec("base_plate", "03_cad/custom_parts/base_plate/base_plate_1100x900x15.step", (0.0, 0.0, -7.5)),
    ComponentSpec(
        "left_y_axis_module",
        "03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step",
        (-360.0, 0.0, 35.0),
        target_axis="Y",
        note="v3 position retained; auto-align long axis to Y",
    ),
    ComponentSpec(
        "right_y_axis_module",
        "03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step",
        (360.0, 0.0, 35.0),
        target_axis="Y",
        note="v3 position retained; auto-align long axis to Y",
    ),
    ComponentSpec(
        "x_axis_module_on_gantry",
        "03_cad/standard_parts/downloaded/x_axis_module/MISUMI_MSA628_X_axis_L750_double_shaft_B1_v1.step",
        (0.0, 0.0, 260.0),
        target_axis="X",
        note="v3 position retained; auto-align long axis to X",
    ),
    ComponentSpec(
        "z_axis_module",
        "03_cad/standard_parts/downloaded/z_axis_module/MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.step",
        (0.0, 0.0, 195.0),
        target_axis="Z",
        note="v3 position retained; auto-align long axis to Z",
    ),
    ComponentSpec(
        "electric_parallel_gripper",
        "03_cad/standard_parts/downloaded/gripper/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.step",
        (0.0, 0.0, 115.0),
        note="v3 position retained",
    ),
    ComponentSpec(
        "input_mixed_tube_rack_4x6",
        "03_cad/custom_parts/tube_bins/input_mixed_tube_rack_4x6.step",
        (-330.0, 300.0, 17.5),
        note="v3 position retained",
    ),
    ComponentSpec(
        "category_A_output_bin_2x3",
        "03_cad/custom_parts/tube_bins/category_A_output_bin_2x3.step",
        (150.0, -160.0, 17.5),
        note="v3 position retained",
    ),
    ComponentSpec(
        "category_B_output_bin_2x3",
        "03_cad/custom_parts/tube_bins/category_B_output_bin_2x3.step",
        (360.0, -160.0, 17.5),
        note="v3 position retained",
    ),
    ComponentSpec(
        "category_C_output_bin_2x3",
        "03_cad/custom_parts/tube_bins/category_C_output_bin_2x3.step",
        (150.0, -330.0, 17.5),
        note="v3 position retained",
    ),
    ComponentSpec(
        "category_D_output_bin_2x3",
        "03_cad/custom_parts/tube_bins/category_D_output_bin_2x3.step",
        (360.0, -330.0, 17.5),
        note="v3 position retained",
    ),
    ComponentSpec(
        "manual_review_bin_2x3",
        "03_cad/custom_parts/tube_bins/manual_review_bin_2x3.step",
        (-250.0, -300.0, 17.5),
        note="v3 position retained",
    ),
    ComponentSpec(
        "barcode_scanner",
        "03_cad/standard_parts/downloaded/barcode_scanner/Cognex_DataMan80_USB_fixed_barcode_reader_v1.step",
        (-180.0, 225.0, 82.0),
        note="v3 position retained",
    ),
    ComponentSpec(
        "photoelectric_sensor",
        "03_cad/standard_parts/downloaded/sensors/Panasonic_CX421J_diffuse_photoelectric_sensor_v1.step",
        (-210.0, 205.0, 62.0),
        note="v3 position retained",
    ),
]

TUBE_PATHS = {
    "purple75": "03_cad/custom_parts/sample_tube/purple_cap_tube_13x75_v2.step",
    "yellow100": "03_cad/custom_parts/sample_tube/yellow_cap_tube_13x100_v2.step",
    "blue75": "03_cad/custom_parts/sample_tube/blue_cap_tube_13x75_v2.step",
    "red75": "03_cad/custom_parts/sample_tube/red_cap_tube_13x75_v2.step",
}


def hole_points(rows: int, cols: int, pitch: float = 28.0) -> list[tuple[float, float]]:
    x0 = -((cols - 1) * pitch) / 2
    y0 = ((rows - 1) * pitch) / 2
    return [(x0 + c * pitch, y0 - r * pitch) for r in range(rows) for c in range(cols)]


def slot_xy(origin: tuple[float, float], rows: int, cols: int, row: int, col: int) -> tuple[float, float]:
    local = hole_points(rows, cols)[row * cols + col]
    return (origin[0] + local[0], origin[1] + local[1])


def build_tube_instances() -> list[ComponentSpec]:
    input_origin = (-330.0, 300.0)
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
    specs: list[ComponentSpec] = []
    for index, (row, col, tube_key) in enumerate(input_slots, start=1):
        x, y = slot_xy(input_origin, 4, 6, row, col)
        specs.append(
            ComponentSpec(
                f"input_demo_tube_{index:02d}_{tube_key}",
                TUBE_PATHS[tube_key],
                (x, y, TUBE_INSERT_Z),
                note=f"input rack row {row + 1}, col {col + 1}",
            )
        )

    specs.append(
        ComponentSpec(
            "scan_station_demo_tube_yellow100",
            TUBE_PATHS["yellow100"],
            (-195.0, 215.0, 35.0),
            note="demo tube near barcode scanner and photoelectric sensor",
        )
    )

    output_a_origin = (150.0, -160.0)
    output_b_origin = (360.0, -160.0)
    for index, (row, col) in enumerate([(0, 0), (1, 1)], start=1):
        x, y = slot_xy(output_a_origin, 2, 3, row, col)
        specs.append(
            ComponentSpec(
                f"category_A_classified_tube_{index:02d}_purple75",
                TUBE_PATHS["purple75"],
                (x, y, TUBE_INSERT_Z),
                note=f"Category A output row {row + 1}, col {col + 1}",
            )
        )
    x, y = slot_xy(output_b_origin, 2, 3, 0, 1)
    specs.append(
        ComponentSpec(
            "category_B_classified_tube_01_yellow100",
            TUBE_PATHS["yellow100"],
            (x, y, TUBE_INSERT_Z),
            note="Category B output row 1, col 2",
        )
    )
    return specs


def generated_components() -> list[tuple[str, object, tuple[float, float, float], tuple[float, float, float], str, cq.Color]]:
    adapter_plate = cq.Workplane("XY").box(120.0, 8.0, 165.0)
    labels = [
        ("label_plate_INPUT", cq.Workplane("XY").box(58.0, 2.0, 16.0), (-330.0, 230.0, 48.0), "INPUT label plate"),
        ("label_plate_A", cq.Workplane("XY").box(30.0, 2.0, 16.0), (150.0, -215.0, 48.0), "A label plate"),
        ("label_plate_B", cq.Workplane("XY").box(30.0, 2.0, 16.0), (360.0, -215.0, 48.0), "B label plate"),
        ("label_plate_C", cq.Workplane("XY").box(30.0, 2.0, 16.0), (150.0, -385.0, 48.0), "C label plate"),
        ("label_plate_D", cq.Workplane("XY").box(30.0, 2.0, 16.0), (360.0, -385.0, 48.0), "D label plate"),
        ("label_plate_REVIEW", cq.Workplane("XY").box(70.0, 2.0, 16.0), (-250.0, -355.0, 48.0), "REVIEW label plate"),
    ]
    generated = [
        (
            "xz_adapter_plate_simplified",
            adapter_plate,
            (0.0, -44.0, 218.0),
            (0.0, 0.0, 0.0),
            "generated simplified X-Z adapter plate",
            cq.Color(0.55, 0.58, 0.60, 1.0),
        )
    ]
    for name, shape, position, note in labels:
        generated.append(
            (
                name,
                shape,
                position,
                (0.0, 0.0, 0.0),
                note,
                cq.Color(0.10, 0.10, 0.10, 1.0),
            )
        )
    return generated


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


def rotate_shape(shape, rotation: Iterable[float]):
    rx, ry, rz = rotation
    rotated = shape
    if rx:
        rotated = rotated.rotate((0, 0, 0), (1, 0, 0), rx)
    if ry:
        rotated = rotated.rotate((0, 0, 0), (0, 1, 0), ry)
    if rz:
        rotated = rotated.rotate((0, 0, 0), (0, 0, 1), rz)
    return rotated


def bbox_values(shape) -> tuple[float, float, float, float, float, float]:
    bbox = shape.BoundingBox()
    return (bbox.xmin, bbox.ymin, bbox.zmin, bbox.xmax, bbox.ymax, bbox.zmax)


def fmt_bbox(values: tuple[float, float, float, float, float, float]) -> str:
    return (
        f"{values[3] - values[0]:.3f} x "
        f"{values[4] - values[1]:.3f} x "
        f"{values[5] - values[2]:.3f} mm"
    )


def validation_row(
    component_name: str,
    source_path: str,
    status: str,
    solid_count: int,
    position: tuple[float, float, float],
    rotation: tuple[float, float, float],
    shape,
    notes: str,
) -> dict[str, object]:
    placed = shape.translate(position)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox_values(placed)
    return {
        "component_name": component_name,
        "source_path": source_path,
        "import_status": status,
        "solid_count": solid_count,
        "target_x_mm": position[0],
        "target_y_mm": position[1],
        "target_z_mm": position[2],
        "rotation_x_deg": rotation[0],
        "rotation_y_deg": rotation[1],
        "rotation_z_deg": rotation[2],
        "bbox_min_x_mm": f"{xmin:.3f}",
        "bbox_min_y_mm": f"{ymin:.3f}",
        "bbox_min_z_mm": f"{zmin:.3f}",
        "bbox_max_x_mm": f"{xmax:.3f}",
        "bbox_max_y_mm": f"{ymax:.3f}",
        "bbox_max_z_mm": f"{zmax:.3f}",
        "notes": notes,
    }


def failed_row(component_name: str, source_path: str, position: tuple[float, float, float], rotation, notes: str, error: str):
    return {
        "component_name": component_name,
        "source_path": source_path,
        "import_status": "FAILED",
        "solid_count": 0,
        "target_x_mm": position[0],
        "target_y_mm": position[1],
        "target_z_mm": position[2],
        "rotation_x_deg": rotation[0],
        "rotation_y_deg": rotation[1],
        "rotation_z_deg": rotation[2],
        "bbox_min_x_mm": "",
        "bbox_min_y_mm": "",
        "bbox_min_z_mm": "",
        "bbox_max_x_mm": "",
        "bbox_max_y_mm": "",
        "bbox_max_z_mm": "",
        "notes": f"{notes}; error={error}",
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    assembly = cq.Assembly(name="blood_sorting_robot_cadquery_rough_layout_v4")
    rows: list[dict[str, object]] = []
    success_count = 0
    failure_count = 0
    total_solids = 0

    for spec in MAIN_COMPONENTS + build_tube_instances():
        path = ROOT / spec.rel_path
        try:
            if not path.is_file():
                raise FileNotFoundError(path)
            workplane = cq.importers.importStep(str(path))
            shape = workplane.val()
            solids = len(workplane.solids().vals())
            if shape is None or solids < 1:
                raise RuntimeError("empty STEP geometry")
            source_axis = axis_from_bbox(shape.BoundingBox())
            auto_rotation = rotation_to_target_axis(source_axis, spec.target_axis)
            rotation = tuple(a + b for a, b in zip(spec.rotation, auto_rotation))
            final_shape = rotate_shape(shape, rotation)
            assembly.add(final_shape, name=spec.name, loc=cq.Location(cq.Vector(*spec.position)))
            rows.append(validation_row(spec.name, spec.rel_path, "OK", solids, spec.position, rotation, final_shape, spec.note))
            success_count += 1
            total_solids += solids
        except Exception as exc:
            rows.append(failed_row(spec.name, spec.rel_path, spec.position, spec.rotation, spec.note, str(exc)))
            failure_count += 1

    for name, workplane, position, rotation, note, color in generated_components():
        try:
            shape = workplane.val()
            solids = len(workplane.solids().vals())
            final_shape = rotate_shape(shape, rotation)
            assembly.add(final_shape, name=name, loc=cq.Location(cq.Vector(*position)), color=color)
            rows.append(validation_row(name, f"generated:{name}", "GENERATED", solids, position, rotation, final_shape, note))
            success_count += 1
            total_solids += solids
        except Exception as exc:
            rows.append(failed_row(name, f"generated:{name}", position, rotation, note, str(exc)))
            failure_count += 1

    if success_count == 0:
        raise RuntimeError("No components were added; STEP export skipped")

    assembly.save(str(STEP_OUT), exportType="STEP")
    reimported = cq.importers.importStep(str(STEP_OUT))
    exported_solids = len(reimported.solids().vals())
    total_bbox_values = bbox_values(reimported.val())

    fieldnames = [
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
    ]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    report_lines = [
        "# CadQuery Rough Assembly v4 Report",
        "",
        "- v4 is based on v3.",
        "- Main mechanical layout remains at v3 coordinates.",
        "- Sample tube family was corrected before v4.",
        "- Curved labels are used on sample tube v2 STEP files.",
        "- Added 12 mixed sample tubes in the input rack.",
        "- Added 1 scan-station demo tube.",
        "- Added classified sample tubes in Category A and Category B output bins.",
        "- Added a simplified X-Z adapter plate.",
        "- Added INPUT/A/B/C/D/REVIEW label plates.",
        f"- Successful imported/generated components: {success_count}",
        f"- Failed components: {failure_count}",
        f"- Total solids: {total_solids} added / {exported_solids} exported",
        f"- Total bbox: {fmt_bbox(total_bbox_values)}",
        f"- Output STEP path: `{STEP_OUT.relative_to(ROOT).as_posix()}`",
        "- Next step: open the v4 STEP in SolidWorks 2026 for inspection.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"success_count={success_count}")
    print(f"failure_count={failure_count}")
    print(f"total_solids={total_solids}")
    print(f"exported_solids={exported_solids}")
    print(f"total_bbox={fmt_bbox(total_bbox_values)}")
    print(f"step={STEP_OUT}")
    print(f"validation_csv={CSV_OUT}")
    print(f"report={REPORT_OUT}")
    return 0 if failure_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
