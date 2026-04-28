# System Architecture

## Overview

The system is an industrial-style desktop dual-side gantry three-axis Cartesian blood sample sorting robot. It moves blood tubes from a 4 x 6 input rack to a 4 x 6 output rack using synchronized left/right Y-axis gantry motion, an X-axis module mounted on the gantry beam, a Z-axis lifting module, and an electric two-finger gripper.

The previous single-axis-combination Cartesian layout is no longer the mainline architecture.

## Mechanical Modules

1. Base and frame module: 800 mm x 500 mm x 12 mm temporary base plate, frame mounting datums, rack locating features, and safety cover interfaces.
2. Left Y-axis support/drive module: left-side Y guide/support and preferred mechanical synchronization drive side.
3. Right Y-axis support/guide module: right-side Y guide/support synchronized with the left side.
4. Gantry beam module: cross beam connecting left and right Y carriages and carrying the X-axis module.
5. X-axis transverse motion module: belt-driven linear module mounted on the gantry beam, moving the Z module and gripper left/right.
6. Z-axis lifting module: lead-screw vertical axis mounted on the X carriage.
7. Electric gripper module: electric two-finger parallel gripper with silicone or TPU soft pads.
8. Input/output tube rack module: two 4 x 6 racks with locating pins and coordinate mapping.
9. Control box and safety module: controller enclosure, emergency stop, limit switches, software limits, and safety cover.
10. Cable chain and wiring management module: moving cable routing for gantry, X carriage, Z module, gripper, and sensors.
11. Isaac Sim visualization module: material, lighting, cameras, and demonstration animation after SolidWorks assembly stabilizes.

## Platform Responsibilities

- SolidWorks owns dual-side gantry geometry, assembly, materials, drawings, interference checks, gantry beam stiffness planning, and manufacturing exports.
- MATLAB/Simulink owns kinematics, trajectory planning, virtual X/Y/Z PID control, motor sizing support, and error analysis.
- Isaac Sim owns visual presentation, material appearance, cameras, lighting, and demonstration animation.
- GitHub owns version history, review checkpoints, release tags, and large-file traceability through Git LFS.

## Control Mapping

The mechanical Y axis has left and right synchronized structures. The control model remains one virtual Y axis:

```text
Y_left = Y_right = y
```

If a future dual-motor Y design is used, a separate synchronization-control and anti-jamming analysis must be created.

## Data Flow

Requirements define travel, accuracy, speed, material, synchronization, and platform constraints. The mechanical design produces mass, stiffness, and travel assumptions for MATLAB/Simulink. Control simulation uses the virtual X/Y/Z model. Final CAD exports and selected animation assets are prepared for Isaac Sim visualization and manufacturing package release.
