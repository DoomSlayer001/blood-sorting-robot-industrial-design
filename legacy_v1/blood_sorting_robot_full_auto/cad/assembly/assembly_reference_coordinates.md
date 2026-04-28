# Assembly Reference Coordinates

Coordinate origin is the lower-left datum of the base plate. Units are mm.

| Component | STEP | X | Y | Z | Rotation | Note |
|---|---:|---:|---:|---:|---|---|
| base_plate | base_plate.step | 250.0 | 175.0 | 5.0 | (0, 0, 0) | world datum: base lower face z=0 |
| input_tube_rack | input_tube_rack.step | 140.5 | 133.0 | 17.5 | (0, 0, 0) | 3x4 input rack |
| output_tube_rack | output_tube_rack.step | 390.5 | 133.0 | 17.5 | (0, 0, 0) | 3x4 output rack |
| input_test_tubes | test_tube_set.step | 140.5 | 133.0 | 25 | (0, 0, 0) | blood sample tubes in input rack |
| output_reference_tubes | test_tube_set.step | 390.5 | 133.0 | 25 | (0, 0, 0) | visual capacity reference |
| y_left_rail | fallback_mgn12_rail.step | 82 | 175.0 | 21 | (0, 0, 90) | Y axis rail |
| y_left_slider | fallback_mgn12_slider.step | 82 | 190 | 27 | (0, 0, 90) | Y carriage block |
| y_right_rail | fallback_mgn12_rail.step | 418 | 175.0 | 21 | (0, 0, 90) | Y axis rail |
| y_right_slider | fallback_mgn12_slider.step | 418 | 190 | 27 | (0, 0, 90) | Y carriage block |
| x_axis_beam | x_axis_beam.step | 250.0 | 190 | 92 | (0, 0, 0) | gantry bridge carried by Y sliders |
| x_axis_rail | fallback_mgn12_rail.step | 250.0 | 190 | 116 | (0, 0, 0) | X axis guide rail |
| x_axis_slider | fallback_mgn12_slider.step | 250 | 190 | 127 | (0, 0, 0) | X carriage carrying Z module |
| z_mounting_plate | z_axis_mounting_plate.step | 250 | 177 | 105 | (90, 0, 0) | vertical adapter plate |
| z_axis_rail | fallback_mgn12_rail.step | 250 | 165 | 80 | (0, -90, 0) | Z axis short rail |
| z_axis_slider | fallback_mgn12_slider.step | 250 | 153 | 60 | (0, -90, 0) | Z carriage block |
| gripper_adapter | gripper_adapter.step | 250 | 148 | 42 | (90, 0, 0) | adapter between Z slider and gripper |
| parallel_gripper | fallback_parallel_gripper.step | 250 | 130 | 24 | (90, 0, 0) | two-finger gripper near pick/place height |
| sensor_bracket | sensor_bracket.step | 288 | 138 | 45 | (90, 0, 0) | scanner/sensor bracket near gripper |
| sensor_module | fallback_sensor_module.step | 292 | 122 | 45 | (90, 0, 0) | barcode/photoelectric sensor appearance |
| x_motor | fallback_nema17_motor.step | 72 | 190 | 119 | (0, 0, 90) | NEMA17 stepper motor |
| y_motor | fallback_nema17_motor.step | 45 | 46 | 34 | (0, 0, 0) | NEMA17 stepper motor |
| z_motor | fallback_nema17_motor.step | 250 | 166 | 152 | (0, 0, 0) | NEMA17 stepper motor |
| x_gt2_belt | fallback_gt2_belt.step | 250 | 202 | 124 | (0, 0, 0) | simplified X belt drive |
| y_gt2_belt | fallback_gt2_belt.step | 82 | 175 | 32 | (0, 0, 90) | simplified Y belt drive |
| z_t8_lead_screw | fallback_t8_lead_screw.step | 262 | 160 | 92 | (0, -90, 0) | simplified Z lead screw |
| cable_chain | fallback_cable_chain.step | 260 | 325 | 70 | (0, 0, 0) | rear cable carrier |
| control_box_mount | control_box_mount.step | 380 | 323 | 18 | (0, 0, 0) | rear mount |
| control_box | fallback_control_box.step | 380 | 323 | 62 | (0, 0, 0) | controller enclosure |
| emergency_stop | fallback_emergency_stop.step | 330 | 275 | 100 | (90, 0, 0) | emergency stop button on control box |
| limit_switches | fallback_limit_switch.step | 70 | 305 | 28 | (0, 0, 0) | representative limit switch |
| fasteners | fallback_fasteners.step | 250 | 45 | 18 | (0, 0, 0) | sample fastener set |
| bearing_block_a | fallback_bearing_block.step | 92 | 190 | 124 | (0, 0, 90) | belt/screw support |
| coupling_z | fallback_coupling.step | 262 | 160 | 145 | (0, -90, 0) | Z motor coupling |