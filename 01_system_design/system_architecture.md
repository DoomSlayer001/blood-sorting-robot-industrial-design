# System Architecture

## Overview

The system is an industrial-style desktop dual-side gantry three-axis Cartesian mixed blood collection tube identification and classification sorting system. It handles blood collection tubes randomly mixed in a 4 x 6 input rack, identifies each tube by barcode or QR code, queries the sample category, and sorts it into one of four category output bins. It uses synchronized left/right Y-axis gantry motion, an X-axis module mounted on the gantry beam, a Z-axis lifting module, and an electric two-finger gripper.

The previous single-axis-combination Cartesian layout is no longer the mainline architecture.

## Mechanical Modules

1. Base and frame module: 800 mm x 500 mm x 12 mm temporary base plate, frame mounting datums, rack locating features, and safety cover interfaces.
2. Left Y-axis support/drive module: left-side Y guide/support and preferred mechanical synchronization drive side.
3. Right Y-axis support/guide module: right-side Y guide/support synchronized with the left side.
4. Gantry beam module: cross beam connecting left and right Y carriages and carrying the X-axis module.
5. X-axis transverse motion module: belt-driven linear module mounted on the gantry beam, moving the Z module and gripper left/right.
6. Z-axis lifting module: lead-screw vertical axis mounted on the X carriage.
7. Electric gripper module: electric two-finger parallel gripper with silicone or TPU soft pads.
8. Input/output/manual-review tube rack module: one 4 x 6 mixed input rack, four 2 x 3 category output bins for Category A/B/C/D, and one 2 x 3 `manual_review_bin` for barcode failure, unknown category, full category output, or abnormal samples.
9. Control box and safety module: controller enclosure, emergency stop, limit switches, software limits, and safety cover.
10. Sensing and barcode module: Panasonic CX-421-J photoelectric sensor detects tube presence at the pick/place or scanning station and triggers the Cognex DataMan 80 USB fixed-mount image-based barcode reader for 1D/2D barcode or QR code reading on tube labels.
11. Cable chain and wiring management module: moving cable routing for gantry, X carriage, Z module, gripper, sensors, and the fixed barcode reader.
12. Isaac Sim visualization module: material, lighting, cameras, and demonstration animation after SolidWorks assembly stabilizes.

## Platform Responsibilities

- SolidWorks owns dual-side gantry geometry, assembly, materials, drawings, interference checks, gantry beam stiffness planning, and manufacturing exports.
- MATLAB/Simulink owns kinematics, trajectory planning, virtual X/Y/Z PID control, motor sizing support, and error analysis.
- Isaac Sim owns visual presentation, material appearance, cameras, lighting, and demonstration animation.
- GitHub owns version history, review checkpoints, release tags, and large-file traceability through Git LFS.

## Control Mapping

The mechanical Y axis has left and right synchronized structures. The control model remains one virtual Y axis:

```text
Y_left = Y_right = y
```

If a future dual-motor Y design is used, a separate synchronization-control and anti-jamming analysis must be created.

## Data Flow

Requirements define travel, accuracy, speed, material, synchronization, recognition workflow, sample category logic, and platform constraints. The mechanical design produces mass, stiffness, rack locations, scanning-station coordinates, and travel assumptions for MATLAB/Simulink. Control simulation uses the virtual X/Y/Z model. Final CAD exports and selected animation assets are prepared for Isaac Sim visualization and manufacturing package release.

## Barcode Identification Flow

The Panasonic CX-421-J photoelectric sensor confirms tube presence before barcode capture. Once presence is confirmed, the Cognex DataMan 80 USB fixed-mount image-based barcode reader reads the tube label. The barcode result is used to query the sample category. If barcode reading fails, the category is unknown, or the selected category output area is full, the sample enters an exception review area / manual review station and should not be logged as a completed normal sort.

## Classification Sorting Logic

- Input: 4 x 6 rack with randomly mixed blood collection tube categories.
- Tube variation: different cap colors, labels, barcodes, and possible heights are allowed; bulk piled feeding is not included.
- Classification quantity: frozen as `n = 4`.
- Physical tube boxes/racks: six total, consisting of one 4 x 6 mixed input rack, four 2 x 3 output bins, and one 2 x 3 manual review bin.
- Output bin mapping: Category A/B/C/D each has its own 2 x 3 output bin.
- Manual review: `manual_review_bin`, 2 x 3, receives barcode failures, unknown categories, full-category cases, or abnormal samples.
- Scanning station: one fixed station in the middle work area; it is not counted as a tube box.

Nominal workflow:

```text
Input rack pick -> scanning station -> presence trigger -> barcode/QR read -> category query -> category output bin placement -> exception/manual-review routing when needed
```

Later software simulation should use `sample_manifest.csv` with fields:

```text
tube_id, barcode, cap_color, height_mm, category, input_row, input_col, target_bin, target_row, target_col, scan_status, note
```

## Recommended Physical Layout

- Base plate: 1100 mm x 900 mm x 15 mm.
- X direction: left-right; Y direction: front-back; Z direction: vertical.
- Rear area: mixed 4 x 6 input rack.
- Middle area: scanning station with Panasonic CX-421-J and Cognex DataMan 80 USB.
- Front or front-right area: four 2 x 3 output bins arranged in a 2 x 2 group.
- Front corner or output edge: 2 x 3 `manual_review_bin`.
- Equipment edge: emergency stop and control box for operator access.
- Motion planning and SolidWorks layout must avoid collisions among output bins, scanning hardware, tube racks, and gripper-held tubes.
