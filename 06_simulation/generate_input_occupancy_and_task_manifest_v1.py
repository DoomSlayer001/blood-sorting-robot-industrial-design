from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"
FIG_DIR = SIM_DIR / "figures"
REPORT_DIR = ROOT / "reports"

INPUT_OCCUPANCY_CSV = SIM_DIR / "input_box_occupancy_map_v1.csv"
TUBE_MANIFEST_CSV = SIM_DIR / "tube_sample_manifest_v1.csv"
TASK_MANIFEST_CSV = SIM_DIR / "sorting_task_manifest_v1.csv"
OUTPUT_BOX_STATE_CSV = SIM_DIR / "output_box_capacity_state_v1.csv"
MANUAL_REVIEW_STATE_CSV = SIM_DIR / "manual_review_capacity_state_v1.csv"
CATEGORY_MAPPING_CSV = SIM_DIR / "category_mapping_v1.csv"
SUMMARY_CSV = SIM_DIR / "input_occupancy_task_summary_v1.csv"
REPORT_MD = REPORT_DIR / "stage_7b1_input_occupancy_task_manifest_report.md"

ROWS = 4
COLS = 6
INPUT_BOX_COUNT = 4
SLOTS_PER_BOX = ROWS * COLS
TOTAL_INPUT_SLOTS = INPUT_BOX_COUNT * SLOTS_PER_BOX
OUTPUT_BOX_CAPACITY = 24
MANUAL_REVIEW_CAPACITY = 6

CATEGORIES = ["category_A", "category_B", "category_C", "category_D"]
CATEGORY_TO_BOX = {
    "category_A": "output_box_A",
    "category_B": "output_box_B",
    "category_C": "output_box_C",
    "category_D": "output_box_D",
}


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def build_input_occupancy() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    tube_index = 1
    abnormal_by_global_slot = {
        5: ("missing_label", "unknown", "missing label"),
        17: ("invalid_barcode", "unknown", "barcode invalid"),
        38: ("abnormal_sample_info", "category_B", "sample information abnormal"),
        61: ("unknown_category", "unknown", "unrecognized category"),
        82: ("missing_label", "unknown", "missing label"),
    }

    for box_number in range(1, INPUT_BOX_COUNT + 1):
        input_box_id = f"input_box_{box_number:02d}"
        box_col = (box_number - 1) % 2
        box_row = (box_number - 1) // 2
        box_origin_x = -240 + box_col * 180
        box_origin_y = -170 + box_row * 160

        for row in range(1, ROWS + 1):
            for col in range(1, COLS + 1):
                global_slot = (box_number - 1) * SLOTS_PER_BOX + (row - 1) * COLS + col
                slot_id = f"R{row}C{col}"
                tube_present = (global_slot % 4 != 0) and (global_slot not in {31, 47, 73})
                tube_id = f"TUBE-7B1-{tube_index:03d}" if tube_present else ""
                if tube_present:
                    tube_index += 1

                rows.append(
                    {
                        "input_box_id": input_box_id,
                        "rack_type": "input_4x6",
                        "slot_row": row,
                        "slot_col": col,
                        "slot_id": slot_id,
                        "tube_present": bool_text(tube_present),
                        "tube_id": tube_id,
                        "x_mm": box_origin_x + (col - 1) * 25,
                        "y_mm": box_origin_y + (row - 1) * 25,
                        "z_pick_mm": 145,
                        "slot_status": "occupied" if tube_present else "empty",
                        "notes": "internal occupancy table source; no camera",
                        "_global_slot": global_slot,
                        "_abnormal_tuple": abnormal_by_global_slot.get(global_slot),
                    }
                )
    return rows


