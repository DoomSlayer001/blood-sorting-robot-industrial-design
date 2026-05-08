# CAD-to-Simulation Frame Alignment v1

## Scope

- This document does not create or edit CAD.
- It records the coordinate-frame convention used to align the current abstract simulation with the existing v7.x CAD planning context.
- The current system does not use a camera; tube pose and occupancy are table-driven.

## Alignment Rule

- `world_frame` and `base_plate_frame` are treated as coincident for Stage 7C-0 calibration.
- Simulation X follows the cross-beam direction from the input-side working region toward the output-side working region.
- Simulation Y follows gantry travel across the input/output box rows.
- Simulation Z is positive upward; pick, scan, and place moves descend from `safe_z_mm` to task-local Z targets.
- `gripper_tcp_frame` is the simulated tool point used by trajectory and collision proxy checks.

## Data Sources

- Existing frame definitions: `06_simulation/digital_twin_coordinate_frames_v1.md`.
- Existing abstract axis definitions: `06_simulation/axis_kinematic_model_v1.md`.
- Slot coordinate reference: `04_simulation/task_planning/multi_box_slot_coordinates_v1.csv` when available.
- Height reference: `04_simulation/task_planning/multi_box_pick_place_height_rules_v1.md` when available.
- CAD validation/interface/accessibility CSV files are reference evidence only; Stage 7C-0 does not claim final CAD-derived hard limits.

## Deferred Mechanical Dependency

Stage 7A-3f XY slider binding remains a deferred mechanical integration issue. It does not block the abstract X/Y/Z simulation calibration because this stage works in task-space coordinates, but it must be resolved before final mechanical workspace and collision acceptance.
