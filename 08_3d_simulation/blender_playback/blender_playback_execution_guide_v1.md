# Blender 3D Keyframe Playback Execution Guide v1

Stage 7D-1A prepares a Blender branch for complete 3D sorting animation playback. This branch is intended for process visualization and presentation-style review. It is not a precise physical simulation and does not replace SolidWorks Motion mate validation.

## CAD Import

1. Use the accepted Stage 7A-3f v1.7 baseline:
   `03_cad/freecad_assembly/blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_7.step`
2. Import CAD into Blender through one of these routes:
   - STEP to glTF/OBJ/FBX conversion.
   - SolidWorks export to glTF/OBJ/FBX.
   - Any validated CAD conversion workflow that preserves part names enough for group assignment.
3. Do not modify Stage 7A CAD in this stage.

## Scene Organization

Build the Blender scene in fixed / Y / X / Z / gripper / tube layers:

1. `/RobotScene/FixedBase`
2. `/RobotScene/YGantryMoving`
3. `/RobotScene/YGantryMoving/XSliderMoving`
4. `/RobotScene/YGantryMoving/XSliderMoving/ZAxisMoving`
5. `/RobotScene/YGantryMoving/XSliderMoving/ZAxisMoving/GripperLeftFinger`
6. `/RobotScene/YGantryMoving/XSliderMoving/ZAxisMoving/GripperRightFinger`
7. `/RobotScene/DynamicTubes`
8. `/RobotScene/EventOverlay`

## Playback Inputs

1. Run `08_3d_simulation/blender_playback/scripts/convert_motion_trace_to_blender_keyframes_v1.py`.
2. The converter reads:
   - `06_simulation/time_stepped_motion_trace_v1.csv`
   - `06_simulation/trajectory_waypoints_v1.csv`
   - `06_simulation/sorting_state_machine_event_log_v1.csv`
3. The converter writes:
   - `08_3d_simulation/blender_playback/blender_keyframe_commands_v1.csv`

## Animation Logic

1. Python reads `blender_keyframe_commands_v1.csv`.
2. Y gantry, X slider, and Z axis receive keyframed locations.
3. Gripper fingers receive keyframed open/close offsets.
4. Tubes attach to the gripper at pick and detach to output or manual review at place.
5. `category_hold`, pending, and resume states are shown with overlay text or color markers.
6. Abnormal tubes use red/orange material cues.
7. Output box full conditions use a warning highlight.

## Output

The final Blender implementation may output an MP4 or an image frame sequence. Stage 7D-1A only prepares the files and skeleton script; it does not render.
