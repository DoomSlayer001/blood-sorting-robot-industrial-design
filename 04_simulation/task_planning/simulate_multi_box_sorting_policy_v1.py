from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = ROOT / "04_simulation" / "task_planning"
FIGURE_DIR = TASK_DIR / "figures"
REPORT_DIR = ROOT / "reports"

SLOT_CSV = TASK_DIR / "multi_box_slot_coordinates_v1.csv"
POLICY_DOC = TASK_DIR / "multi_box_sorting_policy_v1.md"
DATA_MODEL_DOC = TASK_DIR / "multi_box_data_model_v1.md"
STATE_MACHINE_DOC = TASK_DIR / "multi_box_sorting_state_machine_v1.md"
HEIGHT_RULES_DOC = TASK_DIR / "multi_box_pick_place_height_rules_v1.md"

MANIFEST_CSV = TASK_DIR / "multi_box_sample_manifest_v1.csv"
SIMULATION_CSV = TASK_DIR / "multi_box_sorting_policy_simulation_v1.csv"
PENDING_QUEUE_CSV = TASK_DIR / "multi_box_pending_queue_v1.csv"
BIN_OCCUPANCY_CSV = TASK_DIR / "multi_box_bin_occupancy_v1.csv"
OPERATOR_EVENTS_CSV = TASK_DIR / "multi_box_operator_events_v1.csv"
SUMMARY_CSV = TASK_DIR / "multi_box_sorting_policy_summary_v1.csv"
CATEGORY_COUNTS_FIGURE = FIGURE_DIR / "multi_box_policy_category_counts_v1.png"
HOLD_RESUME_FIGURE = FIGURE_DIR / "multi_box_hold_resume_timeline_v1.png"
BIN_OCCUPANCY_FIGURE = FIGURE_DIR / "multi_box_bin_occupancy_v1.png"
REPORT_PATH = REPORT_DIR / "stage_7c_multi_box_sorting_policy_simulation_report.md"

CATEGORY_KEYS = ["A", "B", "C", "D"]
CATEGORY_LABELS = {key: f"Category {key}" for key in CATEGORY_KEYS}
CATEGORY_TO_BOX = {key: f"category_{key}_output_box" for key in CATEGORY_KEYS}
CATEGORY_TO_ZONE = {key: f"output_{key}" for key in CATEGORY_KEYS}
OUTPUT_CAPACITY = 24
MANUAL_REVIEW_CAPACITY = 6

ABNORMAL_PLAN = {
    5: ("missing_label", "missing", "unknown"),
    19: ("scan_failed", "fail", "unknown"),
    37: ("barcode_invalid", "invalid", "unknown"),
    58: ("unknown_category", "success", "unknown"),
    73: ("sample_info_mismatch", "success", "Category C"),
    91: ("physical_tube_abnormal", "success", "Category D"),
}
NORMAL_CATEGORY_COUNTS = {"A": 23, "B": 23, "C": 22, "D": 22}
CAP_COLORS = ["purple", "yellow", "blue", "red"]
HEIGHTS = [75, 100, 75, 75, 100, 75]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def row_sort_key(row: dict[str, str]) -> tuple[int, str, int]:
    box = row["box_id"]
    box_index = int(box.rsplit("_", 1)[1]) if box.startswith("input_box_") else 0
    return (box_index, row["row"], int(row["col"]))


def slot_sort_key(row: dict[str, str]) -> tuple[str, int]:
    return (row["row"], int(row["col"]))


def load_slot_groups() -> tuple[list[dict[str, str]], dict[str, list[dict[str, str]]], list[dict[str, str]]]:
    rows = read_csv(SLOT_CSV)
    input_slots = sorted([row for row in rows if row["zone"] == "input"], key=row_sort_key)
    output_slots: dict[str, list[dict[str, str]]] = {}
    for key in CATEGORY_KEYS:
        box_id = CATEGORY_TO_BOX[key]
        output_slots[key] = sorted([row for row in rows if row["box_id"] == box_id], key=slot_sort_key)
    manual_slots = sorted([row for row in rows if row["zone"] == "manual_review"], key=slot_sort_key)
    return input_slots, output_slots, manual_slots


