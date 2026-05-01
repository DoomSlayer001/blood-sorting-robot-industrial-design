# Run 4D Corrected Internal VBA Macro Guide

## Purpose

Stage 4D corrects the first full internal VBA rough assembly. Stage 4C proved that SolidWorks 2026 internal VBA can insert real components, but the layout was visibly wrong. Stage 4D focuses on corrected component mapping, coordinates, rotations, and transform behavior.

## Files

- Corrected placement table:
  `03_cad/solidworks/component_placement_table_4d_corrected.csv`
- Internal VBA source:
  `03_cad/solidworks/macros/create_4d_corrected_rough_assembly_2026_internal_vba.vba`
- Copy-to-SWP module:
  `03_cad/solidworks/macros/create_4d_corrected_rough_assembly_2026_copy_to_swp.bas`
- Expected output after manual run:
  `03_cad/solidworks/assembly/rough_layout_4d_corrected_2026_v1.SLDASM`

## How To Create The SWP Macro

1. Open SolidWorks 2026.
2. Choose `Tools / Macro / New`.
3. Save a new macro as:

```text
03_cad/solidworks/macros/create_4d_corrected_rough_assembly_2026_internal_vba.swp
```

4. SolidWorks opens the VBA editor.
5. Open `create_4d_corrected_rough_assembly_2026_copy_to_swp.bas` in a text editor.
6. Copy all content into the SolidWorks VBA module.
7. Save the `.swp`.
8. Run with `Tools / Macro / Run`.

## What The 4D Macro Changes

- Uses a corrected placement table.
- Inserts only `insert_in_4d=yes` components.
- Defers cable chain, Y-axis sync placeholder, emergency stop, control box, motors, limit switches, and sample tube instances.
- Uses distinct instance names for Category A/B/C/D and manual review bins, even when reusing the same 2x3 bin geometry.
- Uses `MakeTransform` with coordinates converted from millimeters to meters.
- Supports Euler rotations using `Rz * Ry * Rx`.

## Required Checks After Running

Capture these screenshots:

- Isometric view.
- Top View.
- Front View.
- Right View.
- FeatureManager tree.
- Dual-side gantry local view.
- Input/output bin area.
- Scan station local view.

## Layout Checks

- Left and right Y-axis modules should be separated at approximately `x = -360 mm` and `x = +360 mm`.
- Y-axis modules should run along the Y direction.
- X-axis module should run along X at gantry height.
- Z-axis module should appear vertical or be close enough to identify required rotation correction.
- Output bins should form a 2x2 group on the front-right side.
- Manual review bin should be on the front-left side.
- Scanner and photoelectric sensor should be near the scan station.

## If Layout Is Still Wrong

Do not treat the `.SLDASM` as final. Use screenshots to update:

- `component_placement_table_4d_corrected.csv`
- rotation values in the macro or placement table
- component instance names
- reused geometry mapping notes

Then regenerate a new corrected macro version.
