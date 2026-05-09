# Operator Feedback HMI and Alarm Requirements v1

Stage 7C-2 defines operator feedback logic only. It does not add CAD geometry, does not render, does not enter Isaac Sim, and does not change the Stage 7B sorting policy.

The system still does not use camera logic. Input box occupancy is provided by the internal tube occupancy table.

## Feedback Hardware Concepts

- Stack light / tower light:
  - Green: normal running.
  - Yellow: waiting for operator handling, input box empty, output box near full, barcode abnormal.
  - Red: output box full, manual review full, emergency stop, safety abnormal.
- Per-input-box empty LEDs:
  - `input_box_01_empty_led`
  - `input_box_02_empty_led`
  - `input_box_03_empty_led`
  - `input_box_04_empty_led`
- Per-output-box full LEDs:
  - `output_box_A_full_led`
  - `output_box_B_full_led`
  - `output_box_C_full_led`
  - `output_box_D_full_led`
- Manual review indicator:
  - `manual_review_full_led`
- Buzzer outputs:
  - `buzzer_short_beep`: barcode abnormal or input empty notice.
  - `buzzer_intermit`: output box full or waiting for operator service.
  - `buzzer_continuous`: manual review full or safety alarm.
- Operator input:
  - `operator_ack_button` silences the buzzer after acknowledgement.
  - Acknowledgement does not clear unresolved warning or alarm lights.

## Required Behavior

- Input box empty flashes the corresponding input empty LED. If all input boxes are empty, the system enters `wait_for_input_refill`. Input empty never sends samples to manual review.
- Output box full flashes the corresponding category LED red, starts intermittent buzzer, triggers `category_hold`, and sends normal samples for that category to pending queue. Other categories continue processing. Output full never routes normal samples to manual review.
- Output box replaced or cleared turns off the category full LED, stops the related buzzer, triggers `category_resume`, and resumes pending queue processing.
- Manual review full flashes `manual_review_full_led` red, starts continuous buzzer, and pauses abnormal-sample handling. Normal samples still do not enter manual review.
- Barcode abnormal or missing label gives a short yellow flash and optional short beep. The sample is routed to manual review and an abnormal event is recorded.
- Pick failure is a handling error, not an abnormal sample classification. It may trigger `pick_error_indicator` and operator check or retry logic. It does not route to manual review unless the same sample is already barcode/sample abnormal.

## Design Boundary

This stage defines requirements, HMI state logic, alarm priority, I/O naming, event mapping, and simulation interface rows. Later CAD work may add physical stack light, indicator LEDs, buzzer, and acknowledge button, but that is outside Stage 7C-2.
