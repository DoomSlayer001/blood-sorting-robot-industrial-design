# Preliminary Motor Sizing

## Purpose

This document defines the first-pass motor sizing logic for the industrial three-axis blood sorting robot. It does not finalize motor models. Final motor selection requires real moving mass, actual actuator friction, belt/pulley dimensions, screw lead, efficiency, desired acceleration, and supplier torque-speed curves.

## Parameters To Consider

- Moving mass of each axis.
- Target velocity and acceleration.
- Guide friction and cable-chain drag.
- Belt pitch, pulley pitch diameter, belt stiffness, and belt tension.
- Screw lead, screw efficiency, nut friction, and backlash.
- Z-axis gravity load and holding requirement.
- Gripper mass, tube mass, adapter plate mass, and sensor bracket mass.
- Safety factor for peak acceleration and emergency stop cases.
- Motor torque-speed curve at required speed.
- Driver voltage/current limits and thermal margin.

## X/Y Axis Force Estimate

For horizontal belt-driven axes, the required linear force is estimated as:

```text
F = m*a + F_friction
```

Where:

- `F` is required axis thrust in N.
- `m` is moving mass in kg.
- `a` is target acceleration in m/s^2.
- `F_friction` includes guide friction, belt losses, cable drag, and preload effects.

For early sizing, use a safety factor after estimating thrust:

```text
F_design = SF * F
```

Typical first-pass `SF` may be 1.5-2.0 until real axis data is known.

## Z Axis Force Estimate

For the vertical lead-screw axis, gravity must be included:

```text
Fz = m*a + m*g + F_friction
```

Where:

- `Fz` is required vertical thrust in N.
- `m` is the lifted mass in kg.
- `a` is Z acceleration in m/s^2.
- `g = 9.81 m/s^2`.
- `F_friction` includes screw/nut friction, guide friction, and cable drag.

Holding torque and fail-safe behavior must be reviewed separately. A brake, self-locking screw, counterbalance, or controlled power-off behavior may be required.

## Lead Screw Torque Estimate

The screw torque can be estimated as:

```text
T = F * lead / (2*pi*eta)
```

Where:

- `T` is screw input torque in N*m.
- `F` is axial thrust in N.
- `lead` is screw lead in m/rev.
- `eta` is screw efficiency.

Lower efficiency increases torque demand but may improve holding behavior. Ball screws are efficient but may back-drive more easily; trapezoidal screws can have higher friction and better passive holding.

## Timing Belt Torque Logic

For belt-driven X/Y axes, estimate motor-side torque from required belt force:

```text
T_pulley = F_design * r_pulley / eta_belt
```

Where:

- `T_pulley` is torque at the drive pulley in N*m.
- `F_design` is design thrust after safety factor.
- `r_pulley` is pulley pitch radius in m.
- `eta_belt` is belt-drive efficiency.

If a reducer is used:

```text
T_motor = T_pulley / (gear_ratio * eta_reducer)
```

Motor speed must also be checked:

```text
motor_rpm = linear_speed / pulley_circumference * 60 * gear_ratio
```

The selected motor must provide required torque at this speed, not only holding torque at zero speed.

## Current Stage Limitation

Stage 1 only defines preliminary sizing equations and selection logic. It does not finalize motors. Final motor selection will be made after:

1. Real actuator CAD and mass properties are available.
2. SolidWorks moving assemblies are defined.
3. Belt pulley radius and screw lead are frozen.
4. Required acceleration profile is defined in MATLAB/Simulink.
5. Supplier torque-speed curves and driver voltage/current limits are reviewed.
