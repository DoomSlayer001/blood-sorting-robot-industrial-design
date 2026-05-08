# Manual Review Exception Logic v1

Only abnormal tubes go to manual review.

## Abnormal Conditions

- missing label
- barcode invalid
- sample information abnormal
- unrecognized category

## Non-Abnormal Conditions

A normal tube blocked by a full output category is not abnormal. The correct behavior is to pause that category and continue sorting other categories until the full output box is serviced.

## Current System Rule

No camera is used in the current system version. Tube presence, tube ID, category, and source rack slot are provided by an internal input table. Vision is reserved as a future optional extension only.

