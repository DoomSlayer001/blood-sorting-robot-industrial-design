# Tube Bin Parameters

## Purpose

The tube bin STEP files are simplified custom-part models for the mixed input rack, four category output bins, and manual review bin. They are intended for course design, SolidWorks layout validation, and sorting workflow visualization. Final manufacturing release still requires detailed drawings, tolerances, material confirmation, and reachability checks.

## Common Hole Parameters

| parameter | value |
|---|---:|
| hole pitch | 28 mm |
| hole diameter | 15 mm |
| hole depth | 25 mm |
| body height | 35 mm |
| suggested material | POM or PC |

The holes are blind holes opened from the top face. The current STEP models do not include engraved labels, drain features, fillets for sterilization, or manufacturing tolerances.

## Input Rack

| item | value |
|---|---|
| file | `input_mixed_tube_rack_4x6.step` |
| layout | 4 rows x 6 columns |
| capacity | 24 tubes |
| suggested size | 180 mm x 120 mm x 35 mm |
| purpose | mixed random input area |

## Output Bins

| file | category | layout | capacity | suggested size |
|---|---|---|---:|---|
| `category_A_output_bin_2x3.step` | Category A | 2 x 3 | 6 | 100 mm x 75 mm x 35 mm |
| `category_B_output_bin_2x3.step` | Category B | 2 x 3 | 6 | 100 mm x 75 mm x 35 mm |
| `category_C_output_bin_2x3.step` | Category C | 2 x 3 | 6 | 100 mm x 75 mm x 35 mm |
| `category_D_output_bin_2x3.step` | Category D | 2 x 3 | 6 | 100 mm x 75 mm x 35 mm |

## Manual Review Bin

| item | value |
|---|---|
| file | `manual_review_bin_2x3.step` |
| layout | 2 rows x 3 columns |
| capacity | 6 tubes |
| purpose | barcode failure, unknown category, output bin full, or abnormal sample |

## Hole Numbering Rule

- Rows are lettered from front/local positive-Y side to rear/local negative-Y side: `A`, `B`, `C`, `D` for the 4 x 6 input rack.
- Columns are numbered left to right in local X: `1` to `6` for the input rack.
- 2 x 3 bins use rows `A-B` and columns `1-3`.
- Example input positions: `A1`, `A2`, ..., `D6`.

## Local Coordinate Definition

The bin local origin is at the body center on the bottom plane. X is along columns, Y is along rows, and Z is upward. Hole center coordinates are generated from the center of the array:

```text
x = -(cols - 1) * pitch / 2 + (col - 1) * pitch
y =  (rows - 1) * pitch / 2 - (row_index - 1) * pitch
z = body_top
```

## Relation To sample_manifest.csv

`sample_manifest.csv` uses `input_row`, `input_col`, `target_bin`, `target_row`, and `target_col` to map each sample to physical bin positions. Category A/B/C/D map to the four category bins. Failed scans, unknown categories, full bins, or abnormal samples map to `manual_review_bin`.

## Relation To SolidWorks Assembly Coordinates

The local bin coordinate systems should be constrained to named assembly datums during SolidWorks layout:

- `DATUM_INPUT_RACK_ORIGIN`
- `DATUM_CATEGORY_A_BIN_ORIGIN`
- `DATUM_CATEGORY_B_BIN_ORIGIN`
- `DATUM_CATEGORY_C_BIN_ORIGIN`
- `DATUM_CATEGORY_D_BIN_ORIGIN`
- `DATUM_MANUAL_REVIEW_BIN_ORIGIN`

The gripper centerline must be checked against every local hole coordinate after the bins are placed on the 1100 mm x 900 mm base.
