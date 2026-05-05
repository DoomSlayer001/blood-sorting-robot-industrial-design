# Industrial Three-Axis Blood Sorting Robot Design

This repository is the industrial-design mainline for a desktop dual-side gantry three-axis Cartesian mixed blood collection tube identification and classification sorting system.

## Project Goal

Design an industrial-style digital engineering package for a hospital mixed blood collection tube identification and classification sorting robot, including mechanical system requirements, SolidWorks-oriented CAD planning, MATLAB/Simulink control simulation planning, Isaac Sim visualization planning, BOM templates, manufacturing package structure, and version management.

The system is not only a tube transfer mechanism. It identifies mixed tubes from a 4 x 6 input rack, reads 1D/2D barcode or QR code labels using a fixed Cognex DataMan 80 USB reader triggered by a Panasonic CX-421-J photoelectric sensor, queries the sample category, and places each tube into its corresponding output bin. Barcode failures, unknown categories, full target bins, or abnormal samples are routed to a `manual_review_bin`.

This repository is not the previous concept model as the main project. The previous automatically generated concept model is preserved under `legacy_v1/` for reference only.

The main mechanical route has switched from the earlier single-axis-combination Cartesian platform to a dual-side gantry structure: left and right Y-axis supports move the gantry beam, the X-axis module is mounted on the gantry beam, and the Z-axis screw module carries the electric parallel gripper. The old single-axis-combination scheme is no longer the mainline.

The confirmed X/Y actuator series is MISUMI MSA-628 Guided Belt Drive Actuator. The same `MSA-628-B-AB-B1-0750` CAD/configuration is used as separate SolidWorks instances for `left_y_axis_module`, `right_y_axis_module`, and `x_axis_module_on_gantry`. MISUMI MSA-M6S was considered as a higher-rigidity candidate but is larger and is not used in the current mainline BOM. The Z axis remains a separately selected lead-screw lifting module.

## Frozen Technical Route

- SolidWorks: industrial mechanical modeling, assembly, materials, drawings, interference checks.
- MATLAB/Simulink: kinematics, trajectory planning, PID control, error analysis.
- Isaac Sim: visualization, materials, lighting, cameras, sorting demonstration animation.
- Gazebo: not used.
- GitHub: version control and collaboration.
- Git LFS: large CAD, simulation, media, USD, archive, and release files.

## Directory Structure

```text
00_requirements/              Frozen requirements, constraints, acceptance criteria
01_system_design/             Architecture, axis layout, materials, safety, platform plan
02_bom/                       BOM and material templates
03_cad/                       SolidWorks, STEP, standard/custom parts, drawings, exports
04_simulation/                MATLAB, Simulink, SolidWorks Motion, Isaac Sim workspaces
05_control/                   Trajectory planning, PID, motor sizing, control analysis
06_results/                   Figures, animations, videos, logs
07_report/                    Report, presentation outline, defense script
08_manufacturing_package/     Drawing release, STEP release, BOM release, assembly notes
legacy_v1/                    Archived v1 concept model
```

## Current Stage

- Stage 0: requirements freeze, completed.
- Stage 1: industrial standard-parts selection plan, completed.
- Stage 2: real CAD download workflow and custom-part interface definition, completed.
- Stage 3A: Priority A real CAD download and intake preparation, completed.
- Stage 3A-2: Priority A CAD automatic-download feasibility assessment, completed.
- Architecture switch: dual-side gantry Cartesian robot route, completed.
- Stage 3C: mixed input rack, four category output bins, manual review bin, sample tube models, and `sample_manifest.csv` prepared locally.
- Stage 3D: pre-assembly requirements, scan-station assumptions, failure handling, reachability, and initial workspace layout frozen locally.
- Stage 4A: SolidWorks first rough assembly plan prepared locally.
- Stage 4A-1: rough-assembly placeholder custom parts prepared locally.
- Stage 4B: SolidWorks first rough assembly macro generated locally.

The current repository does not download CAD, does not run simulations, and does not modify `legacy_v1`. New CAD generated in Stage 4A-1 is limited to simple rough-assembly custom placeholders or initial self-made parts, not final production drawings. Supplier CAD is not marked as downloaded unless a real file exists in the standard-parts CAD workspace.