def normal_category_queue() -> list[str]:
    remaining = dict(NORMAL_CATEGORY_COUNTS)
    categories: list[str] = []
    while sum(remaining.values()) > 0:
        for key in CATEGORY_KEYS:
            if remaining[key] > 0:
                categories.append(key)
                remaining[key] -= 1
    return categories


def generate_manifest(input_slots: list[dict[str, str]]) -> list[dict[str, object]]:
    normal_categories = normal_category_queue()
    normal_index = 0
    rows: list[dict[str, object]] = []

    for index, slot in enumerate(input_slots, start=1):
        sample_id = f"MBOX-{index:03d}"
        cap_color = CAP_COLORS[(index - 1) % len(CAP_COLORS)]
        height = HEIGHTS[(index - 1) % len(HEIGHTS)]
        if index in ABNORMAL_PLAN:
            abnormal_reason, barcode_status, category = ABNORMAL_PLAN[index]
            is_abnormal = "yes"
            expected_target_zone = "manual_review"
            notes = "true abnormal sample for Stage 7C policy coverage"
        else:
            category_key = normal_categories[normal_index]
            normal_index += 1
            abnormal_reason = ""
            barcode_status = "success"
            category = CATEGORY_LABELS[category_key]
            is_abnormal = "no"
            expected_target_zone = CATEGORY_TO_ZONE[category_key]
            notes = "deterministic demo distribution; cap color is not a category guarantee"

        rows.append(
            {
                "sample_id": sample_id,
                "input_box_id": slot["box_id"],
                "input_slot_id": slot["slot_id"],
                "row": slot["row"],
                "col": slot["col"],
                "tube_height_mm": height,
                "cap_color": cap_color,
                "barcode_status": barcode_status,
                "category": category,
                "is_abnormal": is_abnormal,
                "abnormal_reason": abnormal_reason,
                "expected_target_zone": expected_target_zone,
                "notes": notes,
            }
        )
    return rows


class RunState:
    def __init__(self, run_id: str, output_slots: dict[str, list[dict[str, str]]], manual_slots: list[dict[str, str]]):
        self.run_id = run_id
        self.output_slots = output_slots
        self.manual_slots = manual_slots
        self.output_occupancy: dict[str, list[dict[str, str]]] = {key: [] for key in CATEGORY_KEYS}
        self.manual_occupancy: list[dict[str, str]] = []
        self.category_status = {key: "available" for key in CATEGORY_KEYS}
        self.category_capacity = {key: OUTPUT_CAPACITY for key in CATEGORY_KEYS}
        self.manual_capacity = MANUAL_REVIEW_CAPACITY
        self.step_id = 0
        self.event_id = 0
        self.pending_event_id = 0
        self.sim_rows: list[dict[str, object]] = []
        self.pending_rows: list[dict[str, object]] = []
        self.operator_events: list[dict[str, object]] = []
        self.paused = False

        if run_id == "forced_category_A_full":
            self.category_capacity["A"] = 4
        if run_id == "forced_manual_review_full":
            self.manual_capacity = 2

    def next_step(self) -> int:
        self.step_id += 1
        return self.step_id

    def next_event(self) -> str:
        self.event_id += 1
        return f"{self.run_id}_EVENT_{self.event_id:03d}"

    def next_pending_event(self) -> str:
        self.pending_event_id += 1
        return f"{self.run_id}_PENDING_{self.pending_event_id:03d}"

    def add_operator_event(self, event_type: str, category: str, trigger_step: int, action: str, response: str, notes: str) -> str:
        event_id = self.next_event()
        self.operator_events.append(
            {
                "run_id": self.run_id,
                "event_id": event_id,
                "event_type": event_type,
                "related_box_id": CATEGORY_TO_BOX.get(category, "manual_review_bin" if category == "manual_review" else ""),
                "related_category": category,
                "trigger_step": trigger_step,
                "operator_action": action,
                "system_response": response,
                "notes": notes,
            }
        )
        return event_id

    def add_sim_row(
        self,
        step_id: int,
        sample: dict[str, object],
        current_category_status: str,
        selected_action: str,
        target_zone: str,
        target_box_id: str,
        target_slot_id: str,
        pending_queue_action: str,
        operator_event: str,
        system_state: str,
        notes: str,
    ) -> None:
        self.sim_rows.append(
            {
                "run_id": self.run_id,
                "step_id": step_id,
                "sample_id": sample["sample_id"],
                "input_box_id": sample["input_box_id"],
                "input_slot_id": sample["input_slot_id"],
                "barcode_status": sample["barcode_status"],
                "category": sample["category"],
                "is_abnormal": sample["is_abnormal"],
                "current_category_status": current_category_status,
                "selected_action": selected_action,
                "target_zone": target_zone,
                "target_box_id": target_box_id,
                "target_slot_id": target_slot_id,
                "pending_queue_action": pending_queue_action,
                "operator_event": operator_event,
                "system_state": system_state,
                "notes": notes,
            }
        )

    def allocate_output(self, category: str, sample_id: str) -> str | None:
        if len(self.output_occupancy[category]) >= self.category_capacity[category]:
            return None
        slot = self.output_slots[category][len(self.output_occupancy[category])]["slot_id"]
        self.output_occupancy[category].append({"slot_id": slot, "sample_id": sample_id})
        return slot

    def allocate_manual_review(self, sample_id: str) -> str | None:
        if len(self.manual_occupancy) >= self.manual_capacity:
            return None
        slot = self.manual_slots[len(self.manual_occupancy)]["slot_id"]
        self.manual_occupancy.append({"slot_id": slot, "sample_id": sample_id})
        return slot

    def queue_pending(self, sample: dict[str, object], category: str, step_id: int, reason: str) -> None:
        self.pending_rows.append(
            {
                "run_id": self.run_id,
                "event_id": self.next_pending_event(),
                "sample_id": sample["sample_id"],
                "category": CATEGORY_LABELS[category],
                "input_box_id": sample["input_box_id"],
                "input_slot_id": sample["input_slot_id"],
                "pending_reason": reason,
                "hold_category": CATEGORY_LABELS[category],
                "queued_at_step": step_id,
                "released_at_step": "",
                "final_target_zone": "",
                "final_target_slot": "",
                "notes": "queued because category output box is held; not routed to manual review",
            }
        )


