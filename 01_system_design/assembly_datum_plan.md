# Assembly Datum Plan

## World Coordinate System

The world coordinate system is the master reference for CAD, controls, and documentation. Units are millimeters.

- X: left-right direction along the 1100 mm base length.
- Y: front-back direction along the 900 mm base width.
- Z: upward vertical direction.

## Base Plate Coordinate System

The recommended base plate size is 1100 mm x 900 mm x 15 mm. The base plate lower-left-front corner is the nominal base origin. The top surface of the base plate is the primary mounting datum for racks, left/right Y axes, safety cover brackets, and control box mounting.

## Dual Y-Axis Datums

- `left_y_axis_datum`: centerline and mounting datum of the left Y guide/module.
- `right_y_axis_datum`: centerline and mounting datum of the right Y guide/module.
- The two Y datums must be parallel and coplanar within the tolerance later defined by the SolidWorks drawings.
- The Y-axis synchronization mechanism must reference both Y datums.
- Left and right Y modules use MISUMI MSA-628, configuration `MSA-628-B-AB-B1-0750`, as separate SolidWorks instances of the same standard CAD.

## Gantry And X-Axis Datums

- `gantry_beam_datum`: datum plane and centerline for the cross beam connecting left and right Y carriages.
- `x_axis_on_gantry_datum`: X-axis module datum mounted on the gantry beam.
- `z_axis_centerline`: vertical datum through the Z module carriage and gripper adapter.
- `gripper_centerline`: midpoint line between gripper fingers, aligned to target tube hole centers.
- The X-axis module on the gantry also uses MISUMI MSA-628, configuration `MSA-628-B-AB-B1-0750`, but it is instantiated with the X-axis orientation.
- The Z-axis centerline belongs to a future lead-screw lifting module and must not be treated as MSA-628 geometry.

## Input Rack Coordinate System

The input rack uses its first tube hole center as local rack origin. The local rack X/Y axes follow the hole array. The rack origin is located relative to the base coordinate system by locating pins and fixing holes. The input rack is 4 x 6 with 24 vertical tube positions, and its tubes may be randomly mixed by category, cap color, label, barcode, and height.

## Output Bin Coordinate Systems

The frozen output layout uses four separate 2 x 3 category output bins. Each bin follows the same first-hole local-origin convention as the input rack. The default course demonstration uses:

- `category_a_bin`: 2 x 3, six positions.
- `category_b_bin`: 2 x 3, six positions.
- `category_c_bin`: 2 x 3, six positions.
- `category_d_bin`: 2 x 3, six positions.

The four output bins are recommended as a 2 x 2 group in the front or front-right area of the base. If the target category bin is full, the tube is routed to the manual review bin.

## Manual Review Bin Coordinate System

The `manual_review_bin` is frozen as a 2 x 3 bin. Its local origin follows the same first-hole convention as the input and output bins. It receives barcode failures, unknown categories, full-category cases, and abnormal samples. It should be placed at a front corner or near the output-bin edge.

## Scanning Station Datum

The scanning station has a fixed datum in the base coordinate system:

- `DATUM_SCAN_STATION_TUBE_CENTER`: nominal tube centerline while scanning.
- `DATUM_PHOTOELECTRIC_SENSOR_AXIS`: Panasonic CX-421-J sensing axis for tube presence confirmation.
- `DATUM_BARCODE_READER_AXIS`: Cognex DataMan 80 USB optical axis for label reading.

The scanning datum must be reachable from the input rack and must allow the gripper to present the tube label toward the barcode reader.

## Reachability Relationship

The X-axis travel on the gantry beam and the Y-axis gantry travel must cover the input rack, scanning station, four category output bin coordinate systems, and manual review bin coordinate system. The gripper centerline must reach every input, output-bin, and manual-review hole center without violating safe height, cover clearance, sensor/scanner clearance, neighboring-bin clearance, or axis travel limits.

## Axis Directions

- X positive: from left side toward right side of the base.
- Y positive: from front toward rear of the base.
- Z positive: upward away from the base.

## Home Position

The home position is the machine reference after limit/home switch calibration. It should place the gantry, X carriage, Z module, and gripper at a safe, non-interfering location outside tube pickup height.

## Safe Height

Safe height is the Z coordinate where the gripper and held tube clear tube caps, rack walls, sensors, gantry beam features, and guard features before X/Y motion.

## SolidWorks Datum Naming

Use clear datum names:

- `DATUM_WORLD_XY`
- `DATUM_BASE_TOP`
- `DATUM_BASE_FRONT`
- `DATUM_BASE_LEFT`
- `DATUM_LEFT_Y_AXIS`
- `DATUM_RIGHT_Y_AXIS`
- `DATUM_Y_PARALLELISM_REFERENCE`
- `DATUM_GANTRY_BEAM`
- `DATUM_X_AXIS_ON_GANTRY`
- `DATUM_Z_AXIS_CENTERLINE`
- `DATUM_GRIPPER_CENTERLINE`
- `DATUM_INPUT_RACK_ORIGIN`
- `DATUM_CATEGORY_A_BIN_ORIGIN`
- `DATUM_CATEGORY_B_BIN_ORIGIN`
- `DATUM_CATEGORY_C_BIN_ORIGIN`
- `DATUM_CATEGORY_D_BIN_ORIGIN`
- `DATUM_MANUAL_REVIEW_BIN_ORIGIN`
- `DATUM_SCAN_STATION_TUBE_CENTER`
- `DATUM_PHOTOELECTRIC_SENSOR_AXIS`
- `DATUM_BARCODE_READER_AXIS`

## MATLAB/Simulink Mapping

MATLAB/Simulink uses the same X/Y/Z convention as SolidWorks. The mechanical dual-side Y-axis structure maps to one virtual Y command:

```text
Y_left = Y_right = y
```

Rack coordinates, scanning-station coordinates, safe height, pick height, and place height must be exported using the same base coordinate system so that planned trajectories map directly to SolidWorks assembly positions.

Later classification simulation should read `sample_manifest.csv` with fields:

```text
tube_id, barcode, cap_color, height_mm, category, input_row, input_col, target_bin, target_row, target_col, scan_status, note
```
