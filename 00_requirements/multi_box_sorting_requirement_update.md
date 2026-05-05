# Multi-box Sorting Requirement Update

Stage 6R revises the sorting workflow from a single-input-rack prototype to a multi-box batch workflow. Existing v6 and Stage 6A-6E results remain valid as single-batch prototype validation.

## Frozen Parameters

| parameter | value |
|---|---:|
| `input_box_count` | 4 |
| `input_box_layout` | 4 x 6 |
| `input_box_capacity` | 24 |
| `total_input_capacity` | 96 |
| `output_category_count` | 4 |
| `output_box_layout` | 4 x 6 |
| `output_box_capacity` | 24 |
| `total_output_capacity` | 96 |
| `manual_review_layout` | 2 x 3 |
| `manual_review_capacity` | 6 |

## Input Area Logic

- The input area supports four identical input boxes: `input_box_1` through `input_box_4`.
- Each input box has a 4 x 6 layout and holds 24 tubes.
- Input boxes are replaceable by medical staff.
- The system should identify or record whether each input box is available or empty.
- Empty input boxes are skipped during sample selection.
- After operator replacement, the new input box becomes available and re-enters the sorting queue.

## Output Area Logic

- Category A/B/C/D each has one replaceable 4 x 6 output box.
- Each output box has independent `available`, `full`, `held`, and `replaced` state.
- When a category output box is full, that category enters `category_hold`.
- During `category_hold`, the system does not pick normal samples belonging to that category.
- The system continues sorting samples for other non-held categories.
- After medical staff clear or replace the full output box, the category enters `category_resume`.

## Manual Review Logic

- `manual_review_bin` is only for true abnormal samples.
- It does not receive normal samples merely because the matching category output box is temporarily full.
- If `manual_review_bin` is full and another abnormal sample requires review, the system enters `PAUSE_ALARM`.

## Difference From Previous Logic

- Old single-batch prototype logic: output full routed normal samples to `manual_review_bin`.
- New multi-box logic: output full triggers `category_hold`.
- Old `manual_review_bin`: used partly as a full-bin fallback.
- New `manual_review_bin`: reserved for true exceptions such as missing label, scan failure, invalid barcode, unknown category, mismatched sample information, or physically abnormal tubes.