Future CAD download and SolidWorks assembly work will follow the dual-side gantry layout, especially the MSA-628 left Y-axis module, MSA-628 right Y-axis module, Y-axis mechanical synchronization mechanism, MSA-628 gantry-mounted X-axis module, Z-axis screw module, and electric parallel gripper.

## Sorting Task Definition

- Input rack: 4 x 6, 24 positions, vertically inserted mixed blood collection tubes.
- Tube variation: different cap colors, labels, barcodes, and possible heights are allowed.
- Recognition: Panasonic CX-421-J confirms tube presence at the scanning station and triggers Cognex DataMan 80 USB barcode/QR reading.
- Classification quantity: frozen as `n = 4`.
- Physical tube boxes/racks: six total.
- Input: one 4 x 6 mixed input rack, 24 positions.
- Output: four separate 2 x 3 output bins for Category A/B/C/D, six positions per bin.
- Manual review: one 2 x 3 `manual_review_bin` for failed scans, unknown categories, full categories, or abnormal samples.
- Scanning station: one fixed station, not counted as a tube box, where the gripper holds the tube for Panasonic-triggered Cognex barcode/QR reading.

Nominal workflow:

```text
Input rack pick -> scanning station -> photoelectric trigger -> barcode/QR read -> category lookup -> category output bin placement -> manual review when abnormal
```

Later simulation data should use `sample_manifest.csv`:

```text
tube_id, barcode, cap_color, height_mm, category, input_row, input_col, target_bin, target_row, target_col, scan_status, note
```

The frozen layout plan is documented in `01_system_design/sorting_task_layout_plan.md`, and the manifest schema is documented in `04_simulation/sample_data/sample_manifest_schema.md`.

Stage 3C generated simplified STEP models for four blood collection tube variants, one 4 x 6 mixed input rack, four 2 x 3 category output bins, and one 2 x 3 manual review bin. It also generated `04_simulation/sample_data/sample_manifest.csv` with 24 mixed input samples. These outputs are for course design, SolidWorks assembly validation, and visualization planning; tube labels and barcodes are visual placeholders.

Stage 3D freezes the pre-assembly assumptions before SolidWorks layout:

- tube labels are assumed to face the scanner-visible side.
- no tube rotation barcode-alignment mechanism is included in the current mainline.
- each category output bin holds six tubes.
- full category bin, scan failure, unknown category, or abnormal sample routes to `manual_review_bin`.
- full `manual_review_bin` pauses the system and alarms.
- 75 mm and 100 mm tubes require height-aware Z pick/place values and a unified safe transfer height.
- initial workspace coordinates are recorded in `03_cad/solidworks/initial_workspace_layout_table.csv`.

Stage 4A prepares the first SolidWorks rough assembly plan without directly generating the final assembly. It uses CAD inventory and component placement CSV tables to constrain Codex/SolidWorks assembly work and reduce the risk of a disorganized imported assembly. The next stage should generate a rough assembly macro and then perform manual screenshot-based checks.

Stage 4A-1 fills the missing rough-assembly components required by that macro plan: `base_plate_1100x900x15.step`, `scan_station_reference_block.step`, `control_box_placeholder_160x120x80.step`, and `y_axis_sync_shaft_placeholder.step`. The base plate is an initial no-hole custom part, while the scan station, control box, and Y-axis synchronization shaft are placeholders. The next stage can enter Stage 4B: generate the SolidWorks rough assembly macro from the updated inventory and placement tables.

Stage 4B generates the SolidWorks rough assembly automation files. The Python COM script and VBA fallback macro only perform coordinate placement from `component_placement_table_v1.csv`; they do not add final mates, identify mounting faces, or select hole patterns. The generated rough layout is intended for manual screenshot checks and does not represent the final engineering assembly.

Stage 4B-3 switches the rough assembly route to a manual-assisted native CAD cache. SolidWorks 2018 can open the STEP files manually, but Python COM cannot reliably handle the template and Import Diagnostics dialogs. The current rough assembly macro therefore reads `03_cad/solidworks/converted_native/native_file_mapping.csv` and inserts only existing `.SLDPRT` or `.SLDASM` files. Priority A files should be manually converted using `manual_native_conversion_todo.csv` before rerunning the macro.

Stage 4C audit found that earlier rough assembly files can exist on disk and still open as empty SolidWorks assemblies. File existence, file size, or a script loop count is therefore no longer accepted as a success criterion. Stage 4C-Redo defines a verified rough assembly standard based on component count, referenced documents, component names, and a close/reopen check.

