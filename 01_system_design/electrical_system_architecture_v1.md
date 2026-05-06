# Electrical System Architecture v1

Stage 7A-3b-0 defines a concept-level electrical architecture for the modular v7.3 layout. It supports later control-box internal refinement, cable-chain modeling, wiring visualization, limit-switch placement, sensor wiring, and final report documentation.

This is not a production electrical design, energized wiring diagram, PCB design, or medical electrical certification claim.

## Power Input Layer

- AC inlet placeholder: rear service side power entry into the closed electrical control box.
- Main power switch: operator/service power isolation placeholder near the control box.
- Fuse / circuit protection: simplified breaker/fuse placeholder upstream of the DC supply.
- 24V DC power supply: main low-voltage supply for controller, sensors, gripper interface, and auxiliary I/O.
- Grounding concept: protective earth bonds the control box, base plate, enclosure frame, gantry metal structure, and cable shield drain points.

## Control Layer

- PLC or MCU controller placeholder: central task controller for sample sorting state logic.
- I/O module placeholder: discrete and communication expansion for sensors, safety placeholders, bin status, and tray presence.
- Communication interface: Ethernet/serial-style barcode scanner link and simplified driver command/status links.
- Control box internal bus concept: internal power, I/O, and communication wiring remains within the closed rear service cabinet.

## Motion Layer

- X axis motor driver: simplified driver for the moving X carriage axis.
- Y-left motor driver: simplified driver for the left Y gantry side.
- Y-right motor driver: simplified driver for the right Y gantry side.
- Z axis motor driver: simplified driver for vertical tool motion.
- Gripper controller: simplified open/close control interface for the SMC electric gripper.

## Sensor Layer

- Barcode scanner: scan station identification device.
- Photoelectric sensor: tube-present / scan-position trigger device.
- X home limit switch: home/reference input placeholder for X axis.
- Y home limit switch: home/reference input placeholder for Y gantry, split as left and right if needed.
- Z home limit switch: home/reference input placeholder for Z axis.
- Bin full detection placeholders: Category A/B/C/D output-box full signals.
- Input tray presence detection placeholders: four replaceable input-box presence/status signals.

## Safety Layer

- Emergency stop: hard safety input placeholder, not a software-only button.
- Door / enclosure interlock placeholder: guard-door state input for later safety design.
- Safety relay placeholder: concept block for emergency stop and interlock chain.
- Motor power enable / disable: safety-controlled output path to enable or inhibit motor drive power.
- Fault alarm output: stack light / buzzer / HMI alarm placeholder.

## Wiring Layer

- Fixed wiring zone: rear service area, control box interior, base-frame sensor routes.
- Moving cable chain zone: Y/X/Z moving members and tool-carriage wiring bundle.
- Sensor wiring: scan station, bin full sensors, input tray sensors, limit switches.
- Motor wiring: driver-to-motor power and feedback placeholders.
- Power wiring: AC input, 24V distribution, protected power distribution.
- Communication wiring: barcode scanner link and simplified driver/controller links.
- Grounding wiring: control box, base plate, frame, enclosure, gantry, and shield drain routes.

## Design Boundary

The architecture is intended for course-level system definition. Final conductor sizing, protection coordination, medical/safety compliance, EMC, cable ratings, connector pinouts, and production drawings require later formal engineering.
