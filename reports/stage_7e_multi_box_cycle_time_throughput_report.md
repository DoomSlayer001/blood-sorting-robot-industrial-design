# Stage 7E Multi-box Cycle Time and Throughput Report

- Goal: estimate multi-box cycle time and throughput from Stage 7D trajectories.
- Input files: `04_simulation/task_planning/multi_box_pick_scan_place_trajectory_v1.csv`, `04_simulation/task_planning/multi_box_motion_summary_v1.csv`, `04_simulation/task_planning/multi_box_trajectory_event_summary_v1.csv`, `04_simulation/task_planning/multi_box_sorting_policy_simulation_v1.csv`, `04_simulation/task_planning/multi_box_operator_events_v1.csv`.
- Time model: XY speed 320 mm/s, Z speed 180 mm/s, pick 0.8 s, place 0.8 s, scan 0.55 s, gripper open/close 0.25 s, settle 0.15 s, operator output clear 12 s, manual-review clear 15 s, alarm response 20 s.
- Baseline: total_batch_time_s=914.992, average_cycle_time_s=9.531, estimated_samples_per_hour=377.708, bottleneck=motion.
- Forced Category A full: total_batch_time_s=929.042, queued=19, resumed=19; operator clear/resume adds 12 s total distributed across pending samples.
- Forced manual review full: processed=37, completed=36, paused=1; PAUSE_ALARM adds manual-review clear and alarm response time.
- Category-level comparison excludes abnormal samples from normal A/B/C/D throughput.
- Figures: 04_simulation/task_planning/figures/multi_box_cycle_time_per_sample_v1.png, 04_simulation/task_planning/figures/multi_box_cycle_time_breakdown_v1.png, 04_simulation/task_planning/figures/multi_box_batch_throughput_comparison_v1.png, 04_simulation/task_planning/figures/multi_box_category_cycle_time_v1.png, 04_simulation/task_planning/figures/multi_box_hold_impact_v1.png

## Bottleneck Analysis

- Baseline bottleneck: motion.
- Category hold scenario bottleneck: motion.
- Manual review full scenario bottleneck: motion.

## Limits

- No dynamics, acceleration limits, or PID response are modeled yet.
- Speeds and operator response times are engineering estimates.
- No parallel handling, path optimization, or collision timing is included.

## Next Steps

- Stage 7F: Multi-box animation update.
- Stage 8A: Kinematics and PID control simulation.
- Stage 8B: Trajectory-to-control interface.
