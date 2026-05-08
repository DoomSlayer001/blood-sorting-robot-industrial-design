# Stage 7B-3 Trajectory Generation and Collision Envelope Pre-check Report

## Scope

- This stage does not use a camera.
- Input occupancy and task routing are driven by internal tables from Stage 7B-1 and state machine results from Stage 7B-2.
- No CAD modeling, rendering, Stage 7A edits, `legacy_v1` edits, or XY slider binding fixes are performed.
- Stage 7A-3f XY slider binding remains a deferred mechanical integration issue and does not block abstract trajectory simulation.

## Waypoint Rules

- Completed output tasks generate pick-scan-output place trajectories.
- Completed manual_review tasks generate pick-scan-manual_review place trajectories.
- Resumed pending tasks generate complete trajectories after category_resume.
- `pick_failed_needs_operator_check` tasks generate pick-attempt and retry waypoints only, with no output/manual_review place trajectory.
- Normal samples never generate manual_review trajectories.

## Height Strategy

- safe_z_mm=190.0; pick_z_mm uses source `z_pick_mm`; scan_z_mm=155.0; place_z_mm=135.0; manual_review_place_z_mm=135.0.
- XY moves occur only at safe_z.
- Z descends are limited to pick, scan alignment, and place target waypoints.
- The safe_z strategy is conservative and remains above the tube top placeholder.

## Scenario Summary

- Generated trajectory task count: 273.
- Not generated task count: 3.
- Trajectory status counts: {'generated_with_warning': 273, 'not_generated_manual_review_full_pause': 2, 'not_generated_pick_failure': 1}.

## Workspace Check

- Workspace PASS/WARNING/FAIL: 0 / 3560 / 0.
- Warnings indicate conservative placeholder soft limits; final calibrated axis limits are not yet available.

## Collision Envelope Pre-check

- Collision PASS/WARNING/FAIL/NOT_CHECKED_APPROXIMATE: 4100 / 4110 / 0 / 18078.
- WARNING and NOT_CHECKED_APPROXIMATE rows are intentional where exact CAD/Isaac Sim collision geometry is unavailable.
- This is a simplified envelope pre-check, not final SolidWorks or Isaac Sim collision verification.

## Downstream Use

- This stage provides trajectory foundations for cycle time, animation, and later Isaac Sim visualization.
- validation_status=PASS
