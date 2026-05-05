# Multi-box Sorting Policy v1

## Sample Selection

- Default selection scans by `input_box_id`, then row, then column.
- If a sample's category is in `category_hold`, skip that sample.
- Continue searching for samples in categories that are not held.
- Skipped samples enter a pending queue.
- After `category_resume`, samples in that category are reprocessed from the pending queue.

## Multi-input Box Policy

- Empty input boxes are marked `empty`.
- Empty boxes do not participate in sample selection.
- After operator replacement, the input box is marked `available`.
- A new input box joins the scan queue after registration.

## Output Box Capacity Policy

- Each Category A/B/C/D output box has capacity 24.
- `filled_count == 24` triggers `category_hold`.
- Operator clear or replacement resets `filled_count`.
- During `category_hold`, the system does not pick normal samples for that category.

## Manual Review Policy

- Manual review capacity is 6.
- Only true abnormal samples enter manual review.
- If manual review is full, the system enters `PAUSE_ALARM`.
- Manual review is not a fallback for normal samples blocked only by a full category output box.

## Sample Exception Definitions

- `missing_label`
- `scan_failed`
- `barcode_invalid`
- `unknown_category`
- `sample_info_mismatch`
- `physical_tube_abnormal`

## Strategy Priority

1. Safety.
2. Prevent wrong classification.
3. Continue processing samples that can be handled.
4. Wait for operator clear/replacement when required.
