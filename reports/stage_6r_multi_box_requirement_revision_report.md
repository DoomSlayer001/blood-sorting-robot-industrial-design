# Stage 6R Multi-box Requirement Revision Report

## Why This Revision Is Needed

The previous v6 and Stage 6A-6E workflow validates a single-batch prototype with one 4 x 6 input rack and small 2 x 3 output bins. That is useful for geometry, reachability, path, timing, exception, and animation proof-of-concept, but it does not match the more realistic batch workflow.

## Problems In The Old Logic

- Single input rack capacity is too small for the target batch workflow.
- Output full previously routed normal samples to manual review.
- Manual review was incorrectly used as a fallback for normal samples blocked by full category bins.

## New Logic Advantages

- Four replaceable 4 x 6 input boxes support 96-tube batch input.
- Category A/B/C/D each use a replaceable 4 x 6 output box.
- A full category output box triggers category hold instead of abnormal routing.
- Other non-held categories continue processing.
- Manual review is reserved for true abnormal samples.

## Impact On Existing Work

v6 and Stage 6A-6E are preserved as single-batch prototype validation. They should not be deleted or rewritten. Future simulations should be regenerated with the multi-box requirements.

## Modules To Re-run Later

- 6A coordinate model and slot table.
- 6B trajectory planning.
- 6C cycle time and throughput.
- 6D failure handling.
- 6E visualization animation.

## PID Timing

PID simulation should be postponed until the multi-box task logic is stable. Otherwise the controller targets would be based on an outdated single-batch workflow.

## Recommended Next Stages

- Stage 7A: Multi-box coordinate model and slot table.
- Stage 7B: Multi-box sorting policy simulation.
- Stage 7C: Multi-box trajectory and cycle time update.
- Stage 8: PID control simulation.
