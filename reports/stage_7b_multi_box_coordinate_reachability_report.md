# Stage 7B Multi-box Coordinate Reachability Report

- Goal: generate the v7.1 multi-box task coordinate model and validate rough gantry reachability.
- Reference files: v7.1 CadQuery generator, v7.1 validation CSV, multi-box architecture, policy, data model, and state machine documents.
- Layout basis: v7.1 recommended multi-box batch layout prototype on a 1200 x 900 x 15 mm base plate.
- Total task points: 199
- Input slots: 96
- Output slots: 96
- Manual review slots: 6
- Scan station slots: 1
- Workspace assumption: x=[-570,570], y=[-420,420], z=[0,280] mm; near-limit margin=30 mm XY / 15 mm Z.
- Reachability summary: reachable=199, near_limit=0, unreachable=0, needs_review=0.
- safe_z reasonable: yes (`safe_z=200 mm`).
- Top-view figure: generated at `04_simulation/task_planning/figures/multi_box_slot_map_top_view_v1.png`

## Zone Summary

- input: reachable=96, near_limit=0, unreachable=0, needs_review=0
- manual_review: reachable=6, near_limit=0, unreachable=0, needs_review=0
- output_A: reachable=24, near_limit=0, unreachable=0, needs_review=0
- output_B: reachable=24, near_limit=0, unreachable=0, needs_review=0
- output_C: reachable=24, near_limit=0, unreachable=0, needs_review=0
- output_D: reachable=24, near_limit=0, unreachable=0, needs_review=0
- scan_station: reachable=1, near_limit=0, unreachable=0, needs_review=0

## Issues

- near_limit / unreachable points: none.

## Limits

- Coordinates are planning coordinates derived from v7.1 script constants, not final machining datums.
- Future updates should follow final SolidWorks assembly constraints, engineered brackets, gripper pads, and released drawings.

## Next Steps

- Stage 7C: multi-box sample manifest and category hold simulation.
- Stage 7D: multi-box trajectory and cycle time update.
- Stage 8: PID / dynamics simulation after multi-box task logic stabilizes.
