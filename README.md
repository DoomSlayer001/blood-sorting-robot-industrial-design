# Industrial Three-Axis Blood Sorting Robot Design

This repository is the industrial-design mainline for a desktop three-axis Cartesian blood sample sorting robot.

## Project Goal

Design an industrial-style digital engineering package for a hospital blood sample sorting robot, including mechanical system requirements, SolidWorks-oriented CAD planning, MATLAB/Simulink control simulation planning, Isaac Sim visualization planning, BOM templates, manufacturing package structure, and version management.

This repository is not the previous concept model as the main project. The previous automatically generated concept model is preserved under `legacy_v1/` for reference only.

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

The current repository still does not generate new CAD models and does not run simulations. Supplier CAD is not marked as downloaded unless a real file exists in the standard-parts CAD workspace.

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

1. Download or manually collect real Priority A supplier CAD where permitted.
2. Record each CAD file in `03_cad/standard_parts/CAD_download_status_v2.md`.
3. Define SolidWorks assembly skeleton, datums, axes, and interface envelopes using real standard-part interfaces.
4. Freeze custom-part interface boundaries before detailed self-made part modeling.
5. Create MATLAB/Simulink baseline trajectory and PID models aligned with real mechanical masses after CAD mass properties become available.
6. Prepare Isaac Sim asset import and visualization conventions after SolidWorks assembly structure is stable.
