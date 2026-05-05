# Multi-box Data Model v1

This draft data model supports future multi-box batch workflow simulation.

## InputBox

| field | meaning |
|---|---|
| `input_box_id` | `input_box_1` through `input_box_4` |
| `status` | `available`, `empty`, or `replaced` |
| `slots` | 4 x 6 slot map |
| `sample_count` | number of tubes currently recorded in the box |
| `last_update_time` | timestamp of operator or system status update |
| `notes` | free text for operator/system comments |

## OutputBox

| field | meaning |
|---|---|
| `category` | `Category A`, `Category B`, `Category C`, or `Category D` |
| `status` | `available`, `full`, `held`, or `replaced` |
| `capacity` | 24 |
| `filled_count` | occupied slots |
| `occupied_slots` | slot map with sample IDs |
| `hold_start_time` | time when category hold began |
| `resume_time` | time when category became available again |

## ManualReviewBin

| field | meaning |
|---|---|
| `capacity` | 6 |
| `filled_count` | occupied slots |
| `occupied_slots` | slot map with abnormal sample IDs |
| `status` | `available` or `full` |

## Sample

| field | meaning |
|---|---|
| `sample_id` | unique sample ID |
| `current_input_box` | source input box |
| `input_slot` | source slot |
| `barcode_status` | scan result |
| `category` | resolved category or unknown |
| `target_category` | intended Category A/B/C/D target |
| `processing_status` | queued, picked, scanned, placed, pending, abnormal, complete |
| `pending_reason` | e.g. category_hold |
| `final_location` | category output slot or manual review slot |
