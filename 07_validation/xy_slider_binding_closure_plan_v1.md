# XY Slider Binding Closure Plan v1

## Current Status

Stage 7A-3f v1.5 is `NOT_ACCEPTED_FOR_FINAL_MECHANICAL_VALIDATION`. The files are preserved as a correction base, but they must not be treated as a passed mechanical interface.

## Why v1.5 Did Not Pass

- The X beam end adapter still does not clearly and physically mount to the original moving Y slider/carriage.
- Some connector geometry appears too close to, or at risk of entering, the fixed Y rail body / rail running zone.
- The issue is not the 7B simulation logic. It is a mechanical assembly interface problem.

## Closure Principle

Do not continue relying on blind FreeCAD/CadQuery guesses for the slider mounting face. The next accepted correction must be based on SolidWorks mates, supplier carriage CAD, measured carriage geometry, or manually marked mounting-face coordinates and bounding boxes.

## Required Load Path

```text
original Y slider/carriage mounting face
-> compact adapter plate
-> X beam end saddle
-> X axis module / X beam
```

## Hard Rules

- Connection parts must not mount to the fixed Y rail body.
- Connection parts must not intrude into the rail running zone.
- Do not add a new motor.
- Do not add a new rail.
- Do not use the enclosure frame as structural support for the moving gantry.
- If CAD automation continues, first read or manually define the slider/carriage mounting face coordinates, hole pattern, and bounding box.

## Closure Evidence Required

- SolidWorks mate evidence for left and right carriage-to-adapter interfaces.
- Clearance measurement from adapter plate to fixed rail body and rail running zone.
- Motion sweep evidence across the full Y travel.
- Final interference result showing zero unacceptable overlaps.
