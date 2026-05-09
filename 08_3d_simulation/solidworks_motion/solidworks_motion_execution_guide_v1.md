# SolidWorks Motion Execution Guide v1

Stage 7D-1A prepares a SolidWorks Motion branch for mechanical verification only. It does not replace the Stage 7B sorting state machine, and it does not attempt complete tube attach/detach logic.

## Baseline

1. Open the accepted Stage 7A-3f v1.7 baseline STEP:
   `03_cad/freecad_assembly/blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_7.step`
2. Confirm the baseline manifest still marks v1.7 as accepted:
   `03_cad/freecad_assembly/current_mechanical_baseline_manifest_v1.csv`
3. Do not edit the Stage 7A CAD source, legacy_v1, or the XY slider binding geometry in this stage.

## Assembly Groups

Organize the imported assembly into these motion groups:

1. `fixed_base_group`: base plate, fixed Y rails, input racks, output racks, manual review area, scan station, enclosure, and control box.
2. `y_gantry_moving_group`: Y sliders/carriages, X beam, X axis module, and Y-moving cable chain side.
3. `x_slider_moving_group`: X slider, Z axis module, Z adapter, gripper body, and cables/hoses carried by X.
4. `z_axis_moving_group`: Z carriage and gripper mounting adapter.
5. `gripper_left_finger_group`: left gripper finger.
6. `gripper_right_finger_group`: right gripper finger.
7. `tube_visual_placeholder_group`: optional visual tube placeholder used for manual motion review.

## Mate and Motion Study Setup

1. Fix `fixed_base_group` to the SolidWorks assembly origin.
2. Add a prismatic mate so `y_gantry_moving_group` moves along the CAD Y axis.
3. Add a prismatic mate so `x_slider_moving_group` moves along the CAD X axis relative to the Y gantry.
4. Add a prismatic mate so `z_axis_moving_group` moves along the CAD Z axis relative to the X slider.
5. Add a fixed mate from `z_axis_moving_group` to the gripper mount.
6. Add linear mates for the left and right gripper fingers so they open and close symmetrically.
7. Create a Motion Study and drive the prismatic mates with tabulated displacement or interpolated motor profiles.

## Driver Reference

Use `06_simulation/time_stepped_motion_trace_v1.csv` as the motion reference:

1. `y_mm` drives Y gantry motion.
2. `x_mm` drives X slider motion.
3. `z_mm` drives Z axis motion.
4. `trajectory_waypoints_v1.gripper_state` provides the open/close reference for the gripper.

SolidWorks Motion should focus on mechanical relationships, travel range, interference, and clearance. It is not responsible for executing the full sorting state machine.

## Tube Visual Simplification

Tube attach/detach may be simplified as a visual placeholder in SolidWorks Motion. For first validation, show the active tube as either seated, attached, or placed without attempting to enforce dynamic parent changes through the full sorting logic.

## Validation Focus

1. Y gantry travel does not collide with input or output racks.
2. X slider and Z axis remain clear of tube racks through the full trajectory envelope.
3. Gripper descent aligns with the intended tube slot.
4. Safe-Z travel clears racks and tube tops.
5. Cable chain, enclosure, control box, and XY adapter remain clear of the moving envelope.
