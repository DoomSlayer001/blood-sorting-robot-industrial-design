# Run Rough Assembly Macro Guide

## Python COM Script

Run from the repository root:

```bash
python 03_cad/solidworks/macros/create_rough_assembly_v1.py
```

The script reads:

```text
03_cad/solidworks/component_placement_table_v1.csv
03_cad/solidworks/current_cad_inventory_for_assembly.csv
```

It writes:

```text
03_cad/solidworks/assembly/rough_assembly_v1_log.md
03_cad/solidworks/assembly/blood_sorting_robot_rough_layout_v1.SLDASM
```

The `.SLDASM` file is created only if SolidWorks COM automation succeeds.

## Stage 4B-4 Auto Retry Script

After repairing the SolidWorks default template settings, the optional retry script can be run:

```bash
python 03_cad/solidworks/macros/create_rough_assembly_auto_retry_v1.py
```

This script first performs a smoke test with:

```text
03_cad/custom_parts/base_plate/base_plate_1100x900x15.step
03_cad/standard_parts/downloaded/gripper/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.step
```

If the smoke test succeeds, it attempts batch STEP/STP conversion and then creates the rough assembly. If the smoke test fails, it stops before batch conversion and preserves the manual native cache workflow.

The current 4B-4 retry result showed SolidWorks COM and templates were available, but `OpenDoc6` still failed for STEP import with SolidWorks error code `2097152`. This means the recommended route remains manual-assisted native conversion unless the local SolidWorks import automation settings are further adjusted.

If `manual_native_conversion_todo.csv` is open in Excel or another program, the auto retry script writes a fallback list:

```text
03_cad/solidworks/converted_native/manual_native_conversion_todo_autoretry.csv
```

## Native Conversion Workflow

Stage 4B-2 changes the rough assembly strategy:

1. Resolve each CAD path from `component_placement_table_v1.csv`.
2. Convert `.step` and `.stp` files to native SolidWorks files.
3. Insert only `.SLDPRT` or `.SLDASM` files into the rough assembly.

Conversion outputs are intended to live under:

```text
03_cad/solidworks/converted_native/parts/
03_cad/solidworks/converted_native/assemblies/
```

Conversion reports are written to:

```text
03_cad/solidworks/conversion_reports/step_to_native_conversion_report.csv
03_cad/solidworks/conversion_reports/step_to_native_conversion_report.md
```

The script first tests:

```text
03_cad/custom_parts/base_plate/base_plate_1100x900x15.step
```

If this base plate STEP cannot be opened and saved as native SolidWorks CAD, batch conversion stops so the project does not produce misleading empty or partial assemblies.

## Assembly Template Configuration

The Python script first reads:

```text
03_cad/solidworks/macros/solidworks_template_config.json
```

Current selected assembly template:

```text
C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2018\templates\gb_assembly.asmdot
```

If this file is missing or the project is moved to another machine, edit `assembly_template_path` in the JSON config. Use a real `.asmdot` file only; do not invent a path.

If SolidWorks has no default assembly template, configure one manually:

1. Open SolidWorks.
2. Go to `Tools > Options > System Options > Default Templates`.
3. Set the assembly template to a valid `.asmdot`.
4. Close and reopen SolidWorks if COM automation still sees the old configuration.
5. Rerun the Python script.

If component insertion still fails after template creation, open one STEP file manually in SolidWorks to confirm import settings and then run the VBA macro from inside SolidWorks.

## Manual STEP Import Diagnostic

If Python conversion fails:

1. Open SolidWorks manually.
2. Use `File > Open`.
3. Select `03_cad/custom_parts/base_plate/base_plate_1100x900x15.step`.
4. Confirm the STEP imports as a part.
5. Save it as `base_plate_1100x900x15.SLDPRT`.
6. Create a new assembly from `gb_assembly.asmdot`.
7. Use `Insert Components` to insert the saved SLDPRT.
8. If this succeeds manually, adjust the macro for the local SolidWorks 2018 COM import settings or run the VBA fallback from inside SolidWorks.

## Recommended Stage 4B-3 Workflow

The current recommended route is manual-assisted native cache conversion:

1. Use `03_cad/solidworks/converted_native/manual_native_conversion_todo.csv`.
2. Open each Priority A STEP/STP manually in SolidWorks.
3. Accept template and Import Diagnostics dialogs.
4. Save as `.SLDPRT` or `.SLDASM` under `converted_native/parts` or `converted_native/assemblies`.
5. Update `03_cad/solidworks/converted_native/native_file_mapping.csv`.
6. Rerun the Python macro.

The Python macro now inserts only registered native `.SLDPRT/.SLDASM` files. It intentionally does not continue trying to open STEP files through COM.

## VBA Fallback Macro

Use this file inside SolidWorks if Python COM automation is unavailable or needs local adjustment:

```text
03_cad/solidworks/macros/create_rough_assembly_v1.vba
```

Recommended steps:

1. Open SolidWorks.
2. Use `Tools > Macro > New` or `Tools > Macro > Edit`.
3. Load or paste the VBA macro.
4. Confirm `REPO_ROOT` matches the local project path.
5. If `step_to_native_conversion_report.csv` contains valid native output paths, update the macro or placement table to use those native paths.
6. Run `Main`.

## Pre-Run Checks

- Confirm `03_cad/solidworks/component_placement_table_v1.csv` exists.
- Confirm every non-`TBD` CAD path in the placement table exists.
- Open several CAD files manually in SolidWorks if import problems appear.
- Confirm SolidWorks document units are interpreted as millimeters.
- Confirm this is only a rough coordinate layout, not the final assembly.

## Post-Run Checks

Open the rough assembly and review it with:

```text
03_cad/solidworks/first_rough_assembly_manual_checklist.md
```

Check:

- top view overall layout screenshot.
- front view gantry height screenshot.
- side view Y-axis and scan-station screenshot.
- left and right Y axes are parallel.
- X axis spans the Y-axis modules.
- Z axis points vertically.
- gripper points downward and aligns with the tube centerline.
- scanner faces the tube label side.
- photoelectric sensor can detect the tube at the scan station.
- input rack, output bins, and manual review bin are reachable.
- cable chain sweep does not collide with racks, scanner, or brackets.

If a component direction is wrong, update the relevant `rotation_x_deg`, `rotation_y_deg`, or `rotation_z_deg` field in `component_placement_table_v1.csv`, then rerun the macro.
