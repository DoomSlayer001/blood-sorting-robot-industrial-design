# Stage 4C SolidWorks 2026 Rough Assembly Generation Report

- Generated at: 2026-05-01T16:22:37
- Branch purpose: controlled SolidWorks 2026 migration validation

## 1. SolidWorks 2026 Template Paths

- part_template_path: `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_part.prtdot`; exists=True
- assembly_template_path: `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_assembly.asmdot`; exists=True
- drawing_template_path: `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_a4.drwdot`; exists=True

## 2. Native Cache Usage

- Native mapping file: `03_cad/solidworks/converted_native/native_file_mapping.csv`
- Native files mapped for placement: 24
- Native mapping rows still missing files: 4
  - limit_switch_x_home
  - limit_switch_y_home
  - limit_switch_z_home
  - control_box_placeholder

## 3. Rough Assembly Result

- Generated 2026 rough assembly: True
- Assembly path: `03_cad/solidworks/assembly/blood_sorting_robot_rough_layout_2026_v1.SLDASM`
- Assembly exists: True
- Assembly size bytes: 36146
- Inserted component rows: 24
- Failed insertion rows: 0
- Skipped component rows: 4

## 4. Skipped Components

- limit_switch_x_home
- limit_switch_y_home
- limit_switch_z_home
- control_box_placeholder

## 5. Required Manual View Checks

- Overall isometric view.
- Top view.
- Front view.
- Side view.
- Gripper and sample tube detail.
- Scan station detail.
- Output bin area detail.

## 6. Manual Orientation Check Components

- base_plate
- left_y_axis_module
- right_y_axis_module
- x_axis_module_on_gantry
- z_axis_module
- electric_parallel_gripper
- x_axis_motor
- y_axis_motor_left_or_common
- y_axis_motor_right_placeholder_or_sync_note
- z_axis_motor
- scan_station_reference
- barcode_scanner
- photoelectric_sensor
- cable_chain_xz
- emergency_stop_placeholder
- y_axis_sync_mechanism
- sample_tube_instances_input_demo
- sample_tube_instances_output_demo

## 7. Notes

- This assembly is a 2026 migration validation artifact, not the final engineering assembly.
- The script used existing native `.SLDPRT/.SLDASM` files only and did not open or convert STEP/STP.
- The existing `blood_sorting_robot_rough_layout_v1.SLDASM` was not overwritten.
