from pathlib import Path

import FreeCAD as App
import Part


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "03_cad" / "freecad_assembly"
FCSTD_OUT = OUT_DIR / "freecad_rough_layout_poc.FCStd"
STEP_OUT = OUT_DIR / "freecad_rough_layout_poc.step"

PARTS = [
    {
        "name": "base_plate",
        "path": ROOT / "03_cad" / "custom_parts" / "base_plate" / "base_plate_1100x900x15.step",
        "placement": (0.0, 0.0, -7.5),
    },
    {
        "name": "input_mixed_tube_rack_4x6",
        "path": ROOT / "03_cad" / "custom_parts" / "tube_bins" / "input_mixed_tube_rack_4x6.step",
        "placement": (-250.0, 250.0, 17.5),
    },
    {
        "name": "category_A_output_bin_2x3",
        "path": ROOT / "03_cad" / "custom_parts" / "tube_bins" / "category_A_output_bin_2x3.step",
        "placement": (180.0, -170.0, 17.5),
    },
    {
        "name": "electric_parallel_gripper",
        "path": ROOT
        / "03_cad"
        / "standard_parts"
        / "downloaded"
        / "gripper"
        / "SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.step",
        "placement": (0.0, 0.0, 120.0),
    },
]


def add_step_part(doc, item):
    shape = Part.Shape()
    shape.read(str(item["path"]))
    if shape.isNull():
        raise RuntimeError(f"Imported null shape: {item['path']}")

    obj = doc.addObject("Part::Feature", item["name"])
    obj.Shape = shape
    x, y, z = item["placement"]
    obj.Placement = App.Placement(App.Vector(x, y, z), App.Rotation(0.0, 0.0, 0.0))
    return obj


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    missing = [str(item["path"]) for item in PARTS if not item["path"].is_file()]
    if missing:
        raise FileNotFoundError("Missing STEP inputs: " + ", ".join(missing))

    doc = App.newDocument("freecad_rough_layout_poc")
    objects = [add_step_part(doc, item) for item in PARTS]
    doc.recompute()

    if len(objects) != len(PARTS):
        raise RuntimeError(f"Expected {len(PARTS)} objects, imported {len(objects)}")
    if any(obj.Shape.isNull() for obj in objects):
        raise RuntimeError("One or more imported objects has a null shape")

    doc.saveAs(str(FCSTD_OUT))
    Part.export(objects, str(STEP_OUT))

    print(f"imported_objects={len(objects)}")
    print(f"fcstd={FCSTD_OUT}")
    print(f"step={STEP_OUT}")


if __name__ == "__main__":
    main()
