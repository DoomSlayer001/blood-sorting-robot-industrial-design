# Rough Assembly v1 Log

## Environment

- Generated at: 2026-04-30T14:23:03
- Platform: Windows-11-10.0.26200-SP0
- Python: 3.13.2

## Native Cache Inputs

- Placement table: `03_cad/solidworks/component_placement_table_v1.csv`
- Native mapping: `03_cad/solidworks/converted_native/native_file_mapping.csv`; exists=True
- Manual conversion TODO: `03_cad/solidworks/converted_native/manual_native_conversion_todo.csv`; exists=True
- Target assembly: `03_cad/solidworks/assembly/blood_sorting_robot_rough_layout_v1.SLDASM`

- FOUND `base_plate` -> `03_cad/solidworks/converted_native/parts/base_plate_1100x900x15.SLDPRT`
- MISSING `left_y_axis_module`; native conversion required.
- MISSING `right_y_axis_module`; native conversion required.
- MISSING `x_axis_module_on_gantry`; native conversion required.
- MISSING `z_axis_module`; native conversion required.
- FOUND `electric_parallel_gripper` -> `03_cad/solidworks/converted_native/assemblies/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.SLDASM`
- MISSING `x_axis_motor`; native conversion required.
- MISSING `y_axis_motor_left_or_common`; native conversion required.
- MISSING `y_axis_motor_right_placeholder_or_sync_note`; native conversion required.
- MISSING `z_axis_motor`; native conversion required.
- MISSING `input_mixed_tube_rack_4x6`; native conversion required.
- MISSING `category_A_output_bin_2x3`; native conversion required.
- MISSING `category_B_output_bin_2x3`; native conversion required.
- MISSING `category_C_output_bin_2x3`; native conversion required.
- MISSING `category_D_output_bin_2x3`; native conversion required.
- MISSING `manual_review_bin_2x3`; native conversion required.
- MISSING `scan_station_reference`; native conversion required.
- MISSING `barcode_scanner`; native conversion required.
- MISSING `photoelectric_sensor`; native conversion required.
- MISSING `limit_switch_x_home`; native conversion required.
- MISSING `limit_switch_y_home`; native conversion required.
- MISSING `limit_switch_z_home`; native conversion required.
- MISSING `cable_chain_xz`; native conversion required.
- FOUND `emergency_stop_placeholder` -> `03_cad/standard_parts/placeholders/safety/emergency_stop_visual_placeholder_v1.sldprt`
- MISSING `control_box_placeholder`; native conversion required.
- MISSING `y_axis_sync_mechanism`; native conversion required.
- MISSING `sample_tube_instances_input_demo`; native conversion required.
- MISSING `sample_tube_instances_output_demo`; native conversion required.

## Critical Component Gate

- Critical native CAD is incomplete. The script will not create a misleading rough assembly.
  - barcode_scanner
  - input_mixed_tube_rack_4x6
  - left_y_axis_module
  - photoelectric_sensor
  - right_y_axis_module
  - x_axis_module_on_gantry
  - z_axis_module
  - at_least_one_category_output_bin

## Summary

- Native files found: 3
- Native files missing: 25
- Inserted rows: 0
- Skipped rows: all rows skipped by critical gate
- Assembly generated: False
