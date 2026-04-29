# Stage 3D Pre-Assembly Review Report

## 1. Stage Goal

Stage 3D freezes pre-assembly requirements, scanning assumptions, exception handling rules, gripper strategy, workspace zones, and initial layout coordinates before SolidWorks total assembly begins.

No CAD is generated in this stage. No simulation is run.

## 2. Frozen Requirement Summary

- Project type: mixed blood collection tube automatic identification and classification sorting system.
- Classification count: `n = 4`.
- Input rack: one 4 x 6 mixed rack, 24 positions.
- Output bins: four independent 2 x 3 bins for Category A/B/C/D.
- Manual review bin: one 2 x 3 bin.
- Scanning station: one fixed identification position, not a tube box.
- Tube types: four visual tube types.
- Tube heights: 75 mm and 100 mm.
- X/Y modules: MISUMI MSA-628.
- Z module: MISUMI LS10.
- Gripper: SMC LEHF20.

## 3. Scanning Assumptions

- No tube rotation mechanism is included.
- Tube label is assumed to face the scanner-visible side.
- Manual loading should keep labels visible.
- Industrial upgrades may add tube rotation, multi-angle scanning, or vision-based label pose detection.

## 4. Output Bin Capacity Rules

- Each category output bin holds six tubes.
- Full target bin routes the tube to `manual_review_bin`.
- Full `manual_review_bin` pauses the system and alarms.

## 5. Gripper Strategy

- Grip target: 13 mm tube body.
- Recommended gripping region: 15-25 mm below cap.
- Soft pads: TPU or silicone.
- Force strategy: low-force gripping below the LEHF20 maximum 28 N value.
- Final gripping force is not frozen until tube material and pad design are confirmed.

## 6. Reachability Planning

The base coordinate system uses the center of the 1100 mm x 900 mm base top surface as origin. The initial work areas include:

- rear mixed input rack.
- middle scanning station.
- front/front-right 2 x 2 output bin group.
- front-side manual review bin.
- edge-mounted control box and emergency stop.

## 7. Initial Workspace Layout

Initial coordinates are recorded in `03_cad/solidworks/initial_workspace_layout_table.csv`. They are planning coordinates only, not final engineering hole positions.

Key positions:

- input rack center: (-250, 250, 0) mm.
- scan station center: (80, 80, 0) mm.
- Category A/B/C/D output bins: around (180, -170), (320, -170), (180, -290), (320, -290) mm.
- manual review bin: (-250, -300, 0) mm.
- control box: (-420, -360, 0) mm.
- emergency stop: (-500, -420, 20) mm.

## 8. Pre-Assembly Risks

- Tube label may not face the scanner if manual loading is inconsistent.
- Scanner line-of-sight and tube label orientation must be verified in SolidWorks.
- 100 mm tubes require safe-height clearance review.
- Scanner/sensor brackets may interfere with gripper paths.
- Cable chain sweep envelope may conflict with gantry or brackets.
- Output bins may be too close if gripper approach clearance is insufficient.
- Bin-full logic is currently software-defined; no physical bin-full sensor is frozen.

## 9. Next Stage 4A Tasks

- Build the SolidWorks base layout using initial workspace coordinates.
- Import real standard-part CAD and simplified custom STEP files.
- Place input rack, four output bins, manual review bin, and scan station.
- Check reach envelope and collision clearances.
- Verify scanner line-of-sight and sensor trigger position.
- Update final layout coordinates after SolidWorks validation.
