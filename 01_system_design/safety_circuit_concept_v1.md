# Safety Circuit Concept v1

This document defines a concept-level safety circuit for the blood sorting robot project. It is not a certified safety design or production wiring diagram.

## Core Principles

- Emergency stop is not a normal software button.
- Emergency stop should cut or disable motor power through a safety-rated path in a later detailed design.
- Door / enclosure interlock is currently a placeholder for the transparent guard access opening.
- Safety relay is currently a placeholder for combining emergency stop and door/interlock logic.
- Motor power enable / disable is modeled as a safety output concept, not a final circuit.
- Fault alarm output is a concept signal for buzzer, stack light, HMI, or controller alarm reporting.

## Sorting Logic Safety Boundary

- `manual_review` is only for true abnormal samples.
- `manual_review` is not used for normal samples blocked by a temporarily full output box.
- Output box full triggers `category_hold`, not manual-review routing.
- After the operator clears or replaces the full output box, that category enters `category_resume`.
- Pending normal samples should resume after the relevant output category becomes available.

## Current Limits

- This concept does not claim compliance with medical device electrical standards, machinery safety standards, EMC requirements, or local electrical codes.
- It does not define conductor sizing, redundancy, safety category, performance level, relay model, or certified interlock hardware.
- Later work must include formal safety assessment, risk analysis, certified component selection, and validated wiring diagrams before any physical build.
