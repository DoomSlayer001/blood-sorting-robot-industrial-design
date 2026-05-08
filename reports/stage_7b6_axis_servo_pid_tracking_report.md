# Stage 7B-6 Axis Servo / PID Tracking Report

## Scope

- This stage is not CAD modeling, rendering, or presentation animation.
- This stage is a concept-level servo tracking simulation based on the accepted Stage 7B-5 reference trajectory.
- No Stage 7A files, `legacy_v1` files, CAD geometry, or XY slider binding files are modified.
- The current system does not use a camera; input occupancy is supplied by the internal tube occupancy table.

## Control Model

- X, Y, and Z are simulated as independent discrete-time servo axes.
- The controller uses PID position error terms plus the reference velocity as feedforward command input.
- The plant is a simplified first-order position servo response; actual velocity and acceleration are derived as concept-level indicators.
- X/Y share the same parameter family; Z has separate parameters because Stage 7B-4 identified `z_motion` as the bottleneck stage.

## Parameter Comparison

- conservative_pid overall RMSE: 3.718 mm; overshoot risk: low.
- balanced_pid overall RMSE: 0.063 mm; overshoot risk: low.
- aggressive_pid overall RMSE: 0.028 mm; overshoot risk: medium.
- Recommended parameter_set: `balanced_pid`.

## Recommended Tracking Results

- X RMSE / max error: 0.082 / 1.354 mm; status=PASS.
- Y RMSE / max error: 0.054 / 1.112 mm; status=PASS.
- Z RMSE / max error: 0.048 / 0.402 mm; status=PASS.
- Overall within_tolerance_rate: 1.0.
- Settling behavior X/Y/Z: settled_within_tolerance / settled_within_tolerance / settled_within_tolerance.
- Overshoot event count X/Y/Z: 0 / 0 / 0.
- Z axis remains the hardest tracked axis: no.

## Stage 7B-4 Consistency

- The Z axis uses tighter tolerance and lower velocity limits than X/Y, so it remains the most sensitive axis for tracking.
- This is consistent with Stage 7B-4, where repeated Z descend/lift operations made `z_motion` the timing bottleneck.

## Limits And Next Work

- This result is not final real hardware control performance.
- Future calibration needs real motor, drive, encoder, load inertia, friction, payload, mechanical compliance, and controller-cycle parameters.
- Stage 7A-3f XY slider binding remains deferred. It does not affect this abstract control simulation, but it does affect final mechanical implementation and physical validation.
- validation_status=PASS
