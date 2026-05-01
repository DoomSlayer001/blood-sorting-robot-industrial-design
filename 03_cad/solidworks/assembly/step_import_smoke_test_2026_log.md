# step_import_smoke_test_2026.SLDASM Build Log

- Generated at: 2026-05-01T16:34:29
- Assembly template: `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_assembly.asmdot`
- Source CAD: original STEP/STP/native paths from `component_placement_table_v1.csv`

- WARN `base_plate`: AddComponent5 returned_object=False; count 0 -> 0.
- WARN `base_plate`: AddComponent4 returned_object=False; count 0 -> 0.
- WARN `base_plate`: AddComponent returned_object=True; count 0 -> 0.
- FAIL `base_plate` from `03_cad/custom_parts/base_plate/base_plate_1100x900x15.step`: AddComponent did not increase component count
- WARN `electric_parallel_gripper`: AddComponent5 returned_object=False; count 0 -> 0.
- WARN `electric_parallel_gripper`: AddComponent4 returned_object=False; count 0 -> 0.
- WARN `electric_parallel_gripper`: AddComponent returned_object=True; count 0 -> 0.
- FAIL `electric_parallel_gripper` from `03_cad/standard_parts/downloaded/gripper/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.step`: AddComponent did not increase component count
- WARN `input_mixed_tube_rack_4x6`: AddComponent5 returned_object=False; count 0 -> 0.
- WARN `input_mixed_tube_rack_4x6`: AddComponent4 returned_object=False; count 0 -> 0.
- WARN `input_mixed_tube_rack_4x6`: AddComponent returned_object=True; count 0 -> 0.
- FAIL `input_mixed_tube_rack_4x6` from `03_cad/custom_parts/tube_bins/input_mixed_tube_rack_4x6.step`: AddComponent did not increase component count

## Insert Summary

- Attempted components: 3
- Inserted components: 0
- Failed components: 3
- Skipped components: 0
- Critical components all satisfied: False
- Critical components missing:
  - barcode_scanner
  - base_plate
  - category_A_output_bin_2x3
  - category_B_output_bin_2x3
  - category_C_output_bin_2x3
  - category_D_output_bin_2x3
  - electric_parallel_gripper
  - input_mixed_tube_rack_4x6
  - left_y_axis_module
  - manual_review_bin_2x3
  - photoelectric_sensor
  - right_y_axis_module
  - x_axis_module_on_gantry
  - z_axis_module

## Reopen Verification

- Saved: False
- File size bytes: None
- Component count before save: 0
- Component count after reopen: 0
- Referenced document count: 0
- Screenshot exported: False
- Verified success: False

## Component Names After Reopen

- None

## Failed Components

- base_plate: AddComponent did not increase component count
- electric_parallel_gripper: AddComponent did not increase component count
- input_mixed_tube_rack_4x6: AddComponent did not increase component count