def category_key(sample: dict[str, object]) -> str | None:
    category = str(sample["category"])
    if category.startswith("Category "):
        return category.split()[-1]
    return None


def process_sample(state: RunState, sample: dict[str, object]) -> None:
    step_id = state.next_step()
    if sample["is_abnormal"] == "yes":
        slot = state.allocate_manual_review(str(sample["sample_id"]))
        if slot is None:
            event_id = state.add_operator_event(
                "manual_review_full_alarm",
                "manual_review",
                step_id,
                "operator clears manual review bin and acknowledges alarm",
                "PAUSE_ALARM",
                f"{sample['abnormal_reason']} requires manual review but no slot is available",
            )
            state.add_sim_row(step_id, sample, "not_applicable", "PAUSE_ALARM", "manual_review", "manual_review_bin", "", "none", event_id, "PAUSE_ALARM", "manual_review full on true abnormal sample")
            state.paused = True
            return
        state.add_sim_row(
            step_id,
            sample,
            "not_applicable",
            "MOVE_TO_MANUAL_REVIEW",
            "manual_review",
            "manual_review_bin",
            slot,
            "none",
            "",
            "COMPLETE_SAMPLE",
            "true abnormal sample routed to manual review",
        )
        return

    category = category_key(sample)
    if not category:
        slot = state.allocate_manual_review(str(sample["sample_id"]))
        state.add_sim_row(step_id, sample, "not_applicable", "MOVE_TO_MANUAL_REVIEW", "manual_review", "manual_review_bin", slot or "", "none", "", "COMPLETE_SAMPLE" if slot else "PAUSE_ALARM", "category parse fallback")
        return

    if state.category_status[category] == "held":
        state.queue_pending(sample, category, step_id, "category_hold")
        state.add_sim_row(
            step_id,
            sample,
            "held",
            "SKIP_HELD_CATEGORY",
            "",
            "",
            "",
            "queued",
            "",
            "CONTINUE_OTHER_CATEGORIES",
            "normal sample skipped because category output box is held",
        )
        return

    slot = state.allocate_output(category, str(sample["sample_id"]))
    if slot is not None:
        state.add_sim_row(
            step_id,
            sample,
            "available",
            "PLACE_TO_OUTPUT",
            CATEGORY_TO_ZONE[category],
            CATEGORY_TO_BOX[category],
            slot,
            "none",
            "",
            "COMPLETE_SAMPLE",
            "normal sample placed into category output box",
        )
        return

    state.category_status[category] = "held"
    event_id = state.add_operator_event(
        f"category_{category}_hold",
        category,
        step_id,
        "operator clear/replacement required",
        f"category_{category}_hold",
        "category output capacity reached; normal sample is not routed to manual review",
    )
    state.queue_pending(sample, category, step_id, "category_output_full")
    state.add_sim_row(
        step_id,
        sample,
        "held",
        "HOLD_CATEGORY",
        "",
        "",
        "",
        "queued",
        event_id,
        "CONTINUE_OTHER_CATEGORIES",
        "category output full triggers hold and pending queue",
    )


