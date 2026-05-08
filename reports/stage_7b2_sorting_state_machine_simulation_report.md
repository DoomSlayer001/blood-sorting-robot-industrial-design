# Stage 7B-2 Sorting State Machine and Hold/Resume Simulation Report

## Scope

- This stage does not use a camera.
- Input occupancy comes from the internal Stage 7B-1 input table.
- Stage 7B-1 sorting task manifest is used as the task source for the state machine.
- No CAD modeling, rendering, Stage 7A editing, `legacy_v1` editing, or XY slider binding work is performed.
- Stage 7A-3f XY slider binding remains a deferred mechanical integration issue and does not block abstract sorting simulation.

## Scenario Results

### baseline

- Generated task count: 69.
- Completed output count: 64.
- Completed manual_review count: 5.
- Pending waiting resume count: 0.
- Paused manual_review full count: 0.
- Pick failed needs operator check count: 0.
- Category hold count: 0.
- Category resume count: 0.
- Pending enqueue/dequeue counts: 0 / 0.

### forced_category_A_full

- Generated task count: 69.
- Completed output count: 64.
- Completed manual_review count: 5.
- Pending waiting resume count: 0.
- Paused manual_review full count: 0.
- Pick failed needs operator check count: 0.
- Category hold count: 1.
- Category resume count: 1.
- Pending enqueue/dequeue counts: 16 / 16.

### manual_review_limited_capacity

- Generated task count: 69.
- Completed output count: 64.
- Completed manual_review count: 3.
- Pending waiting resume count: 0.
- Paused manual_review full count: 2.
- Pick failed needs operator check count: 0.
- Category hold count: 0.
- Category resume count: 0.
- Pending enqueue/dequeue counts: 0 / 0.

### pick_failure_test

- Generated task count: 69.
- Completed output count: 63.
- Completed manual_review count: 5.
- Pending waiting resume count: 0.
- Paused manual_review full count: 0.
- Pick failed needs operator check count: 1.
- Category hold count: 0.
- Category resume count: 0.
- Pending enqueue/dequeue counts: 0 / 0.

## Logic Notes

- `category_hold` is triggered when a normal sample targets a full output box.
- Pending normal samples remain in the pending queue until `operator_cleared_output_box` and `category_resume`.
- Other categories continue to be processed while one category is held.
- Manual review only handles true abnormal samples: missing label, invalid barcode, abnormal sample information, or unknown category.
- Output full never becomes an abnormal reason and never sends a normal sample to manual_review.
- `pick_failed` represents a robot execution failure or possible empty-slot mismatch, not abnormal sample classification.

## Generated Outputs

- `06_simulation/sorting_state_machine_event_log_v1.csv`
- `06_simulation/sorting_state_machine_task_result_v1.csv`
- `06_simulation/output_box_occupancy_timeline_v1.csv`
- `06_simulation/manual_review_occupancy_timeline_v1.csv`
- `06_simulation/category_hold_resume_events_v1.csv`
- `06_simulation/pending_queue_log_v1.csv`
- `06_simulation/abnormal_handling_log_v1.csv`
- `06_simulation/pick_failure_log_v1.csv`
- `06_simulation/sorting_state_machine_summary_v1.csv`

## Consistency Check

- validation_status=PASS
- This stage provides the logical basis for later trajectory, cycle time, animation, and Isaac Sim work.
