# Stage 7C-0 CAD-to-Simulation Calibration Report

## Scope

- This stage does not create CAD, rendering, PPT, or animation.
- This stage reduces placeholder/abstract uncertainty in the Stage 7B simulation chain by documenting frame alignment, axis-limit estimates, height rules, slot coordinate sources, and collision proxy classes.
- The current system still does not use a camera; input occupancy comes from the internal tube occupancy table.

## Frame Alignment

- The current calibration treats `world_frame` and `base_plate_frame` as coincident for task-space simulation.
- X follows cross-beam travel, Y follows gantry travel, and Z is positive upward.
- CAD validation/interface/accessibility CSV files are reference evidence only; final CAD-derived hard limits are not claimed in this stage.
- CAD reference evidence found: validation CSV=49, interface CSV=10, accessibility CSV=19.

## Axis Limits And Heights

- X/Y/Z axis limits are conservative calibrated estimates, not final hardware limits.
- Current planning soft limits are documented in `calibrated_axis_limits_v1.csv`.
- Current Stage 7B height rules are safe_z=190 mm, pick_z=145 mm, scan_z=155 mm, output/manual-review place_z=135 mm.
- XY moves must remain at safe_z; low-Z motion remains target-local for pick, scan, and place.
- Optional historical planning reference exists: `04_simulation/task_planning/multi_box_pick_place_height_rules_v1.md`.

## Collision Proxy Refinement

- The combined abstract rack/control/enclosure proxies are split into named input, output, manual review, tube, gripper, Z-axis, X-beam, enclosure, cable-chain, and control-box proxies.
- `usable_for_abstract_check` proxies can support future abstract reruns.
- `warning_only`, `not_checked_until_solidworks`, and `not_checked_until_isaac` proxies must remain warnings or future-validation items.

## Warning Resolution

- Stage 7B-3 workspace WARNING count is 3560 because final calibrated CAD/axis soft limits were not yet available.
- Calibrated axis limits reduce uncertainty, but the warnings should not be blindly converted to final PASS until physical axis travel is verified.
- Collision WARNING count is 4110 and NOT_CHECKED_APPROXIMATE count is 18078.
- Safe-Z XY travel checks are already meaningful at the abstract level; local vertical and static/sweep envelope checks still need exact SolidWorks or Isaac Sim validation.

## Deferred XY Slider Binding

- Stage 7A-3f XY slider binding remains deferred.
- It does not block current simulation calibration because this stage calibrates task-space frames and proxy assumptions, not final mechanical load paths.
- It does affect final mechanical workspace, mate, and collision validation.

## Rerun Recommendation

- Immediate rerun of Stage 7B-3 is not recommended until final CAD/axis soft limits are validated; this stage only prepares calibrated inputs for a future rerun.
- Immediate rerun of Stage 7B-5 is not recommended until Stage 7B-3 workspace/collision rules are updated from final validation.

## Next Options

- SolidWorks real collision check.
- Isaac Sim import preparation.
- Final report integration.

No next stage is executed by this report.
