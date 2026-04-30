# STEP To Native Conversion Report

- Generated at: 2026-04-30T13:14:04
- Base plate diagnostic status: failed
- Base plate diagnostic detail: OpenDoc6_doc_type_1_returned_None; errors=2097152; warnings=0 | OpenDoc6_doc_type_2_returned_None; errors=2097152; warnings=0 | LoadFile4_arg_r_com_error: (-2147352571, '类型不匹配。', None, 3) | LoadFile4_arg_empty_com_error: (-2147352571, '类型不匹配。', None, 3)
- Successful native outputs or reused native files: 0
- Failed conversions: 1
- Skipped rows: 27
- Rough assembly generated: False

## Native Files Used Or Produced

- None.

## Failed Rows

- `base_plate`: OpenDoc6_doc_type_1_returned_None; errors=2097152; warnings=0 | OpenDoc6_doc_type_2_returned_None; errors=2097152; warnings=0 | LoadFile4_arg_r_com_error: (-2147352571, '类型不匹配。', None, 3) | LoadFile4_arg_empty_com_error: (-2147352571, '类型不匹配。', None, 3)

## Skipped Rows

- `left_y_axis_module`: stopped_after_base_plate_failure
- `right_y_axis_module`: stopped_after_base_plate_failure
- `x_axis_module_on_gantry`: stopped_after_base_plate_failure
- `z_axis_module`: stopped_after_base_plate_failure
- `electric_parallel_gripper`: stopped_after_base_plate_failure
- `x_axis_motor`: stopped_after_base_plate_failure
- `y_axis_motor_left_or_common`: stopped_after_base_plate_failure
- `y_axis_motor_right_placeholder_or_sync_note`: stopped_after_base_plate_failure
- `z_axis_motor`: stopped_after_base_plate_failure
- `input_mixed_tube_rack_4x6`: stopped_after_base_plate_failure
- `category_A_output_bin_2x3`: stopped_after_base_plate_failure
- `category_B_output_bin_2x3`: stopped_after_base_plate_failure
- `category_C_output_bin_2x3`: stopped_after_base_plate_failure
- `category_D_output_bin_2x3`: stopped_after_base_plate_failure
- `manual_review_bin_2x3`: stopped_after_base_plate_failure
- `scan_station_reference`: stopped_after_base_plate_failure
- `barcode_scanner`: stopped_after_base_plate_failure
- `photoelectric_sensor`: stopped_after_base_plate_failure
- `limit_switch_x_home`: stopped_after_base_plate_failure
- `limit_switch_y_home`: stopped_after_base_plate_failure
- `limit_switch_z_home`: stopped_after_base_plate_failure
- `cable_chain_xz`: stopped_after_base_plate_failure
- `emergency_stop_placeholder`: stopped_after_base_plate_failure
- `control_box_placeholder`: stopped_after_base_plate_failure
- `y_axis_sync_mechanism`: stopped_after_base_plate_failure
- `sample_tube_instances_input_demo`: stopped_after_base_plate_failure
- `sample_tube_instances_output_demo`: stopped_after_base_plate_failure

## Next Step

If Python COM conversion or insertion fails, run the VBA fallback from inside SolidWorks or manually verify opening `base_plate_1100x900x15.step`, saving it as `.SLDPRT`, and inserting it into a new assembly.
