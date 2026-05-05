# Project Next Phase Roadmap

## Stage 7A: Multi-box Coordinate Model And Slot Table

- Expand the coordinate model from one input rack to four replaceable 4 x 6 input boxes.
- Replace 2 x 3 category output bins with 4 x 6 category output boxes.
- Keep manual review as 2 x 3.
- Generate multi-box slot tables and reachability checks.
- Preserve v6 and Stage 6A-6E as single-batch prototype validation evidence.

## Stage 7B: Multi-box Sorting Policy Simulation

- Implement category hold when a Category A/B/C/D output box is full.
- Continue processing other non-held categories.
- Add pending queue behavior for held categories.
- Add operator clear/replace and category resume events.
- Keep manual review only for true abnormal samples.

## Stage 7C: Multi-box Trajectory And Cycle-time Update

- Regenerate pick-scan-place trajectories for four input boxes and four 4 x 6 output boxes.
- Recalculate cycle time and throughput for 96-tube batch capacity.
- Quantify the effect of category hold and operator replacement delays.
- Regenerate 2D visualization for the multi-box workflow.

## Stage 8: Kinematics And PID Control Simulation

- Build an X/Y/Z Cartesian kinematic model using the Stage 6A coordinate frame.
- Build equivalent axis dynamics for X, Y, and Z using estimated moving masses and motor/load parameters.
- Generate trapezoidal or S-curve target trajectories for representative pick-scan-place moves.
- Run PID tracking simulations for each axis.
- Output tracking error curves, RMSE, maximum error, settling behavior, and control-input curves.
- Recommended first output: a baseline MATLAB/Python simulation with CSV and plots after the multi-box workflow is stable, before moving to Simulink.

## Phase 9: Mechanical Engineering Detail

- Formalize the X-Z adapter plate with dimensions, hole pattern, material, thickness, and tolerances.
- Formalize barcode scanner and photoelectric sensor brackets.
- Add gripper soft pads and tube-contact assumptions.
- Add deferred hardware: limit switches, cable chain, emergency stop, control box, guards, and mounting accessories.
- Produce self-made part material choices, hole locations, tolerance notes, and engineering drawing candidates.

## Phase 10: Visualization / Digital Twin

- Build a 3D visualization in Isaac Sim or a lighter Blender/Three.js fallback.
- Show gripper pick, scan-station presentation, category placement, and manual-review routing.
- Add camera views, material colors, labels, and a short demonstration video.
- Keep this as visualization unless a physics-grade simulator is explicitly added later.

## Phase 11: Engineering Deliverables

- Release BOM xlsx and material list xlsx.
- Release standard parts procurement list and vendor/source notes.
- Prepare assembly instructions and inspection checklist.
- Prepare final report with CAD, trajectory, timing, exception, control, and visualization evidence.
- Prepare PPT outline, final slides, and defense script.
- Package final deliverables into the manufacturing/report directories with traceable file names.
