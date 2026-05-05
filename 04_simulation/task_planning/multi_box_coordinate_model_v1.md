# Multi-box Coordinate Model v1

This coordinate model is based on the validated v7.1 multi-box CadQuery/OCP rough layout.

## Global Frame

- Origin: center of the 1200 x 900 x 15 mm base plate.
- +X: left-to-right across the machine, from input side toward output side.
- +Y: rearward along the base plate.
- +Z: upward from the base plate top/robot workspace.
- Units: millimeters.

## Coordinate Sources

- Input boxes: `input_box_1..4` from `generate_cadquery_multi_box_layout_v7_1.py`, using origins `(-330,285)`, `(-330,155)`, `(-330,25)`, `(-330,-105)`.
- Output boxes: Category A/B/C/D from v7.1 origins `(160,170)`, `(370,170)`, `(160,-40)`, `(370,-40)`.
- Manual review: v7.1 `manual_review_bin` origin `(-180,-300)`.
- Scan station: v7.1 scan tube holder origin `(-140,60)`.
- Slot pitch: 28 mm, matching the v7.1 4 x 6 rack helper.

These coordinates are for task planning and reachability checks only. They are not final machining datums and should be updated after final SolidWorks assembly constraints, drawings, gripper pads, and engineered brackets are frozen.
