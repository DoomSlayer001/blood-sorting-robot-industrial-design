# SolidWorks Assembly Skeleton Preparation

## Why Custom Hole Positions Cannot Be Frozen Yet

Custom part holes and datums must be driven by real supplier CAD. Without real CAD for the linear modules, gripper, motors, limit switches, and emergency stop, the mounting hole positions, carriage heights, flange planes, cable exits, and motion envelopes are provisional.

Freezing custom part holes from placeholder geometry would create rework risk and could invalidate the industrial assembly.

## Required Skeleton Datums

The SolidWorks top-level assembly skeleton shall include:

- `base datum`
- `world origin`
- `X axis datum`
- `Y axis datum`
- `Z axis datum`
- `input rack datum`
- `output rack datum`
- `gripper centerline`

These datums must align with `01_system_design/assembly_datum_plan.md`.

## Standard CAD Required Before Skeleton Freeze

The assembly skeleton can be started conceptually, but the datum and mounting interface freeze requires real CAD for:

- X-axis module.
- Y-axis module or dual-rail synchronized assembly.
- Z-axis lead screw module.
- Electric parallel gripper.
- X/Y/Z motors.
- Limit switches.
- Emergency stop button.

## Suggested Later Assembly Steps

1. Import real Priority A standard-part CAD into the correct `downloaded/` folders.
2. Verify file names and extensions with `tools/check_standard_cad_files.py`.
3. Update `CAD_download_status_v2.md` and the BOM only after real files exist.
4. Create SolidWorks top assembly datums.
5. Place the base plate as the fixed root reference.
6. Add X/Y/Z modules using supplier mounting faces and centerlines.
7. Add gripper and align the gripper centerline to rack hole coordinates.
8. Add limit switches and emergency stop after panel and axis end locations are known.
9. Only then finalize self-made part holes and engineering drawings.
