# Stage 4B SolidWorks Rough Assembly Macro Report

## 1. Stage Goal

Stage 4B generates the first SolidWorks rough assembly macro workflow. The goal is a coordinate-based Level 2 review assembly, not a final engineering assembly.

## 2. Why This Is Rough Assembly Only

The first macro does not add final mates, does not identify mounting faces, and does not select hole patterns. Imported supplier CAD and placeholder custom parts need manual orientation and spacing checks before any bracket, hole, or mate strategy is frozen.

## 3. Input Tables

The macro workflow uses:

```text
03_cad/solidworks/component_placement_table_v1.csv
03_cad/solidworks/current_cad_inventory_for_assembly.csv
```

The placement table is the primary input for component path, instance name, approximate position, rotation, and manual check notes.

## 4. Generated Macro Files

```text
03_cad/solidworks/macros/create_rough_assembly_v1.py
03_cad/solidworks/macros/create_rough_assembly_v1.vba
03_cad/solidworks/macros/run_rough_assembly_macro_guide.md
```

The Python script is the preferred automation route when SolidWorks COM works. The VBA macro is a SolidWorks-internal fallback.

## 5. SolidWorks Automation Environment Check

- Operating system: Windows 11.
- Python: available.
- `win32com.client`: available.
- SolidWorks COM ProgID: `SldWorks.Application` dispatch succeeded.
- SolidWorks executable detected earlier at `C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe`.

## 6. Macro Run Result

The Python COM script was executed once:

```text
python 03_cad/solidworks/macros/create_rough_assembly_v1.py
```

Result:

- SolidWorks COM dispatch succeeded.
- CSV precheck found 26 usable component CAD paths.
- Two scenario wildcard rows were skipped intentionally:
  - `sample_tube_instances_input_demo`
  - `sample_tube_instances_output_demo`
- `.SLDASM` was not generated because the local SolidWorks installation does not have a default assembly template configured.

Diagnostic log:

```text
03_cad/solidworks/assembly/rough_assembly_v1_log.md
```

Expected output path after template configuration:

```text
03_cad/solidworks/assembly/blood_sorting_robot_rough_layout_v1.SLDASM
```

## 7. Manual Next Step

Configure a default SolidWorks assembly template, or edit the Python/VBA macro to point to a known `.asmdot` template. Then rerun the macro and inspect the assembly using:

```text
03_cad/solidworks/first_rough_assembly_manual_checklist.md
```

## 8. Stage 4C Preview

Stage 4C should:

- run the macro inside a fully configured SolidWorks environment.
- save the rough `.SLDASM`.
- capture top/front/side and local-detail screenshots.
- check Y-axis parallelism, X-axis span, Z/gripper orientation, scanner line-of-sight, sensor trigger position, rack reachability, and cable-chain sweep.
- revise `component_placement_table_v1.csv` if orientation or spacing is wrong.
