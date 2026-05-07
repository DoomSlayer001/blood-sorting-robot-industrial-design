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

Stage 7A returns to layout modeling for the revised multi-box requirement. v6 remains the single-batch prototype validation, while v7 is the multi-box batch layout prototype generated with CadQuery/OCP on a recommended 1200 x 900 x 15 mm base. The next step is SolidWorks 2026 manual inspection of the v7 STEP, followed by a multi-box coordinate and reachability rerun.

Stage 7A-1 refines v7 after SolidWorks 2026 visual inspection. v7.1 keeps the same multi-box batch concept but improves input/output box accessibility, groups the scan station more clearly, and changes the transparent guard placeholder to show front/top replacement access. SolidWorks 2026 manual inspection confirmed v7.1 as the current recommended multi-box batch layout prototype. The next stage is Stage 7B multi-box coordinate and reachability planning.

Stage 7A-2 completes the v7.1 multi-box layout with electrical, safety, enclosure, cable-chain, wiring, and limit-switch placeholders. v7.2 keeps the accepted input/output/manual-review/scan/gantry anchors and adds a control box, power inlet, motor-driver placeholders, E-stop, transparent guard access openings, cable routes, drag chain, and X/Y/Z limit switch placeholders. The next check is to open the v7.2 STEP in SolidWorks 2026 before continuing animation or Stage 8A control simulation work.

Stage 7A-3a pauses full v7.3 assembly generation and switches to cleaner module-by-module detailed modeling. The first refined module is the enclosure / transparent safety guard: sample-tube curved labels are preserved, but non-tube region label plates are removed from the preview model. The next step is to open `03_cad/freecad_assembly/blood_sorting_robot_v7_3a_enclosure_preview.step` in SolidWorks 2026 and check visibility, access openings, and guard clearances.

Stage 7A-3a v1.1 refines the enclosure after SolidWorks 2026 visual review. The guard is simplified from a display-cover-like form into a lower rectangular transparent safety frame with lighter rear/side panels, simple front access openings, and an open top. SolidWorks 2026 manual inspection accepted v1.1 as the enclosure module for later v7.3 modular whole-machine integration; sample-tube curved labels remain, and non-tube region label plates remain removed.

Stage 7A-3b adds the electrical control box as a separate module and a lightweight integration preview with the accepted enclosure v1.1. The module models a rear service-mounted control box with housing, service lid, DIN rails, controller board, motor drivers, power supply, terminal blocks, rear cable glands, ventilation slots, and mounting brackets. It intentionally avoids full wiring and cable-chain routing; those remain separate later modules.

Stage 7A-3b v1.1 refines the electrical control box after SolidWorks 2026 visual review. The control box is smaller, orthogonally mounted closer to the rear service zone, uses four short rear-facing cable glands, and adds a clearer bottom/rear mounting bracket so it reads as part of the equipment rather than a tilted add-on. The next step is manual inspection of the v1.1 control-box preview before detailed cable-chain and wiring modules.

Stage 7A-3b v1.2 revises the electrical control box again after v1.1 visual review. The preview now uses a closed rear service cabinet with visible door seams, screw markers, ventilation, rear cable glands, and mounting brackets; internal electrical components are not exposed in the integrated machine preview. The next step is manual inspection of the v1.2 control-box preview.

Stage 7A-3b v1.2 has passed SolidWorks 2026 manual inspection. It is accepted as the electrical control box module for later modular v7.3 whole-machine integration; broader material realism will be handled later in a unified Material / Appearance pass.

Stage 7A-3b-0 adds the concept-level electrical architecture needed before cable-chain and wiring CAD. It defines the electrical component list, I/O map, wiring interface table, safety circuit concept, control-box internal layout plan, and cable routing plan without generating new CAD or STEP files. Stage 7A-3c should use the wiring interface table for cable-chain / wiring module modeling.

Stage 7A-3c adds Gantry Mechanical Support and Drive Completion v1 before the cable-chain pass. It supplements the accepted v7.1/v7.3b layout with Y-axis base mounts, Y-carriage adapter plates, X cross-beam supports, an X-axis saddle, engineered X-Z and Z-gripper adapter plates, motor placeholders, drive-transmission placeholders, fastener patterns, and cable-chain mounting tabs. This is still layout-level mechanical completion, not final manufacturing drawings; Stage 7A-3d should add cable chain / wiring based on the reserved tabs and wiring interface table.

Stage 7A-3c v1.1 fixes the gantry mechanical support preview display state after SolidWorks 2026 showed the v1 STEP as initially blank until parts were manually restored. The v1.1 preview uses a compound/multi-solid STEP fallback so the unchanged geometry should open visible by default for manual re-check.

Stage 7A-3c v1.1 has passed SolidWorks 2026 manual inspection. The gantry support/drive preview is visible by default, the added mechanical supports read correctly, cable-chain mounting tabs are reserved, and full cable chain / wiring remain deferred to Stage 7A-3d.

