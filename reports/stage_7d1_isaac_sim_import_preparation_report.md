# Stage 7D-1 Isaac Sim / 3D CAD Import Preparation Report

- Stage scope: Isaac Sim / 3D CAD import and playback preparation.
- This stage is not a 2D animation.
- This stage is not PPT.
- This stage is not ordinary rendering.
- This stage prepares true 3D moving-part simulation import/playback assets and does not force Isaac Sim to run.
- Current mechanical baseline: Stage 7A-3f v1.7, `03_cad/freecad_assembly/blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_7.step`.
- Stage 7A CAD, `legacy_v1`, and Stage 7B results were not modified.

## Group And Joint Mapping

The Isaac scene hierarchy maps the imported robot under `/World/blood_sorting_robot`. The fixed base contains static environment geometry: base, input boxes, output boxes, manual review area, scan station, enclosure frame, control box, and fixed Y rails.

The Y gantry moving group is a child of the robot root and is driven by `joint_y_gantry`. The X slider moving group is nested under the Y gantry and is driven by `joint_x_slider`. The Z axis moving group is nested under the X slider and is driven by `joint_z_axis`. The gripper fingers are nested under the Z axis and use mirrored gripper prismatic joints.

## Motion Trace Conversion

`convert_motion_trace_to_isaac_commands_v1.py` reads `06_simulation/time_stepped_motion_trace_v1.csv` and writes `08_3d_simulation/isaac_import/isaac_joint_command_timeseries_v1.csv`. X/Y/Z values are converted from millimeters to Isaac meters using scale `0.001`. The trace `gripper_state` maps to left/right finger opening commands.

## Tube Attach/Detach

The tube event file defines `before_pick`, `attach_to_gripper`, `scan_attached`, `detach_to_output_box`, `detach_to_manual_review`, and `pick_failed_no_attach`. During later Isaac playback, these events should either re-parent the active tube visual or switch visible tube instances. Scan behavior remains table/state-machine driven; no camera logic is introduced.

## Collision And Visuals

Collision proxies are simplified approximations for import preparation. They cover fixed base, input racks, output boxes, manual review, X beam, Z axis, gripper, tube, enclosure, control box, and cable chain. They are not final high-fidelity CAD mesh collision.

## Environment Status

The environment check records Python availability, repository path validity, trace and STEP existence, Isaac Sim module availability, and pending USD/import validation. If Isaac Sim is not installed in the current environment, that is recorded as WARNING only and does not block Stage 7D-1 preparation.

## Next Stage Boundary

Stage 7D-2 may attempt actual Isaac Sim import/playback using these files. Stage 7D-1 stops at preparation and does not automatically enter the next stage.
