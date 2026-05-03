# Sorting State Machine v1

Stage 6A defines the first task-level state machine for the blood sorting robot. It is intended for reachability and sequence planning, not controller code generation.

## States

| state | purpose |
|---|---|
| `IDLE` | Robot is powered and waiting for a sorting task. |
| `LOAD_SAMPLE_MANIFEST` | Load the sample manifest and slot/category data. |
| `MOVE_TO_INPUT_SLOT` | Move above the selected input rack slot. |
| `PICK_TUBE` | Descend to the tube-specific grip height and close the gripper. |
| `LIFT_TO_SAFE_Z` | Lift the tube to safe travel height. |
| `MOVE_TO_SCAN_STATION` | Move to the scan station tube holder. |
| `SCAN_BARCODE` | Trigger barcode scan and presence check. |
| `CLASSIFY_SAMPLE` | Map the scan result to Category A/B/C/D or exception handling. |
| `SELECT_OUTPUT_SLOT` | Select the next free slot in the target output bin. |
| `MOVE_TO_OUTPUT_SLOT` | Move above the selected output or review slot. |
| `PLACE_TUBE` | Descend to the tube-specific place height and release the gripper. |
| `HANDLE_SCAN_FAIL` | Route unreadable samples to manual review. |
| `HANDLE_UNKNOWN_CATEGORY` | Route unknown categories to manual review. |
| `HANDLE_OUTPUT_FULL` | Route overflow samples to manual review. |
| `MOVE_TO_MANUAL_REVIEW` | Move above the selected manual review slot. |
| `COMPLETE` | Sorting sequence is complete. |
| `PAUSE_ALARM` | Stop for operator action when manual review is full or another blocking fault occurs. |

## Nominal Flow

`IDLE -> LOAD_SAMPLE_MANIFEST -> MOVE_TO_INPUT_SLOT -> PICK_TUBE -> LIFT_TO_SAFE_Z -> MOVE_TO_SCAN_STATION -> SCAN_BARCODE -> CLASSIFY_SAMPLE -> SELECT_OUTPUT_SLOT -> MOVE_TO_OUTPUT_SLOT -> PLACE_TUBE -> LIFT_TO_SAFE_Z`

The loop repeats for each manifest row. After the final row, the state transitions to `COMPLETE`.

## Exception Flow

- Scan failure: `SCAN_BARCODE -> HANDLE_SCAN_FAIL -> MOVE_TO_MANUAL_REVIEW -> PLACE_TUBE`.
- Unknown category: `CLASSIFY_SAMPLE -> HANDLE_UNKNOWN_CATEGORY -> MOVE_TO_MANUAL_REVIEW -> PLACE_TUBE`.
- Output full: `SELECT_OUTPUT_SLOT -> HANDLE_OUTPUT_FULL -> MOVE_TO_MANUAL_REVIEW -> PLACE_TUBE`.
- Manual review full: transition to `PAUSE_ALARM`.
