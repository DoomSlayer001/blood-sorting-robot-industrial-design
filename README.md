# Industrial Three-Axis Blood Sorting Robot Design

This repository is the industrial-design mainline for a desktop dual-side gantry three-axis Cartesian blood sample sorting robot.

## Project Goal

Design an industrial-style digital engineering package for a hospital blood sample sorting robot, including mechanical system requirements, SolidWorks-oriented CAD planning, MATLAB/Simulink control simulation planning, Isaac Sim visualization planning, BOM templates, manufacturing package structure, and version management.

This repository is not the previous concept model as the main project. The previous automatically generated concept model is preserved under `legacy_v1/` for reference only.

The main mechanical route has switched from the earlier single-axis-combination Cartesian platform to a dual-side gantry structure: left and right Y-axis supports move the gantry beam, the X-axis module is mounted on the gantry beam, and the Z-axis screw module carries the electric parallel gripper. The old single-axis-combination scheme is no longer the mainline.

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

The current repository still does not generate new CAD models, does not download CAD, does not run simulations, and does not modify `legacy_v1`. Supplier CAD is not marked as downloaded unless a real file exists in the standard-parts CAD workspace.

Future CAD download and SolidWorks assembly work will follow the dual-side gantry layout, especially the left Y-axis module, right Y-axis module, Y-axis mechanical synchronization mechanism, gantry-mounted X-axis module, Z-axis screw module, and electric parallel gripper.

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
5. Define SolidWorks assembly skeleton, datums, axes, and interface envelopes using real standard-part interfaces.
6. Freeze custom-part interface boundaries before detailed self-made part modeling.
7. Create MATLAB/Simulink baseline trajectory and PID models aligned with real mechanical masses after CAD mass properties become available.
