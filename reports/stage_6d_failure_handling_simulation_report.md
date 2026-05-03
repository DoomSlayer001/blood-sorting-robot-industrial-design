# Stage 6D Failure Handling Simulation Report

## Inputs

- `04_simulation/task_planning/sorting_sequence_v1.csv`
- `04_simulation/task_planning/rack_slot_coordinates_v1.csv`
- `04_simulation/task_planning/pick_scan_place_trajectory_v1.csv`
- `04_simulation/task_planning/cycle_time_estimate_v1.csv`
- `04_simulation/task_planning/batch_throughput_summary_v1.csv`
- `01_system_design/failure_handling_logic.md`
- `04_simulation/task_planning/sorting_state_machine_v1.md`

## Results

- Covered exception types: scan_failed, unknown_category, target_bin_full, manual_review_bin_full, gripper_pick_failed, gripper_place_failed.
- Baseline manifest status: PASS_NO_ALARM
- Baseline normal completed: 22 / 24
- Manual review used count across enabled runs: 13
- Alarm count: 4; paused runs: 4
- Target bin full events: 5 route to manual review when review space is available.
- Manual review full events: 2 trigger PAUSE_ALARM.
- Injected pick/place failures trigger PAUSE_ALARM under the conservative v1 policy.
- Figures: 04_simulation/task_planning/figures/failure_type_counts_v1.png, 04_simulation/task_planning/figures/bin_occupancy_summary_v1.png

## Limits

- This is a discrete logic simulation; it does not replay controller timing, retry loops, or sensor debounce.
- Pick/place failure recovery is intentionally conservative and pauses for operator inspection.

## Next

- 6E: action animation / sorting flow visualization.
- 6F: control-system interface and pseudocode.
- 6G: final report / PPT summary.
