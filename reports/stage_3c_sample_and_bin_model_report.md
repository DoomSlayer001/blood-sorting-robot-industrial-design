# Stage 3C Sample Tube And Tube Bin Model Report

## 1. Stage Goal

Stage 3C creates simplified engineering STEP models and sample data for the mixed blood collection tube identification and classification sorting task. The outputs support SolidWorks layout planning, later Isaac Sim visualization, and future MATLAB/Simulink trajectory generation.

## 2. Task Definition

The robot handles mixed blood collection tubes placed vertically in the input rack. It picks one tube, moves to the scanning station, triggers barcode reading through the Panasonic CX-421-J photoelectric sensor, reads the label with the Cognex DataMan 80 USB barcode reader, queries the category, and places the tube into the corresponding output bin. Failed, unknown, full-bin, or abnormal samples go to `manual_review_bin`.

## 3. Classification Quantity

```text
n = 4
```

The categories are Category A, Category B, Category C, and Category D.

## 4. Six Tube Boxes / Racks

| item | layout | capacity | purpose |
|---|---|---:|---|
| input mixed tube rack | 4 x 6 | 24 | random mixed input |
| Category A output bin | 2 x 3 | 6 | classified output |
| Category B output bin | 2 x 3 | 6 | classified output |
| Category C output bin | 2 x 3 | 6 | classified output |
| Category D output bin | 2 x 3 | 6 | classified output |
| manual review bin | 2 x 3 | 6 | exception handling |

The scanning station is not counted as a tube box.

## 5. Sample Tube Models

| file | category | height |
|---|---|---:|
| `03_cad/custom_parts/sample_tube/purple_cap_tube_13x75.step` | Category A | 75 mm |
| `03_cad/custom_parts/sample_tube/yellow_cap_tube_13x100.step` | Category B | 100 mm |
| `03_cad/custom_parts/sample_tube/blue_cap_tube_13x75.step` | Category C | 75 mm |
| `03_cad/custom_parts/sample_tube/red_cap_tube_13x75.step` | Category D | 75 mm |

These are simplified scene/consumable models and not production drawings.

## 6. Tube Bin Models

| file | layout |
|---|---|
| `03_cad/custom_parts/tube_bins/input_mixed_tube_rack_4x6.step` | 4 x 6 |
| `03_cad/custom_parts/tube_bins/category_A_output_bin_2x3.step` | 2 x 3 |
| `03_cad/custom_parts/tube_bins/category_B_output_bin_2x3.step` | 2 x 3 |
| `03_cad/custom_parts/tube_bins/category_C_output_bin_2x3.step` | 2 x 3 |
| `03_cad/custom_parts/tube_bins/category_D_output_bin_2x3.step` | 2 x 3 |
| `03_cad/custom_parts/tube_bins/manual_review_bin_2x3.step` | 2 x 3 |

All tube bins use 15 mm blind holes, 25 mm hole depth, and 28 mm pitch. Material is recommended as POM or PC.

## 7. sample_manifest.csv Summary

- File: `04_simulation/sample_data/sample_manifest.csv`
- Rows: 24 samples.
- Input positions: A1-D6 are fully covered.
- Normal sample distribution: Category A = 6, Category B = 6, Category C = 5, Category D = 5.
- Exception samples: 2 samples with `barcode = UNKNOWN`, `category = unknown`, and `scan_status = fail`.
- Heights: 75 mm and 100 mm are included.
- Cap colors: purple, yellow, blue, and red are included.

## 8. Recognition Chain

Panasonic CX-421-J confirms tube presence at the scanning station. Cognex DataMan 80 USB reads the tube label barcode or QR code after the presence trigger. The barcode result is used to query Category A/B/C/D. Failed or unknown results are routed to `manual_review_bin`.

## 9. SolidWorks Assembly Use

The STEP files should be inserted as simplified custom parts. The tube bin local coordinate systems should later be constrained to:

- `DATUM_INPUT_RACK_ORIGIN`
- `DATUM_CATEGORY_A_BIN_ORIGIN`
- `DATUM_CATEGORY_B_BIN_ORIGIN`
- `DATUM_CATEGORY_C_BIN_ORIGIN`
- `DATUM_CATEGORY_D_BIN_ORIGIN`
- `DATUM_MANUAL_REVIEW_BIN_ORIGIN`

Tube instances should be placed according to `sample_manifest.csv` during layout and visualization work.

## 10. Current Risks

- Blood collection tubes are simplified scene models.
- Label and barcode graphics are visual placeholders and are not readable codes.
- Tube bin hole positions must be checked against gripper reachability in SolidWorks.
- Scanner line of sight and tube label orientation must be checked in the scanning station layout.
- Final tube bins require engineering drawings, manufacturing tolerances, material review, and cleaning/handling considerations.
