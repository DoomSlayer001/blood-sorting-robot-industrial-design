# Digital Twin Coordinate Frames v1

No camera frame is defined in the current system version. Tube pose inputs come from the internal tube occupancy table.

| frame | parent frame | purpose | approximate origin rule | axis convention | used by |
|---|---|---|---|---|---|
| world_frame | none | Global simulation reference | Base plate center at nominal assembly origin | X left/right across boxes, Y front/back rack direction, Z upward | all modules |
| base_plate_frame | world_frame | Robot base and fixed layout | Base plate center on top plane | Same as world_frame | CAD digital twin, collision check |
| input_rack_frame | base_plate_frame | Input tube rack slot positions | Rack local center or first slot datum | X columns, Y rows, Z upward from rack top | task planner, occupancy table |
| output_box_frame | base_plate_frame | Output box slot positions | Output box local center or first slot datum | X columns, Y rows, Z upward from box top | sorting logic, task planner |
| manual_review_frame | base_plate_frame | Exception/manual review placement | Manual review tray or exception area origin | X/Y slot layout, Z upward | exception logic |
| x_axis_frame | base_plate_frame | Cross-beam X motion reference | X linear module nominal center at gantry home | X positive along cross beam | kinematic model |
| left_y_axis_frame | base_plate_frame | Left Y axis reference | Left Y module nominal origin | Y positive along gantry travel, Z upward | kinematic model |
| right_y_axis_frame | base_plate_frame | Right Y axis reference | Right Y module nominal origin | Y positive along gantry travel, Z upward | kinematic model |
| z_axis_frame | x_axis_frame | Vertical axis reference | X carriage / Z module nominal mount | Z positive upward, command descends negative Z | kinematic model |
| gripper_tcp_frame | z_axis_frame | Pick/place tool center point | Center between gripper jaws at nominal pick pose | Z along tube axis, X/Y inherited | pick/place planner |
| tube_frame | rack or box frame | Individual tube pose | Slot center and tube top/pick height from table | Z along tube axis | tube state, collision check |

