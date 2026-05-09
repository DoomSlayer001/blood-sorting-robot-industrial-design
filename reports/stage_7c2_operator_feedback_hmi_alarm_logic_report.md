# Stage 7C-2 Operator Feedback HMI and Alarm Logic Report

- Stage scope: operator feedback HMI and alarm logic definition.
- This stage is not camera logic. Input occupancy remains table-driven by the internal occupancy table.
- This stage does not create CAD, does not render, does not enter Isaac Sim, does not modify `legacy_v1`, and does not change Stage 7B sorting behavior.
- Current mechanical baseline remains Stage 7A-3f v1.7.

## Why Feedback Is Needed

Input box empty feedback prevents the operator from assuming the robot is faulted when it is simply waiting for refill. A single empty input box can be skipped, while all input boxes empty moves the system to `wait_for_input_refill`.

Output box full feedback is required because full category capacity affects scheduling. It flashes the corresponding output LED, starts intermittent buzzer, triggers `category_hold`, and sends normal same-category samples to pending queue. Other categories continue processing. Normal samples are not sent to manual review because output capacity is a logistics condition, not a sample abnormality.

## Light and Buzzer Coordination

The tower light provides broad machine state: green for normal running, yellow for warning or waiting, and red for alarms. Local LEDs identify the exact input box, output box, manual review rack, or pick error. The buzzer adds urgency: short beep for notices, intermittent for output full/operator service, and continuous for manual review full or safety alarms. The acknowledge button can silence the buzzer, but it does not clear unresolved indicator lights.

## Category Hold and Resume

When an output box is full, the HMI maps the condition to `category_hold`. The held category uses pending queue logic from Stage 7B-2, while other categories can continue. When the output box is replaced or cleared, the LED and buzzer clear, `category_resume` is triggered, and pending queue processing resumes.

## Manual Review Full Versus Output Full

Manual review full blocks abnormal-sample handling and uses a higher priority continuous buzzer. Output full blocks only the affected normal category and uses intermittent buzzer. These states are intentionally separate: manual review is reserved for true abnormal samples, while output full is handled through category hold and pending queue.

## Pick Failure Boundary

`pick_failed` is not the same as barcode abnormal or sample abnormal. It may trigger a pick error indicator, retry, or operator check. It does not route a sample to manual review unless that same sample also has barcode or sample abnormal status.

## Generated Files

- `07_validation/operator_feedback_hmi_requirements_v1.md`
- `07_validation/operator_feedback_state_logic_v1.csv`
- `07_validation/operator_feedback_io_map_v1.csv`
- `07_validation/operator_alarm_priority_table_v1.csv`
- `07_validation/operator_feedback_event_mapping_v1.csv`
- `07_validation/operator_feedback_simulation_interface_v1.csv`
- `07_validation/check_operator_feedback_tables_v1.py`

Later CAD stages may add small status lights, a buzzer, and an acknowledge button to the mechanical/electrical layout. Stage 7C-2 only defines the logic and interface.
