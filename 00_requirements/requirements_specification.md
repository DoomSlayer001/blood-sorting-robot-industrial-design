# Requirements Specification v1.2

## 1. Device Type

Desktop dual-side gantry three-axis Cartesian mixed blood collection tube identification and classification sorting system.

The system is not a simple tube transfer device. It automatically identifies mixed blood collection tubes placed in the input rack, reads each tube label barcode or QR code, queries the sample category, and sorts the tube into the corresponding output category area. Tubes with failed barcode reading, unknown category, full target category, or other abnormal conditions are routed to a manual review area.

The main mechanical architecture is no longer a single-side or simple stacked Cartesian platform. The robot uses left and right Y-axis support/guide structures to carry a gantry beam. The X-axis module is mounted on the gantry beam, and the Z-axis module with the electric gripper is mounted on the X-axis carriage.

The confirmed X/Y standard actuator route is MISUMI MSA-628 Guided Belt Drive Actuator. The same MSA-628 CAD/configuration, `MSA-628-B-AB-B1-0750`, is used as separate SolidWorks instances for the left Y-axis module, right Y-axis module, and X-axis module on the gantry. MISUMI MSA-M6S was considered as a higher-rigidity candidate, but it is larger and is not used as the current mainline BOM item.

## 2. Tube Rack And Sorting Bin Layout

- Input tube rack: 4 x 6, 24 positions.
- Input tubes are randomly mixed by sample category.
- Tubes may have different cap colors, labels, barcodes, and heights.
- Tubes are inserted vertically in the input rack. Loose, piled, or bulk random feeding is outside the current scope.
- Classification quantity is frozen as `n = 4`.
- Physical tube box/rack count is frozen as six:
  - one mixed input tube rack, 4 x 6, 24 positions.
  - four category output bins, one each for Category A/B/C/D, each 2 x 3 with six positions.
  - one `manual_review_bin`, 2 x 3 with six positions.
- The fixed scanning station is not counted as a tube box. It is a gripper-held scanning position paired with the Panasonic CX-421-J photoelectric sensor and Cognex DataMan 80 USB barcode reader.

## 3. Equipment Size

- Base plate: recommended 1100 mm x 900 mm x 15 mm.
- X direction: left-right direction along the 1100 mm base length.
- Y direction: front-back direction along the 900 mm base width.
- Z direction: vertical up-down direction.
- The larger base is selected to reserve space for the MSA-628 dual Y-axis modules, gantry beam, X-axis MSA-628 module, cable chain, safety cover, mixed input rack, scanning station, four category output bins, and manual review bin.
- Layout principle: the mixed input rack is placed in the rear area, the scanning station is placed in the middle area, the four output bins are arranged in a 2 x 2 group in the front or front-right area, and the manual review bin is placed at a front corner or near the output-bin edge.
- Emergency stop and control box should be placed near the equipment edge for easy operator access.

## 4. Test Tube Specification

- Diameter: 13 mm.
- Nominal height: 75 mm.
- Mixed input tubes may have different heights; the gripper and safe-height strategy must reserve clearance for the expected height range.
- Single tube mass: 15-20 g.

## 5. Accuracy Targets

- Repeatability: +/-0.5 mm.
- Placement error: <=1 mm.

## 6. Speed Targets

- Single-tube sorting cycle: 6-8 s.
- X/Y maximum speed: 200-300 mm/s.
- Z maximum speed: 80-120 mm/s.

## 7. Motion Travel

- X axis: 450-500 mm.
- Y axis: 260-300 mm.
- Z axis: 120 mm.

## 8. Mechanical Axis Definition

- Y axis: left and right MISUMI MSA-628 modules move the gantry beam forward and backward.
- X axis: MISUMI MSA-628 belt-driven linear module mounted on the gantry beam moves the Z module and gripper left and right.
- Z axis: lead-screw lifting module mounted on the X carriage performs vertical pick/place motion.
- End effector: electric two-finger parallel gripper with silicone or TPU soft pads.

## 9. Drive Method

- Y axis: dual-side support/guide structure with mechanical synchronization preferred.
- Recommended Y implementation: single motor plus synchronization shaft or synchronization belt linkage.
- Independent dual Y motors are not preferred. If used later, a separate synchronization-control and anti-jamming risk document is required.
- X/Y axes: MISUMI MSA-628 Guided Belt Drive Actuator, configuration `MSA-628-B-AB-B1-0750`, instantiated separately for left Y, right Y, and X-on-gantry.
- Z axis: lead-screw lifting module, still requiring separate selection. Z does not use MSA-628.

