# Axis Component Selection

## Architecture Basis

The mainline architecture is now a dual-side gantry Cartesian robot. The Y axis is split mechanically into left and right support/guide sides, but the control model still treats it as one virtual axis:

```text
Y_left = Y_right = y
```

The preferred Y implementation is a single drive source with mechanical synchronization through a timing shaft, cross belt, or equivalent linkage. Independent dual Y motors are not the preferred baseline; if they are introduced later, synchronization control and anti-racking risk must be documented separately.

## Why X Uses A Belt-Driven Module On The Gantry

The X axis is mounted on the gantry beam and moves the Z module, gripper, tube, local sensors, and moving cables across the rack field. A belt-driven industrial linear module is suitable because it provides high speed, a long 450-500 mm stroke range, compact packaging, and clear carriage/motor interfaces for SolidWorks assembly.

Real X-module CAD is required before the gantry beam holes, Z adapter plate, motor side, and drag-chain bracket can be frozen.

## Why Y Uses Dual-Side Support With Mechanical Synchronization

The Y axis carries the gantry beam, X module, Z module, gripper, tube, moving cable chain segment, and auxiliary brackets. A single unsupported Y axis would create a higher racking risk. Dual-side support improves stiffness and keeps the gantry beam square to the base.

Mechanical synchronization is preferred because it makes the left and right Y sides follow the same displacement without relying on two independent motor loops. The synchronization mechanism may use a timing shaft, belt linkage, matched pulleys, couplings, and bearing supports.

Real left/right Y CAD and synchronization component data are required before the base plate, Y support plates, gantry beam end plates, and bearing brackets can be finalized.

## Why Z Uses A Lead-Screw Lifting Module

The Z axis moves vertically and must control descent toward tubes and racks. A lead-screw lifting module is preferred because it provides stable vertical positioning, direct torque-to-thrust sizing, and better holding behavior than a belt-only vertical axis.

The final choice between trapezoidal screw, ball screw, and integrated lead-screw actuator depends on backlash, efficiency, required holding behavior, and motor brake strategy.

## Why Use An Electric Two-Finger Parallel Gripper

The project handles 13 mm diameter blood sample tubes. An electric two-finger parallel gripper provides controllable opening, repeatable stroke, compact packaging, and no requirement for a pneumatic system. Silicone or TPU pads should be added to reduce tube stress and improve friction.

The gripper must be selected using real supplier CAD before design freeze because its mounting flange, mass, finger stroke, finger length, cable exit, and pad interface affect the Z module and end-effector bracket.

## Motion Load Sources

- X moving mass: X carriage, Z lifting module, gripper, tube, sensor bracket, scanner envelope, and cables attached to X motion.
- Y moving mass: left/right Y carriages, gantry beam, X module, Z module, gripper, tube, cable chain moving segment, sensors, and brackets.
- Z moving mass: Z carriage, gripper, pads, tube, small sensor bracket, and adapter plate.

## Mechanical Factors To Consider

- Moving mass: required for thrust, torque, acceleration, beam deflection, and vibration estimates.
- Acceleration: affects peak belt force, synchronization shaft torque, and motor torque.
- Friction: includes guide friction, belt losses, screw/nut friction, cable-chain drag, and left/right Y guide mismatch.
- Belt tension: affects stiffness, repeatability, bearing loads, and pulley shaft load.
- Y synchronization: must prevent gantry skew and binding under acceleration.
- Z-axis gravity: must be included in thrust and holding torque.
- Gripper and tube load: small in mass but important for safety, impact, and tube handling.

## SolidWorks Assembly Datum Strategy

Real standard parts will become assembly references:

- Left/right Y modules: base mounting face, rail centerline, carriage top face, carriage hole pattern, left/right height match, and drive/sync input side.
- Y synchronization mechanism: pulley pitch datum, shaft centerline, bearing block center height, coupling length, belt path, and tension adjustment slot.
- Gantry beam hardware: beam end plate faces, dowel/reference holes, carriage adapter holes, and squareness references.
- X module on gantry: module base mounting face, carriage top face, carriage hole pattern, rail centerline, and motor mount face.
- Z lead-screw module: vertical rail axis, screw centerline, carriage plate interface, and motor flange plane.
- Gripper: mounting flange, finger center plane, finger stroke direction, and cable exit.
- Sensors and scanner: sensing axis, mounting face, and connector clearance.
- Drag chain: fixed end, moving end, bend radius envelope, and cable exit direction.

Custom parts should reference these real datums rather than concept-model dimensions.
