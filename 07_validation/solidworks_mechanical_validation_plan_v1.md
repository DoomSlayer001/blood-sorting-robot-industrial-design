# SolidWorks Mechanical Validation Plan v1

## Scope

- This plan does not create new CAD geometry.
- This plan does not render, build PPT material, or enter Isaac Sim.
- This plan prepares the manual SolidWorks validation workflow needed before final CAD acceptance.

## Validation Targets

1. Verify the XY slider binding load path in SolidWorks using true carriage faces and mates.
2. Verify X/Y/Z moving assemblies against racks, tubes, enclosure, cable chain, and control box.
3. Measure critical clearances and record measured values before final acceptance.
4. Keep Stage 7A-3f v1.5 as a preserved correction base, not as an accepted final CAD state.

## Required SolidWorks Workflow

1. Open the preserved v1.5 preview and module STEP files.
2. Identify the original Y slider/carriage mounting face and hole pattern from supplier CAD or manual measurement.
3. Mate adapter plates to the moving carriage face, not to the fixed rail body.
4. Mate X beam end saddles to compact adapter plates.
5. Sweep Y gantry travel, X carriage travel, and Z descend/lift poses.
6. Record all checklist, collision, and clearance results in the validation CSV tables.

## Current Acceptance Boundary

The Stage 7B/7C abstract simulation chain is accepted for planning and control analysis. Final mechanical CAD, exact SolidWorks interference, and Isaac Sim readiness remain deferred until the mechanical validation tables are completed.
