from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "03_cad" / "freecad_assembly"
STEP_OUT = OUT_DIR / "blood_sorting_robot_cadquery_rough_layout_v1.step"
CSV_OUT = OUT_DIR / "blood_sorting_robot_cadquery_rough_layout_v1_validation.csv"
REPORT_OUT = ROOT / "reports" / "cadquery_rough_assembly_v1_report.md"


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    rel_path: str
    position: tuple[float, float, float]
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    target_axis: str | None = None
    note: str = ""


COMPONENTS = [
    ComponentSpec(
        "base_plate",
        "03_cad/custom_parts/base_plate/base_plate_1100x900x15.step",
        (0.0, 0.0, -7.5),
    ),
    ComponentSpec(
        "left_y_axis_module",
        "03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step",
        (-360.0, 0.0, 35.0),
        target_axis="Y",
        note="auto-align long axis to Y",
    ),
    ComponentSpec(
        "right_y_axis_module",
        "03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step",
        (360.0, 0.0, 35.0),
        target_axis="Y",
        note="auto-align long axis to Y",
    ),
    ComponentSpec(
        "x_axis_module_on_gantry",
        "03_cad/standard_parts/downloaded/x_axis_module/MISUMI_MSA628_X_axis_L750_double_shaft_B1_v1.step",
        (0.0, 0.0, 260.0),
        target_axis="X",
        note="auto-align long axis to X",
    ),
    ComponentSpec(
        "z_axis_module",
        "03_cad/standard_parts/downloaded/z_axis_module/MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.step",
        (0.0, 0.0, 220.0),
        target_axis="Z",
        note="auto-align long axis to Z",
    ),
    ComponentSpec(
        "electric_parallel_gripper",
        "03_cad/standard_parts/downloaded/gripper/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.step",
        (0.0, 0.0, 120.0),
    ),
    ComponentSpec(
        "input_mixed_tube_rack_4x6",
        "03_cad/custom_parts/tube_bins/input_mixed_tube_rack_4x6.step",
        (-250.0, 250.0, 17.5),
    ),
    ComponentSpec(
        "category_A_output_bin_2x3",
        "03_cad/custom_parts/tube_bins/category_A_output_bin_2x3.step",
        (180.0, -170.0, 17.5),
    ),
    ComponentSpec(
        "category_B_output_bin_2x3",
        "03_cad/custom_parts/tube_bins/category_B_output_bin_2x3.step",
        (320.0, -170.0, 17.5),
    ),
    ComponentSpec(
        "category_C_output_bin_2x3",
        "03_cad/custom_parts/tube_bins/category_C_output_bin_2x3.step",
        (180.0, -290.0, 17.5),
    ),
    ComponentSpec(
        "category_D_output_bin_2x3",
        "03_cad/custom_parts/tube_bins/category_D_output_bin_2x3.step",
        (320.0, -290.0, 17.5),
    ),
    ComponentSpec(
        "manual_review_bin_2x3",
        "03_cad/custom_parts/tube_bins/manual_review_bin_2x3.step",
        (-250.0, -300.0, 17.5),
    ),
    ComponentSpec(
        "barcode_scanner",
        "03_cad/standard_parts/downloaded/barcode_scanner/Cognex_DataMan80_USB_fixed_barcode_reader_v1.step",
        (80.0, 160.0, 80.0),
    ),
    ComponentSpec(
        "photoelectric_sensor",
        "03_cad/standard_parts/downloaded/sensors/Panasonic_CX421J_diffuse_photoelectric_sensor_v1.step",
        (20.0, 80.0, 60.0),
    ),
]


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


def bbox_tuple(shape) -> tuple[float, float, float]:
    bbox = shape.BoundingBox()
    return (bbox.xlen, bbox.ylen, bbox.zlen)


