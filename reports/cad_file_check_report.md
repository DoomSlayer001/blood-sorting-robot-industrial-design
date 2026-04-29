# CAD File Check Report

- Generated at: 2026-04-29T19:56:49
- Scan directory: `03_cad/standard_parts/downloaded`
- File count scanned: 6
- Supported CAD file count: 5
- Valid CAD file count: 5
- Supplementary vendor document count: 1
- Invalid / unsupported CAD candidate count: 0

## CAD File Results

| file | size_bytes | status |
|---|---:|---|
| `03_cad/standard_parts/downloaded/x_axis_module/MISUMI_MSA628_X_axis_L750_double_shaft_B1_v1.step` | 5514777 | OK |
| `03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step` | 5514777 | OK |
| `03_cad/standard_parts/downloaded/y_axis_module/MSA-628-B-AB-B1-0750.STEP` | 5514777 | OK |
| `03_cad/standard_parts/downloaded/z_axis_module/LS1004-140-T42_STEP_AP214_20260429/LS1004-140-T42.stp` | 903383 | OK |
| `03_cad/standard_parts/downloaded/z_axis_module/MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.step` | 903383 | OK |

## Supplementary Vendor Documents

| file | size_bytes | note |
|---|---:|---|
| `03_cad/standard_parts/downloaded/z_axis_module/LS1004-140-T42_STEP_AP214_20260429/readme-and-terms-of-use-3d-cad-models.txt` | 2684 | supplementary vendor document |

## Rules

- This script does not modify CAD files.
- This script does not mark any file as downloaded in BOM or CAD status tables.
- Allowed extensions: `.step`, `.stp`, `.sldprt`, `.sldasm`, `.x_t`, `.igs`, `.iges`.
- File names must not contain Chinese characters or spaces.
- Supplementary vendor documents such as `.txt`, `.pdf`, `.html`, `.htm`, readme, terms, or license files are reported separately and are not counted as invalid CAD.
