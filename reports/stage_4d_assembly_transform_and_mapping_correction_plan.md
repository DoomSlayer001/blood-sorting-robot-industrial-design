# Stage 4D Assembly Transform And Mapping Correction Plan

## Objective

Prepare a corrected SolidWorks 2026 internal VBA rough assembly workflow after Stage 4C proved that real component insertion works but the layout is not yet correct.

## Stage 4C Success Point

Stage 4C full internal VBA assembly succeeded in creating a non-empty `.SLDASM`. FeatureManager contained real components, and the assembly remained populated after save, close, and reopen.

This validates the SolidWorks 2026 internal VBA route.

## Stage 4C Layout Problems

The generated assembly is not yet an acceptable rough layout. Observed problems:

- Components are stacked.
- The dual-side gantry structure is not expanded into the intended spatial relationship.
- Y-axis and X-axis directions appear incorrect.
- Several output bin instances show as `category_A_output_bin_2x3`, suggesting reused geometry and instance naming are not clearly separated.
- Cable chain and Y-axis synchronization placeholder interfere with layout inspection.
- Coordinates, orientations, and Transform handling require recalibration.

## Macro Audit Summary

The Stage 4C full macro used correct native files for many major parts, but it reused the same MSA-628 geometry for left Y, right Y, and X without enough rotation handling. It also reused Category A output bin geometry for B/C/D and manual review bins. Geometry reuse is acceptable for rough layout, but each instance must have a clear semantic instance name.

The previous transform function used identity rotation. Stage 4D adds Euler rotation support.

## Corrected Placement Table

New table:

```text
03_cad/solidworks/component_placement_table_4d_corrected.csv
```

The table adds:

- `instance_name`
- corrected `x_mm`, `y_mm`, `z_mm`
- `rot_x_deg`, `rot_y_deg`, `rot_z_deg`
- `insert_in_4d`
- `critical_for_layout`
- notes for manual orientation checks

## Transform Definition

New VBA function:

```vb
Function MakeTransform(x_mm, y_mm, z_mm, rx_deg, ry_deg, rz_deg) As Object
```

Rules:

- Coordinates are converted from millimeters to meters.
- Rotation order is `Rz * Ry * Rx`.
- `TransformData(0..8)` stores the rotation matrix.
- `TransformData(9..11)` stores translation in meters.
- This replaces the previous identity-only transform.

## Corrected Macro Files

- Internal VBA:
  `03_cad/solidworks/macros/create_4d_corrected_rough_assembly_2026_internal_vba.vba`
- Copy-to-SWP:
  `03_cad/solidworks/macros/create_4d_corrected_rough_assembly_2026_copy_to_swp.bas`
- Run guide:
  `03_cad/solidworks/macros/run_4d_corrected_internal_vba_guide.md`

Expected output after manual SolidWorks run:

```text
03_cad/solidworks/assembly/rough_layout_4d_corrected_2026_v1.SLDASM
```

## Deferred Components

The following are intentionally deferred in 4D so the main body layout can be corrected first:

- `cable_chain_xz`
- `y_axis_sync_mechanism`
- `emergency_stop_placeholder`
- `control_box_placeholder`
- `x_axis_motor`
- `y_axis_motor_left_or_common`
- `y_axis_motor_right_placeholder_or_sync_note`
- `z_axis_motor`
- `limit_switch_x_home`
- `limit_switch_y_home`
- `limit_switch_z_home`
- `sample_tube_instances_input_demo`
- `sample_tube_instances_output_demo`

## 4D Inserted Components

The corrected 4D macro inserts:

- `base_plate`
- `left_y_axis_module`
- `right_y_axis_module`
- `x_axis_module_on_gantry`
- `z_axis_module`
- `electric_parallel_gripper`
- `input_mixed_tube_rack_4x6`
- `category_A_output_bin_2x3`
- `category_B_output_bin_2x3`
- `category_C_output_bin_2x3`
- `category_D_output_bin_2x3`
- `manual_review_bin_2x3`
- `scan_station_reference`
- `barcode_scanner`
- `photoelectric_sensor`

## Next Action

The user should create a SolidWorks `.swp` macro, copy in:

```text
03_cad/solidworks/macros/create_4d_corrected_rough_assembly_2026_copy_to_swp.bas
```

Then run it inside SolidWorks 2026 and capture:

- Isometric view.
- Top View.
- Front View.
- Right View.
- FeatureManager.
- Gantry local view.
- Input/output bin area.
- Scan station local view.

Those screenshots will drive the next coordinate and orientation correction pass.
