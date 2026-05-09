# Stage 7B-9 Python Simulation Animation Package Report

- Generated at: 2026-05-09T17:48:19
- Stage scope: Python animation package, not Isaac Sim.
- Camera status: no camera logic is used.
- Input occupancy source: internal tube occupancy table.
- Data basis: Stage 7B state machine, trajectory waypoints/segments, and time-stepped Cartesian motion trace.
- Mechanical baseline: Stage 7A-3f v1.7 is the accepted current baseline; v1.8 is rejected.

## Generated animation logic

- Top-view animation shows the input rack, output boxes, manual review area, TCP/gripper XY motion, tube pick/place movement, abnormal samples routed to manual review, and category hold/resume overlay.
- XYZ animation shows X/Y/Z over time, safe_z, pick_z, place_z, scan_z, and low-Z samples constrained to pick/place/scan zones.
- Output/pending timeline animation shows output box occupancy, capacity, pending queue size, and hold/resume scheduling markers.
- Dashboard summarizes baseline throughput, total samples, abnormal samples, bottleneck stage, 7B-6 tracking RMSE, 7B-7 robustness RMSE, and selected mechanical baseline v1.7.

## Successful GIF outputs

- `06_simulation/animations/top_view_sorting_animation_v1.gif` (276 frames)
- `06_simulation/animations/xyz_motion_trajectory_animation_v1.gif` (90 frames)
- `06_simulation/animations/output_pending_timeline_animation_v1.gif` (92 frames)

## MP4 status

- top_view_sorting_animation_v1=warning; xyz_motion_trajectory_animation_v1=warning; output_pending_timeline_animation_v1=warning
- MP4 generation failure or absence is only a warning and does not affect GIF acceptance.

## Dashboard metrics

- baseline throughput: 432.104 samples/hour
- total samples: 69
- abnormal samples: 5
- bottleneck stage: z_motion
- 7B-6 tracking RMSE: 0.082 mm max axis, balanced_pid
- 7B-7 robustness RMSE: 0.333 mm max axis mean
- mechanical baseline: Stage 7A-3f v1.7 accepted; v1.8 rejected

## Intended use and next stages

- These animations are for course presentation and report explanation.
- A future stage may still prepare SolidWorks presentation screenshots or Isaac Sim high-quality display simulation.
- This stage does not automatically enter the next stage.
