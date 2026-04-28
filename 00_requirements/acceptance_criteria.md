# Acceptance Criteria

## 1. Mechanical Design Acceptance

The project shall define a desktop three-axis Cartesian gantry mechanism with X/Y/Z travel matching the frozen requirements and no six-axis robot-arm architecture.

## 2. Standard Parts BOM Acceptance

The standard parts BOM shall identify motors, guide rails, sliders, belt modules, pulleys, lead screw, coupling, bearing blocks, aluminum profiles, drag chain, limit switches, sensors, emergency stop, gripper, and fasteners.

## 3. Material Definition Acceptance

Major custom parts shall include material choices and the reason for selection, including 6061-T6 aluminum, POM/PC, transparent PC, silicone/TPU, and 304 stainless steel.

## 4. SolidWorks Assembly Acceptance

The SolidWorks assembly shall use organized subassemblies, datums, linear-axis references, named components, and importable standard-part CAD where available.

## 5. Interference Check Acceptance

The design shall support interference checks for tube rack clearance, gripper clearance, X/Y/Z travel limits, cable chain routing, and protective cover volume.

## 6. Kinematics Model Acceptance

The kinematics model shall define Cartesian joint variables, forward kinematics, inverse kinematics, travel limits, rack coordinate mapping, safe height, and pick/place height.

## 7. PID Control Simulation Acceptance

MATLAB/Simulink simulation shall include trajectory reference generation, independent axis PID loops, equivalent dynamic parameters, error metrics, and tracking plots.

## 8. Isaac Sim Visualization Acceptance

Isaac Sim assets shall show the robot structure, materials, lighting, cameras, and a sorting demonstration animation. Isaac Sim is not the primary PID validation platform.

## 9. Engineering Drawings And Manufacturing Files Acceptance

The manufacturing package shall include PDF/DWG drawings, STEP release files, BOM release files, assembly instructions, inspection checklist, and manufacturing notes.

## 10. GitHub Version Management Acceptance

The repository shall use `main` as the default branch, Git LFS for large files, clear directory structure, traceable commits, and preserved `legacy_v1` archive.
