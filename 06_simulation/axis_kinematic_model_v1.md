# Axis Kinematic Model v1

This model is an abstract Cartesian motion model. It does not depend on the unresolved Stage 7A-3f XY physical slider binding geometry. The XY mechanical connection is a deferred mechanical integration issue and does not block task-level simulation.

## Y Axis

- Role: gantry longitudinal motion.
- Direction: positive Y follows the left/right Y axis travel convention.
- Stroke assumption: conservative placeholder, derived from rack and box reach envelope.
- Home position: rear or service-safe gantry home, `y_mm = 0` placeholder.
- Soft limit: configured from validated rack/output coverage before final simulation.
- Position state variable: `y_position_mm`.

## X Axis

- Role: cross-beam slider motion.
- Direction: positive X follows the cross-beam axis from input side toward output side.
- Stroke assumption: conservative placeholder covering input racks, scan area, output boxes, and manual review area.
- Home position: central or service-safe X carriage home, `x_mm = 0` placeholder.
- Soft limit: configured from validated workspace width.
- Position state variable: `x_position_mm`.

## Z Axis

- Role: vertical gripper motion.
- Direction: positive Z upward; pick/place descends by reducing Z.
- Stroke assumption: conservative placeholder covering tube top, grip depth, and safe travel height.
- Home position: raised safe height.
- Soft limit: `z_safe_mm`, `z_pick_mm`, and `z_place_mm` from task table or rack definitions.
- Position state variable: `z_position_mm`.

## Motion Command Format

```text
command_id, axis, target_position_mm, velocity_mm_s, acceleration_mm_s2, tolerance_mm
```

Commands are accepted only after task-state and collision-envelope checks pass.

