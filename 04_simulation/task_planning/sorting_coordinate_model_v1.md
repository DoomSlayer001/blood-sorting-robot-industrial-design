# Sorting Coordinate Model v1

Stage 6A uses the validated CadQuery/OCP rough layout v6 as the source for task-planning coordinates. These values are for sorting logic and reachability checks only; they are not final manufacturing datums or machining coordinates.

## Global Frame

- Origin: center of the 1100 x 900 mm base plate.
- Unit: millimeter.
- X axis: left/right across the gantry X axis, positive toward the Category B/D side.
- Y axis: front/back along the gantry Y axes, positive toward the input rack side.
- Z axis: vertical, positive upward.
- Base top reference: `z = 0 mm`; the rough-layout base plate is centered at `z = -7.5 mm`.

## Coordinate Sources

- Input rack origin: `(-160, 300)` from v6 `InputRackModule`.
- Input rack slots: 4 rows x 6 columns, 28 mm pitch, centered on the input rack origin.
- Scan station tube center: `(-92, 170)` from v6 `ScanStationModule`.
- Output bin origins:
  - Category A: `(90, -160)`
  - Category B: `(250, -160)`
  - Category C: `(90, -330)`
  - Category D: `(250, -330)`
  - Manual review: `(-205, -330)`
- Output bin slots: 2 rows x 3 columns, 28 mm pitch, centered on each bin origin.

## Planning Notes

- Current slot coordinates intentionally follow the v6 modular/anchor layout.
- Tube insert height is treated as `z_insert_mm = 25 mm`.
- Pick/place/scanning heights are defined separately in `pick_place_height_rules_v1.md`.
- Future detailed CAD, gripper jaw geometry, and compliance pad dimensions may require small offsets.
