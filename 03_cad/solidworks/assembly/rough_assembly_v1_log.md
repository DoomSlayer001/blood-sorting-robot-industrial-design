# Rough Assembly v1 Log

## Environment

- Generated at: 2026-04-30T13:04:11
- Platform: Windows-11-10.0.26200-SP0
- Python: 3.13.2
- win32com.client: available

## Input

- Placement table: `03_cad/solidworks/component_placement_table_v1.csv`
- CAD inventory: `03_cad/solidworks/current_cad_inventory_for_assembly.csv`; exists=True
- Template config: `03_cad/solidworks/macros/solidworks_template_config.json`; exists=True
- Target assembly: `03_cad/solidworks/assembly/blood_sorting_robot_rough_layout_v1.SLDASM`

## Row Precheck

- OK `base_plate` -> `03_cad/custom_parts/base_plate/base_plate_1100x900x15.step`
- OK `left_y_axis_module` -> `03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step`
- OK `right_y_axis_module` -> `03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step`
- OK `x_axis_module_on_gantry` -> `03_cad/standard_parts/downloaded/x_axis_module/MISUMI_MSA628_X_axis_L750_double_shaft_B1_v1.step`
- OK `z_axis_module` -> `03_cad/standard_parts/downloaded/z_axis_module/MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.step`
- OK `electric_parallel_gripper` -> `03_cad/standard_parts/downloaded/gripper/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.step`
- OK `x_axis_motor` -> `03_cad/standard_parts/downloaded/motors/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.step`
- OK `y_axis_motor_left_or_common` -> `03_cad/standard_parts/downloaded/motors/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.step`
- OK `y_axis_motor_right_placeholder_or_sync_note` -> `03_cad/standard_parts/downloaded/motors/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.step`
- OK `z_axis_motor` -> `03_cad/standard_parts/downloaded/motors/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.step`
- OK `input_mixed_tube_rack_4x6` -> `03_cad/custom_parts/tube_bins/input_mixed_tube_rack_4x6.step`
- OK `category_A_output_bin_2x3` -> `03_cad/custom_parts/tube_bins/category_A_output_bin_2x3.step`
- OK `category_B_output_bin_2x3` -> `03_cad/custom_parts/tube_bins/category_B_output_bin_2x3.step`
- OK `category_C_output_bin_2x3` -> `03_cad/custom_parts/tube_bins/category_C_output_bin_2x3.step`
- OK `category_D_output_bin_2x3` -> `03_cad/custom_parts/tube_bins/category_D_output_bin_2x3.step`
- OK `manual_review_bin_2x3` -> `03_cad/custom_parts/tube_bins/manual_review_bin_2x3.step`
- OK `scan_station_reference` -> `03_cad/custom_parts/scan_station/scan_station_reference_block.step`
- OK `barcode_scanner` -> `03_cad/standard_parts/downloaded/barcode_scanner/Cognex_DataMan80_USB_fixed_barcode_reader_v1.step`
- OK `photoelectric_sensor` -> `03_cad/standard_parts/downloaded/sensors/Panasonic_CX421J_diffuse_photoelectric_sensor_v1.step`
- OK `limit_switch_x_home` -> `03_cad/standard_parts/downloaded/sensors/OMRON_D4N_roller_lever_limit_switch_v1.step`
- OK `limit_switch_y_home` -> `03_cad/standard_parts/downloaded/sensors/OMRON_D4N_roller_lever_limit_switch_v1.step`
- OK `limit_switch_z_home` -> `03_cad/standard_parts/downloaded/sensors/OMRON_D4N_roller_lever_limit_switch_v1.step`
- OK `cable_chain_xz` -> `03_cad/standard_parts/downloaded/cable_chain/MISUMI_MHPKS204_cable_carrier_R38_18links_v1.step`
- OK `emergency_stop_placeholder` -> `03_cad/standard_parts/placeholders/safety/emergency_stop_visual_placeholder_v1.sldprt`
- OK `control_box_placeholder` -> `03_cad/custom_parts/control_box/control_box_placeholder_160x120x80.step`
- OK `y_axis_sync_mechanism` -> `03_cad/custom_parts/y_axis_sync_mechanism/y_axis_sync_shaft_placeholder.step`
- SKIP `sample_tube_instances_input_demo`: wildcard_path_not_expanded_in_4B; path=`03_cad/custom_parts/sample_tube/*.step`
- SKIP `sample_tube_instances_output_demo`: wildcard_path_not_expanded_in_4B; path=`03_cad/custom_parts/sample_tube/*.step`

## SolidWorks Automation

- COM dispatch: succeeded (`SldWorks.Application`).
- Assembly template from config: `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2018\templates\gb_assembly.asmdot`
- MathUtility: unavailable; components will use AddComponent5 coordinate placement only. com_error: (-2147352573, '找不到成员。', None, None)

## Insert Results

- FAIL `base_plate_1100x900x15_v1`: AddComponent5 returned None.
- FAIL `left_y_axis_module_v1`: AddComponent5 returned None.
- FAIL `right_y_axis_module_v1`: AddComponent5 returned None.
- FAIL `x_axis_module_on_gantry_v1`: AddComponent5 returned None.
- FAIL `z_axis_module_v1`: AddComponent5 returned None.
- FAIL `electric_parallel_gripper_v1`: AddComponent5 returned None.
- FAIL `x_axis_motor_v1`: AddComponent5 returned None.
- FAIL `y_axis_motor_common_v1`: AddComponent5 returned None.
- FAIL `y_axis_motor_right_reference_v1`: AddComponent5 returned None.
- FAIL `z_axis_motor_v1`: AddComponent5 returned None.
- FAIL `input_mixed_tube_rack_4x6_v1`: AddComponent5 returned None.
- FAIL `category_A_output_bin_2x3_v1`: AddComponent5 returned None.
- FAIL `category_B_output_bin_2x3_v1`: AddComponent5 returned None.
- FAIL `category_C_output_bin_2x3_v1`: AddComponent5 returned None.
- FAIL `category_D_output_bin_2x3_v1`: AddComponent5 returned None.
- FAIL `manual_review_bin_2x3_v1`: AddComponent5 returned None.
- FAIL `scan_station_reference_v1`: AddComponent5 returned None.
- FAIL `barcode_scanner_v1`: AddComponent5 returned None.
- FAIL `photoelectric_sensor_v1`: AddComponent5 returned None.
- FAIL `limit_switch_x_home_v1`: AddComponent5 returned None.
- FAIL `limit_switch_y_home_v1`: AddComponent5 returned None.
- FAIL `limit_switch_z_home_v1`: AddComponent5 returned None.
- FAIL `cable_chain_xz_v1`: AddComponent5 returned None.
- FAIL `emergency_stop_placeholder_v1`: AddComponent5 returned None.
- FAIL `control_box_placeholder_v1`: AddComponent5 returned None.
- FAIL `y_axis_sync_shaft_placeholder_v1`: AddComponent5 returned None.

## Save Result

- SaveAs3 returned: `0`
- Output exists: `True`
- Removed incomplete or failed rough assembly output to avoid treating it as a valid SLDASM.

## Summary

- Total CSV rows: 28
- Valid CAD rows attempted: 26
- Skipped rows: 2
- Inserted rows: 0
- Failed insertions: 26
- Assembly generated: False
- Output assembly path: `03_cad/solidworks/assembly/blood_sorting_robot_rough_layout_v1.SLDASM`

This log is diagnostic only. The rough assembly remains a coordinate scaffold and requires manual SolidWorks review.