Stage 4C-Redo attempts a verified STEP-based rough assembly using original STEP/STP CAD and SolidWorks 2026. The smoke test currently fails because SolidWorks COM insertion calls return without increasing assembly component count, so no new verified rough assembly is accepted yet. The next SolidWorks automation step must solve the insertion API behavior before screenshot review.

Stage 4C-Internal-VBA pauses external Python COM as the main assembly creation route. A user-recorded internal SolidWorks VBA macro proved that `OpenDoc6`, `ActivateDoc3`, `AddComponent5`, and `SetTransformAndSolve2` can insert a native component when run inside SolidWorks. The project now includes a minimum verified internal VBA macro and a full rough-assembly VBA skeleton. The next action is to run `03_cad/solidworks/macros/create_minimal_verified_rough_assembly_2026_internal_vba.vba` inside SolidWorks 2026 and verify real FeatureManager components after save, close, and reopen.

Stage 4C-Internal-VBA minimum validation is now complete. The manually run SolidWorks 2026 internal VBA macro generated `03_cad/solidworks/assembly/minimal_verified_internal_macro_rough_layout_2026_v1.SLDASM`, and FeatureManager showed six real components after save, close, and reopen. The next step is to run or refine the full verified internal VBA rough assembly macro.

Stage 4C full internal VBA assembly validation is also complete. The manually run full macro generated `03_cad/solidworks/assembly/full_verified_internal_macro_rough_layout_2026_v1.SLDASM`, and FeatureManager contains real components after save, close, and reopen. This validates the internal VBA insertion route, but the current layout is not final: components are stacked, the gantry structure is not correctly expanded, and reused output bin geometry/naming needs correction. The next stage is 4D: assembly placement correction and transform audit.

Stage 4D prepares a corrected SolidWorks 2026 internal VBA rough layout. It adds `component_placement_table_4d_corrected.csv`, a new corrected VBA macro with Euler rotation support, and a copy-to-SWP module. The 4D pass focuses on component mapping, distinct instance names, rotation matrix handling, and a cleaner main-body layout. Cable chain, Y-axis sync placeholder, emergency stop, control box, motors, limit switches, and sample tube demo instances are deferred until the gantry and sample-bin layout is correct.

Stage 4E prepares a transform and bounding box audit for the non-empty 4D assembly. The current 4D result is classified as valid component insertion but incorrect layout. The next success standard is no longer only "components exist"; component positions, dominant axes, and bounding boxes must match the target coordinate plan. The audit macro exports measured component transforms and bounding boxes for the next correction pass.

Stage 4F switches the rough-layout automation route from SolidWorks COM / internal VBA to CadQuery/OCP STEP assembly generation. FreeCAD is not available in the current local environment, while CadQuery/OCP can import STEP/STP files, apply coordinate/rotation placements, and export a combined STEP for SolidWorks 2026 manual inspection. `03_cad/freecad_assembly/blood_sorting_robot_cadquery_rough_layout_v2.step` has been opened successfully in SolidWorks 2026, with the base plate, dual Y axes, X axis, Z axis, gripper, input rack, output bins, barcode scanner, and photoelectric sensor visible. This validates the CadQuery/OCP automatic rough-assembly route for the current stage; SolidWorks remains the manual inspection tool.

Stage 4F v5 adds a color-manifest fallback and an automated interference/clearance audit. `03_cad/freecad_assembly/blood_sorting_robot_cadquery_rough_layout_v5.step` has been opened in SolidWorks 2026: colors are visible, demo tubes are readable, and no obvious overlap was observed. v5 is the current recommended automated rough assembly layout.

Stage 4F v5.1 is a presentation refinement based on v5. It adds simple scanner and photoelectric sensor brackets plus a clearer X-Z adapter plate while keeping CadQuery/OCP as the main automated assembly route and SolidWorks 2026 as the inspection/screenshot tool. SolidWorks COM and FreeCAD remain outside the main route.

Stage 4F v5.2 is a small alignment-correction pass based on v5.1. It keeps the recommended CadQuery/OCP route and the v5/v5.1 main layout while aligning the X-Z adapter/Z-axis/gripper tool chain and regrouping the scan station before SolidWorks 2026 manual inspection.

