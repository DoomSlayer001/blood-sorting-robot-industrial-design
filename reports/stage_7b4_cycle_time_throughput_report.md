# Stage 7B-4 Trajectory-Based Cycle Time and Throughput Simulation Report

## Scope

- This stage does not use a camera.
- Cycle time is estimated from Stage 7B-3 trajectory segments and Stage 7B-2 state-machine outcomes.
- No CAD modeling, rendering, Stage 7A edits, `legacy_v1` edits, or XY slider binding fixes are performed.
- Stage 7A-3f XY slider binding remains deferred; it does not affect abstract cycle-time estimation but does affect final mechanical validation.

## Timing Model

- The timing model is concept-level and not final measured hardware performance.
- XY speed=350.0 mm/s; Z speed=120.0 mm/s.
- Grip close/open=0.6 / 0.5 s.
- Scan wait=1.0 s.
- Category hold operator service=20.0 s; manual_review alarm pause=10.0 s.

## Scenario Results

- Baseline: robot_active_time_s=574.861, total_elapsed_time_s=574.861, robot_active throughput=432.104 samples/hour, elapsed throughput=432.104 samples/hour.
- forced_category_A_full: operator_wait_time_s=20.0, elapsed throughput=417.577 samples/hour, throughput impact vs baseline elapsed=3.362%.
- manual_review_limited_capacity: completed_sample_count=67, operator_wait_time_s=20.0, elapsed throughput=417.556 samples/hour.
- pick_failure_test: completed_sample_count=68, pick_failed_count=2, elapsed throughput=425.366 samples/hour.

## Bottleneck

- Baseline bottleneck stage: z_motion.
- Robot active throughput excludes operator service delay; elapsed throughput includes output service and manual_review alarm pauses.

## Downstream Use

- These estimates support report tables, animation timing, and later Isaac Sim presentation setup.
- Future calibration must use real motor speed/acceleration, Z-axis travel tuning, gripper timing, and scanner response measurements.
- validation_status=PASS