def build_tube_manifest(occupancy_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    manifest: list[dict[str, object]] = []
    normal_category_index = 0

    for row in occupancy_rows:
        if row["tube_present"] != "true":
            continue

        abnormal_tuple = row.get("_abnormal_tuple")
        if abnormal_tuple:
            barcode_status, sample_category, abnormal_reason = abnormal_tuple
            abnormal_flag = True
            target_output_box = "manual_review"
            sample_status = "abnormal_to_manual_review"
        else:
            sample_category = CATEGORIES[normal_category_index % len(CATEGORIES)]
            normal_category_index += 1
            barcode_status = "valid"
            abnormal_reason = ""
            abnormal_flag = False
            target_output_box = CATEGORY_TO_BOX[sample_category]
            sample_status = "normal_pending_sort"

        manifest.append(
            {
                "tube_id": row["tube_id"],
                "input_box_id": row["input_box_id"],
                "source_slot_id": row["slot_id"],
                "tube_present": "true",
                "barcode_status": barcode_status,
                "sample_category": sample_category,
                "abnormal_flag": bool_text(abnormal_flag),
                "abnormal_reason": abnormal_reason,
                "target_output_box": target_output_box,
                "priority": 1 if abnormal_flag else 3,
                "sample_status": sample_status,
                "notes": "normal full-output condition uses category hold, not manual review"
                if not abnormal_flag
                else "true abnormal sample routed to manual review",
            }
        )

    return manifest


def build_output_state() -> list[dict[str, object]]:
    initial = {
        "output_box_A": 3,
        "output_box_B": 8,
        "output_box_C": 21,
        "output_box_D": 24,
    }
    rows: list[dict[str, object]] = []
    for category, output_box_id in CATEGORY_TO_BOX.items():
        occupied = initial[output_box_id]
        available = OUTPUT_BOX_CAPACITY - occupied
        if available == 0:
            state = "full"
        elif available <= 4:
            state = "near_full"
        else:
            state = "available"
        rows.append(
            {
                "output_box_id": output_box_id,
                "sample_category": category,
                "capacity_slots": OUTPUT_BOX_CAPACITY,
                "occupied_initial": occupied,
                "available_slots": available,
                "state": state,
                "notes": "full category triggers category_hold and later category_resume after service"
                if state == "full"
                else "available for initial task generation",
            }
        )
    return rows


def build_manual_review_state(abnormal_count: int) -> list[dict[str, object]]:
    occupied_initial = 0
    available_slots = MANUAL_REVIEW_CAPACITY - occupied_initial
    return [
        {
            "manual_review_box_id": "manual_review_01",
            "capacity_slots": MANUAL_REVIEW_CAPACITY,
            "occupied_initial": occupied_initial,
            "available_slots": available_slots,
            "state": "available",
            "notes": f"manual review accepts true abnormal samples only; generated abnormal tasks={abnormal_count}",
        }
    ]


def build_category_mapping() -> list[dict[str, object]]:
    return [
        {
            "sample_category": category,
            "target_output_box": output_box_id,
            "box_capacity": OUTPUT_BOX_CAPACITY,
            "category_hold_enabled": "true",
            "resume_condition": "operator clears or replaces output box, then category_resume is emitted",
            "notes": "normal samples are held when full; they are not routed to manual_review",
        }
        for category, output_box_id in CATEGORY_TO_BOX.items()
    ]


def build_tasks(
    occupancy_rows: list[dict[str, object]],
    tube_manifest: list[dict[str, object]],
    output_state: list[dict[str, object]],
) -> list[dict[str, object]]:
    occupancy_by_key = {
        (row["input_box_id"], row["slot_id"]): row for row in occupancy_rows if row["tube_present"] == "true"
    }
    output_state_by_box = {row["output_box_id"]: row for row in output_state}
    next_target_slot: defaultdict[str, int] = defaultdict(int)
    tasks: list[dict[str, object]] = []

    for index, sample in enumerate(tube_manifest, start=1):
        source = occupancy_by_key[(sample["input_box_id"], sample["source_slot_id"])]
        abnormal = sample["abnormal_flag"] == "true"

        if abnormal:
            target_type = "manual_review"
            target_box_id = "manual_review_01"
            target_slot_id = f"MR{index:02d}"
            initial_task_status = "queued_manual_review"
            notes = "true abnormal sample; route to manual_review"
        else:
            target_type = "output_box"
            target_box_id = sample["target_output_box"]
            target_state = output_state_by_box[target_box_id]["state"]
            if target_state == "full":
                target_slot_id = ""
                initial_task_status = "category_hold_pending"
                notes = "target category output box is full; hold category, do not route to manual_review"
            else:
                next_target_slot[target_box_id] += 1
                target_slot_id = f"S{next_target_slot[target_box_id]:02d}"
                initial_task_status = "queued_output"
                notes = "normal sample output task"

        tasks.append(
            {
                "task_id": f"TASK-7B1-{index:03d}",
                "tube_id": sample["tube_id"],
                "source_input_box_id": sample["input_box_id"],
                "source_slot_id": sample["source_slot_id"],
                "source_x_mm": source["x_mm"],
                "source_y_mm": source["y_mm"],
                "source_z_pick_mm": source["z_pick_mm"],
                "requires_scan": "false",
                "scan_station_id": "",
                "barcode_status": sample["barcode_status"],
                "sample_category": sample["sample_category"],
                "abnormal_flag": sample["abnormal_flag"],
                "target_type": target_type,
                "target_box_id": target_box_id,
                "target_slot_id": target_slot_id,
                "task_priority": sample["priority"],
                "initial_task_status": initial_task_status,
                "notes": notes,
            }
        )

    return tasks


def validate(
    occupancy_rows: list[dict[str, object]],
    tube_manifest: list[dict[str, object]],
    tasks: list[dict[str, object]],
    output_state: list[dict[str, object]],
    manual_review_state: list[dict[str, object]],
) -> tuple[str, list[str]]:
    issues: list[str] = []
    if len(occupancy_rows) != TOTAL_INPUT_SLOTS:
        issues.append("input slot total is not 96")
    if len({row["input_box_id"] for row in occupancy_rows}) != INPUT_BOX_COUNT:
        issues.append("input box count is not 4")
    for box_id in sorted({row["input_box_id"] for row in occupancy_rows}):
        if sum(1 for row in occupancy_rows if row["input_box_id"] == box_id) != SLOTS_PER_BOX:
            issues.append(f"{box_id} does not have 24 slots")
    if len({row["tube_id"] for row in tube_manifest}) != len(tube_manifest):
        issues.append("tube_id is not unique")
    for row in occupancy_rows:
        if row["tube_present"] == "true" and not row["tube_id"]:
            issues.append(f"occupied slot missing tube_id: {row['input_box_id']} {row['slot_id']}")
        if row["tube_present"] == "false" and row["tube_id"]:
            issues.append(f"empty slot has tube_id: {row['input_box_id']} {row['slot_id']}")

    task_tubes = {row["tube_id"] for row in tasks}
    empty_tubes = {row["tube_id"] for row in occupancy_rows if row["tube_present"] == "false" and row["tube_id"]}
    if task_tubes.intersection(empty_tubes):
        issues.append("empty slot generated pick task")

    task_by_tube = {row["tube_id"]: row for row in tasks}
    for sample in tube_manifest:
        task = task_by_tube.get(sample["tube_id"])
        if not task:
            issues.append(f"missing task for occupied tube {sample['tube_id']}")
            continue
        if sample["abnormal_flag"] == "true" and task["target_type"] != "manual_review":
            issues.append(f"abnormal sample not routed to manual_review: {sample['tube_id']}")
        if sample["abnormal_flag"] == "false" and task["target_type"] != "output_box":
            issues.append(f"normal sample not routed to output_box: {sample['tube_id']}")
        if sample["abnormal_flag"] == "false" and task["target_box_id"] != CATEGORY_TO_BOX[sample["sample_category"]]:
            issues.append(f"normal sample target mismatch: {sample['tube_id']}")

    for row in output_state:
        if int(row["capacity_slots"]) != OUTPUT_BOX_CAPACITY:
            issues.append(f"output capacity is not 24: {row['output_box_id']}")
    for row in manual_review_state:
        if int(row["capacity_slots"]) != MANUAL_REVIEW_CAPACITY:
            issues.append("manual review capacity is not 6")

    return ("PASS" if not issues else "FAIL", issues)


def write_summary(
    occupancy_rows: list[dict[str, object]],
    tube_manifest: list[dict[str, object]],
    tasks: list[dict[str, object]],
    validation_status: str,
    issues: list[str],
) -> list[dict[str, object]]:
    occupied_slots = sum(1 for row in occupancy_rows if row["tube_present"] == "true")
    empty_slots = TOTAL_INPUT_SLOTS - occupied_slots
    abnormal_count = sum(1 for row in tube_manifest if row["abnormal_flag"] == "true")
    normal_count = len(tube_manifest) - abnormal_count
    category_counts = Counter(row["sample_category"] for row in tube_manifest)
    status_counts = Counter(row["target_type"] for row in tasks)

    summary = [
        {"metric": "total_input_slots", "value": TOTAL_INPUT_SLOTS, "notes": "4 input boxes x 4 x 6"},
        {"metric": "occupied_slots", "value": occupied_slots, "notes": "tube_present=true"},
        {"metric": "empty_slots", "value": empty_slots, "notes": "empty slots skipped; no pick task"},
        {"metric": "normal_sample_count", "value": normal_count, "notes": "valid barcode and category_A-D"},
        {"metric": "abnormal_sample_count", "value": abnormal_count, "notes": "manual_review only"},
        {"metric": "generated_task_count", "value": len(tasks), "notes": "one task per occupied tube"},
        {"metric": "output_box_task_count", "value": status_counts.get("output_box", 0), "notes": "normal samples"},
        {"metric": "manual_review_task_count", "value": status_counts.get("manual_review", 0), "notes": "abnormal samples"},
        {"metric": "category_A_count", "value": category_counts.get("category_A", 0), "notes": ""},
        {"metric": "category_B_count", "value": category_counts.get("category_B", 0), "notes": ""},
        {"metric": "category_C_count", "value": category_counts.get("category_C", 0), "notes": ""},
        {"metric": "category_D_count", "value": category_counts.get("category_D", 0), "notes": "output_box_D starts full for hold test"},
        {"metric": "unknown_category_count", "value": category_counts.get("unknown", 0), "notes": "abnormal only"},
        {"metric": "validation_status", "value": validation_status, "notes": "; ".join(issues) if issues else "all checks passed"},
    ]
    write_csv(SUMMARY_CSV, ["metric", "value", "notes"], summary)
    return summary


def create_figures(occupancy_rows: list[dict[str, object]], tube_manifest: list[dict[str, object]]) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(9, 6), constrained_layout=True)
    for box_number, ax in enumerate(axes.flat, start=1):
        input_box_id = f"input_box_{box_number:02d}"
        matrix = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        for row in occupancy_rows:
            if row["input_box_id"] == input_box_id:
                matrix[int(row["slot_row"]) - 1][int(row["slot_col"]) - 1] = 1 if row["tube_present"] == "true" else 0
        ax.imshow(matrix, cmap="Greens", vmin=0, vmax=1)
        ax.set_title(input_box_id)
        ax.set_xticks(range(COLS), labels=[str(i) for i in range(1, COLS + 1)])
        ax.set_yticks(range(ROWS), labels=[str(i) for i in range(1, ROWS + 1)])
        ax.set_xlabel("slot_col")
        ax.set_ylabel("slot_row")
        for y in range(ROWS):
            for x in range(COLS):
                ax.text(x, y, "T" if matrix[y][x] else "-", ha="center", va="center", fontsize=8)
    fig.suptitle("Input Box Occupancy Map v1")
    fig.savefig(FIG_DIR / "input_box_occupancy_heatmap_v1.png", dpi=160)
    plt.close(fig)

    category_counts = Counter(row["sample_category"] for row in tube_manifest)
    category_labels = ["category_A", "category_B", "category_C", "category_D", "unknown"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(category_labels, [category_counts.get(label, 0) for label in category_labels], color="#4f81bd")
    ax.set_title("Sample Category Distribution v1")
    ax.set_ylabel("sample count")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "sample_category_distribution_v1.png", dpi=160)
    plt.close(fig)

    normal = sum(1 for row in tube_manifest if row["abnormal_flag"] == "false")
    abnormal = sum(1 for row in tube_manifest if row["abnormal_flag"] == "true")
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(["normal", "abnormal"], [normal, abnormal], color=["#70ad47", "#c0504d"])
    ax.set_title("Normal vs Abnormal Samples v1")
    ax.set_ylabel("sample count")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "normal_vs_abnormal_samples_v1.png", dpi=160)
    plt.close(fig)


