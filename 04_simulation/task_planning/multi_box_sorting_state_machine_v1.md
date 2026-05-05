# Multi-box Sorting State Machine v1

This state machine supersedes the single-input demonstration flow for future multi-box batch simulation. Stage 6A-6E remain valid as single-batch prototype validation.

## States

| state | purpose |
|---|---|
| `IDLE` | Wait for operator start. |
| `LOAD_INPUT_BOXES` | Load or register four input boxes. |
| `SCAN_INPUT_BOX_STATUS` | Determine which input boxes are available or empty. |
| `SELECT_NEXT_SAMPLE` | Select the next candidate sample by input box, row, and column. |
| `CHECK_SAMPLE_CATEGORY_HOLD` | Check whether the sample category is currently held. |
| `SKIP_HELD_CATEGORY` | Skip normal samples whose category output box is full. |
| `SELECT_ALTERNATIVE_SAMPLE` | Search for another sample from a non-held category. |
| `MOVE_TO_INPUT_BOX_SLOT` | Move to the selected input-box slot. |
| `PICK_TUBE` | Pick the tube. |
| `MOVE_TO_SCAN` | Move to the scan station. |
| `SCAN_BARCODE` | Read barcode or trigger scan failure handling. |
| `CLASSIFY_SAMPLE` | Resolve Category A/B/C/D or abnormal status. |
| `CHECK_OUTPUT_CAPACITY` | Check target category output box capacity. |
| `HOLD_CATEGORY` | Mark a full category as held. |
| `MOVE_TO_OUTPUT_BOX` | Move to the selected category output box. |
| `PLACE_TUBE` | Place a normal classified tube. |
| `MOVE_TO_MANUAL_REVIEW` | Place a true abnormal tube into manual review. |
| `CHECK_INPUT_BOX_EMPTY` | Update input-box empty status. |
| `WAIT_OPERATOR_REPLACE_INPUT_BOX` | Wait for a new full input box. |
| `WAIT_OPERATOR_CLEAR_OUTPUT` | Wait for operator to clear or replace a full category output box. |
| `RESUME_HELD_CATEGORY` | Resume a category after its output box is available again. |
| `CHECK_MANUAL_REVIEW_CAPACITY` | Check exception-bin capacity before routing abnormal sample. |
| `PAUSE_ALARM` | Pause for manual intervention. |
| `COMPLETE` | Finish all available and unheld samples. |

## Key Rules

- Output full is not an abnormal sample.
- Output full triggers `HOLD_CATEGORY` and `WAIT_OPERATOR_CLEAR_OUTPUT`.
- True abnormal samples go to `MOVE_TO_MANUAL_REVIEW`.
- Manual review full triggers `PAUSE_ALARM`.
- After `RESUME_HELD_CATEGORY`, previously skipped samples in that category return from the pending queue.