def release_pending_category(state: RunState, category: str) -> None:
    pending_for_category = [row for row in state.pending_rows if row["hold_category"] == CATEGORY_LABELS[category] and not row["released_at_step"]]
    if not pending_for_category:
        return
    clear_step = state.next_step()
    clear_event = state.add_operator_event(
        f"clear_or_replace_category_{category}_output_box",
        category,
        clear_step,
        f"clear_or_replace_category_{category}_output_box",
        f"category_{category}_available",
        "operator clears/replaces full output box before resuming pending samples",
    )
    state.output_occupancy[category] = []
    state.category_capacity[category] = OUTPUT_CAPACITY
    state.category_status[category] = "available"

    resume_step = state.next_step()
    resume_event = state.add_operator_event(
        f"resume_category_{category}",
        category,
        resume_step,
        f"resume_category_{category}",
        "pending_queue_released",
        "system resumes held category and processes queued samples",
    )

    sample_by_id = {row["sample_id"]: row for row in state.manifest_rows}
    for pending in pending_for_category:
        sample = sample_by_id[pending["sample_id"]]
        step_id = state.next_step()
        slot = state.allocate_output(category, str(sample["sample_id"]))
        pending["released_at_step"] = step_id
        pending["final_target_zone"] = CATEGORY_TO_ZONE[category]
        pending["final_target_slot"] = slot or ""
        pending["notes"] = "released after operator clear and category resume"
        state.add_sim_row(
            step_id,
            sample,
            "available",
            "PROCESS_RESUMED_PENDING",
            CATEGORY_TO_ZONE[category],
            CATEGORY_TO_BOX[category],
            slot or "",
            "released",
            f"{clear_event};{resume_event}",
            "COMPLETE_SAMPLE",
            "pending sample placed after category resume",
        )


def simulate_run(run_id: str, manifest_rows: list[dict[str, object]], output_slots: dict[str, list[dict[str, str]]], manual_slots: list[dict[str, str]]) -> RunState:
    state = RunState(run_id, output_slots, manual_slots)
    state.manifest_rows = manifest_rows
    for sample in manifest_rows:
        if state.paused:
            break
        process_sample(state, sample)

    if run_id == "forced_category_A_full" and not state.paused:
        release_pending_category(state, "A")
    return state


def occupancy_rows(state: RunState) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for category in CATEGORY_KEYS:
        box_id = CATEGORY_TO_BOX[category]
        occupied = {row["slot_id"]: row["sample_id"] for row in state.output_occupancy[category]}
        status = "held" if state.category_status[category] == "held" else "available"
        if state.run_id == "forced_category_A_full" and category == "A":
            status = "resumed" if state.category_status[category] == "available" else "held"
        for slot in state.output_slots[category]:
            slot_id = slot["slot_id"]
            rows.append(
                {
                    "run_id": state.run_id,
                    "zone": CATEGORY_TO_ZONE[category],
                    "box_id": box_id,
                    "category": CATEGORY_LABELS[category],
                    "slot_id": slot_id,
                    "occupied_by_sample_id": occupied.get(slot_id, ""),
                    "filled_count": len(state.output_occupancy[category]),
                    "capacity": OUTPUT_CAPACITY,
                    "box_status": status,
                    "notes": "normal category output; full category causes hold, not manual review",
                }
            )
    manual_occupied = {row["slot_id"]: row["sample_id"] for row in state.manual_occupancy}
    for slot in state.manual_slots:
        rows.append(
            {
                "run_id": state.run_id,
                "zone": "manual_review",
                "box_id": "manual_review_bin",
                "category": "manual_review",
                "slot_id": slot["slot_id"],
                "occupied_by_sample_id": manual_occupied.get(slot["slot_id"], ""),
                "filled_count": len(state.manual_occupancy),
                "capacity": state.manual_capacity,
                "box_status": "full" if len(state.manual_occupancy) >= state.manual_capacity else "available",
                "notes": "manual review stores true abnormal samples only",
            }
        )
    return rows


