from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"
FIG_DIR = SIM_DIR / "figures"
REPORT_DIR = ROOT / "reports"

INPUT_OCCUPANCY_CSV = SIM_DIR / "input_box_occupancy_map_v1.csv"
TUBE_MANIFEST_CSV = SIM_DIR / "tube_sample_manifest_v1.csv"
TASK_MANIFEST_CSV = SIM_DIR / "sorting_task_manifest_v1.csv"
CATEGORY_MAPPING_CSV = SIM_DIR / "category_mapping_v1.csv"

EVENT_LOG_CSV = SIM_DIR / "sorting_state_machine_event_log_v1.csv"
TASK_RESULT_CSV = SIM_DIR / "sorting_state_machine_task_result_v1.csv"
OUTPUT_TIMELINE_CSV = SIM_DIR / "output_box_occupancy_timeline_v1.csv"
MANUAL_TIMELINE_CSV = SIM_DIR / "manual_review_occupancy_timeline_v1.csv"
HOLD_RESUME_CSV = SIM_DIR / "category_hold_resume_events_v1.csv"
PENDING_QUEUE_CSV = SIM_DIR / "pending_queue_log_v1.csv"
ABNORMAL_LOG_CSV = SIM_DIR / "abnormal_handling_log_v1.csv"
PICK_FAILURE_CSV = SIM_DIR / "pick_failure_log_v1.csv"
SUMMARY_CSV = SIM_DIR / "sorting_state_machine_summary_v1.csv"
REPORT_MD = REPORT_DIR / "stage_7b2_sorting_state_machine_simulation_report.md"

OUTPUT_CAPACITY = 24
MANUAL_REVIEW_CAPACITY = 6

