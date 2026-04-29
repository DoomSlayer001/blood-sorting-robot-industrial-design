from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
SAMPLE_TUBE_DIR = ROOT / "03_cad" / "custom_parts" / "sample_tube"
TUBE_BIN_DIR = ROOT / "03_cad" / "custom_parts" / "tube_bins"


def ensure_dirs() -> None:
    SAMPLE_TUBE_DIR.mkdir(parents=True, exist_ok=True)
    TUBE_BIN_DIR.mkdir(parents=True, exist_ok=True)


def make_tube(path: Path, name: str, body_height: float, cap_color: tuple[float, float, float]) -> None:
    body_radius = 6.5
    cap_radius = 8.0
    cap_height = 12.0
    label_height = 40.0
    label_width = 10.0
    label_thickness = 0.35

    body = cq.Workplane("XY").circle(body_radius).extrude(body_height)
    cap = cq.Workplane("XY").circle(cap_radius).extrude(cap_height).translate((0, 0, body_height))
    label = (
        cq.Workplane("XY")
        .box(label_thickness, label_width, label_height)
        .translate((body_radius + label_thickness / 2 + 0.05, 0, 34.0))
    )

    asm = cq.Assembly(name=name)
    asm.add(body, name="transparent_light_gray_body", color=cq.Color(0.82, 0.86, 0.88, 0.45))
    asm.add(cap, name="colored_cap", color=cq.Color(*cap_color, 1.0))
    asm.add(label, name="white_label_placeholder", color=cq.Color(1.0, 1.0, 1.0, 1.0))

    for idx, y in enumerate([-3.6, -2.4, -1.2, 0.4, 1.7, 3.1]):
        width = 0.35 if idx % 2 else 0.55
        stripe = (
            cq.Workplane("XY")
            .box(label_thickness + 0.08, width, 28.0)
            .translate((body_radius + label_thickness + 0.12, y, 34.0))
        )
        asm.add(stripe, name=f"black_barcode_placeholder_{idx+1}", color=cq.Color(0.0, 0.0, 0.0, 1.0))

    asm.save(str(path), exportType="STEP")


def hole_points(rows: int, cols: int, pitch: float) -> list[tuple[float, float]]:
    x0 = -((cols - 1) * pitch) / 2
    y0 = ((rows - 1) * pitch) / 2
    return [(x0 + c * pitch, y0 - r * pitch) for r in range(rows) for c in range(cols)]


def make_bin(path: Path, name: str, rows: int, cols: int, length: float, width: float, height: float, color: tuple[float, float, float]) -> None:
    pitch = 28.0
    hole_diameter = 15.0
    hole_depth = 25.0

    points = hole_points(rows, cols, pitch)
    base = (
        cq.Workplane("XY")
        .box(length, width, height)
        .faces(">Z")
        .workplane()
        .pushPoints(points)
        .hole(hole_diameter, depth=hole_depth)
        .edges("|Z")
        .chamfer(1.0)
    )

    stripe = (
        cq.Workplane("XY")
        .box(length - 12.0, 4.0, 2.0)
        .translate((0, -(width / 2) + 5.0, height / 2 + 1.0))
    )

    asm = cq.Assembly(name=name)
    asm.add(base, name="pom_or_pc_bin_body", color=cq.Color(0.92, 0.93, 0.90, 1.0))
    asm.add(stripe, name="category_color_marker", color=cq.Color(*color, 1.0))
    asm.save(str(path), exportType="STEP")


def main() -> None:
    ensure_dirs()

    tubes = [
        ("purple_cap_tube_13x75.step", "purple_cap_tube_13x75", 75.0, (0.45, 0.16, 0.75)),
        ("yellow_cap_tube_13x100.step", "yellow_cap_tube_13x100", 100.0, (1.0, 0.82, 0.05)),
        ("blue_cap_tube_13x75.step", "blue_cap_tube_13x75", 75.0, (0.08, 0.34, 0.95)),
        ("red_cap_tube_13x75.step", "red_cap_tube_13x75", 75.0, (0.86, 0.05, 0.05)),
    ]
    for filename, name, height, color in tubes:
        make_tube(SAMPLE_TUBE_DIR / filename, name, height, color)

    bins = [
        ("input_mixed_tube_rack_4x6.step", "input_mixed_tube_rack_4x6", 4, 6, 180.0, 120.0, 35.0, (0.35, 0.35, 0.35)),
        ("category_A_output_bin_2x3.step", "category_A_output_bin_2x3", 2, 3, 100.0, 75.0, 35.0, (0.45, 0.16, 0.75)),
        ("category_B_output_bin_2x3.step", "category_B_output_bin_2x3", 2, 3, 100.0, 75.0, 35.0, (1.0, 0.82, 0.05)),
        ("category_C_output_bin_2x3.step", "category_C_output_bin_2x3", 2, 3, 100.0, 75.0, 35.0, (0.08, 0.34, 0.95)),
        ("category_D_output_bin_2x3.step", "category_D_output_bin_2x3", 2, 3, 100.0, 75.0, 35.0, (0.86, 0.05, 0.05)),
        ("manual_review_bin_2x3.step", "manual_review_bin_2x3", 2, 3, 100.0, 75.0, 35.0, (1.0, 0.45, 0.0)),
    ]
    for filename, name, rows, cols, length, width, height, color in bins:
        make_bin(TUBE_BIN_DIR / filename, name, rows, cols, length, width, height, color)

    print("Generated sample tube and tube bin STEP files.")


if __name__ == "__main__":
    main()
