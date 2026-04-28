# System Architecture

## Overview

The system is an industrial-style desktop three-axis Cartesian blood sample sorting robot. It moves blood tubes from a 4 x 6 input rack to a 4 x 6 output rack using a gantry mechanism, an electric two-finger gripper, and coordinated X/Y/Z motion.

## Mechanical Modules

- Base and frame module: 600 mm x 400 mm base plate, aluminum supports, mounting datums.
- Y-axis gantry module: dual-side belt-driven linear motion supporting the bridge.
- X-axis bridge module: belt-driven cross axis mounted on the gantry.
- Z-axis lifting module: lead-screw vertical axis carrying the gripper.
- End-effector module: electric parallel gripper with silicone or TPU pads.
- Sample handling module: input rack, output rack, tube geometry, safe approach zones.
- Safety and enclosure module: protective cover, emergency stop, limit switches, cable chain.

## Platform Responsibilities

- SolidWorks owns mechanical geometry, assembly, materials, drawings, interference checks, and manufacturing exports.
- MATLAB/Simulink owns kinematics, trajectory planning, PID control, motor sizing support, and error analysis.
- Isaac Sim owns visual presentation, material appearance, cameras, lighting, and demonstration animation.
- GitHub owns version history, review checkpoints, release tags, and large-file traceability through Git LFS.

## Data Flow

Requirements define travel, accuracy, speed, material, and platform constraints. The mechanical design produces mass and travel assumptions for MATLAB/Simulink. Control simulation produces trajectory and timing results for design review. Final CAD exports and selected animation assets are prepared for Isaac Sim visualization and manufacturing package release.
