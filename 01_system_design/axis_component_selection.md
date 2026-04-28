# Axis Component Selection

## Why X/Y Use Belt-Driven Linear Modules

The X and Y axes are horizontal motion axes. Their main requirement is fast movement between rack positions while maintaining repeatability around +/-0.5 mm. Belt-driven linear modules are suitable because they provide high speed, long stroke options, compact packaging, and straightforward motor integration.

The X axis moves the Z module and gripper across the rack field. The Y axis moves the gantry bridge and carries the X module, Z module, gripper, cables, and part of the sensor hardware. For this reason, the Y axis should be treated as the higher-load horizontal axis and may need dual guide support or synchronized dual-side drive to avoid gantry racking.

## Why Z Uses A Lead-Screw Lifting Module

The Z axis moves vertically and must control descent toward tubes and racks. A lead-screw lifting module is preferred because it provides stable vertical positioning, good holding behavior, and a direct torque-to-thrust relationship for sizing. Compared with a belt-only vertical axis, the lead-screw option better supports gravity load and controlled pick/place motion.

The final choice between trapezoidal screw, ball screw, and integrated lead-screw actuator depends on backlash, efficiency, required holding behavior, and motor brake strategy.

## Why Use An Electric Two-Finger Parallel Gripper

The project handles 13 mm diameter blood sample tubes. An electric two-finger parallel gripper provides controllable opening, repeatable stroke, compact packaging, and no requirement for a pneumatic system. Silicone or TPU pads should be added to reduce tube stress and improve friction.

The gripper must be selected using real supplier CAD before design freeze because its mounting flange, mass, finger stroke, finger length, cable exit, and pad interface affect the Z module and end-effector bracket.

## Motion Load Sources

- X moving mass: X carriage, Z lifting module, gripper, tube, sensor bracket, scanner envelope, cables attached to X motion.
- Y moving mass: gantry bridge, X module, Z module, gripper, tube, cable chain moving segment, sensors, brackets.
- Z moving mass: Z carriage, gripper, pads, tube, small sensor bracket or adapter plate.

## Mechanical Factors To Consider

- Moving mass: required for thrust, torque, acceleration, and vibration estimates.
- Acceleration: affects peak belt force and motor torque.
- Friction: includes guide friction, belt losses, screw/nut friction, cable-chain drag.
- Belt tension: affects stiffness, repeatability, bearing loads, and pulley shaft load.
- Z-axis gravity: must be included in thrust and holding torque.
- Gripper and tube load: small in mass but important for safety, impact, and tube handling.

## SolidWorks Assembly Datum Strategy

Real standard parts will become assembly references:

- Belt linear modules: base mounting face, carriage top face, carriage hole pattern, rail centerline, motor mount face.
- Linear guides: rail datum face, rail centerline, block top face, block mounting holes.
- Z lead-screw module: vertical rail axis, screw centerline, carriage plate interface, motor flange plane.
- Gripper: mounting flange, finger center plane, finger stroke direction, cable exit.
- Sensors and scanner: sensing axis, mounting face, connector clearance.
- Drag chain: fixed end, moving end, bend radius envelope, cable exit direction.

Custom parts should reference these real datums rather than concept-model dimensions.
