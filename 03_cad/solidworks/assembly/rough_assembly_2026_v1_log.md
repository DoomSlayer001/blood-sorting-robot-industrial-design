# Rough Assembly v1 Log

## Environment

- Generated at: 2026-05-01T16:22:26
- Platform: Windows-11-10.0.26200-SP0
- Python: 3.13.2

## Native Cache Inputs

- Placement table: `03_cad/solidworks/component_placement_table_v1.csv`
- Native mapping: `03_cad/solidworks/converted_native/native_file_mapping.csv`; exists=True
- Manual conversion TODO: `03_cad/solidworks/converted_native/manual_native_conversion_todo.csv`; exists=True
- Target assembly: `03_cad/solidworks/assembly/blood_sorting_robot_rough_layout_2026_v1.SLDASM`

- FOUND `base_plate` -> `03_cad/solidworks/converted_native/parts/base_plate_1100x900x15.SLDPRT`
- FOUND `left_y_axis_module` -> `03_cad/solidworks/converted_native/parts/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM`
- FOUND `right_y_axis_module` -> `03_cad/solidworks/converted_native/parts/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM`
- FOUND `x_axis_module_on_gantry` -> `03_cad/solidworks/converted_native/parts/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM`
- FOUND `z_axis_module` -> `03_cad/solidworks/converted_native/parts/MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.SLDASM`
- FOUND `electric_parallel_gripper` -> `03_cad/solidworks/converted_native/assemblies/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.SLDASM`
- FOUND `x_axis_motor` -> `03_cad/solidworks/converted_native/parts/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.SLDPRT`
- FOUND `y_axis_motor_left_or_common` -> `03_cad/solidworks/converted_native/parts/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.SLDPRT`
- FOUND `y_axis_motor_right_placeholder_or_sync_note` -> `03_cad/solidworks/converted_native/parts/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.SLDPRT`
- FOUND `z_axis_motor` -> `03_cad/solidworks/converted_native/parts/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.SLDPRT`
- FOUND `input_mixed_tube_rack_4x6` -> `03_cad/solidworks/converted_native/parts/input_mixed_tube_rack_4x6.SLDASM`
- FOUND `category_A_output_bin_2x3` -> `03_cad/solidworks/converted_native/parts/category_A_output_bin_2x3.SLDASM`
- FOUND `category_B_output_bin_2x3` -> `03_cad/solidworks/converted_native/parts/category_A_output_bin_2x3.SLDASM`
- FOUND `category_C_output_bin_2x3` -> `03_cad/solidworks/converted_native/parts/category_A_output_bin_2x3.SLDASM`
- FOUND `category_D_output_bin_2x3` -> `03_cad/solidworks/converted_native/parts/category_A_output_bin_2x3.SLDASM`
- FOUND `manual_review_bin_2x3` -> `03_cad/solidworks/converted_native/parts/category_A_output_bin_2x3.SLDASM`
- FOUND `scan_station_reference` -> `03_cad/solidworks/converted_native/parts/scan_station_reference_block.SLDPRT`
- FOUND `barcode_scanner` -> `03_cad/solidworks/converted_native/parts/Cognex_DataMan80_USB_fixed_barcode_reader_v1.SLDPRT`
- FOUND `photoelectric_sensor` -> `03_cad/solidworks/converted_native/parts/Panasonic_CX421J_diffuse_photoelectric_sensor_v1.SLDPRT`
- MISSING `limit_switch_x_home`; native conversion required.
- MISSING `limit_switch_y_home`; native conversion required.
- MISSING `limit_switch_z_home`; native conversion required.
- FOUND `cable_chain_xz` -> `03_cad/solidworks/converted_native/parts/MISUMI_MHPKS204_cable_carrier_R38_18links_v1.SLDASM`
- FOUND `emergency_stop_placeholder` -> `03_cad/standard_parts/placeholders/safety/emergency_stop_visual_placeholder_v1.sldprt`
- MISSING `control_box_placeholder`; native conversion required.
- FOUND `y_axis_sync_mechanism` -> `03_cad/solidworks/converted_native/parts/y_axis_sync_shaft_placeholder.SLDPRT`
- FOUND `sample_tube_instances_input_demo` -> `03_cad/solidworks/converted_native/parts/purple_cap_tube_13x75.SLDASM`
- FOUND `sample_tube_instances_output_demo` -> `03_cad/solidworks/converted_native/parts/purple_cap_tube_13x75.SLDASM`

