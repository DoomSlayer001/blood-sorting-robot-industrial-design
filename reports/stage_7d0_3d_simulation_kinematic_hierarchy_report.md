# Stage 7D-0 3D Simulation Kinematic Hierarchy Report

- Stage scope: true 3D moving-part simulation preparation.
- This stage is not a 2D animation, not a PPT stage, and not a rendering stage.
- The accepted mechanical baseline is Stage 7A-3f v1.7: `03_cad/freecad_assembly/blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_7.step`.
- Stage 7A-3f v1.8 remains rejected and is not used.
- Stage 7B simulation results are referenced but not modified.

## Why A STEP File Is Not Enough

STEP is a static geometry exchange format. It can preserve part shapes and assembly placement, but it does not automatically preserve the runtime kinematic hierarchy, parent-child moving groups, simulation joints, dynamic tube parenting, or state-machine playback logic. Without this Stage 7D-0 mapping, imported CAD would appear as a static model and key parts would not know how to move with X/Y/Z or the gripper.

## Kinematic Hierarchy

The fixed base group contains the base plate, input boxes, output boxes, manual review area, scan station, enclosure frame, control box, and fixed Y rail bodies. This group is the static world/environment.

The Y axis moving group contains the left/right Y slider or carriage, X beam, X axis module, X beam end mounts, and the moving side of the cable chain. It moves along `joint_y_gantry` relative to the fixed base.

The X axis moving group contains the X slider, Z axis module, Z adapter, gripper body, and cable/hose portions that travel with the X slider. It moves along `joint_x_slider` relative to the Y gantry moving group.

The Z axis moving group contains the Z carriage or vertical moving part, gripper mounting adapter, and gripper body. It moves along `joint_z_axis` relative to the X slider moving group.

The gripper finger groups use mirrored prismatic open/close joints. `joint_gripper_left` and `joint_gripper_right` are driven by `trajectory_waypoints_v1.gripper_state`.

## Tube Attach/Detach

The tube starts parented to an input slot. At `grip_close_at_pick`, the active tube is re-parented to the gripper TCP and follows the X/Y/Z hierarchy through transport and scan wait. At output placement, the tube detaches to the output box slot. At manual review placement, it detaches to the manual review slot. If `pick_failed` occurs, the tube is not attached and no output/manual review place event is created.

## Trajectory Mapping

`time_stepped_motion_trace_v1.csv` drives the 3D playback time and X/Y/Z prismatic joint positions:

- `x_mm` -> `joint_x_slider`
- `y_mm` -> `joint_y_gantry`
- `z_mm` -> `joint_z_axis`

`trajectory_waypoints_v1.csv` supplies gripper state, sample category color, target type, and task context. State-machine tables support category hold/resume overlays and abnormal sample manual review display.

## Platform Readiness

The next Isaac Sim step is import preparation: convert or import the v1.7 STEP, split fixed and moving groups, create prismatic joints, add tube attach/detach logic, import collision proxies, and validate playback. Current tables indicate this project can enter Isaac Sim import preparation, but actual USD conversion, Isaac playback script creation, and final import validation are still pending.

SolidWorks Motion can be used as an auxiliary check for mate-based X/Y/Z and gripper motion. It is less suitable for the complete sorting state machine and dynamic tube attach/detach behavior.

Stage 7D-0 does not automatically enter the next stage.
