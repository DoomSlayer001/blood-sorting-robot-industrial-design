# ADR-001: Switch To Dual-Side Gantry Architecture

## Status

Accepted.

Updated after standard actuator confirmation: X/Y axes use MISUMI MSA-628 Guided Belt Drive Actuator as the mainline standard actuator series.

## Original Architecture

The previous mainline described a simpler three-axis Cartesian layout with generic X/Y/Z belt or screw modules. It was suitable for early planning but did not fully define a robust industrial gantry support structure.

## New Architecture

The new mainline is a dual-side gantry three-axis Cartesian robot:

- Left and right Y-axis support/guide structures move the gantry beam.
- The X-axis belt module is mounted on the gantry beam.
- The Z-axis lead-screw module is mounted on the X carriage.
- The electric two-finger gripper is mounted below the Z module.
- The control model remains three-axis with `Y_left = Y_right = y`.

The selected X/Y module series is MISUMI MSA-628. The active CAD/configuration is `MSA-628-B-AB-B1-0750` and can be instantiated multiple times in SolidWorks for left Y, right Y, and X-on-gantry. MSA-M6S was considered as a higher-rigidity candidate but is larger and is not part of the current mainline BOM.

## Reason For Change

The blood sample sorting workspace requires reliable coverage of input/output racks, better gantry stiffness, clearer cable routing, and a more industrial mechanical architecture. A dual-side gantry is better aligned with desktop sample-handling machines than a loosely defined stacked axis platform.

## Impact

- Base plate changes from 600 mm x 400 mm x 12 mm to recommended 1100 mm x 900 mm x 15 mm.
- X travel changes from 420 mm to 450-500 mm.
- Y travel changes from 260 mm to 260-300 mm.
- BOM must distinguish left Y axis, right Y axis, Y synchronization mechanism, gantry beam hardware, and X module on gantry.
- BOM now records left Y, right Y, and X-on-gantry as MISUMI MSA-628 instances.
- CAD download planning must prioritize left/right Y modules, synchronization parts, and gantry beam interfaces.
- Z remains a separate lead-screw lifting module and is not based on MSA-628.
- Control remains a virtual X/Y/Z model, with mechanical synchronization mapped to one Y axis.

## Risks

- Left/right Y-axis misalignment can cause gantry skew and binding.
- If dual Y motors are used later, synchronization errors can create jamming risk.
- Gantry beam deflection can reduce placement accuracy.
- Larger 1100 mm x 900 mm base size affects enclosure, footprint, and material cost.
- More real standard-part CAD is required before self-made part holes can be frozen.

## Follow-Up Actions

1. Register the MSA-628 CAD file as left Y, right Y, and X-on-gantry standard-part instances.
2. Prioritize real CAD for Y synchronization parts and the future Z lead-screw module.
3. Define gantry beam stiffness assumptions and later perform strength/deflection review.
4. Update SolidWorks assembly datums for left/right Y and gantry beam references.
5. Update MATLAB/Simulink documentation to map `Y_left = Y_right = y`.
6. If dual Y motors are considered, create a separate synchronization-control and anti-jamming risk document.
