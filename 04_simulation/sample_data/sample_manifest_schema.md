# Sample Manifest Schema

Future software simulation will use `sample_manifest.csv` to describe the 24 mixed input tubes. This stage only freezes the schema; it does not generate `sample_manifest.csv`.

## Fields

```text
tube_id,
barcode,
cap_color,
height_mm,
category,
input_row,
input_col,
target_bin,
target_row,
target_col,
scan_status,
note
```

## Field Meaning

| field | meaning |
|---|---|
| `tube_id` | unique tube identifier used by the simulation and report |
| `barcode` | 1D/2D barcode or QR code text read from the tube label |
| `cap_color` | tube cap color for visual classification display |
| `height_mm` | tube height in millimeters |
| `category` | `Category A`, `Category B`, `Category C`, `Category D`, or `unknown` |
| `input_row` | row index in the 4 x 6 mixed input rack |
| `input_col` | column index in the 4 x 6 mixed input rack |
| `target_bin` | `category_a_bin`, `category_b_bin`, `category_c_bin`, `category_d_bin`, or `manual_review_bin` |
| `target_row` | row index in the selected target bin |
| `target_col` | column index in the selected target bin |
| `scan_status` | `success` or `fail` |
| `note` | optional explanation, such as full bin, unreadable code, or abnormal sample |

## Routing Rules

- `Category A` maps to `category_a_bin`.
- `Category B` maps to `category_b_bin`.
- `Category C` maps to `category_c_bin`.
- `Category D` maps to `category_d_bin`.
- If `scan_status = success`, the sample enters the matching category output bin when a slot is available.
- If `scan_status = fail`, the sample enters `manual_review_bin`.
- If `category = unknown`, the sample enters `manual_review_bin`.
- If the target category bin is full, the sample enters `manual_review_bin`.

## Planned Data Size

The future `sample_manifest.csv` will contain 24 sample rows, matching the 4 x 6 mixed input rack. The CSV is intentionally not generated in this stage.
