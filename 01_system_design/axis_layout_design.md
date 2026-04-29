# Axis Layout Design

## Axis Definition

- Y axis: dual-side gantry base axis. Left and right MISUMI MSA-628 Guided Belt Drive Actuator modules move the gantry beam forward and backward.
- X axis: transverse axis mounted on the gantry beam. It uses the same MISUMI MSA-628 series and moves the Z-axis module and gripper left and right.
- Z axis: end-effector lifting axis mounted on the X-axis carriage. It performs vertical pick/place motion.

The confirmed X/Y configuration is `MSA-628-B-AB-B1-0750`. The same supplier CAD can be instantiated multiple times in SolidWorks: left Y, right Y, and X-on-gantry. Z remains a separate lead-screw lifting module and does not use MSA-628.

## Travel

- X travel: 450-500 mm.
- Y travel: 260-300 mm.
- Z travel: 120 mm.

The base plate recommendation is now 1100 mm x 900 mm x 15 mm. X is the left-right direction along 1100 mm, Y is the front-back direction along 900 mm, and Z is vertical.

## Y-Axis Synchronization

The mechanical Y axis has two sides:

```text
Y_left = Y_right = y
```

The preferred implementation is a mechanically synchronized gantry using one motor plus a synchronization shaft or synchronization belt linkage. Independent dual Y motors are not the default design route.

If a dual-motor Y-axis design is introduced later, the project must add synchronization control, skew detection, and anti-jamming risk analysis before design freeze.

## Drive Method

- Left/right Y axis: dual-side support/guide structure with mechanical synchronization preferred.
- X axis: MISUMI MSA-628 belt-driven linear module mounted on the gantry beam.
- Z axis: lead-screw lifting module for vertical load holding and controlled descent; selected separately later.

## Motion Direction

The base coordinate system uses the base plate as the primary datum. X is aligned with the 1100 mm long side of the base plate, Y is aligned with the 900 mm side, and Z is positive upward.

## SolidWorks Assembly Requirements

SolidWorks must include:

- Left Y-axis guide/support and carriage.
- Right Y-axis guide/support and carriage.
- Gantry beam connected to both Y carriages.
- X-axis module mounted to the gantry beam.
- Z-axis module mounted to the X carriage.
- Gripper centerline aligned to rack hole coordinates.

The left and right Y sliders and the gantry beam must be constrained so the beam remains square to the Y-axis travel direction.

## MATLAB/Simulink Mapping

MATLAB/Simulink continues to use one virtual `y(t)` command for Y-axis motion. The equivalent Y moving mass must later include the gantry beam, X module, Z module, gripper, tube, cable chain moving segment, sensors, and brackets.
