# Rough Assembly v1 Log

## Environment

- Generated at: 2026-04-30T13:14:03
- Platform: Windows-11-10.0.26200-SP0
- Python: 3.13.2
- win32com.client: available

## Input

- Placement table: `03_cad/solidworks/component_placement_table_v1.csv`
- CAD inventory: `03_cad/solidworks/current_cad_inventory_for_assembly.csv`; exists=True
- Template config: `03_cad/solidworks/macros/solidworks_template_config.json`; exists=True
- Target assembly: `03_cad/solidworks/assembly/blood_sorting_robot_rough_layout_v1.SLDASM`

## Path Precheck

- `base_plate` original=`03_cad/custom_parts/base_plate/base_plate_1100x900x15.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\custom_parts\base_plate\base_plate_1100x900x15.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `left_y_axis_module` original=`03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\y_axis_module\MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `right_y_axis_module` original=`03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\y_axis_module\MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `x_axis_module_on_gantry` original=`03_cad/standard_parts/downloaded/x_axis_module/MISUMI_MSA628_X_axis_L750_double_shaft_B1_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\x_axis_module\MISUMI_MSA628_X_axis_L750_double_shaft_B1_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `z_axis_module` original=`03_cad/standard_parts/downloaded/z_axis_module/MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\z_axis_module\MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `electric_parallel_gripper` original=`03_cad/standard_parts/downloaded/gripper/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\gripper\SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `x_axis_motor` original=`03_cad/standard_parts/downloaded/motors/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\motors\OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `y_axis_motor_left_or_common` original=`03_cad/standard_parts/downloaded/motors/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\motors\OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `y_axis_motor_right_placeholder_or_sync_note` original=`03_cad/standard_parts/downloaded/motors/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\motors\OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `z_axis_motor` original=`03_cad/standard_parts/downloaded/motors/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\motors\OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `input_mixed_tube_rack_4x6` original=`03_cad/custom_parts/tube_bins/input_mixed_tube_rack_4x6.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\custom_parts\tube_bins\input_mixed_tube_rack_4x6.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `category_A_output_bin_2x3` original=`03_cad/custom_parts/tube_bins/category_A_output_bin_2x3.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\custom_parts\tube_bins\category_A_output_bin_2x3.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `category_B_output_bin_2x3` original=`03_cad/custom_parts/tube_bins/category_B_output_bin_2x3.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\custom_parts\tube_bins\category_B_output_bin_2x3.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `category_C_output_bin_2x3` original=`03_cad/custom_parts/tube_bins/category_C_output_bin_2x3.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\custom_parts\tube_bins\category_C_output_bin_2x3.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `category_D_output_bin_2x3` original=`03_cad/custom_parts/tube_bins/category_D_output_bin_2x3.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\custom_parts\tube_bins\category_D_output_bin_2x3.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `manual_review_bin_2x3` original=`03_cad/custom_parts/tube_bins/manual_review_bin_2x3.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\custom_parts\tube_bins\manual_review_bin_2x3.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `scan_station_reference` original=`03_cad/custom_parts/scan_station/scan_station_reference_block.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\custom_parts\scan_station\scan_station_reference_block.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `barcode_scanner` original=`03_cad/standard_parts/downloaded/barcode_scanner/Cognex_DataMan80_USB_fixed_barcode_reader_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\barcode_scanner\Cognex_DataMan80_USB_fixed_barcode_reader_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `photoelectric_sensor` original=`03_cad/standard_parts/downloaded/sensors/Panasonic_CX421J_diffuse_photoelectric_sensor_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\sensors\Panasonic_CX421J_diffuse_photoelectric_sensor_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `limit_switch_x_home` original=`03_cad/standard_parts/downloaded/sensors/OMRON_D4N_roller_lever_limit_switch_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\sensors\OMRON_D4N_roller_lever_limit_switch_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `limit_switch_y_home` original=`03_cad/standard_parts/downloaded/sensors/OMRON_D4N_roller_lever_limit_switch_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\sensors\OMRON_D4N_roller_lever_limit_switch_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `limit_switch_z_home` original=`03_cad/standard_parts/downloaded/sensors/OMRON_D4N_roller_lever_limit_switch_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\sensors\OMRON_D4N_roller_lever_limit_switch_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `cable_chain_xz` original=`03_cad/standard_parts/downloaded/cable_chain/MISUMI_MHPKS204_cable_carrier_R38_18links_v1.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\downloaded\cable_chain\MISUMI_MHPKS204_cable_carrier_R38_18links_v1.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `emergency_stop_placeholder` original=`03_cad/standard_parts/placeholders/safety/emergency_stop_visual_placeholder_v1.sldprt` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\standard_parts\placeholders\safety\emergency_stop_visual_placeholder_v1.sldprt` exists=True ext=`.sldprt` notes=`contains_chinese` status=ok 
- `control_box_placeholder` original=`03_cad/custom_parts/control_box/control_box_placeholder_160x120x80.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\custom_parts\control_box\control_box_placeholder_160x120x80.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `y_axis_sync_mechanism` original=`03_cad/custom_parts/y_axis_sync_mechanism/y_axis_sync_shaft_placeholder.step` resolved=`C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\custom_parts\y_axis_sync_mechanism\y_axis_sync_shaft_placeholder.step` exists=True ext=`.step` notes=`contains_chinese` status=ok 
- `sample_tube_instances_input_demo` original=`03_cad/custom_parts/sample_tube/*.step` resolved=`None` exists=False ext=`` notes=`` status=skipped wildcard_path_not_expanded_in_4B2
- `sample_tube_instances_output_demo` original=`03_cad/custom_parts/sample_tube/*.step` resolved=`None` exists=False ext=`` notes=`` status=skipped wildcard_path_not_expanded_in_4B2

## SolidWorks Automation

- COM dispatch: succeeded (`SldWorks.Application`).
- Assembly template from config: `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2018\templates\gb_assembly.asmdot`
- MathUtility: unavailable; insertion will use AddComponent5 coordinates only. com_error: (-2147352573, '找不到成员。', None, None)

## Base Plate Single-File Diagnostic

- Base plate conversion failed: OpenDoc6_doc_type_1_returned_None; errors=2097152; warnings=0 | OpenDoc6_doc_type_2_returned_None; errors=2097152; warnings=0 | LoadFile4_arg_r_com_error: (-2147352571, '类型不匹配。', None, 3) | LoadFile4_arg_empty_com_error: (-2147352571, '类型不匹配。', None, 3)
- Base plate diagnostic failed; batch conversion stopped by design.
