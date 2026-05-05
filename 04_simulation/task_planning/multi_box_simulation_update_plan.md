# Multi-box Simulation Update Plan

Existing v6 and Stage 6A-6E results are retained as single-batch prototype validation. The following modules need later updates for the multi-box batch workflow.

## 6A Coordinate Model

- Expand from one input rack to four input boxes.
- Change Category A/B/C/D output boxes from 2 x 3 to 4 x 6.
- Keep manual review as 2 x 3.

## 6B Trajectory

- Support multiple `input_box_id` origins.
- Support category hold and skipped samples.
- Add a pending queue and resume behavior after output box replacement.

## 6C Cycle Time

- Re-estimate multi-box batch processing time.
- Include category hold, operator clear/replace delay, and pending queue effects.

## 6D Failure Handling

- Replace output-full-to-manual-review logic with `category_hold` / `category_resume`.
- Reserve manual review for true abnormal samples only.
- Keep manual review full as `PAUSE_ALARM`.

## 6E Animation

- Display four input boxes.
- Display 4 x 6 category output boxes.
- Display held category state.
- Display operator clear/replace events.
