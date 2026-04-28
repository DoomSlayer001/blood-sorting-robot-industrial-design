# Standard Parts Selection Report v1

## Purpose

Stage 1 freezes the industrial standard-part selection logic for the three-axis blood sample sorting robot. The goal is to prepare real supplier part candidates for later SolidWorks assembly, not to create CAD, download CAD, or run simulation.

## Frozen Design Inputs

- Input rack: 4 x 6, 24 positions.
- Output rack: 4 x 6, 24 positions.
- Base plate: 600 mm x 400 mm x 12 mm.
- Tube: 13 mm diameter, 75 mm height, 15-20 g per tube.
- Travel: X = 420 mm, Y = 260 mm, Z = 120 mm.
- X/Y drive: belt-driven linear modules.
- Z drive: lead-screw lifting module.
- Gripper: electric two-finger parallel gripper.
- Accuracy target: repeatability +/-0.5 mm, placement error <=1 mm.
- Cycle target: 6-8 s per tube.

## Selection Summary

X/Y axes should use belt-driven industrial linear modules or equivalent belt-drive assemblies because the horizontal axes require high speed, moderate precision, and clean packaging. Z should use a lead-screw lifting module because vertical holding, controlled descent, and gravity load management matter more than maximum speed.

The gripper should be an electric two-finger parallel gripper from a real industrial supplier such as SMC or Festo. The soft pads may be custom silicone or TPU because they must match the 13 mm tube surface and avoid tube damage.

## Must Use Real CAD Before Design Freeze

The following parts must be represented by real supplier CAD before SolidWorks design freeze:

- X-axis belt-driven linear module.
- Y-axis belt-driven linear module or dual-guide belt assembly.
- Z-axis lead-screw lifting module.
- X/Y/Z motors.
- X/Y/Z linear guides and sliders if not integrated into selected modules.
- Timing pulleys, lead screw, couplings, and bearing supports.
- Electric two-finger gripper.
- Limit switches, photoelectric sensor, and emergency stop.

These parts define mounting holes, datums, mass distribution, safety interfaces, or drive geometry. Fallback models are not acceptable as final industrial references.

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

No CAD is marked as downloaded in Stage 1. Supplier portals often require login, registration, captcha, CAD format selection, or product configurators. Such items are marked `manual_download_required`.

## Main Risks

- Moving mass is not yet known, so motor sizing cannot be final.
- Belt stiffness and pulley diameter affect repeatability and torque.
- Z-axis screw lead affects vertical speed, holding force, and torque.
- Gripper force must be limited to protect tubes.
- Sensor and scanner positions depend on final gripper and rack geometry.
- Enclosure and drag-chain routing depend on final axis packaging.

## Stage 2 Inputs

Stage 2 should download real standard-part CAD, define self-made part boundary envelopes, and establish SolidWorks assembly datums. The Stage 1 BOM provides the candidate categories and supplier paths for that work.