Stage 7A-3d adds the concept-level cable chain / wiring module based on `01_system_design/electrical_wiring_interface_table_v1.csv` and `01_system_design/cable_routing_plan_v1.md`. It models the rear fixed cable tray, control-box gland stubs, main drag chain, moving X/Z cable bundle, sensor/motor cable stubs, clamps, and anchors using the stable compound STEP export approach; material / appearance refinement remains a later pass.

Stage 7A-3d v1.1 cleans up the cable chain / wiring route after manual review. Long straight wire runs are reduced into rear service routing, an L-shaped drag-chain path, and short local round-cable stubs, while preserving the accepted enclosure, closed control box, gantry support, tube labels, and removed non-tube region labels.

Stage 7A-3d v1.2 completes a clean visual cable-management pass. The preview simplifies the visible wiring to a rear main drag chain plus one continuous flexible hose-like moving bundle, while secondary sensor/motor wiring remains logically documented in the wiring route manifest for later detailed engineering.

Stage 7A-3e adds a concept-level two-finger electric parallel gripper module to clarify the end-effector. It replaces the unclear old gripper placeholder in the preview with a Z-axis adapter plate, gripper body, visible left/right jaws, soft tube-contact pads, and pick-geometry documentation.

Stage 7A-3f adds a gantry joint adapter module to make the X/Y gantry load path clearer. It removes the long needle-like TCP reference from the preview while keeping TCP data in CSV, and adds custom Y-carriage adapter plates, X-beam end mounts, side brackets, reinforcement ribs, and fastener patterns.

Stage 7A-3f v1.1 refines the gantry joint physical logic after manual review. The left/right X/Y joints are reorganized into compact mirrored assemblies with main Y-carriage adapter plates, boxed side brackets, X-beam end seats, reinforcement ribs, and clearer fastener patterns so the Y-carriage-to-X-beam load path is easier to read.

Stage 7A-3h refines X/Y drive motor placement and transmission after manual review. Oversized motor placeholders are replaced with compact axis-end motor concepts, visible pulley/idler pairs, simplified timing-belt paths, and belt clamp markers while keeping all box positions unchanged.

Stage 7A-3h-1 corrects the v7.3h direction after manual review. It restores the intended industrial-linear-module logic by using the original downloaded X/Y/Z modules and their implied sliders/carriages as the motion interfaces, hiding unwanted auxiliary drive/motor expressions, and adding only custom binding plates, saddles, adapter markers, and clearance checks while keeping all box positions unchanged.

Stage 7B builds the multi-box coordinate model from v7.1 without generating CAD. It defines 199 task points across 96 input slots, 96 output slots, 6 manual-review slots, and 1 scan-station point, then verifies reachability in the v7.1 planning envelope. The next stage should create the multi-box sample manifest, category hold/resume simulation, and updated trajectory/cycle-time model.

Stage 7C generates a 96-sample multi-box manifest and validates the new batch sorting policy. The simulation covers `category_hold`, `pending_queue`, operator clear/replacement, `category_resume`, and manual-review-full alarm behavior. Normal samples blocked by a full category output box are held and resumed, not routed to manual review; `manual_review` remains reserved for true abnormal samples. The next stage should update multi-box trajectories and cycle-time estimates.

Stage 7D generates multi-box pick-scan-place trajectories from the Stage 7B coordinates and Stage 7C policy simulation. The trajectory set covers the baseline 96-sample run, forced category hold/resume, pending queue release, manual review placement, and manual-review-full `PAUSE_ALARM` behavior without generating new CAD. The next stage should update multi-box cycle time and throughput estimates.

Stage 7E estimates multi-box cycle time and throughput from the Stage 7D trajectories. It compares baseline, category hold/resume, and manual-review-full scenarios, with motion identified as the current dominant bottleneck under the first-pass timing assumptions. The next stage should update the multi-box process animation.

Stage 7F generates multi-box sorting process animations for report and presentation use. The project now covers multi-box CAD layout, coordinate/reachability validation, category hold/resume policy simulation, multi-box trajectories, cycle-time/throughput estimates, and 2D process animation. The next stage should move into Stage 8A kinematics and trajectory-to-control modeling.

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
12. Use v7.1 as the current recommended multi-box batch layout prototype.
13. Revise Stage 6A-6E task planning for the multi-box batch workflow before freezing PID targets, continuing with the multi-box animation update.
14. Create MATLAB/Simulink baseline trajectory and PID models aligned with the stable multi-box workflow and real mechanical masses.

### Stage 7A-3h v1.2 X/Y Slider Binding Patch
- Stage 7A-3h v1.2 patches the X/Y slider binding visual logic after manual review.
- The preview removes the generated oversized external X drive block and does not add auxiliary rails.
- The X beam ends now sit through compact custom adapter plates/end mounts on the original left/right Y slider interfaces; the original X slider remains the Z-axis interface.
- Box layout, enclosure, cable management, closed control box, gripper, tube labels, and non-tube-label removal are preserved.

