# Standard Parts File Naming Rule

## Required Format

Real supplier CAD files must use this naming pattern:

```text
supplier_parttype_model_spec_version.ext
```

Examples:

```text
MISUMI_linear_module_X_420mm_v1.step
HIWIN_linear_guide_MGN12_300mm_v1.step
NEMA17_closed_loop_motor_42mm_v1.step
SMC_parallel_gripper_small_v1.step
```

## Rules

1. File names must not use Chinese characters.
2. File names must not contain spaces.
3. Use lowercase or clear ASCII words separated by underscores.
4. Every real downloaded part must map to a `part_id` in `02_bom/standard_parts_bom_v1.csv`.
5. Every real downloaded part must record source, download date, format, and whether manual download was required in `03_cad/standard_parts/CAD_download_status_v2.md`.
6. If the same part is available in multiple formats, keep the preferred format in the downloaded folder and record backup formats in the status table note.

## Format Preference

Preferred CAD format order:

```text
SLDPRT / SLDASM > STEP / STP > X_T > IGES > STL
```

STL is acceptable only for visual reference and is not acceptable for mechanical interface design.

## Versioning

Use `v1`, `v2`, and later suffixes when replacing a CAD file with a corrected or more suitable supplier export. Do not overwrite a released supplier CAD file without updating the status table.
