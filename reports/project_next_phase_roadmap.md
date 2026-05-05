# Project Next Phase Roadmap

## Phase 7: Kinematics And PID Control Simulation

- Build an X/Y/Z Cartesian kinematic model using the Stage 6A coordinate frame.
- Build equivalent axis dynamics for X, Y, and Z using estimated moving masses and motor/load parameters.
- Generate trapezoidal or S-curve target trajectories for representative pick-scan-place moves.
- Run PID tracking simulations for each axis.
- Output tracking error curves, RMSE, maximum error, settling behavior, and control-input curves.
- Recommended first output: a baseline MATLAB/Python simulation with CSV and plots before moving to Simulink.

## Phase 8: Mechanical Engineering Detail

- Formalize the X-Z adapter plate with dimensions, hole pattern, material, thickness, and tolerances.
- Formalize barcode scanner and photoelectric sensor brackets.
- Add gripper soft pads and tube-contact assumptions.
- Add deferred hardware: limit switches, cable chain, emergency stop, control box, guards, and mounting accessories.
- Produce self-made part material choices, hole locations, tolerance notes, and engineering drawing candidates.

## Phase 9: Visualization / Digital Twin

- Build a 3D visualization in Isaac Sim or a lighter Blender/Three.js fallback.
- Show gripper pick, scan-station presentation, category placement, and manual-review routing.
- Add camera views, material colors, labels, and a short demonstration video.
- Keep this as visualization unless a physics-grade simulator is explicitly added later.

## Phase 10: Engineering Deliverables

- Release BOM xlsx and material list xlsx.
- Release standard parts procurement list and vendor/source notes.
- Prepare assembly instructions and inspection checklist.
- Prepare final report with CAD, trajectory, timing, exception, control, and visualization evidence.
- Prepare PPT outline, final slides, and defense script.
- Package final deliverables into the manufacturing/report directories with traceable file names.