def fmt_bbox(values: tuple[float, float, float]) -> str:
    return f"{values[0]:.3f} x {values[1]:.3f} x {values[2]:.3f} mm"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)

    assembly = cq.Assembly(name="blood_sorting_robot_cadquery_rough_layout_v1")
    rows: list[dict[str, object]] = []
    success_count = 0
    failure_count = 0
    total_solids = 0

    for spec in COMPONENTS:
        path = ROOT / spec.rel_path
        row: dict[str, object] = {
            "name": spec.name,
            "path": spec.rel_path,
            "x_mm": spec.position[0],
            "y_mm": spec.position[1],
            "z_mm": spec.position[2],
            "target_axis": spec.target_axis or "",
            "note": spec.note,
        }

        try:
            if not path.is_file():
                raise FileNotFoundError(path)

            workplane = cq.importers.importStep(str(path))
            shape = workplane.val()
            solids = len(workplane.solids().vals())
            if shape is None or solids < 1:
                raise RuntimeError("empty STEP geometry")

            source_bbox = shape.BoundingBox()
            source_axis = axis_from_bbox(source_bbox)
            auto_rotation = rotation_to_target_axis(source_axis, spec.target_axis)
            rotation = tuple(a + b for a, b in zip(spec.rotation, auto_rotation))
            final_shape = rotate_shape(shape, rotation)
            final_bbox = bbox_tuple(final_shape)

            assembly.add(
                final_shape,
                name=spec.name,
                loc=cq.Location(cq.Vector(*spec.position)),
            )

            row.update(
                {
                    "status": "OK",
                    "source_solids": solids,
                    "source_axis": source_axis,
                    "rot_x_deg": rotation[0],
                    "rot_y_deg": rotation[1],
                    "rot_z_deg": rotation[2],
                    "bbox_x_mm": f"{final_bbox[0]:.3f}",
                    "bbox_y_mm": f"{final_bbox[1]:.3f}",
                    "bbox_z_mm": f"{final_bbox[2]:.3f}",
                    "error": "",
                }
            )
            success_count += 1
            total_solids += solids
        except Exception as exc:
            row.update(
                {
                    "status": "FAILED",
                    "source_solids": 0,
                    "source_axis": "",
                    "rot_x_deg": "",
                    "rot_y_deg": "",
                    "rot_z_deg": "",
                    "bbox_x_mm": "",
                    "bbox_y_mm": "",
                    "bbox_z_mm": "",
                    "error": str(exc),
                }
            )
            failure_count += 1

        rows.append(row)

    if success_count == 0:
        raise RuntimeError("No components were imported; STEP export skipped")

    assembly.save(str(STEP_OUT), exportType="STEP")
    reimported = cq.importers.importStep(str(STEP_OUT))
    exported_solids = len(reimported.solids().vals())
    total_bbox = bbox_tuple(reimported.val())

    fieldnames = [
        "name",
        "status",
        "path",
        "x_mm",
        "y_mm",
        "z_mm",
        "target_axis",
        "source_axis",
        "rot_x_deg",
        "rot_y_deg",
        "rot_z_deg",
        "source_solids",
        "bbox_x_mm",
        "bbox_y_mm",
        "bbox_z_mm",
        "note",
        "error",
    ]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    report_lines = [
        "# CadQuery Rough Assembly v1 Report",
        "",
        f"- Successful imported components: {success_count}",
        f"- Failed components: {failure_count}",
        f"- Total solids: {total_solids} imported / {exported_solids} exported",
        f"- Total bbox: {fmt_bbox(total_bbox)}",
        f"- Output STEP path: `{STEP_OUT.relative_to(ROOT).as_posix()}`",
        "- Next step: open the STEP in SolidWorks 2026 for inspection.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"success_count={success_count}")
    print(f"failure_count={failure_count}")
    print(f"total_solids={total_solids}")
    print(f"exported_solids={exported_solids}")
    print(f"total_bbox={fmt_bbox(total_bbox)}")
    print(f"step={STEP_OUT}")
    print(f"validation_csv={CSV_OUT}")
    print(f"report={REPORT_OUT}")
    return 0 if failure_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
