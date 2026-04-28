# Standard Parts Selection Report v1.1

## Purpose

Stage 1 established the industrial standard-part selection logic. This v1.1 update aligns that logic with the dual-side gantry architecture. The goal is still to prepare real supplier part candidates for later SolidWorks assembly, not to create CAD, download CAD, or run simulation.

## Frozen Design Inputs After Gantry Switch

- Architecture: dual-side gantry three-axis Cartesian robot.
- Input rack: 4 x 6, 24 positions.
- Output rack: 4 x 6, 24 positions.
- Base plate: temporarily 800 mm x 500 mm x 12 mm.
- Tube: 13 mm diameter, 75 mm height, 15-20 g per tube.
- Travel: X = 450-500 mm, Y = 260-300 mm, Z = 120 mm.
- Y axis: left/right support or guide sides with mechanical synchronization preferred.
- X axis: belt-driven module mounted on the gantry beam.
- Z axis: lead-screw lifting module.
- Gripper: electric two-finger parallel gripper.
- Accuracy target: repeatability +/-0.5 mm, placement error <=1 mm.
- Cycle target: 6-8 s per tube.

## Selection Summary

The horizontal X axis remains a belt-driven industrial linear module, but it is now mounted on the gantry beam. The Y axis is no longer treated as one generic module: it is a dual-side support/guide structure with a preferred single-motor mechanical synchronization mechanism. This improves gantry stiffness and reduces the risk of left/right mismatch compared with two independent Y motors.

The Z axis remains a lead-screw lifting module because vertical holding, controlled descent, and gravity load management matter more than maximum speed.

The gripper should be an electric two-finger parallel gripper from a real industrial supplier such as SMC or Festo. The soft pads may be custom silicone or TPU because they must match the 13 mm tube surface and avoid tube damage.

## Must Use Real CAD Before Design Freeze

The following parts must be represented by real supplier CAD before SolidWorks design freeze:

- Left Y-axis module or guide assembly.
- Right Y-axis module or guide assembly.
- Y-axis mechanical synchronization mechanism.
- X-axis belt module mounted on the gantry.
- Z-axis lead-screw lifting module.
- X/Y/Z motors.
- X/Y/Z linear guides and sliders if not integrated into selected modules.
- Timing pulleys, lead screw, couplings, and bearing supports.
- Electric two-finger gripper.
- Limit switches, photoelectric sensor, and emergency stop.

These parts define mounting holes, datums, mass distribution, safety interfaces, drive geometry, gantry squareness, and synchronization layout. Fallback models are not acceptable as final industrial references.

## Temporary Fallback Allowed

Temporary fallback is allowed only for early envelope planning of:

- Gripper soft pads.
- Cable drag chain routing envelope.
- Barcode scanner envelope.
- Control enclosure envelope.
- Aluminum profile frame and angle brackets before profile family is fixed.
- Common fasteners before release drawings.
- Transparent PC guard panels and selected guard hardware before enclosure concept is frozen.

Fallback models remain placeholders and must be replaced by real CAD, drawings, or release BOM information before manufacturing package release.

## CAD Status Policy

No CAD is marked as downloaded. Supplier portals often require login, registration, captcha, CAD format selection, or product configurators. Such items remain `manual_download_required`.

## Main Risks

- Left/right Y side height mismatch can cause gantry racking or binding.
- Mechanical synchronization shaft, belt tension, and bearing alignment affect repeatability.
- Gantry beam stiffness and deflection affect X-axis datum and tube placement accuracy.
- Moving mass is not yet known, so motor sizing cannot be final.
- Belt stiffness and pulley diameter affect repeatability and torque.
- Z-axis screw lead affects vertical speed, holding force, and torque.
- Gripper force must be limited to protect tubes.
- Sensor and scanner positions depend on final gripper and rack geometry.
- Enclosure and drag-chain routing depend on final axis packaging.

## Next Inputs

The next CAD phase should manually download real standard-part CAD where permitted, verify naming and source records, and then define the SolidWorks assembly skeleton around the dual-side Y datums, gantry beam datum, X-on-gantry datum, Z centerline, and gripper centerline.
