# Requirements Specification v1.2

## 1. Device Type

Desktop dual-side gantry three-axis Cartesian blood sample sorting robot.

The main mechanical architecture is no longer a single-side or simple stacked Cartesian platform. The robot uses left and right Y-axis support/guide structures to carry a gantry beam. The X-axis module is mounted on the gantry beam, and the Z-axis module with the electric gripper is mounted on the X-axis carriage.

The confirmed X/Y standard actuator route is MISUMI MSA-628 Guided Belt Drive Actuator. The same MSA-628 CAD/configuration, `MSA-628-B-AB-B1-0750`, is used as separate SolidWorks instances for the left Y-axis module, right Y-axis module, and X-axis module on the gantry. MISUMI MSA-M6S was considered as a higher-rigidity candidate, but it is larger and is not used as the current mainline BOM item.

## 2. Tube Racks

- Input tube rack: 4 x 6, 24 positions.
- Output tube rack: 4 x 6, 24 positions.

## 3. Equipment Size

- Base plate: recommended 1100 mm x 900 mm x 15 mm.
- X direction: left-right direction along the 1100 mm base length.
- Y direction: front-back direction along the 900 mm base width.
- Z direction: vertical up-down direction.
- The larger base is selected to reserve space for the MSA-628 dual Y-axis modules, gantry beam, X-axis MSA-628 module, cable chain, safety cover, and input/output rack reachability.

## 4. Test Tube Specification

- Diameter: 13 mm.
- Height: 75 mm.
- Single tube mass: 15-20 g.

## 5. Accuracy Targets

- Repeatability: +/-0.5 mm.
- Placement error: <=1 mm.

## 6. Speed Targets

- Single-tube sorting cycle: 6-8 s.
- X/Y maximum speed: 200-300 mm/s.
- Z maximum speed: 80-120 mm/s.

## 7. Motion Travel

- X axis: 450-500 mm.
- Y axis: 260-300 mm.
- Z axis: 120 mm.

## 8. Mechanical Axis Definition

- Y axis: left and right MISUMI MSA-628 modules move the gantry beam forward and backward.
- X axis: MISUMI MSA-628 belt-driven linear module mounted on the gantry beam moves the Z module and gripper left and right.
- Z axis: lead-screw lifting module mounted on the X carriage performs vertical pick/place motion.
- End effector: electric two-finger parallel gripper with silicone or TPU soft pads.

## 9. Drive Method

- Y axis: dual-side support/guide structure with mechanical synchronization preferred.
- Recommended Y implementation: single motor plus synchronization shaft or synchronization belt linkage.
- Independent dual Y motors are not preferred. If used later, a separate synchronization-control and anti-jamming risk document is required.
- X/Y axes: MISUMI MSA-628 Guided Belt Drive Actuator, configuration `MSA-628-B-AB-B1-0750`, instantiated separately for left Y, right Y, and X-on-gantry.
- Z axis: lead-screw lifting module, still requiring separate selection. Z does not use MSA-628.

## 10. Control Model

The control model remains a three-axis equivalent model:

```text
q = [x, y, z]
```

The mechanical dual-side Y structure maps to one virtual control axis:

```text
Y_left = Y_right = y
```

MATLAB/Simulink may continue to use a single `y(t)` command for the Y axis, while SolidWorks must show the left/right Y guide structures and gantry beam connection.

## 11. Materials

- Base plate and mounting plates: 6061-T6 aluminum alloy.
- Tube racks: POM or PC.
- Protective cover: transparent PC.
- Fasteners: 304 stainless steel.

## 12. Software Platforms

- SolidWorks: mechanical modeling, assembly, materials, engineering drawings.
- MATLAB/Simulink: kinematics, trajectory planning, PID control, error analysis.
- Isaac Sim: visual presentation, materials, lighting, cameras, sorting demonstration animation.
- Gazebo: not used.
