# Pre-Assembly Requirement Freeze

## 1. Final Task Definition

This project is a mixed blood collection tube automatic identification and classification sorting system.

Frozen requirements:

- Mixed blood collection tubes are batch-loaded into the input tube rack.
- Input positions are random and categories are mixed.
- Every tube is vertically inserted in the rack; loose or piled feeding is out of scope.
- The robot picks tubes one by one.
- The robot moves each tube to the scanning station.
- Panasonic CX-421-J detects tube presence and triggers barcode reading.
- Cognex DataMan 80 USB reads the tube label barcode, 2D code, or QR code.
- The system maps the barcode result to a sample category.
- The robot places the tube into the corresponding category output bin.
- Abnormal samples enter `manual_review_bin`.

## 2. Frozen Task Scale

| item | frozen value |
|---|---|
| classification count | `n = 4` |
| input rack | one 4 x 6 rack, 24 positions |
| output bins | four bins, one each for Category A/B/C/D |
| output bin capacity | 2 x 3, six tubes per category |
| manual review bin | one 2 x 3 bin, six positions |
| scanning station | one station, not counted as a tube box |
| visual tube types | four |
| tube heights | 75 mm and 100 mm |

## 3. Scanning Assumptions

Frozen assumptions for the course-design mainline:

- The project does not include a tube rotation mechanism for barcode alignment.
- The tube label is assumed to face the scanner-visible side during scanning.
- Manual loading should ensure labels face outward or remain visible to the scanner.
- Barcode/QR marks in the CAD scene are visual placeholders, not readable machine-vision targets.

Future industrial upgrade options:

- tube rotation scanning mechanism.
- multi-angle barcode readers.
- vision-based label pose detection.
- automatic retry and rotation logic.

## 4. Output Bin Capacity Rules

- Each category output bin holds six tubes.
- If the target category bin is full, the sample is routed to `manual_review_bin`.
- If `manual_review_bin` is full, the system pauses and alarms.
- Full-bin detection is a software state in the current design stage; physical bin-full sensing is not frozen.

## 5. Tube Height Handling Rules

- `sample_manifest.csv` uses `height_mm` to distinguish 75 mm and 100 mm tubes.
- Z-axis pick and place heights must be adjusted according to `height_mm`.
- X/Y transfer uses a unified safe height that clears the tallest expected tube, cap, rack wall, scanner bracket, and gripper.
- Later MATLAB/Simulink trajectory planning must include height-dependent pick/place Z coordinates.

## 6. Gripper Strategy

- The gripped object is the 13 mm tube body.
- Recommended grip location: tube body region about 15-25 mm below the cap.
- TPU or silicone soft pads are required for the gripper fingers.
- Low-force gripping should be used to avoid damaging the tube.
- SMC LEHF20 maximum gripping force is 28 N, but real operating force should be below the maximum and tuned after tube material and pad design are confirmed.

## 7. Safety And Exception Rules

- Emergency stop is used for manual emergency shutdown.
- OMRON D4N switches are used for X/Y/Z homing and travel limit detection.
- Software limits prevent commands outside the planned work envelope.
- `scan_failed`, `barcode_unknown`, `target_bin_full`, `gripper_pick_failed`, and `gripper_place_failed` enter the exception handling flow.
- Motion limit trigger stops motion immediately.
- `manual_review_bin_full` pauses the system and raises an alarm.

## 8. Assumptions Versus Frozen Requirements

Frozen requirements:

- `n = 4`.
- one 4 x 6 mixed input rack.
- four independent 2 x 3 category output bins.
- one 2 x 3 manual review bin.
- one scanning station.
- no Gazebo route.
- SolidWorks + MATLAB/Simulink + Isaac Sim route.

Current assumptions:

- labels face the scanner-visible side.
- no tube rotation mechanism.
- bin-full state is tracked in software.
- exact pick/place Z offsets will be refined in SolidWorks and MATLAB/Simulink.
