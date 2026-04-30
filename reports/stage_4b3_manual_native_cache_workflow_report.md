# Stage 4B-3 Manual Native Cache Workflow Report

## 1. Manual Verification Conclusion

Manual SolidWorks verification showed that the CAD files are not corrupted:

- `base_plate_1100x900x15.step` can be opened manually.
- base plate can be saved as `.SLDPRT`.
- SMC LEHF20 gripper STEP can be opened manually and saved.
- native `.SLDPRT/.SLDASM` files can be inserted into a new SolidWorks assembly.

## 2. COM Automation Failure Analysis

Python COM automation failed because SolidWorks 2018 presents template and Import Diagnostics dialogs during STEP import. The COM script cannot reliably answer those dialogs, so automatic STEP conversion is not dependable on this workstation.

## 3. Workflow Change

The rough assembly workflow now uses a manual-assisted native CAD cache:

1. manually open STEP/STP files in SolidWorks.
2. save them as `.SLDPRT` or `.SLDASM`.
3. register them in `native_file_mapping.csv`.
4. run `create_rough_assembly_v1.py`, which inserts only native files.

The script no longer attempts automatic STEP/STP conversion.

## 4. Registered Native Files

Current native mapping summary:

- native files registered and present: 3.
- manual conversion todo rows: 25.
- Priority A manual conversion todo rows: 12.

Registered native files:

- `base_plate` -> `03_cad/solidworks/converted_native/parts/base_plate_1100x900x15.SLDPRT`
- `electric_parallel_gripper` -> `03_cad/solidworks/converted_native/assemblies/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.SLDASM`
- `emergency_stop_placeholder` -> `03_cad/standard_parts/placeholders/safety/emergency_stop_visual_placeholder_v1.sldprt`

The manually saved source native files were also preserved:

- `03_cad/custom_parts/base_plate/base_plate_1100x900x15.SLDPRT`
- `03_cad/standard_parts/downloaded/gripper/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.SLDASM`

## 5. Minimum Rough Assembly Needs

Before a useful rough assembly can be generated, the following Priority A native CAD should be added:

- left Y-axis module.
- right Y-axis module.
- X-axis module on gantry.
- Z-axis module.
- input mixed tube rack.
- at least one category output bin.
- barcode scanner.
- photoelectric sensor.

The project todo list recommends converting all Priority A rack/bin and sensing components before rerunning the macro.

## 6. Generated Management Files

```text
03_cad/solidworks/converted_native/native_file_mapping.csv
03_cad/solidworks/converted_native/manual_native_conversion_todo.csv
03_cad/solidworks/converted_native/manual_native_conversion_guide.md
```

## 7. Next Step

Use `manual_native_conversion_todo.csv` to convert Priority A files in SolidWorks, update `native_file_mapping.csv`, rerun:

```bash
python 03_cad/solidworks/macros/create_rough_assembly_v1.py
```

Then proceed to Stage 4C screenshot checks if the rough assembly is generated.
