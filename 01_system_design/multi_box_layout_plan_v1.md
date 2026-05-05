# Multi-box Layout Plan v1

Stage 7A converts the validated single-batch v6 rough layout into a multi-box batch layout prototype. This is a layout-level CAD plan, not final production geometry.

## Layout Strategy

- Input area: four replaceable 4 x 6 input boxes on the left side of the base.
- Output area: four replaceable 4 x 6 Category A/B/C/D output boxes on the right side.
- Manual review: one 2 x 3 bin near the front/left for easy operator access.
- Scan station: between the input area and the central gantry workspace.
- Gantry coverage: dual Y axes and X/Z/gripper chain should cover the input boxes, scan station, output boxes, and manual review pickup/place points.
- Electrical/safety placeholders: control box at rear/right, emergency stop at front edge, cable-chain path along the rear gantry area, limit-switch placeholders on axis ends, and a transparent perimeter guard frame.

## Base Plate Options

| option | size | assessment |
|---|---|---|
| option_1 | 1100 x 900 x 15 mm | Preserves v6 single-batch footprint but becomes crowded with four input boxes, four output boxes, manual review, scan station, and safety/electrical placeholders. |
| option_2 | 1200 x 900 x 15 mm | Adds side margin for replaceable boxes, control box, emergency stop, and guard frame while keeping the same depth. Recommended for v7. |

## Recommended v7 Base

Use `1200 x 900 x 15 mm` for v7. The earlier `1100 x 900 x 15 mm` remains valid for v6 single-batch prototype validation, but the multi-box workflow benefits from the wider base.

## Deferred Details

The v7 layout includes placeholders only for control box, emergency stop, cable chain, limit switches, and guard frame. Final engineering still needs formal brackets, hole patterns, tolerances, wiring routes, protective covers, and manufacturing drawings.
