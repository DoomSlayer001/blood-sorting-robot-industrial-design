# Failure Handling Logic

## 1. Normal Flow

```text
input rack -> scan station -> category output bin
```

## 2. Exception Types

| code | meaning |
|---|---|
| `scan_failed` | barcode/QR code was not read successfully |
| `barcode_unknown` | barcode read succeeded but category lookup failed |
| `target_bin_full` | matching category output bin has no available slot |
| `gripper_pick_failed` | tube pickup failed or tube was not detected after pickup |
| `gripper_place_failed` | placement failed or tube release was not confirmed |
| `tube_height_mismatch` | actual tube height does not match expected handling profile |
| `motion_limit_triggered` | axis home/limit/software boundary was triggered |
| `manual_review_bin_full` | exception bin has no available slot |

## 3. Handling Rules

| exception | handling |
|---|---|
| `scan_failed` | place tube into `manual_review_bin` |
| `barcode_unknown` | place tube into `manual_review_bin` |
| `target_bin_full` | place tube into `manual_review_bin` |
| `gripper_pick_failed` | pause for operator check, or route to `manual_review_bin` if tube is securely held |
| `gripper_place_failed` | pause for operator check, or route to `manual_review_bin` if recovery is safe |
| `tube_height_mismatch` | route to `manual_review_bin` after safe-height recovery |
| `motion_limit_triggered` | stop motion immediately and require reset |
| `manual_review_bin_full` | pause and alarm |

## 4. Relation To sample_manifest.csv

- `scan_status = success` maps to normal sorting when the category is known and the target bin has space.
- `scan_status = fail` maps to `manual_review_bin`.
- `category = unknown` maps to `manual_review_bin`.
- A full target category bin overrides normal category placement and routes the tube to `manual_review_bin`.

## 5. Notes For Later Simulation

The current `sample_manifest.csv` models scan success/failure and category lookup result. Later trajectory planning should add state transitions for scan station arrival, scan result, bin slot allocation, and exception routing.
