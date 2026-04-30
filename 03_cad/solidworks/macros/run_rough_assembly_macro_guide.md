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
5. Run `Main`.

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