def plot_figures(manifest_rows: list[dict[str, object]], states: dict[str, RunState]) -> list[str]:
    generated: list[str] = []
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        return [f"matplotlib unavailable: {exc}"]

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    normal_counts = Counter()
    abnormal_count = 0
    for row in manifest_rows:
        if row["is_abnormal"] == "yes":
            abnormal_count += 1
        else:
            normal_counts[category_key(row) or "unknown"] += 1
    labels = ["A", "B", "C", "D", "abnormal"]
    values = [normal_counts["A"], normal_counts["B"], normal_counts["C"], normal_counts["D"], abnormal_count]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(labels, values, color=["#7b3294", "#d8b365", "#4393c3", "#d6604d", "#666666"])
    ax.set_title("Stage 7C Manifest Category Counts")
    ax.set_ylabel("sample count")
    fig.tight_layout()
    fig.savefig(CATEGORY_COUNTS_FIGURE, dpi=180)
    plt.close(fig)
    generated.append(str(CATEGORY_COUNTS_FIGURE))

    forced = states["forced_category_A_full"]
    event_steps = [int(row["trigger_step"]) for row in forced.operator_events]
    event_labels = [row["event_type"] for row in forced.operator_events]
    pending_steps = [int(row["queued_at_step"]) for row in forced.pending_rows]
    release_steps = [int(row["released_at_step"]) for row in forced.pending_rows if row["released_at_step"]]
    fig, ax = plt.subplots(figsize=(9, 4))
    if pending_steps:
        ax.scatter(pending_steps, [1] * len(pending_steps), label="pending queued", color="#d95f02")
    if release_steps:
        ax.scatter(release_steps, [2] * len(release_steps), label="pending released", color="#1b9e77")
    for step, label in zip(event_steps, event_labels):
        ax.axvline(step, color="#444444", linewidth=0.8, alpha=0.5)
        ax.text(step, 2.4, label, rotation=90, fontsize=7, va="bottom")
    ax.set_yticks([1, 2])
    ax.set_yticklabels(["queued", "released"])
    ax.set_xlabel("simulation step")
    ax.set_title("Forced Category A Hold / Resume Timeline")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(HOLD_RESUME_FIGURE, dpi=180)
    plt.close(fig)
    generated.append(str(HOLD_RESUME_FIGURE))

    baseline = states["baseline_multi_box_run"]
    occupancy = {CATEGORY_LABELS[key]: len(baseline.output_occupancy[key]) for key in CATEGORY_KEYS}
    occupancy["manual_review"] = len(baseline.manual_occupancy)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(list(occupancy.keys()), list(occupancy.values()), color=["#7b3294", "#d8b365", "#4393c3", "#d6604d", "#666666"])
    ax.axhline(24, color="#999999", linestyle="--", linewidth=0.8, label="category capacity")
    ax.axhline(6, color="#333333", linestyle=":", linewidth=0.8, label="manual review capacity")
    ax.set_title("Baseline Final Bin Occupancy")
    ax.set_ylabel("filled slots")
    ax.legend()
    fig.tight_layout()
    fig.savefig(BIN_OCCUPANCY_FIGURE, dpi=180)
    plt.close(fig)
    generated.append(str(BIN_OCCUPANCY_FIGURE))
    return generated


