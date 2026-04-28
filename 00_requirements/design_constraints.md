# Design Constraints

1. Do not use a six-axis robot arm.
2. The mechanical architecture must be a three-axis Cartesian Robot.
3. The main mechanical structure is a dual-side gantry architecture with left and right Y-axis support/guide structures.
4. The Y-axis dual-side structure must explicitly consider synchronization.
5. Mechanical synchronization for the Y axis is preferred, using a single motor plus synchronization shaft or synchronization belt linkage where feasible.
6. If a dual-motor Y-axis solution is used later, it must include a separate synchronization-control and anti-jamming risk analysis.
7. The gantry beam must be checked for stiffness and deflection because it carries the X-axis module, Z-axis module, gripper, cable load, and tube load.
8. The gantry beam, Y-axis support parts, and Z-axis connection plate are key strength-check objects.
9. Standard parts should preferentially use real manufacturer CAD.
10. Fallback models are temporary placeholders only.
11. Custom parts must define material, manufacturing method, hole locations, and assembly datums.
12. The control model may use simplified three-axis dynamics, but parameters must correspond logically to the dual-side gantry mechanical design.
13. Isaac Sim is used only as the visual presentation platform, not as the primary PID verification platform.
14. Gazebo is not used.
15. Before production, a professional engineer must review dimensions, tolerances, strength, safety, synchronization, and manufacturability.
