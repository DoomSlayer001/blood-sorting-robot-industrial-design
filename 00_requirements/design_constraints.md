# Design Constraints

1. Do not use a six-axis robot arm.
2. The mechanical architecture must be a three-axis Cartesian Robot.
3. Standard parts should preferentially use real manufacturer CAD.
4. Fallback models are temporary placeholders only.
5. Custom parts must define material, manufacturing method, hole locations, and assembly datums.
6. The control model may use simplified dynamics, but parameters must correspond logically to the mechanical design.
7. Isaac Sim is used only as the visual presentation platform, not as the primary PID verification platform.
8. Before production, a professional engineer must review dimensions, tolerances, strength, safety, and manufacturability.
