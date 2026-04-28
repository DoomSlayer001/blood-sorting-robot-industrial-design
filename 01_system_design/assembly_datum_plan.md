# Assembly Datum Plan

## World Coordinate System

The world coordinate system is the master reference for CAD, controls, and documentation. Units are millimeters.

- X: left-right direction along the 600 mm base length.
- Y: front-back direction along the 400 mm base width.
- Z: upward vertical direction.

## Base Plate Coordinate System

The base plate lower-left-front corner is the nominal base origin. The top surface of the base plate is the primary mounting datum for racks, axis supports, and enclosure brackets.

## Input Rack Coordinate System

The input rack uses its first tube hole center as local rack origin. The local rack X/Y axes follow the hole array. The rack origin is located relative to the base coordinate system by locating pins and fixing holes.

## Output Rack Coordinate System

The output rack follows the same local convention as the input rack. It is placed on the opposite side of the work envelope while preserving a clear gripper approach path.

## Axis Directions

- X positive: from left side toward right side of the base.
- Y positive: from front toward rear of the base.
- Z positive: upward away from the base.

## Gripper Centerline

The gripper centerline is the line midway between the two gripper fingers. It must align with the target tube hole center during pick/place.

## Home Position

The home position is the machine reference after limit/home switch calibration. It should place the end effector at a safe, non-interfering location outside tube pickup height.

## Safe Height

Safe height is the Z coordinate where the gripper and held tube clear tube caps, rack walls, sensors, and guard features before X/Y motion.

## SolidWorks Datum Naming

Use clear datum names:

- `DATUM_WORLD_XY`
- `DATUM_BASE_TOP`
- `DATUM_BASE_FRONT`
- `DATUM_BASE_LEFT`
- `DATUM_X_AXIS_CENTERLINE`
- `DATUM_Y_AXIS_CENTERLINE_LEFT`
- `DATUM_Y_AXIS_CENTERLINE_RIGHT`
- `DATUM_Z_AXIS_CENTERLINE`
- `DATUM_GRIPPER_CENTERLINE`
- `DATUM_INPUT_RACK_ORIGIN`
- `DATUM_OUTPUT_RACK_ORIGIN`

## MATLAB/Simulink Mapping

MATLAB/Simulink uses the same X/Y/Z convention as SolidWorks. Rack coordinates, safe height, pick height, and place height must be exported using the same base coordinate system so that planned trajectories map directly to SolidWorks assembly positions.
