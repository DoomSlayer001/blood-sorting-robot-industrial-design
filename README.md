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

The current repository still does not generate new CAD models, does not download CAD, does not run simulations, and does not modify `legacy_v1`. Supplier CAD is not marked as downloaded unless a real file exists in the standard-parts CAD workspace.

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
5. Enter SolidWorks total assembly layout freeze using real standard-part interfaces, tube bin STEP files, sample tube scene objects, scanning station datums, and the frozen 1100 mm x 900 mm base layout.
6. Define custom-part interface boundaries before detailed self-made part engineering drawings.
7. Create MATLAB/Simulink baseline trajectory and PID models aligned with real mechanical masses after CAD mass properties become available.
