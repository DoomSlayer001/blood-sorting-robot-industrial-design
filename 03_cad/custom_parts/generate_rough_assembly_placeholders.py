from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
CUSTOM_DIR = ROOT / "03_cad" / "custom_parts"

BASE_PLATE_DIR = CUSTOM_DIR / "base_plate"
SCAN_STATION_DIR = CUSTOM_DIR / "scan_station"
CONTROL_BOX_DIR = CUSTOM_DIR / "control_box"
Y_SYNC_DIR = CUSTOM_DIR / "y_axis_sync_mechanism"


def ensure_dirs() -> None:
    for folder in [BASE_PLATE_DIR, SCAN_STATION_DIR, CONTROL_BOX_DIR, Y_SYNC_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def export_step(shape: cq.Workplane, path: Path) -> None:
    cq.exporters.export(shape, str(path), exportType="STEP")


def make_base_plate() -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(1100.0, 900.0, 15.0)
        .translate((0.0, 0.0, -7.5))
        .edges("|Z")
        .chamfer(1.0)
    )


def make_scan_station_reference() -> cq.Workplane:
    base = cq.Workplane("XY").box(120.0, 80.0, 20.0).edges("|Z").chamfer(0.8)
    center_mark = cq.Workplane("XY").box(36.0, 4.0, 1.0).translate((0.0, 0.0, 10.5))
    return base.union(center_mark)


def make_control_box_placeholder() -> cq.Workplane:
    box = cq.Workplane("XY").box(160.0, 120.0, 80.0).edges("|Z").chamfer(1.2)
    front_panel = cq.Workplane("XY").box(150.0, 2.0, 68.0).translate((0.0, -61.0, 0.0))
    return box.union(front_panel)


def make_y_sync_shaft_placeholder() -> cq.Workplane:
    return cq.Workplane("YZ").circle(7.0).extrude(720.0).translate((-360.0, 0.0, 0.0))


def main() -> None:
    ensure_dirs()
    export_step(make_base_plate(), BASE_PLATE_DIR / "base_plate_1100x900x15.step")
    export_step(make_scan_station_reference(), SCAN_STATION_DIR / "scan_station_reference_block.step")
    export_step(make_control_box_placeholder(), CONTROL_BOX_DIR / "control_box_placeholder_160x120x80.step")
    export_step(make_y_sync_shaft_placeholder(), Y_SYNC_DIR / "y_axis_sync_shaft_placeholder.step")
    print("Generated rough assembly placeholder STEP files.")


if __name__ == "__main__":
    main()
