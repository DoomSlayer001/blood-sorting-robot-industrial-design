# Mechanical Interface Definition

## X-Axis Module Interfaces

- Mounting face: the lower datum face of the X-axis belt module or rail base.
- Mounting hole positions: supplier CAD hole pattern must drive X bridge adapter and carriage plate design.
- Effective travel: at least 420 mm usable travel after end clearances and limit zones.
- Slider mounting face: top face of X carriage for Z module connection.
- Motor mounting direction: must be recorded as left/right/rear orientation in the SolidWorks assembly.
- Drag-chain fixed point: define fixed end on bridge or rear frame and moving end on X carriage.

## Y-Axis Module Interfaces

- Left/right guide mounting datums: base plate datum surfaces and rail centerlines must be parallel.
- Bridge connection position: Y carriage top faces define X bridge mounting height and hole pattern.
- Belt or drive side position: drive side must leave clearance for motor, pulley, bearing block and guard cover.
- Motion parallelism: left/right Y guides must be constrained by common base datums and bridge connection references.

## Z-Axis Module Interfaces

- X carriage connection face: Z module rear or base face mounts to X slider adapter plate.
- Z slider mounting face: front carriage face defines gripper adapter location.
- Screw/motor space: reserve vertical and rear clearance for motor, screw, coupling and cable exit.
- Gripper adapter holes: supplier gripper flange and Z carriage hole pattern define adapter plate holes.

## Gripper Interfaces

- Z adapter mounting holes: use real gripper flange CAD or supplier drawing.
- Finger opening range: must clear 13 mm tube diameter plus tolerance and soft-pad thickness.
- Gripping centerline: centerline must align with tube rack hole center coordinates.
- Tube gripping height: soft pads should grip below cap and above rack top surface, with clearance for 75 mm tube height.

## Tube Rack Interfaces

- Fixing holes: rack mounting holes attach to base plate with repeatable location.
- Locating pins: recommended for input/output rack repeatability.
- Hole array origin: define first hole center as local rack origin reference.
- Input/output coordinate systems: each rack has a local coordinate system mapped into the base/world coordinate system.

## Rule

Custom parts must not be finalized from placeholder geometry. They must reference real standard-part CAD faces, axes, and hole patterns before design freeze.
