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

## Functional Work Areas

- Input area: 4 x 6 input rack with 24 vertically inserted mixed blood collection tubes.
- Scanning station: fixed location where the gripper presents a tube to the Panasonic CX-421-J trigger sensor and Cognex DataMan 80 USB barcode reader.
- Output area: four separate 2 x 3 category output bins for Category A/B/C/D, arranged as a 2 x 2 group in the front or front-right area.
- Manual review area: one 2 x 3 `manual_review_bin` in a front corner or near the output edge for barcode failure, unknown category, full output category, or abnormal samples.
- Scanning station count: one, not counted as a tube box because the tube is held by the gripper during scanning.

The X/Y reachable workspace must cover every input hole, the scanning station, every category output-bin slot, and every manual-review slot. Z safe height must clear the tallest expected mixed tube, cap features, rack walls, sensor brackets, barcode reader bracket, and neighboring bins.

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

For classification simulation, trajectory generation should include an intermediate scanning waypoint between input pickup and category placement. Target selection is not a fixed input-to-output index pair; it is computed from `sample_manifest.csv` category data and available category-bin slots. Unknown, failed, full-bin, or abnormal reads route to `manual_review_bin`.
