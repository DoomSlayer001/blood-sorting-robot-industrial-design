# Stage 6E Sorting Animation Report

## Inputs

- `04_simulation/task_planning/pick_scan_place_trajectory_v1.csv`
- `04_simulation/task_planning/sorting_motion_summary_v1.csv`
- `04_simulation/task_planning/rack_slot_coordinates_v1.csv`
- `04_simulation/task_planning/failure_handling_simulation_v1.csv`
- `04_simulation/task_planning/cycle_time_estimate_v1.csv`

## Outputs

- Animation output: gif `04_simulation/task_planning/figures/sorting_process_top_view_v1.gif`
- Static key frames: 04_simulation/task_planning/figures/sorting_animation_frame_start_v1.png, 04_simulation/task_planning/figures/sorting_animation_frame_scan_v1.png, 04_simulation/task_planning/figures/sorting_animation_frame_output_v1.png, 04_simulation/task_planning/figures/sorting_animation_frame_review_v1.png
- Event summary: `04_simulation/task_planning/sorting_animation_event_summary_v1.csv`

## Display Logic

- The figure shows input rack, scan station, Category A/B/C/D bins, manual review, active sample position, active path segment, and completed target placements.
- Category outputs use distinct colors; manual review / scan-failed / unknown-category samples use a red exception marker.

## Limits

- 2D top-view only.
- Does not show real robot arm posture, gripper orientation, acceleration, or controller blending.
- Intended for report/PPT visualization, not final control simulation.

## Next

- 6F: control-system pseudocode and interface definition.
- 6G: final report / PPT organization.