def summary_rows(manifest_rows: list[dict[str, object]], states: dict[str, RunState]) -> list[dict[str, object]]:
    normal_rows = [row for row in manifest_rows if row["is_abnormal"] == "no"]
    abnormal_rows = [row for row in manifest_rows if row["is_abnormal"] == "yes"]
    normal_counts = Counter(category_key(row) for row in normal_rows)
    baseline = states["baseline_multi_box_run"]
    forced_a = states["forced_category_A_full"]
    forced_review = states["forced_manual_review_full"]
    hold_events = [row for state in states.values() for row in state.operator_events if "hold" in row["event_type"]]
    alarm_events = [row for state in states.values() for row in state.operator_events if row["event_type"] == "manual_review_full_alarm"]
    pending_total = sum(len(state.pending_rows) for state in states.values())
    resumed_total = sum(1 for state in states.values() for row in state.pending_rows if row["released_at_step"])
    manual_review_used = len(baseline.manual_occupancy)

    baseline_status = "PASS_NO_ALARM" if not baseline.paused and not any(row["target_box_id"] == "manual_review_bin" and row["is_abnormal"] == "no" for row in baseline.sim_rows) else "NEEDS_REVIEW"
    forced_full_status = "PASS_HOLD_RESUME" if forced_a.pending_rows and all(row["released_at_step"] for row in forced_a.pending_rows) and not forced_a.paused else "NEEDS_REVIEW"
    forced_review_status = "PASS_PAUSE_ALARM_EXPECTED" if forced_review.paused and alarm_events else "NEEDS_REVIEW"
    return [
        {"metric": "total_samples", "value": len(manifest_rows), "unit": "sample", "notes": "generated from Stage 7B input slots"},
        {"metric": "normal_sample_count", "value": len(normal_rows), "unit": "sample", "notes": "normal samples routed to A/B/C/D"},
        {"metric": "abnormal_sample_count", "value": len(abnormal_rows), "unit": "sample", "notes": "true abnormal samples routed to manual review"},
        {"metric": "category_A_count", "value": normal_counts["A"], "unit": "sample", "notes": "normal Category A"},
        {"metric": "category_B_count", "value": normal_counts["B"], "unit": "sample", "notes": "normal Category B"},
        {"metric": "category_C_count", "value": normal_counts["C"], "unit": "sample", "notes": "normal Category C"},
        {"metric": "category_D_count", "value": normal_counts["D"], "unit": "sample", "notes": "normal Category D"},
        {"metric": "manual_review_used_count", "value": manual_review_used, "unit": "sample", "notes": "baseline true abnormal samples"},
        {"metric": "category_hold_event_count", "value": len(hold_events), "unit": "event", "notes": "injected forced category full scenario"},
        {"metric": "pending_queue_count", "value": pending_total, "unit": "sample", "notes": "queued while category held"},
        {"metric": "resumed_pending_count", "value": resumed_total, "unit": "sample", "notes": "released after operator clear/resume"},
        {"metric": "alarm_count", "value": len(alarm_events), "unit": "event", "notes": "manual review full injected scenario"},
        {"metric": "baseline_run_status", "value": baseline_status, "unit": "status", "notes": "baseline should have no alarm"},
        {"metric": "forced_category_full_status", "value": forced_full_status, "unit": "status", "notes": "category hold/resume expected"},
        {"metric": "forced_manual_review_full_status", "value": forced_review_status, "unit": "status", "notes": "pause alarm expected"},
    ]


