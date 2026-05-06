# Control Box Internal Layout Plan v1

The electrical control box module v1.2 is represented in the integrated CAD preview as a closed rear service cabinet. This is intentional: the running machine should not expose live internal electrical parts in the main equipment view.

## Planned Internal Zones

1. Power supply zone: AC protection and 24V DC power supply on one side of the cabinet.
2. Controller / I/O zone: PLC or MCU controller plus I/O expansion near the service door for diagnostics.
3. Motor driver zone: X, Y-left, Y-right, and Z driver placeholders grouped along DIN rail.
4. Terminal block zone: sensor, safety, and actuator terminal strips near cable gland exits.
5. Safety relay zone: emergency-stop and door-interlock placeholder relay near motor-enable distribution.
6. Grounding terminal zone: protective earth terminal block tied to cabinet, frame, base, and cable shields.
7. Cable gland exit zone: rear or bottom service-side glands, matching the v1.2 closed cabinet model.
8. Service lid / maintenance access: rear-facing service door used for inspection and maintenance.

## Preview Policy

- The integrated v7.3 preview should show the cabinet closed.
- Internal electrical parts are described in documents and may be shown only in a separate service/open-view module if needed later.
- Hiding internals in the integrated preview avoids the tray-like appearance seen in v1.1 and better matches real equipment operation.

## Later Detail Needed

Final work still needs a real electrical architecture, I/O map, terminal numbering, connector selection, grounding plan, service clearances, cable strain relief, mounting holes, and engineering drawings.
