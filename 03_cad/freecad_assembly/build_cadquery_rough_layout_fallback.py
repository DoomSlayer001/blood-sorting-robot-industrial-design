from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "03_cad" / "freecad_assembly"
STEP_OUT = OUT_DIR / "freecad_rough_layout_poc.step"

PARTS = [
    (
        "base_plate",
        ROOT / "03_cad" / "custom_parts" / "base_plate" / "base_plate_1100x900x15.step",
        (0.0, 0.0, -7.5),
    ),
    (
        "input_mixed_tube_rack_4x6",
        ROOT / "03_cad" / "custom_parts" / "tube_bins" / "input_mixed_tube_rack_4x6.step",
        (-250.0, 250.0, 17.5),
    ),
    (
        "category_A_output_bin_2x3",
        ROOT / "03_cad" / "custom_parts" / "tube_bins" / "category_A_output_bin_2x3.step",
        (180.0, -170.0, 17.5),
    ),
    (
        "electric_parallel_gripper",
        ROOT
        / "03_cad"
        / "standard_parts"
        / "downloaded"
        / "gripper"
        / "SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.step",
        (0.0, 0.0, 120.0),
    ),
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    missing = [str(path) for _, path, _ in PARTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing STEP inputs: " + ", ".join(missing))

    assembly = cq.Assembly(name="freecad_rough_layout_poc")
    imported = []

    for name, path, xyz in PARTS:
        workplane = cq.importers.importStep(str(path))
        shape = workplane.val()
        solids = len(workplane.solids().vals())
        if shape is None or solids < 1:
            raise RuntimeError(f"Imported empty STEP geometry: {path}")

        assembly.add(shape, name=name, loc=cq.Location(cq.Vector(*xyz)))
        imported.append((name, solids, shape.BoundingBox()))

    if len(imported) != len(PARTS):
        raise RuntimeError(f"Expected {len(PARTS)} parts, imported {len(imported)}")

    assembly.save(str(STEP_OUT), exportType="STEP")

    print(f"fallback_step={STEP_OUT}")
    print(f"imported_objects={len(imported)}")
    for name, solids, bbox in imported:
        print(
            f"{name}: solids={solids}, "
            f"bbox_mm=({bbox.xlen:.3f}, {bbox.ylen:.3f}, {bbox.zlen:.3f})"
        )


if __name__ == "__main__":
    main()