def write_report(manifest_rows: list[dict[str, object]], states: dict[str, RunState], figures: list[str], summary: list[dict[str, object]]) -> None:
    metrics = {row["metric"]: row["value"] for row in summary}
    figure_text = ", ".join(Path(path).relative_to(ROOT).as_posix() if Path(path).is_file() else path for path in figures)
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Stage 7C Multi-box Sorting Policy Simulation Report",
                "",
                "- Goal: validate 96-sample multi-box sorting policy with category hold/resume and manual review rules.",
                f"- Input files: `{SLOT_CSV.relative_to(ROOT).as_posix()}`, `{POLICY_DOC.relative_to(ROOT).as_posix()}`, `{DATA_MODEL_DOC.relative_to(ROOT).as_posix()}`, `{STATE_MACHINE_DOC.relative_to(ROOT).as_posix()}`, `{HEIGHT_RULES_DOC.relative_to(ROOT).as_posix()}`.",
                "- Manifest generation: deterministic 96-sample set from four 4 x 6 input boxes, with interleaved Category A/B/C/D normals and six true abnormal samples.",
                f"- Baseline result: {metrics['baseline_run_status']}; normal samples route to category boxes and abnormal samples route to manual review.",
                f"- Forced Category A full result: {metrics['forced_category_full_status']}; Category A normal samples enter pending queue while B/C/D continue.",
                "- Pending queue behavior: held-category samples are skipped, queued, then released after operator clear/replacement and category resume.",
                f"- Forced manual review full result: {metrics['forced_manual_review_full_status']}; a true abnormal sample triggers PAUSE_ALARM when review capacity is unavailable.",
                "- Manual review distinction: normal samples blocked only by output full are not sent to manual review; only true abnormal samples use manual review.",
                f"- Summary: total_samples={metrics['total_samples']}, abnormal={metrics['abnormal_sample_count']}, pending={metrics['pending_queue_count']}, resumed={metrics['resumed_pending_count']}, alarms={metrics['alarm_count']}.",
                f"- Figures: {figure_text}",
                "",
                "## Limits",
                "",
                "- This is a discrete policy simulation, not motion timing, collision checking, or controller simulation.",
                "- Operator timing is represented as deterministic clear/resume events for v1 policy validation.",
                "",
                "## Next Steps",
                "",
                "- Stage 7D: multi-box trajectory update.",
                "- Stage 7E: multi-box cycle time update.",
                "- Stage 8: PID / dynamics simulation after multi-box task logic stabilizes.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    input_slots, output_slots, manual_slots = load_slot_groups()
    manifest_rows = generate_manifest(input_slots)
    states = {
        run_id: simulate_run(run_id, manifest_rows, output_slots, manual_slots)
        for run_id in ["baseline_multi_box_run", "forced_category_A_full", "forced_manual_review_full"]
    }
    figures = plot_figures(manifest_rows, states)
    summary = summary_rows(manifest_rows, states)
    write_report(manifest_rows, states, figures, summary)

    write_csv(
        MANIFEST_CSV,
        manifest_rows,
        ["sample_id", "input_box_id", "input_slot_id", "row", "col", "tube_height_mm", "cap_color", "barcode_status", "category", "is_abnormal", "abnormal_reason", "expected_target_zone", "notes"],
    )
    write_csv(
        SIMULATION_CSV,
        [row for state in states.values() for row in state.sim_rows],
        ["run_id", "step_id", "sample_id", "input_box_id", "input_slot_id", "barcode_status", "category", "is_abnormal", "current_category_status", "selected_action", "target_zone", "target_box_id", "target_slot_id", "pending_queue_action", "operator_event", "system_state", "notes"],
    )
    write_csv(
        PENDING_QUEUE_CSV,
        [row for state in states.values() for row in state.pending_rows],
        ["run_id", "event_id", "sample_id", "category", "input_box_id", "input_slot_id", "pending_reason", "hold_category", "queued_at_step", "released_at_step", "final_target_zone", "final_target_slot", "notes"],
    )
    write_csv(
        BIN_OCCUPANCY_CSV,
        [row for state in states.values() for row in occupancy_rows(state)],
        ["run_id", "zone", "box_id", "category", "slot_id", "occupied_by_sample_id", "filled_count", "capacity", "box_status", "notes"],
    )
    write_csv(
        OPERATOR_EVENTS_CSV,
        [row for state in states.values() for row in state.operator_events],
        ["run_id", "event_id", "event_type", "related_box_id", "related_category", "trigger_step", "operator_action", "system_response", "notes"],
    )
    write_csv(SUMMARY_CSV, summary, ["metric", "value", "unit", "notes"])

    metrics = {row["metric"]: row["value"] for row in summary}
    print(f"manifest_sample_count={metrics['total_samples']}")
    print(f"baseline_run_status={metrics['baseline_run_status']}")
    print(f"abnormal_sample_count={metrics['abnormal_sample_count']}")
    print(f"category_hold_event_count={metrics['category_hold_event_count']}")
    print(f"pending_queue_count={metrics['pending_queue_count']}")
    print(f"resumed_pending_count={metrics['resumed_pending_count']}")
    print(f"alarm_count={metrics['alarm_count']}")
    print(f"manifest_csv={MANIFEST_CSV}")
    print(f"simulation_csv={SIMULATION_CSV}")
    print(f"pending_queue_csv={PENDING_QUEUE_CSV}")
    print(f"report={REPORT_PATH}")
    return 0 if metrics["baseline_run_status"] == "PASS_NO_ALARM" and metrics["forced_category_full_status"] == "PASS_HOLD_RESUME" and metrics["forced_manual_review_full_status"] == "PASS_PAUSE_ALARM_EXPECTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