## Critical Component Gate

- Critical native CAD gate passed.

## SolidWorks Native Insert

- COM dispatch: succeeded (`SldWorks.Application`).
- Assembly template from config: `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_assembly.asmdot`
- WARN `base_plate_1100x900x15.SLDPRT`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `base_plate_1100x900x15_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `base_plate_1100x900x15_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `base_plate_1100x900x15_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `base_plate_1100x900x15_v1` from `03_cad/solidworks/converted_native/parts/base_plate_1100x900x15.SLDPRT`. manual orientation check required
- WARN `MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `left_y_axis_module_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `left_y_axis_module_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `left_y_axis_module_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `left_y_axis_module_v1` from `03_cad/solidworks/converted_native/parts/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM`. manual orientation check required
- WARN `MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `right_y_axis_module_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `right_y_axis_module_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `right_y_axis_module_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `right_y_axis_module_v1` from `03_cad/solidworks/converted_native/parts/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM`. manual orientation check required
- WARN `MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `x_axis_module_on_gantry_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `x_axis_module_on_gantry_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `x_axis_module_on_gantry_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `x_axis_module_on_gantry_v1` from `03_cad/solidworks/converted_native/parts/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM`. manual orientation check required
- WARN `MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.SLDASM`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `z_axis_module_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `z_axis_module_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `z_axis_module_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `z_axis_module_v1` from `03_cad/solidworks/converted_native/parts/MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.SLDASM`. manual orientation check required
- WARN `SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.SLDASM`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `electric_parallel_gripper_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `electric_parallel_gripper_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `electric_parallel_gripper_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `electric_parallel_gripper_v1` from `03_cad/solidworks/converted_native/assemblies/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.SLDASM`. manual orientation check required
- WARN `OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.SLDPRT`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `x_axis_motor_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `x_axis_motor_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `x_axis_motor_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `x_axis_motor_v1` from `03_cad/solidworks/converted_native/parts/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.SLDPRT`. manual orientation check required
- WARN `OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.SLDPRT`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `y_axis_motor_common_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `y_axis_motor_common_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `y_axis_motor_common_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `y_axis_motor_common_v1` from `03_cad/solidworks/converted_native/parts/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.SLDPRT`. manual orientation check required
- WARN `OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.SLDPRT`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `y_axis_motor_right_reference_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `y_axis_motor_right_reference_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `y_axis_motor_right_reference_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `y_axis_motor_right_reference_v1` from `03_cad/solidworks/converted_native/parts/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.SLDPRT`. manual orientation check required
- WARN `OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.SLDPRT`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `z_axis_motor_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `z_axis_motor_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `z_axis_motor_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `z_axis_motor_v1` from `03_cad/solidworks/converted_native/parts/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.SLDPRT`. manual orientation check required
- WARN `input_mixed_tube_rack_4x6.SLDASM`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `input_mixed_tube_rack_4x6_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `input_mixed_tube_rack_4x6_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `input_mixed_tube_rack_4x6_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `input_mixed_tube_rack_4x6_v1` from `03_cad/solidworks/converted_native/parts/input_mixed_tube_rack_4x6.SLDASM`.
- WARN `category_A_output_bin_2x3.SLDASM`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `category_A_output_bin_2x3_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `category_A_output_bin_2x3_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `category_A_output_bin_2x3_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `category_A_output_bin_2x3_v1` from `03_cad/solidworks/converted_native/parts/category_A_output_bin_2x3.SLDASM`.
- WARN `category_A_output_bin_2x3.SLDASM`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `category_B_output_bin_2x3_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `category_B_output_bin_2x3_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `category_B_output_bin_2x3_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `category_B_output_bin_2x3_v1` from `03_cad/solidworks/converted_native/parts/category_A_output_bin_2x3.SLDASM`.
- WARN `category_A_output_bin_2x3.SLDASM`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `category_C_output_bin_2x3_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `category_C_output_bin_2x3_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `category_C_output_bin_2x3_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `category_C_output_bin_2x3_v1` from `03_cad/solidworks/converted_native/parts/category_A_output_bin_2x3.SLDASM`.
- WARN `category_A_output_bin_2x3.SLDASM`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `category_D_output_bin_2x3_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `category_D_output_bin_2x3_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `category_D_output_bin_2x3_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `category_D_output_bin_2x3_v1` from `03_cad/solidworks/converted_native/parts/category_A_output_bin_2x3.SLDASM`.
- WARN `category_A_output_bin_2x3.SLDASM`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `manual_review_bin_2x3_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `manual_review_bin_2x3_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `manual_review_bin_2x3_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `manual_review_bin_2x3_v1` from `03_cad/solidworks/converted_native/parts/category_A_output_bin_2x3.SLDASM`.
- WARN `scan_station_reference_block.SLDPRT`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `scan_station_reference_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `scan_station_reference_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `scan_station_reference_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `scan_station_reference_v1` from `03_cad/solidworks/converted_native/parts/scan_station_reference_block.SLDPRT`. manual orientation check required
- WARN `Cognex_DataMan80_USB_fixed_barcode_reader_v1.SLDPRT`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `barcode_scanner_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `barcode_scanner_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `barcode_scanner_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `barcode_scanner_v1` from `03_cad/solidworks/converted_native/parts/Cognex_DataMan80_USB_fixed_barcode_reader_v1.SLDPRT`. manual orientation check required
- WARN `Panasonic_CX421J_diffuse_photoelectric_sensor_v1.SLDPRT`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `photoelectric_sensor_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `photoelectric_sensor_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `photoelectric_sensor_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `photoelectric_sensor_v1` from `03_cad/solidworks/converted_native/parts/Panasonic_CX421J_diffuse_photoelectric_sensor_v1.SLDPRT`. manual orientation check required
- WARN `MISUMI_MHPKS204_cable_carrier_R38_18links_v1.SLDASM`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `cable_chain_xz_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `cable_chain_xz_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `cable_chain_xz_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `cable_chain_xz_v1` from `03_cad/solidworks/converted_native/parts/MISUMI_MHPKS204_cable_carrier_R38_18links_v1.SLDASM`. manual orientation check required
- WARN `emergency_stop_visual_placeholder_v1.sldprt`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `emergency_stop_placeholder_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `emergency_stop_placeholder_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `emergency_stop_placeholder_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `emergency_stop_placeholder_v1` from `03_cad/standard_parts/placeholders/safety/emergency_stop_visual_placeholder_v1.sldprt`. manual orientation check required
- WARN `y_axis_sync_shaft_placeholder.SLDPRT`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `y_axis_sync_shaft_placeholder_v1`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `y_axis_sync_shaft_placeholder_v1`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `y_axis_sync_shaft_placeholder_v1`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `y_axis_sync_shaft_placeholder_v1` from `03_cad/solidworks/converted_native/parts/y_axis_sync_shaft_placeholder.SLDPRT`. manual orientation check required
- WARN `purple_cap_tube_13x75.SLDASM`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `sample_tube_input_demo_instances`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `sample_tube_input_demo_instances`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `sample_tube_input_demo_instances`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `sample_tube_input_demo_instances` from `03_cad/solidworks/converted_native/parts/purple_cap_tube_13x75.SLDASM`. manual orientation check required
- WARN `purple_cap_tube_13x75.SLDASM`: native OpenDoc6 before insertion failed: com_error: (-2147352571, '类型不匹配。', None, 5)
- WARN `sample_tube_output_demo_instances`: AddComponent5 returned None; trying AddComponent4 fallback.
- WARN `sample_tube_output_demo_instances`: AddComponent4 returned None; trying legacy AddComponent fallback.
- WARN `sample_tube_output_demo_instances`: fixed component step failed: AttributeError: 'bool' object has no attribute 'Select4'
- INSERTED `sample_tube_output_demo_instances` from `03_cad/solidworks/converted_native/parts/purple_cap_tube_13x75.SLDASM`. manual orientation check required

## Insert Gate

- Critical components inserted: 10 / 10
- Output bin inserted: True

## Save Result

- SaveAs3 returned: `0`
- Output exists: `True`
- Output size bytes: `36146`

## Summary

- Native files found: 24
- Native files missing: 4
- Inserted rows: 24
- Insertion failed rows: 0
- Skipped rows: 4
- Assembly generated: True
- Generated SLDASM path: `03_cad/solidworks/assembly/blood_sorting_robot_rough_layout_2026_v1.SLDASM`
- Generated SLDASM size bytes: `36146`

## Manual Orientation Check Components

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
