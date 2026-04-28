# Acceptance Criteria

## 1. Mechanical Design Acceptance

The project shall define a desktop dual-side gantry three-axis Cartesian mechanism with X/Y/Z travel matching the frozen requirements and no six-axis robot-arm architecture.

The left and right Y-axis structures must be arranged symmetrically around the working area.

## 2. Gantry Reach Acceptance

The gantry beam and X-axis module must cover the input and output tube rack areas. The gripper centerline must be able to reach all rack hole positions within the defined safe height, pick height, and place height strategy.

## 3. Y-Axis Synchronization Acceptance

The Y-axis synchronization strategy must be documented. Mechanical synchronization is preferred. If dual Y motors are used later, the design must include synchronization control, skew detection, and anti-jamming risk analysis.

## 4. Standard Parts BOM Acceptance

The standard parts BOM shall identify left/right Y-axis modules or guide assemblies, Y-axis synchronization mechanism, gantry beam mounting hardware, X-axis module on gantry, Z-axis module, motors, guide rails, sliders, belt modules, pulleys, lead screw, coupling, bearing blocks, aluminum profiles, drag chain, limit switches, sensors, emergency stop, gripper, and fasteners.

## 5. Material Definition Acceptance

Major custom parts shall include material choices and the reason for selection, including 6061-T6 aluminum, POM/PC, transparent PC, silicone/TPU, and 304 stainless steel.

## 6. SolidWorks Assembly Acceptance

The SolidWorks assembly shall show the left Y-axis structure, right Y-axis structure, gantry beam connection, X-axis module mounted on the gantry beam, Z-axis module mounted on the X carriage, and gripper centerline.

## 7. Interference Check Acceptance

The design shall support interference checks for tube rack clearance, gripper clearance, gantry beam travel, left/right Y-axis clearance, X/Y/Z travel limits, cable chain routing, and protective cover volume.

## 8. Kinematics Model Acceptance

The kinematics model shall define Cartesian joint variables, forward kinematics, inverse kinematics, travel limits, rack coordinate mapping, safe height, and pick/place height.

The control model may treat the dual-side Y structure as one virtual axis with:

```text
Y_left = Y_right = y
```

The documentation must explain the mapping between the mechanical dual-side Y axis and the virtual Y control axis.

## 9. PID Control Simulation Acceptance

MATLAB/Simulink simulation shall include trajectory reference generation, independent virtual X/Y/Z axis PID loops, equivalent dynamic parameters, error metrics, and tracking plots. The Y-axis equivalent mass must later reflect the gantry beam, X module, Z module, gripper, and moving cable mass.

## 10. Isaac Sim Visualization Acceptance

Isaac Sim assets shall show the dual-side gantry structure, materials, lighting, cameras, and a sorting demonstration animation. Isaac Sim is not the primary PID validation platform.

## 11. Engineering Drawings And Manufacturing Files Acceptance

The manufacturing package shall include PDF/DWG drawings, STEP release files, BOM release files, assembly instructions, inspection checklist, and manufacturing notes.

## 12. GitHub Version Management Acceptance

The repository shall use `main` as the default branch, Git LFS for large files, clear directory structure, traceable commits, and preserved `legacy_v1` archive.