VALID_NORMAL_CATEGORIES = {"category_A", "category_B", "category_C", "category_D"}
ABNORMAL_BARCODE_STATUS = {
    "missing_label",
    "invalid_barcode",
    "abnormal_sample_info",
    "unknown_category",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def bool_text(value: bool) -> str:
    return "true" if value else "false"


@dataclass
class ScenarioConfig:
    scenario_id: str
    output_initial: dict[str, int]
    manual_capacity: int = MANUAL_REVIEW_CAPACITY
    pick_failures: dict[str, int] = field(default_factory=dict)
    service_full_categories: bool = False


@dataclass
class SimulationState:
    scenario_id: str
    output_occupied: dict[str, int]
    manual_occupied: int = 0
    manual_capacity: int = MANUAL_REVIEW_CAPACITY
    held_categories: set[str] = field(default_factory=set)
    pending_by_category: dict[str, list[dict[str, str]]] = field(default_factory=lambda: defaultdict(list))
    event_index: int = 0
    queue_event_index: int = 0
    hold_event_index: int = 0

    def output_state(self, output_box_id: str) -> str:
        occupied = self.output_occupied[output_box_id]
        if occupied >= OUTPUT_CAPACITY:
            return "full"
        if OUTPUT_CAPACITY - occupied <= 4:
            return "near_full"
        return "available"

    def manual_state(self) -> str:
        if self.manual_occupied >= self.manual_capacity:
            return "full"
        if self.manual_capacity - self.manual_occupied <= 1:
            return "near_full"
        return "available"

    def pending_size(self) -> int:
        return sum(len(items) for items in self.pending_by_category.values())


def make_scenarios(category_to_box: dict[str, str], tasks: list[dict[str, str]]) -> list[ScenarioConfig]:
    pick_failure_ids = {
        tasks[1]["task_id"]: 1,  # retry once and complete
        tasks[8]["task_id"]: 2,  # retry once, still fails, operator check
    }
    return [
        ScenarioConfig(
            scenario_id="baseline",
            output_initial={box: 0 for box in category_to_box.values()},
            manual_capacity=MANUAL_REVIEW_CAPACITY,
        ),
        ScenarioConfig(
            scenario_id="forced_category_A_full",
            output_initial={
                category_to_box["category_A"]: OUTPUT_CAPACITY,
                category_to_box["category_B"]: 0,
                category_to_box["category_C"]: 0,
                category_to_box["category_D"]: 0,
            },
            manual_capacity=MANUAL_REVIEW_CAPACITY,
            service_full_categories=True,
        ),
        ScenarioConfig(
            scenario_id="manual_review_limited_capacity",
            output_initial={box: 0 for box in category_to_box.values()},
            manual_capacity=3,
        ),
        ScenarioConfig(
            scenario_id="pick_failure_test",
            output_initial={box: 0 for box in category_to_box.values()},
            manual_capacity=MANUAL_REVIEW_CAPACITY,
            pick_failures=pick_failure_ids,
        ),
    ]


class SimulationRunner:
    def __init__(self) -> None:
        self.occupancy = read_csv(INPUT_OCCUPANCY_CSV)
        self.samples = read_csv(TUBE_MANIFEST_CSV)
        self.tasks = read_csv(TASK_MANIFEST_CSV)
        self.category_mapping = read_csv(CATEGORY_MAPPING_CSV)
        self.sample_by_tube = {row["tube_id"]: row for row in self.samples}
        self.category_to_box = {
            row["sample_category"]: row["target_output_box"] for row in self.category_mapping
        }
        self.rows: dict[str, list[dict[str, object]]] = {
            "events": [],
            "results": [],
            "output_timeline": [],
            "manual_timeline": [],
            "hold_resume": [],
            "pending": [],
            "abnormal": [],
            "pick_failure": [],
            "summary": [],
        }

    def add_event(
        self,
        state: SimulationState,
        task: dict[str, str],
        state_before: str,
        event: str,
        state_after: str,
        output_before: str = "",
        output_after: str = "",
        manual_before: str = "",
        manual_after: str = "",
        notes: str = "",
    ) -> None:
        state.event_index += 1
        self.rows["events"].append(
            {
                "scenario_id": state.scenario_id,
                "event_index": state.event_index,
                "timestamp_step": state.event_index,
                "task_id": task.get("task_id", ""),
                "tube_id": task.get("tube_id", ""),
                "state_before": state_before,
                "event": event,
                "state_after": state_after,
                "source_input_box_id": task.get("source_input_box_id", ""),
                "source_slot_id": task.get("source_slot_id", ""),
                "barcode_status": task.get("barcode_status", ""),
                "sample_category": task.get("sample_category", ""),
                "abnormal_flag": task.get("abnormal_flag", ""),
                "target_type": task.get("target_type", ""),
                "target_box_id": task.get("target_box_id", ""),
                "target_slot_id": task.get("target_slot_id", ""),
                "output_box_state_before": output_before,
                "output_box_state_after": output_after,
                "manual_review_state_before": manual_before,
                "manual_review_state_after": manual_after,
                "pending_queue_size": state.pending_size(),
                "notes": notes,
            }
        )

    def add_output_timeline(self, state: SimulationState, output_box_id: str, event: str) -> None:
        occupied = state.output_occupied[output_box_id]
        self.rows["output_timeline"].append(
            {
                "scenario_id": state.scenario_id,
                "timestamp_step": state.event_index,
                "output_box_id": output_box_id,
                "occupied_slots": occupied,
                "available_slots": OUTPUT_CAPACITY - occupied,
                "state": state.output_state(output_box_id),
                "event": event,
                "notes": "output capacity is capped at 24",
            }
        )

    def add_manual_timeline(self, state: SimulationState, event: str) -> None:
        self.rows["manual_timeline"].append(
            {
                "scenario_id": state.scenario_id,
                "timestamp_step": state.event_index,
                "manual_review_box_id": "manual_review_01",
                "occupied_slots": state.manual_occupied,
                "available_slots": state.manual_capacity - state.manual_occupied,
                "capacity_slots": state.manual_capacity,
                "state": state.manual_state(),
                "event": event,
                "notes": "manual review is reserved for true abnormal samples",
            }
        )

    def add_hold_event(
        self,
        state: SimulationState,
        sample_category: str,
        output_box_id: str,
        event_type: str,
        reason: str,
        before: int,
        after: int,
        action_required: bool,
        action_completed: bool,
        notes: str,
    ) -> None:
        state.hold_event_index += 1
        self.rows["hold_resume"].append(
            {
                "scenario_id": state.scenario_id,
                "event_index": state.hold_event_index,
                "sample_category": sample_category,
                "output_box_id": output_box_id,
                "event_type": event_type,
                "reason": reason,
                "pending_queue_size_before": before,
                "pending_queue_size_after": after,
                "operator_action_required": bool_text(action_required),
                "operator_action_completed": bool_text(action_completed),
                "notes": notes,
            }
        )

    def add_pending_event(
        self,
        state: SimulationState,
        task: dict[str, str],
        queue_action: str,
        reason: str,
        notes: str,
    ) -> None:
        state.queue_event_index += 1
        self.rows["pending"].append(
            {
                "scenario_id": state.scenario_id,
                "queue_event_index": state.queue_event_index,
                "tube_id": task["tube_id"],
                "task_id": task["task_id"],
                "sample_category": task["sample_category"],
                "target_output_box": task["target_box_id"],
                "queue_action": queue_action,
                "reason": reason,
                "queue_size_after": state.pending_size(),
                "notes": notes,
            }
        )

    def add_result(
        self,
        scenario_id: str,
        task: dict[str, str],
        final_status: str,
        placed_successfully: bool,
        went_to_manual_review: bool,
        entered_pending_queue: bool,
        resumed_from_pending: bool,
        pick_failed: bool,
        retry_count: int,
        notes: str,
    ) -> None:
        self.rows["results"].append(
            {
                "scenario_id": scenario_id,
                "task_id": task["task_id"],
                "tube_id": task["tube_id"],
                "source_input_box_id": task["source_input_box_id"],
                "source_slot_id": task["source_slot_id"],
                "barcode_status": task["barcode_status"],
                "sample_category": task["sample_category"],
                "abnormal_flag": task["abnormal_flag"],
                "target_type": task["target_type"],
                "target_box_id": task["target_box_id"],
                "target_slot_id": task.get("target_slot_id", ""),
                "final_status": final_status,
                "placed_successfully": bool_text(placed_successfully),
                "went_to_manual_review": bool_text(went_to_manual_review),
                "entered_pending_queue": bool_text(entered_pending_queue),
                "resumed_from_pending": bool_text(resumed_from_pending),
                "pick_failed": bool_text(pick_failed),
                "retry_count": retry_count,
                "notes": notes,
            }
        )

    def handle_pick_failure(
        self, state: SimulationState, task: dict[str, str], attempts_to_fail: int
    ) -> tuple[bool, int, str]:
        if attempts_to_fail <= 0:
            return False, 0, ""
        first_note = "injected pick failure; execution failure only, not abnormal sample"
        self.add_event(
            state,
            task,
            "MOVE_TO_PICK",
            "pick_failed",
            "RETRY_PICK" if attempts_to_fail == 1 else "PICK_ERROR",
            notes=first_note,
        )
        self.rows["pick_failure"].append(
            {
                "scenario_id": state.scenario_id,
                "task_id": task["task_id"],
                "tube_id": task["tube_id"],
                "sample_category": task["sample_category"],
                "abnormal_flag": task["abnormal_flag"],
                "failure_event": "pick_failed",
                "retry_count": 1,
                "final_pick_status": "retry_completed" if attempts_to_fail == 1 else "operator_check_required",
                "notes": first_note,
            }
        )
        if attempts_to_fail == 1:
            self.add_event(state, task, "RETRY_PICK", "retry_success", "GRIP_TUBE", notes="retry_once succeeded")
            return False, 1, "pick_failed_retried_completed"
        self.add_event(
            state,
            task,
            "RETRY_PICK",
            "retry_failed",
            "skipped_for_operator_check",
            notes="retry failed; do not route normal sample to manual_review",
        )
        return True, 1, "pick_failed_needs_operator_check"

    def complete_output(
        self,
        state: SimulationState,
        task: dict[str, str],
        resumed_from_pending: bool = False,
        entered_pending_queue: bool = False,
        pick_retried_status: str = "",
        retry_count: int = 0,
    ) -> None:
        output_box_id = task["target_box_id"]
        before = state.output_state(output_box_id)
        state.output_occupied[output_box_id] += 1
        after = state.output_state(output_box_id)
        self.add_event(
            state,
            task,
            "MOVE_TO_PLACE",
            "place_output_box",
            "UPDATE_TABLE",
            output_before=before,
            output_after=after,
            notes="normal sample placed in mapped output box",
        )
        self.add_output_timeline(state, output_box_id, "place_output_box")
        final_status = pick_retried_status or "completed_output"
        self.add_result(
            state.scenario_id,
            task,
            final_status,
            placed_successfully=True,
            went_to_manual_review=False,
            entered_pending_queue=entered_pending_queue,
            resumed_from_pending=resumed_from_pending,
            pick_failed=bool(pick_retried_status),
            retry_count=retry_count,
            notes="normal sample completed to output box",
        )

    def complete_manual_review(self, state: SimulationState, task: dict[str, str]) -> None:
        manual_before = state.manual_state()
        if state.manual_occupied >= state.manual_capacity:
            self.add_event(
                state,
                task,
                "CHECK_MANUAL_REVIEW_CAPACITY",
                "manual_review_full",
                "PAUSE_FOR_OPERATOR",
                manual_before=manual_before,
                manual_after=manual_before,
                notes="abnormal sample paused because manual_review capacity is full",
            )
            self.rows["abnormal"].append(
                {
                    "scenario_id": state.scenario_id,
                    "tube_id": task["tube_id"],
                    "task_id": task["task_id"],
                    "barcode_status": task["barcode_status"],
                    "abnormal_reason": task["barcode_status"],
                    "manual_review_slot_id": "",
                    "manual_review_status": "paused_manual_review_full",
                    "notes": "true abnormal sample paused; normal samples are not routed here",
                }
            )
            self.add_result(
                state.scenario_id,
                task,
                "paused_manual_review_full",
                placed_successfully=False,
                went_to_manual_review=False,
                entered_pending_queue=False,
                resumed_from_pending=False,
                pick_failed=False,
                retry_count=0,
                notes="manual_review full alarm/pause",
            )
            return

        state.manual_occupied += 1
        slot_id = f"MR{state.manual_occupied:02d}"
        manual_after = state.manual_state()
        self.add_event(
            state,
            task,
            "HANDLE_EXCEPTION",
            "place_manual_review",
            "UPDATE_TABLE",
            manual_before=manual_before,
            manual_after=manual_after,
            notes="true abnormal sample placed in manual_review",
        )
        self.add_manual_timeline(state, "place_manual_review")
        self.rows["abnormal"].append(
            {
                "scenario_id": state.scenario_id,
                "tube_id": task["tube_id"],
                "task_id": task["task_id"],
                "barcode_status": task["barcode_status"],
                "abnormal_reason": task["barcode_status"],
                "manual_review_slot_id": slot_id,
                "manual_review_status": "completed_manual_review",
                "notes": "manual_review is used only for true abnormal samples",
            }
        )
        self.add_result(
            state.scenario_id,
            task,
            "completed_manual_review",
            placed_successfully=True,
            went_to_manual_review=True,
            entered_pending_queue=False,
            resumed_from_pending=False,
            pick_failed=False,
            retry_count=0,
            notes="true abnormal sample completed to manual_review",
        )

    def enqueue_pending(self, state: SimulationState, task: dict[str, str]) -> None:
        category = task["sample_category"]
        output_box_id = task["target_box_id"]
        before = state.pending_size()
        if category not in state.held_categories:
            state.held_categories.add(category)
            self.add_hold_event(
                state,
                category,
                output_box_id,
                "category_hold",
                "output_box_full",
                before,
                before,
                True,
                False,
                "normal samples for this category enter pending queue, not manual_review",
            )
            self.add_event(
                state,
                task,
                "CHECK_CATEGORY_AVAILABLE",
                "category_hold",
                "WAIT_OUTPUT_BOX_SERVICE",
                output_before=state.output_state(output_box_id),
                output_after=state.output_state(output_box_id),
                notes="output full; category hold starts",
            )
        state.pending_by_category[category].append(task)
        self.add_pending_event(
            state,
            task,
            "enqueue",
            "output_box_full",
            "normal sample waits for category_resume",
        )

    def service_and_resume(self, state: SimulationState) -> None:
        for category in sorted(list(state.held_categories)):
            pending_items = state.pending_by_category[category]
            if not pending_items:
                continue
            output_box_id = self.category_to_box[category]
            before = state.pending_size()
            self.add_hold_event(
                state,
                category,
                output_box_id,
                "operator_service_required",
                "pending_queue_nonempty",
                before,
                before,
                True,
                False,
                "operator must clear or replace full output box",
            )
            state.output_occupied[output_box_id] = 0
            self.add_hold_event(
                state,
                category,
                output_box_id,
                "operator_cleared_output_box",
                "operator_service_completed",
                before,
                before,
                False,
                True,
                "output box reset to empty for resumed category",
            )
            self.add_output_timeline(state, output_box_id, "operator_cleared_output_box")
            self.add_hold_event(
                state,
                category,
                output_box_id,
                "category_resume",
                "output_box_available",
                before,
                before,
                False,
                True,
                "resume pending queue for held category",
            )

            while pending_items:
                task = pending_items.pop(0)
                self.add_pending_event(
                    state,
                    task,
                    "dequeue_resume",
                    "category_resume",
                    "pending normal sample resumes output placement",
                )
                self.complete_output(
                    state,
                    task,
                    resumed_from_pending=True,
                    entered_pending_queue=True,
                )
            state.held_categories.remove(category)

    def run_scenario(self, config: ScenarioConfig) -> None:
        state = SimulationState(
            scenario_id=config.scenario_id,
            output_occupied=dict(config.output_initial),
            manual_capacity=config.manual_capacity,
        )
        for output_box_id in sorted(state.output_occupied):
            self.add_output_timeline(state, output_box_id, "scenario_start")
        self.add_manual_timeline(state, "scenario_start")

        pending_task_ids: set[str] = set()
        for task in self.tasks:
            abnormal = task["abnormal_flag"] == "true"
            if task["tube_id"] not in self.sample_by_tube:
                continue

            self.add_event(
                state,
                task,
                "IDLE",
                "load_task",
                "SELECT_NEXT_TUBE",
                notes="tube_present=true task from Stage 7B-1 manifest",
            )

            pick_blocked, retry_count, retry_status = self.handle_pick_failure(
                state, task, config.pick_failures.get(task["task_id"], 0)
            )
            if pick_blocked:
                self.add_result(
                    state.scenario_id,
                    task,
                    "pick_failed_needs_operator_check",
                    placed_successfully=False,
                    went_to_manual_review=False,
                    entered_pending_queue=False,
                    resumed_from_pending=False,
                    pick_failed=True,
                    retry_count=retry_count,
                    notes="pick failure is not abnormal classification",
                )
                continue

            if abnormal:
                self.complete_manual_review(state, task)
                continue

            category = task["sample_category"]
            output_box_id = task["target_box_id"]
            if category in state.held_categories or state.output_occupied[output_box_id] >= OUTPUT_CAPACITY:
                self.enqueue_pending(state, task)
                pending_task_ids.add(task["task_id"])
                continue

            self.complete_output(
                state,
                task,
                pick_retried_status=retry_status,
                retry_count=retry_count,
            )

        if config.service_full_categories:
            self.service_and_resume(state)
        else:
            for category, items in state.pending_by_category.items():
                for task in items:
                    self.add_pending_event(
                        state,
                        task,
                        "remain_pending",
                        "no_operator_service_in_scenario",
                        "task remains pending at scenario end",
                    )
                    self.add_result(
                        state.scenario_id,
                        task,
                        "pending_waiting_resume",
                        placed_successfully=False,
                        went_to_manual_review=False,
                        entered_pending_queue=True,
                        resumed_from_pending=False,
                        pick_failed=False,
                        retry_count=0,
                        notes="pending queue not resumed in this scenario",
                    )

        self.add_summary_for_scenario(config.scenario_id, config.manual_capacity)

    def add_summary_for_scenario(self, scenario_id: str, manual_capacity: int) -> None:
        results = [row for row in self.rows["results"] if row["scenario_id"] == scenario_id]
        events = [row for row in self.rows["hold_resume"] if row["scenario_id"] == scenario_id]
        pending_rows = [row for row in self.rows["pending"] if row["scenario_id"] == scenario_id]
        abnormal_rows = [row for row in self.rows["abnormal"] if row["scenario_id"] == scenario_id]
        pick_rows = [row for row in self.rows["pick_failure"] if row["scenario_id"] == scenario_id]
        status_counts = Counter(row["final_status"] for row in results)
        self.rows["summary"].append(
            {
                "scenario_id": scenario_id,
                "generated_task_count": len(self.tasks),
                "completed_output_count": status_counts.get("completed_output", 0)
                + status_counts.get("pick_failed_retried_completed", 0),
                "completed_manual_review_count": status_counts.get("completed_manual_review", 0),
                "pending_waiting_resume_count": status_counts.get("pending_waiting_resume", 0),
                "paused_manual_review_full_count": status_counts.get("paused_manual_review_full", 0),
                "pick_failed_needs_operator_check_count": status_counts.get("pick_failed_needs_operator_check", 0),
                "category_hold_count": sum(1 for row in events if row["event_type"] == "category_hold"),
                "category_resume_count": sum(1 for row in events if row["event_type"] == "category_resume"),
                "pending_enqueue_count": sum(1 for row in pending_rows if row["queue_action"] == "enqueue"),
                "pending_dequeue_resume_count": sum(1 for row in pending_rows if row["queue_action"] == "dequeue_resume"),
                "abnormal_handled_count": sum(
                    1 for row in abnormal_rows if row["manual_review_status"] == "completed_manual_review"
                ),
                "manual_review_capacity": manual_capacity,
                "manual_review_normal_sample_count": sum(
                    1 for row in results if row["abnormal_flag"] == "false" and row["went_to_manual_review"] == "true"
                ),
                "pick_failed_count": len(pick_rows),
                "notes": "scenario summary generated by deterministic Stage 7B-2 simulation",
            }
        )

    def validate_internal(self) -> str:
        issues: list[str] = []
        scenario_ids = {row["scenario_id"] for row in self.rows["summary"]}
        for scenario_id in scenario_ids:
            results = [row for row in self.rows["results"] if row["scenario_id"] == scenario_id]
            if len(results) != len(self.tasks):
                issues.append(f"{scenario_id}: task result count does not match generated task count")
            if any(row["abnormal_flag"] == "false" and row["went_to_manual_review"] == "true" for row in results):
                issues.append(f"{scenario_id}: normal sample entered manual_review")

        for row in self.rows["output_timeline"]:
            if int(row["occupied_slots"]) > OUTPUT_CAPACITY:
                issues.append(f"{row['scenario_id']}: output capacity exceeded")
        for row in self.rows["manual_timeline"]:
            if int(row["occupied_slots"]) > int(row["capacity_slots"]):
                issues.append(f"{row['scenario_id']}: manual review capacity exceeded")
            if int(row["capacity_slots"]) > MANUAL_REVIEW_CAPACITY:
                issues.append(f"{row['scenario_id']}: manual review capacity greater than 6")

        self.validation_issues = issues
        return "PASS" if not issues else "FAIL"

    def write_outputs(self, validation_status: str) -> None:
        write_csv(
            EVENT_LOG_CSV,
            [
                "scenario_id",
                "event_index",
                "timestamp_step",
                "task_id",
                "tube_id",
                "state_before",
                "event",
                "state_after",
                "source_input_box_id",
                "source_slot_id",
                "barcode_status",
                "sample_category",
                "abnormal_flag",
                "target_type",
                "target_box_id",
                "target_slot_id",
                "output_box_state_before",
                "output_box_state_after",
                "manual_review_state_before",
                "manual_review_state_after",
                "pending_queue_size",
                "notes",
            ],
            self.rows["events"],
        )
        write_csv(
            TASK_RESULT_CSV,
            [
                "scenario_id",
                "task_id",
                "tube_id",
                "source_input_box_id",
                "source_slot_id",
                "barcode_status",
                "sample_category",
                "abnormal_flag",
                "target_type",
                "target_box_id",
                "target_slot_id",
                "final_status",
                "placed_successfully",
                "went_to_manual_review",
                "entered_pending_queue",
                "resumed_from_pending",
                "pick_failed",
                "retry_count",
                "notes",
            ],
            self.rows["results"],
        )
        write_csv(
            OUTPUT_TIMELINE_CSV,
            [
                "scenario_id",
                "timestamp_step",
                "output_box_id",
                "occupied_slots",
                "available_slots",
                "state",
                "event",
                "notes",
            ],
            self.rows["output_timeline"],
        )
        write_csv(
            MANUAL_TIMELINE_CSV,
            [
                "scenario_id",
                "timestamp_step",
                "manual_review_box_id",
                "occupied_slots",
                "available_slots",
                "capacity_slots",
                "state",
                "event",
                "notes",
            ],
            self.rows["manual_timeline"],
        )
        write_csv(
            HOLD_RESUME_CSV,
            [
                "scenario_id",
                "event_index",
                "sample_category",
                "output_box_id",
                "event_type",
                "reason",
                "pending_queue_size_before",
                "pending_queue_size_after",
                "operator_action_required",
                "operator_action_completed",
                "notes",
            ],
            self.rows["hold_resume"],
        )
        write_csv(
            PENDING_QUEUE_CSV,
            [
                "scenario_id",
                "queue_event_index",
                "tube_id",
                "task_id",
                "sample_category",
                "target_output_box",
                "queue_action",
                "reason",
                "queue_size_after",
                "notes",
            ],
            self.rows["pending"],
        )
        write_csv(
            ABNORMAL_LOG_CSV,
            [
                "scenario_id",
                "tube_id",
                "task_id",
                "barcode_status",
                "abnormal_reason",
                "manual_review_slot_id",
                "manual_review_status",
                "notes",
            ],
            self.rows["abnormal"],
        )
        write_csv(
            PICK_FAILURE_CSV,
            [
                "scenario_id",
                "task_id",
                "tube_id",
                "sample_category",
                "abnormal_flag",
                "failure_event",
                "retry_count",
                "final_pick_status",
                "notes",
            ],
            self.rows["pick_failure"],
        )
        write_csv(
            SUMMARY_CSV,
            [
                "scenario_id",
                "generated_task_count",
                "completed_output_count",
                "completed_manual_review_count",
                "pending_waiting_resume_count",
                "paused_manual_review_full_count",
                "pick_failed_needs_operator_check_count",
                "category_hold_count",
                "category_resume_count",
                "pending_enqueue_count",
                "pending_dequeue_resume_count",
                "abnormal_handled_count",
                "manual_review_capacity",
                "manual_review_normal_sample_count",
                "pick_failed_count",
                "notes",
            ],
            self.rows["summary"]
            + [
                {
                    "scenario_id": "validation",
                    "generated_task_count": len(self.tasks),
                    "completed_output_count": "",
                    "completed_manual_review_count": "",
                    "pending_waiting_resume_count": "",
                    "paused_manual_review_full_count": "",
                    "pick_failed_needs_operator_check_count": "",
                    "category_hold_count": "",
                    "category_resume_count": "",
                    "pending_enqueue_count": "",
                    "pending_dequeue_resume_count": "",
                    "abnormal_handled_count": "",
                    "manual_review_capacity": "",
                    "manual_review_normal_sample_count": sum(
                        1
                        for row in self.rows["results"]
                        if row["abnormal_flag"] == "false" and row["went_to_manual_review"] == "true"
                    ),
                    "pick_failed_count": len(self.rows["pick_failure"]),
                    "notes": f"validation_status={validation_status}",
                }
            ],
        )
        self.write_figures()
        self.write_report(validation_status)

    def write_figures(self) -> None:
        FIG_DIR.mkdir(parents=True, exist_ok=True)
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        summary = [row for row in self.rows["summary"] if row["scenario_id"] != "validation"]
        labels = [row["scenario_id"] for row in summary]

        fig, ax = plt.subplots(figsize=(10, 4))
        status_keys = [
            "completed_output_count",
            "completed_manual_review_count",
            "paused_manual_review_full_count",
            "pick_failed_needs_operator_check_count",
        ]
        bottoms = [0] * len(labels)
        colors = ["#70ad47", "#5b9bd5", "#c0504d", "#ffc000"]
        for key, color in zip(status_keys, colors):
            values = [int(row[key]) for row in summary]
            ax.bar(labels, values, bottom=bottoms, label=key, color=color)
            bottoms = [left + value for left, value in zip(bottoms, values)]
        ax.set_title("Sorting State Machine Task Status v1")
        ax.set_ylabel("task count")
        ax.tick_params(axis="x", rotation=20)
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "sorting_state_machine_task_status_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(10, 4))
        for scenario_id in labels:
            rows = [row for row in self.rows["output_timeline"] if row["scenario_id"] == scenario_id]
            steps = list(range(len(rows)))
            occupied = [int(row["occupied_slots"]) for row in rows]
            ax.plot(steps, occupied, label=scenario_id)
        ax.set_title("Output Box Occupancy Timeline v1")
        ax.set_xlabel("timeline row")
        ax.set_ylabel("occupied slots")
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "output_box_occupancy_timeline_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4))
        hold_counts = [
            sum(1 for row in self.rows["hold_resume"] if row["scenario_id"] == scenario_id and row["event_type"] == "category_hold")
            for scenario_id in labels
        ]
        resume_counts = [
            sum(1 for row in self.rows["hold_resume"] if row["scenario_id"] == scenario_id and row["event_type"] == "category_resume")
            for scenario_id in labels
        ]
        x = range(len(labels))
        ax.bar([i - 0.2 for i in x], hold_counts, width=0.4, label="hold", color="#c0504d")
        ax.bar([i + 0.2 for i in x], resume_counts, width=0.4, label="resume", color="#70ad47")
        ax.set_xticks(list(x), labels, rotation=20)
        ax.set_title("Category Hold Resume Timeline v1")
        ax.set_ylabel("event count")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG_DIR / "category_hold_resume_timeline_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(9, 4))
        for scenario_id in labels:
            rows = [row for row in self.rows["manual_timeline"] if row["scenario_id"] == scenario_id]
            ax.plot(range(len(rows)), [int(row["occupied_slots"]) for row in rows], label=scenario_id)
        ax.set_title("Manual Review Occupancy v1")
        ax.set_ylabel("occupied slots")
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "manual_review_occupancy_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4))
        pending_counts = [
            sum(1 for row in self.rows["pending"] if row["scenario_id"] == scenario_id and row["queue_action"] == "enqueue")
            for scenario_id in labels
        ]
        ax.bar(labels, pending_counts, color="#8064a2")
        ax.set_title("Pending Queue Size v1")
        ax.set_ylabel("enqueue count")
        ax.tick_params(axis="x", rotation=20)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "pending_queue_size_v1.png", dpi=160)
        plt.close(fig)

    def write_report(self, validation_status: str) -> None:
        summary_by_id = {row["scenario_id"]: row for row in self.rows["summary"]}
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Stage 7B-2 Sorting State Machine and Hold/Resume Simulation Report",
            "",
            "## Scope",
            "",
            "- This stage does not use a camera.",
            "- Input occupancy comes from the internal Stage 7B-1 input table.",
            "- Stage 7B-1 sorting task manifest is used as the task source for the state machine.",
            "- No CAD modeling, rendering, Stage 7A editing, `legacy_v1` editing, or XY slider binding work is performed.",
            "- Stage 7A-3f XY slider binding remains a deferred mechanical integration issue and does not block abstract sorting simulation.",
            "",
            "## Scenario Results",
            "",
        ]
        for scenario_id in [
            "baseline",
            "forced_category_A_full",
            "manual_review_limited_capacity",
            "pick_failure_test",
        ]:
            row = summary_by_id[scenario_id]
            lines.extend(
                [
                    f"### {scenario_id}",
                    "",
                    f"- Generated task count: {row['generated_task_count']}.",
                    f"- Completed output count: {row['completed_output_count']}.",
                    f"- Completed manual_review count: {row['completed_manual_review_count']}.",
                    f"- Pending waiting resume count: {row['pending_waiting_resume_count']}.",
                    f"- Paused manual_review full count: {row['paused_manual_review_full_count']}.",
                    f"- Pick failed needs operator check count: {row['pick_failed_needs_operator_check_count']}.",
                    f"- Category hold count: {row['category_hold_count']}.",
                    f"- Category resume count: {row['category_resume_count']}.",
                    f"- Pending enqueue/dequeue counts: {row['pending_enqueue_count']} / {row['pending_dequeue_resume_count']}.",
                    "",
                ]
            )
        lines.extend(
            [
                "## Logic Notes",
                "",
                "- `category_hold` is triggered when a normal sample targets a full output box.",
                "- Pending normal samples remain in the pending queue until `operator_cleared_output_box` and `category_resume`.",
                "- Other categories continue to be processed while one category is held.",
                "- Manual review only handles true abnormal samples: missing label, invalid barcode, abnormal sample information, or unknown category.",
                "- Output full never becomes an abnormal reason and never sends a normal sample to manual_review.",
                "- `pick_failed` represents a robot execution failure or possible empty-slot mismatch, not abnormal sample classification.",
                "",
                "## Generated Outputs",
                "",
                "- `06_simulation/sorting_state_machine_event_log_v1.csv`",
                "- `06_simulation/sorting_state_machine_task_result_v1.csv`",
                "- `06_simulation/output_box_occupancy_timeline_v1.csv`",
                "- `06_simulation/manual_review_occupancy_timeline_v1.csv`",
                "- `06_simulation/category_hold_resume_events_v1.csv`",
                "- `06_simulation/pending_queue_log_v1.csv`",
                "- `06_simulation/abnormal_handling_log_v1.csv`",
                "- `06_simulation/pick_failure_log_v1.csv`",
                "- `06_simulation/sorting_state_machine_summary_v1.csv`",
                "",
                "## Consistency Check",
                "",
                f"- validation_status={validation_status}",
                "- This stage provides the logical basis for later trajectory, cycle time, animation, and Isaac Sim work.",
            ]
        )
        REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def run(self) -> str:
        scenarios = make_scenarios(self.category_to_box, self.tasks)
        for scenario in scenarios:
            self.run_scenario(scenario)
        validation_status = self.validate_internal()
        self.write_outputs(validation_status)
        return validation_status


def main() -> int:
    runner = SimulationRunner()
    validation_status = runner.run()
    summary = {row["scenario_id"]: row for row in runner.rows["summary"]}
    print(f"validation_status={validation_status}")
    print(f"baseline_completed_count={int(summary['baseline']['completed_output_count']) + int(summary['baseline']['completed_manual_review_count'])}")
    print(f"forced_category_A_full_hold_count={summary['forced_category_A_full']['category_hold_count']}")
    print(f"forced_category_A_full_resume_count={summary['forced_category_A_full']['category_resume_count']}")
    print(f"pending_queue_count={summary['forced_category_A_full']['pending_enqueue_count']}")
    print(f"abnormal_sample_handled_count={sum(int(row['abnormal_handled_count']) for row in runner.rows['summary'])}")
    print(
        "manual_review_normal_sample_count="
        + str(
            sum(
                int(row["manual_review_normal_sample_count"])
                for row in runner.rows["summary"]
            )
        )
    )
    print(f"pick_failed_count={len(runner.rows['pick_failure'])}")
    if runner.validation_issues:
        for issue in runner.validation_issues:
            print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
