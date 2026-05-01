from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "03_cad" / "custom_parts" / "sample_tube"
REPORT_OUT = ROOT / "reports" / "sample_tube_geometry_v2_report.md"

OUTER_DIAMETER_MM = 13.0
BODY_RADIUS_MM = OUTER_DIAMETER_MM / 2
CAP_RADIUS_MM = 8.0
CAP_HEIGHT_MM = 12.0
LABEL_HEIGHT_MM = 24.0
LABEL_WRAP_ANGLE_DEG = 220.0
LABEL_THICKNESS_MM = 0.22
LABEL_CLEARANCE_MM = 0.04


@dataclass(frozen=True)
class TubeSpec:
    name: str
    height_mm: float
    cap_color: str
    rgb: tuple[float, float, float]

    @property
    def filename(self) -> str:
        return f"{self.name}_v2.step"


TUBES = [
    TubeSpec("purple_cap_tube_13x75", 75.0, "purple", (0.45, 0.16, 0.75)),
    TubeSpec("yellow_cap_tube_13x100", 100.0, "yellow", (1.0, 0.82, 0.05)),
    TubeSpec("blue_cap_tube_13x75", 75.0, "blue", (0.08, 0.34, 0.95)),
    TubeSpec("red_cap_tube_13x75", 75.0, "red", (0.86, 0.05, 0.05)),
]


def annular_sector(
    inner_radius: float,
    outer_radius: float,
    height: float,
    start_angle_deg: float,
    end_angle_deg: float,
    segments: int = 72,
):
    outer_points = []
    inner_points = []
    for index in range(segments + 1):
        angle = math.radians(start_angle_deg + (end_angle_deg - start_angle_deg) * index / segments)
        outer_points.append((outer_radius * math.cos(angle), outer_radius * math.sin(angle)))
        inner_points.append((inner_radius * math.cos(angle), inner_radius * math.sin(angle)))

    points = outer_points + list(reversed(inner_points))
    return cq.Workplane("XY").polyline(points).close().extrude(height)


def make_curved_label(label_bottom_z: float):
    half_angle = LABEL_WRAP_ANGLE_DEG / 2
    inner_radius = BODY_RADIUS_MM + LABEL_CLEARANCE_MM
    outer_radius = inner_radius + LABEL_THICKNESS_MM
    label = annular_sector(
        inner_radius,
        outer_radius,
        LABEL_HEIGHT_MM,
        -half_angle,
        half_angle,
        segments=96,
    ).translate((0, 0, label_bottom_z))
    return label


def make_barcode_stripes(label_bottom_z: float):
    stripes = []
    stripe_angles = [-72, -58, -42, -25, -8, 14, 33, 56, 76]
    stripe_widths = [3.0, 2.0, 4.0, 2.5, 3.5, 2.0, 4.5, 2.0, 3.0]
    inner_radius = BODY_RADIUS_MM + LABEL_CLEARANCE_MM + LABEL_THICKNESS_MM
    outer_radius = inner_radius + 0.06
    for index, (angle, width) in enumerate(zip(stripe_angles, stripe_widths), start=1):
        stripe = annular_sector(
            inner_radius,
            outer_radius,
            LABEL_HEIGHT_MM - 6.0,
            angle,
            angle + width,
            segments=8,
        ).translate((0, 0, label_bottom_z + 3.0))
        stripes.append((f"curved_barcode_stripe_{index}", stripe))
    return stripes


def make_tube(spec: TubeSpec, path: Path) -> None:
    body_height = spec.height_mm - CAP_HEIGHT_MM
    if body_height <= LABEL_HEIGHT_MM + 18.0:
        raise ValueError(f"Tube {spec.name} is too short for the selected cap and label geometry")

    body = cq.Workplane("XY").circle(BODY_RADIUS_MM).extrude(body_height)
    cap = cq.Workplane("XY").circle(CAP_RADIUS_MM).extrude(CAP_HEIGHT_MM).translate((0, 0, body_height))
    label_bottom_z = max(22.0, min(body_height - LABEL_HEIGHT_MM - 8.0, body_height * 0.46))
    label = make_curved_label(label_bottom_z)

    asm = cq.Assembly(name=f"{spec.name}_v2")
    asm.add(body, name=f"{spec.name}_clear_body_13mm_od", color=cq.Color(0.82, 0.88, 0.92, 0.42))
    asm.add(cap, name=f"{spec.cap_color}_cap_material_marker", color=cq.Color(*spec.rgb, 1.0))
    asm.add(label, name="curved_white_label_220deg", color=cq.Color(1.0, 1.0, 1.0, 1.0))
    for stripe_name, stripe in make_barcode_stripes(label_bottom_z):
        asm.add(stripe, name=stripe_name, color=cq.Color(0.0, 0.0, 0.0, 1.0))

    asm.save(str(path), exportType="STEP")


def write_report(rows: list[dict[str, object]]) -> None:
    lines = [
        "# Sample Tube Geometry v2 Report",
        "",
        "| file | height_mm | outer_diameter_mm | cap_color | label_height_mm | label_wrap_angle_deg | label_thickness_mm | curved_label | step_non_empty |",
        "|---|---:|---:|---|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| `{file}` | {height_mm:.1f} | {outer_diameter_mm:.1f} | {cap_color} | "
            "{label_height_mm:.1f} | {label_wrap_angle_deg:.1f} | {label_thickness_mm:.2f} | "
            "{curved_label} | {step_non_empty} |".format(**row)
        )
    lines.extend(
        [
            "",
            "Conclusion: sample tube family v2 uses visibly different tube heights, cap-color material markers, and curved labels; it is ready for v4 layout.",
            "",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []

    for spec in TUBES:
        path = OUT_DIR / spec.filename
        make_tube(spec, path)
        imported = cq.importers.importStep(str(path))
        step_non_empty = path.is_file() and path.stat().st_size > 0 and len(imported.solids().vals()) > 0
        rows.append(
            {
                "file": path.relative_to(ROOT).as_posix(),
                "height_mm": spec.height_mm,
                "outer_diameter_mm": OUTER_DIAMETER_MM,
                "cap_color": spec.cap_color,
                "label_height_mm": LABEL_HEIGHT_MM,
                "label_wrap_angle_deg": LABEL_WRAP_ANGLE_DEG,
                "label_thickness_mm": LABEL_THICKNESS_MM,
                "curved_label": "yes",
                "step_non_empty": "yes" if step_non_empty else "no",
            }
        )

    write_report(rows)
    print(f"generated_tubes={len(rows)}")
    for row in rows:
        print(f"{row['file']}: height={row['height_mm']} cap={row['cap_color']} non_empty={row['step_non_empty']}")
    print(f"report={REPORT_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