## 10. Control Model

The control model remains a three-axis equivalent model:

```text
q = [x, y, z]
```

The mechanical dual-side Y structure maps to one virtual control axis:

```text
Y_left = Y_right = y
```

MATLAB/Simulink may continue to use a single `y(t)` command for the Y axis, while SolidWorks must show the left/right Y guide structures and gantry beam connection.

## 10.1 Tube Presence And Barcode Reading

- Panasonic CX-421-J photoelectric sensor: detects whether a tube has reached the pick/place or scanning station and provides the scan trigger condition.
- Cognex DataMan 80 USB fixed-mount image-based barcode reader: reads 1D/2D barcode or QR code labels on blood tubes after tube presence is confirmed.
- Barcode recognition result: used to query the sample category before the robot selects the output target slot.
- Exception handling: if barcode reading fails, the category is unknown, or the target category area is full, the sample is routed to an exception review area / manual review station instead of being treated as successfully sorted.
- Scanning assumption: the current mainline does not include a tube rotation/alignment mechanism; tube labels are assumed to face the scanner-visible side through manual loading or fixture orientation.

## 10.2 Classification Sorting Workflow

The frozen nominal workflow is:

```text
Pick tube from mixed input rack -> move to scanning station -> photoelectric presence detection -> Cognex barcode reader reads tube label -> query sample category -> place tube into matching output bin -> route failed/unknown/full/abnormal samples to manual_review_bin
```

Output classification is frozen as:

- Category A: one 2 x 3 output bin.
- Category B: one 2 x 3 output bin.
- Category C: one 2 x 3 output bin.
- Category D: one 2 x 3 output bin.

The `manual_review_bin` is a 2 x 3 bin for barcode failure, unknown category, full category output bin, or other abnormal samples.

Capacity and pause rules:

- each category output bin capacity is six tubes.
- if the target category bin is full, the sample enters `manual_review_bin`.
- if `manual_review_bin` is full, the system pauses and alarms.

Height handling:

- `sample_manifest.csv` records `height_mm`.
- Z-axis pick/place height is adjusted for 75 mm and 100 mm tubes.
- X/Y transfer uses a unified safe height above the tallest tube and all rack/scanner features.

## 10.3 Sample Manifest Data

Later software simulation should use `sample_manifest.csv` to describe the mixed input tubes and target classification result.

Recommended fields:

```text
tube_id, barcode, cap_color, height_mm, category, input_row, input_col, target_rack, target_slot
```

The frozen schema is defined in `04_simulation/sample_data/sample_manifest_schema.md`, and the Stage 3C sample table is available at `04_simulation/sample_data/sample_manifest.csv`.

## 10.4 Modeling Impact

Future CAD and visualization stages need mixed blood collection tube models with varied cap colors, labels, barcode/QR label areas, and possible height variants. The mechanical layout must include the mixed input tube rack, four separate category output bins, `manual_review_bin`, and fixed scanning station. Robot motion must avoid interference between output bins, scanner/sensor brackets, racks, and gripper-held tubes.

## 10.5 Stage 3D Pre-Assembly Freeze

Stage 3D freezes the pre-assembly assumptions and initial workspace planning before SolidWorks assembly:

- scanning label-facing assumption and no tube rotation mechanism.
- output bin and manual review capacity rules.
- gripper strategy for 13 mm tube body gripping with TPU/silicone pads.
- initial base coordinate system and workspace area placement.
- exception handling and system pause rules.

The detailed documents are:

- `01_system_design/pre_assembly_requirement_freeze.md`
- `01_system_design/scan_station_definition.md`
- `01_system_design/failure_handling_logic.md`
- `01_system_design/reachability_and_workspace_plan.md`

## 11. Materials

- Base plate and mounting plates: 6061-T6 aluminum alloy.
- Tube racks: POM or PC.
- Protective cover: transparent PC.
- Fasteners: 304 stainless steel.

## 12. Software Platforms

- SolidWorks: mechanical modeling, assembly, materials, engineering drawings.
- MATLAB/Simulink: kinematics, trajectory planning, PID control, error analysis.
- Isaac Sim: visual presentation, materials, lighting, cameras, sorting demonstration animation.
- Gazebo: not used.