def write_report(summary: list[dict[str, object]], validation_status: str) -> None:
    metrics = {row["metric"]: row["value"] for row in summary}
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(
        "\n".join(
            [
                "# Stage 7B-1 Input Occupancy Map and Sorting Task Manifest Simulation Report",
                "",
                "## Scope",
                "",
                "- This stage does not use a camera.",
                "- Tube occupancy is provided by the internal input occupancy table.",
                "- No CAD modeling, rendering, Stage 7A file edits, `legacy_v1` edits, or XY slider binding fixes are performed in this stage.",
                "- Stage 7A-3f XY slider binding remains a deferred mechanical integration issue and does not block this abstract simulation layer.",
                "",
                "## Input Occupancy",
                "",
                f"- Input boxes: 4.",
                f"- Input box format: 4 x 6.",
                f"- Total input slots: {metrics['total_input_slots']}.",
                f"- Occupied slots: {metrics['occupied_slots']}.",
                f"- Empty slots: {metrics['empty_slots']}.",
                "- Empty slots are recorded in the occupancy map only and do not generate pick tasks.",
                "",
                "## Sorting Logic",
                "",
                f"- Normal sample count: {metrics['normal_sample_count']}.",
                f"- Abnormal sample count: {metrics['abnormal_sample_count']}.",
                f"- Generated task count: {metrics['generated_task_count']}.",
                "- Valid category_A-D samples generate `output_box` tasks.",
                "- True abnormal samples generate `manual_review` tasks.",
                "- Manual review is reserved for missing label, invalid barcode, abnormal sample information, and unrecognized category.",
                "- A full output category triggers category_hold; after operator service it triggers category_resume.",
                "- A normal sample blocked by a full output box is not sent to manual_review.",
                "- `pick_failed` is treated as a robot execution failure state, not an abnormal sample classification.",
                "",
                "## Capacity State",
                "",
                "- Output boxes: 4, each 4 x 6 with 24 slots.",
                "- `output_box_D` is initialized as full to exercise category_hold logic.",
                "- Manual review capacity: 2 x 3, 6 slots.",
                "- Manual review capacity is not used for normal samples.",
                "",
                "## Simulation Use",
                "",
                "- This dataset is the base for later state machine execution, trajectory timing, cycle simulation, animation, and Isaac Sim visualization.",
                "- Python task logic and collision-envelope checks remain the priority for near-term simulation.",
                "",
                "## Generated Files",
                "",
                "- `06_simulation/input_box_occupancy_map_v1.csv`",
                "- `06_simulation/tube_sample_manifest_v1.csv`",
                "- `06_simulation/sorting_task_manifest_v1.csv`",
                "- `06_simulation/output_box_capacity_state_v1.csv`",
                "- `06_simulation/manual_review_capacity_state_v1.csv`",
                "- `06_simulation/category_mapping_v1.csv`",
                "- `06_simulation/input_occupancy_task_summary_v1.csv`",
                "- `06_simulation/figures/input_box_occupancy_heatmap_v1.png`",
                "- `06_simulation/figures/sample_category_distribution_v1.png`",
                "- `06_simulation/figures/normal_vs_abnormal_samples_v1.png`",
                "",
                "## Validation",
                "",
                f"- validation_status={validation_status}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    occupancy_rows = build_input_occupancy()
    tube_manifest = build_tube_manifest(occupancy_rows)
    output_state = build_output_state()
    manual_review_state = build_manual_review_state(
        sum(1 for row in tube_manifest if row["abnormal_flag"] == "true")
    )
    category_mapping = build_category_mapping()
    tasks = build_tasks(occupancy_rows, tube_manifest, output_state)

    public_occupancy = [{k: v for k, v in row.items() if not k.startswith("_")} for row in occupancy_rows]
    write_csv(
        INPUT_OCCUPANCY_CSV,
        [
            "input_box_id",
            "rack_type",
            "slot_row",
            "slot_col",
            "slot_id",
            "tube_present",
            "tube_id",
            "x_mm",
            "y_mm",
            "z_pick_mm",
            "slot_status",
            "notes",
        ],
        public_occupancy,
    )
    write_csv(
        TUBE_MANIFEST_CSV,
        [
            "tube_id",
            "input_box_id",
            "source_slot_id",
            "tube_present",
            "barcode_status",
            "sample_category",
            "abnormal_flag",
            "abnormal_reason",
            "target_output_box",
            "priority",
            "sample_status",
            "notes",
        ],
        tube_manifest,
    )
    write_csv(
        TASK_MANIFEST_CSV,
        [
            "task_id",
            "tube_id",
            "source_input_box_id",
            "source_slot_id",
            "source_x_mm",
            "source_y_mm",
            "source_z_pick_mm",
            "requires_scan",
            "scan_station_id",
            "barcode_status",
            "sample_category",
            "abnormal_flag",
            "target_type",
            "target_box_id",
            "target_slot_id",
            "task_priority",
            "initial_task_status",
            "notes",
        ],
        tasks,
    )
    write_csv(
        OUTPUT_BOX_STATE_CSV,
        ["output_box_id", "sample_category", "capacity_slots", "occupied_initial", "available_slots", "state", "notes"],
        output_state,
    )
    write_csv(
        MANUAL_REVIEW_STATE_CSV,
        ["manual_review_box_id", "capacity_slots", "occupied_initial", "available_slots", "state", "notes"],
        manual_review_state,
    )
    write_csv(
        CATEGORY_MAPPING_CSV,
        ["sample_category", "target_output_box", "box_capacity", "category_hold_enabled", "resume_condition", "notes"],
        category_mapping,
    )

    validation_status, issues = validate(occupancy_rows, tube_manifest, tasks, output_state, manual_review_state)
    summary = write_summary(occupancy_rows, tube_manifest, tasks, validation_status, issues)
    create_figures(occupancy_rows, tube_manifest)
    write_report(summary, validation_status)

    print(f"total_input_slots={TOTAL_INPUT_SLOTS}")
    print(f"occupied_slots={sum(1 for row in occupancy_rows if row['tube_present'] == 'true')}")
    print(f"empty_slots={sum(1 for row in occupancy_rows if row['tube_present'] == 'false')}")
    print(f"normal_sample_count={sum(1 for row in tube_manifest if row['abnormal_flag'] == 'false')}")
    print(f"abnormal_sample_count={sum(1 for row in tube_manifest if row['abnormal_flag'] == 'true')}")
    print(f"generated_task_count={len(tasks)}")
    print(f"validation_status={validation_status}")
    if issues:
        print("issues=" + "; ".join(issues))
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
