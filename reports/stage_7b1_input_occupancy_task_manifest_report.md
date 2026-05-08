# Stage 7B-1 Input Occupancy Map and Sorting Task Manifest Simulation Report

## Scope

- This stage does not use a camera.
- Tube occupancy is provided by the internal input occupancy table.
- No CAD modeling, rendering, Stage 7A file edits, `legacy_v1` edits, or XY slider binding fixes are performed in this stage.
- Stage 7A-3f XY slider binding remains a deferred mechanical integration issue and does not block this abstract simulation layer.

## Input Occupancy

- Input boxes: 4.
- Input box format: 4 x 6.
- Total input slots: 96.
- Occupied slots: 69.
- Empty slots: 27.
- Empty slots are recorded in the occupancy map only and do not generate pick tasks.

## Sorting Logic

- Normal sample count: 64.
- Abnormal sample count: 5.
- Generated task count: 69.
- Valid category_A-D samples generate `output_box` tasks.
- True abnormal samples generate `manual_review` tasks.
- Manual review is reserved for missing label, invalid barcode, abnormal sample information, and unrecognized category.
- A full output category triggers category_hold; after operator service it triggers category_resume.
- A normal sample blocked by a full output box is not sent to manual_review.
- `pick_failed` is treated as a robot execution failure state, not an abnormal sample classification.

## Capacity State

- Output boxes: 4, each 4 x 6 with 24 slots.
- `output_box_D` is initialized as full to exercise category_hold logic.
- Manual review capacity: 2 x 3, 6 slots.
- Manual review capacity is not used for normal samples.

## Simulation Use

- This dataset is the base for later state machine execution, trajectory timing, cycle simulation, animation, and Isaac Sim visualization.
- Python task logic and collision-envelope checks remain the priority for near-term simulation.

## Generated Files

- `06_simulation/input_box_occupancy_map_v1.csv`
- `06_simulation/tube_sample_manifest_v1.csv`
- `06_simulation/sorting_task_manifest_v1.csv`
- `06_simulation/output_box_capacity_state_v1.csv`
- `06_simulation/manual_review_capacity_state_v1.csv`
- `06_simulation/category_mapping_v1.csv`
- `06_simulation/input_occupancy_task_summary_v1.csv`
- `06_simulation/figures/input_box_occupancy_heatmap_v1.png`
- `06_simulation/figures/sample_category_distribution_v1.png`
- `06_simulation/figures/normal_vs_abnormal_samples_v1.png`

## Validation

- validation_status=PASS