Stage 4F v6 refactors the rough-layout generator into module and anchor-based CadQuery/OCP assembly logic. It keeps SolidWorks 2026 as the final inspection and screenshot tool while reducing absolute-coordinate drift in the tool chain, scan station, input rack tubes, output-bin tubes, and label plates. SolidWorks 2026 manual inspection confirmed that v6 opens normally, colors are visible, tubes align to slot centers, the scan station is coherent, and the Z-axis/adapter/gripper tool chain is clear. v6 is the current recommended modular CadQuery rough assembly layout; SolidWorks COM and FreeCAD remain outside the current main route.

Stage 6A starts the non-CAD task-planning layer after the validated v6 rough layout. It defines sorting coordinates, rack/slot tables, pick/place height rules, the sorting state machine, sample-driven routing, and an initial reachability check without generating new CAD.

Stage 6B generates the first pick-scan-place trajectory sequence for all 24 manifest samples. The project has moved from CAD rough assembly into sorting motion planning: waypoint CSVs, workspace checks, motion summaries, and a 2D top-view path figure are generated without creating new CAD.

Stage 6C estimates cycle time and throughput from the Stage 6B trajectory waypoints. The project now has four validation layers: rough CAD layout, task coordinates/reachability, pick-scan-place paths, and first-pass timing/throughput analysis.

Stage 6D simulates failure handling and exception flow for the sorting task. The project now covers rough CAD layout, reachability validation, trajectory paths, cycle-time estimation, and exception handling before moving to visualization and controller-interface planning.

Stage 6E generates a 2D top-view sorting process animation for report and presentation use. The project now has CAD rough layout, task paths, cycle-time estimates, exception-flow simulation, and a process visualization layer.

Requirements traceability review confirms that v6 + Stage 6A-6E are a rough assembly and task-validation milestone, not final project completion. The next major work should close the gap toward PID/dynamics simulation first, then mechanical detail, digital-twin visualization, and final engineering deliverables.

Stage 6R revises the target workflow to a multi-box batch sorting requirement: four replaceable 4 x 6 input boxes, four replaceable 4 x 6 category output boxes, and one 2 x 3 manual review bin reserved only for true abnormal samples. v6 and Stage 6A-6E are retained as single-batch prototype validation; the next stage should update the coordinate model, sorting policy, trajectories, cycle time, and animation for the multi-box workflow before PID/dynamics simulation.

## Git LFS Usage

Git LFS is enabled for CAD, SolidWorks, USD, media, and archive files:

```bash
git lfs install
git lfs track
git lfs ls-files
```

Before committing large files, confirm that files such as `*.step`, `*.sldasm`, `*.usd`, `*.gif`, and `*.mp4` are tracked by LFS.

## Legacy v1

`legacy_v1/blood_sorting_robot_full_auto/` contains the previous course-design concept model and generated outputs. It is retained for traceability and comparison, but it is not the industrial-design mainline.

## Next Stage Plan

1. Manually download or import Priority A real standard-part CAD around the dual-side gantry architecture where permitted.
2. Use `02_bom/priority_a_auto_download_feasibility.csv` and `02_bom/priority_a_manual_download_queue.md` to track which sources require manual download.
3. Run `python tools/check_standard_cad_files.py` after CAD files are placed in `03_cad/standard_parts/downloaded/`.
4. Record each verified CAD file in `03_cad/standard_parts/CAD_download_status_v2.md`.
5. Use CadQuery/OCP as the main automated rough-layout generator and export combined STEP files for SolidWorks 2026 inspection.
6. Keep SolidWorks COM and FreeCAD out of the current rough-layout automation path unless a later stage explicitly reopens them.
7. Refine the CadQuery/OCP layout with small coordinate corrections, starting with Z-axis and gripper height adjustment.
8. Add an X-Z adapter plate concept to explain the Z-axis mounting relationship.
9. Open each accepted CadQuery/OCP STEP in SolidWorks 2026 and capture the required overall, top, front, side, gripper/tube, scan station, and output-bin screenshots.
10. Verify reach, collision, scanner line-of-sight, photoelectric trigger position, cable chain sweep envelope, and emergency-stop accessibility.
11. Define custom-part interface boundaries before detailed self-made part engineering drawings.
12. Revise Stage 6A-6E task planning for the multi-box batch workflow before freezing PID targets.
13. Create MATLAB/Simulink baseline trajectory and PID models aligned with the stable multi-box workflow and real mechanical masses.
