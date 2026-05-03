# Stage 6C Cycle Time And Throughput Report

## Inputs

- `04_simulation/task_planning/pick_scan_place_trajectory_v1.csv`
- `04_simulation/task_planning/sorting_motion_summary_v1.csv`
- `04_simulation/task_planning/trajectory_workspace_check_v1.csv`
- `04_simulation/task_planning/pick_place_height_rules_v1.md`

## Time Model

- Parameters: xy_speed_mm_s=300, z_speed_mm_s=120, gripper_close_s=0.8, gripper_open_s=0.6, barcode_scan_s=1.2, classify_decision_s=0.2, settle_time_per_pick_s=0.3, settle_time_per_place_s=0.3, manual_review_extra_s=0.5
- These are initial engineering estimates, not final controller or vendor timing values.

## Results

- Sample count: 24
- Total sorting time: 274.273 s (4.571 min)
- Average cycle time: 11.428 s/sample
- Estimated throughput: 315.015 samples/hour
- Manual review samples: 2
- Main bottleneck: motion
- Figures: 04_simulation/task_planning/figures/cycle_time_per_sample_v1.png, 04_simulation/task_planning/figures/cycle_time_breakdown_v1.png

## Limits

- Ignores acceleration, jerk, gripper compliance, controller blending, and real scanner retry behavior.
- Assumes each sample is handled sequentially without parallel prefetching.

## Next

- 6D: exception handling logic simulation.
- 6E: action animation or visualization demo.
- 6F: control-system interface and pseudocode.
