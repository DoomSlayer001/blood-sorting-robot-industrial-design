# Stage 7B-7 Servo Robustness S-curve Report

## Scope

- This stage is not CAD modeling, rendering, or presentation animation.
- This stage adds S-curve / jerk-limited reference smoothing, encoder noise, load disturbance, control delay, and repeated robustness trials after Stage 7B-6.
- The current system does not use a camera; input occupancy remains supplied by the internal tube occupancy table.
- Stage 7A-3f XY slider binding remains deferred. It does not affect this abstract control simulation, but it affects final mechanical implementation.

## Why This Stage Is Needed

- Stage 7B-6 Review found zero_error_rate=0.982, which means the first servo tracking model was useful but too idealized.
- Stage 7B-7 checks whether the recommended `balanced_pid` remains acceptable when the reference is smoothed and disturbance/noise/delay are added.

## Model And Parameters

- S-curve reference differs from the original Stage 7B-5 reference by limiting acceleration change with axis-specific jerk limits.
- Jerk limits X/Y/Z: 4000.0 / 4000.0 / 1200.0 mm/s^3.
- Encoder noise std X/Y/Z: 0.05 / 0.05 / 0.03 mm.
- Load disturbance std X/Y/Z: 0.1 / 0.1 / 0.08 mm.
- control_delay_steps=1; z_axis_load_factor=1.25; robustness_trial_count=5.

## Robustness Results

- X RMSE mean / max error / tolerance rate: 0.225 / 3.324 / 0.999747.
- Y RMSE mean / max error / tolerance rate: 0.141 / 2.568 / 0.99989.
- Z RMSE mean / max error / tolerance rate: 0.333 / 0.695 / 1.0.
- Worst axis by max error: x.
- Highest RMS tracking axis: z.
- X has a small number of transition samples above the preferred 2.0 mm tolerance, but remains below the 5.0 mm unacceptable limit.
- balanced_pid remains acceptable under robustness model: yes.
- validation_status=PASS.

## Z Axis Interpretation

- Z uses lower jerk and velocity assumptions and a heavier load factor; in this run it has the highest RMS tracking error, while X has the largest isolated transition error.
- This is consistent with Stage 7B-4 identifying repeated Z motion as the timing bottleneck.

## Limits And Next Work

- This is still a concept-level robustness simulation, not final hardware performance.
- Later calibration needs real motor, driver, encoder, load inertia, friction, payload, sampling period, and actual controller parameters.
- The generated S-curve and disturbed traces can be used as input foundations for later realistic servo, S-curve, and load models.
