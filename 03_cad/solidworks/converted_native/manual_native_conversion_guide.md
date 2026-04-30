# Manual Native Conversion Guide

## Why Manual Conversion Is Required

SolidWorks 2018 can open the project STEP files manually, but opening STEP through Python COM is blocked by template, import diagnostics, and confirmation dialogs. Python cannot reliably answer those dialogs in this environment, so the rough assembly workflow now uses a manual-assisted native CAD cache.

## Target Cache Folders

Save converted files into:

```text
03_cad/solidworks/converted_native/parts/
03_cad/solidworks/converted_native/assemblies/
```

Use `parts/` for files saved as `.SLDPRT` and `assemblies/` for files saved as `.SLDASM`.

## Manual Conversion Steps

1. Open SolidWorks.
2. Use `File > Open`.
3. Select the STEP/STP file listed in `manual_native_conversion_todo.csv`.
4. Confirm any default template dialogs.
5. If Import Diagnostics appears, choose the repair option recommended by SolidWorks.
6. Use `File > Save As`.
7. Save as `.SLDPRT` if the imported model is a part.
8. Save as `.SLDASM` if the imported model is an assembly.
9. Save to the recommended `converted_native/parts` or `converted_native/assemblies` path.
10. Do not delete or overwrite the original STEP/STP supplier file.

## Naming Rules

- Use English names based on `component_name` or the supplier/model name.
- Do not use Chinese characters.
- Do not use spaces.
- Avoid parentheses and special symbols.
- Keep one reusable native file for repeated components such as left/right Y modules or repeated motors.

## Minimum Priority A Set

To generate a meaningful rough assembly, convert at least:

- left and right Y-axis modules.
- X-axis module on gantry.
- Z-axis module.
- input mixed tube rack.
- at least one category output bin, preferably all four.
- manual review bin.
- barcode scanner.
- photoelectric sensor.

Base plate and SMC LEHF20 gripper are already registered in the native cache. The emergency stop placeholder is already available as a native placeholder.

## Rerun

After manual conversion, rerun:

```bash
python 03_cad/solidworks/macros/create_rough_assembly_v1.py
```

The script will read `native_file_mapping.csv` and insert only existing `.SLDPRT` or `.SLDASM` files. If a new native file was added, update the mapping table before rerunning.
