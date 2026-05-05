# Multi-box Sorting Architecture

Stage 6R defines the target architecture for batch sorting with replaceable input and output boxes.

## Multi-input Box Area

- `input_box_1`: 4 x 6, replaceable.
- `input_box_2`: 4 x 6, replaceable.
- `input_box_3`: 4 x 6, replaceable.
- `input_box_4`: 4 x 6, replaceable.
- The system selects the next sample according to the multi-box sorting policy.
- Empty input boxes are skipped until replaced.

## Multi-output Box Area

- `category_A_output_box`: 4 x 6, Category A only.
- `category_B_output_box`: 4 x 6, Category B only.
- `category_C_output_box`: 4 x 6, Category C only.
- `category_D_output_box`: 4 x 6, Category D only.
- Each output box has an independent `full` / `available` state.
- A full category output box places that category into hold, not into manual review.

## Manual Review Bin

- `manual_review_bin`: 2 x 3.
- Only true abnormal samples enter this bin.
- Full manual review bin triggers `PAUSE_ALARM`.

## Operator Interaction

- Replace empty input box.
- Clear or replace full output box.
- Clear manual review bin.
- Acknowledge pause alarm.
- Resume held category after output box replacement.

## System State Changes

- `input_box_empty`
- `output_category_full`
- `category_hold`
- `category_resume`
- `manual_review_full`
- `pause_alarm`
