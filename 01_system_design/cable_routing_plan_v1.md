# Cable Routing Plan v1

This plan defines concept-level cable routing before Stage 7A-3c cable-chain / wiring CAD modeling. It should guide routing geometry without becoming a production harness drawing.

## Fixed Rear Service Route

- Runs from the closed rear control box along the rear service side.
- Serves power entry, enclosure/door interlock placeholder, rear fixed sensors, alarm/status placeholder, and Y-axis fixed-side wiring.
- Keeps cables away from the front operator access openings.

## Base Fixed Sensor Route

- Runs from the rear control box down to base-mounted input/output sensors.
- Covers input tray presence sensors and Category A/B/C/D bin full sensors.
- Should stay below or beside tray edges, not across the tops of replaceable boxes.

## Moving Gantry Cable Chain Route

- Runs from the rear service side to the moving gantry and then toward the X/Z carriage.
- Carries X motor wiring, Z motor wiring, gripper control, Z limit, X limit, and future tool-side I/O.
- Stage 7A-3c will model the physical cable-chain placeholder using this route.

## Scanner / Photoelectric Route

- Runs from barcode scanner and photoelectric sensor brackets back to the control box through fixed scan-station routing.
- Should not cross the input box replacement path or the scan tube holder.

## Grounding Route

- Bonds control box, base plate, aluminum frame, enclosure frame, and gantry metal structure.
- Cable shield drain points should terminate at the grounding terminal concept in the control box.

## Service Access Principle

- Wires must not pass through input-box replacement space.
- Wires must not obstruct output-box replacement or manual_review removal.
- Wires must not enter gripper travel or tube transfer paths.
- Wires must not cross over tube racks where they could interfere with pick/place operation.
- Moving cables must be constrained by a cable chain or guided bundle.
