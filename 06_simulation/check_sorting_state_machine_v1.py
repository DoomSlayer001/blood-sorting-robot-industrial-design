from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"

INPUT_OCCUPANCY_CSV = SIM_DIR / "input_box_occupancy_map_v1.csv"
TASK_MANIFEST_CSV = SIM_DIR / "sorting_task_manifest_v1.csv"
EVENT_LOG_CSV = SIM_DIR / "sorting_state_machine_event_log_v1.csv"
TASK_RESULT_CSV = SIM_DIR / "sorting_state_machine_task_result_v1.csv"
OUTPUT_TIMELINE_CSV = SIM_DIR / "output_box_occupancy_timeline_v1.csv"
MANUAL_TIMELINE_CSV = SIM_DIR / "manual_review_occupancy_timeline_v1.csv"
HOLD_RESUME_CSV = SIM_DIR / "category_hold_resume_events_v1.csv"
PENDING_QUEUE_CSV = SIM_DIR / "pending_queue_log_v1.csv"
ABNORMAL_LOG_CSV = SIM_DIR / "abnormal_handling_log_v1.csv"
PICK_FAILURE_CSV = SIM_DIR / "pick_failure_log_v1.csv"
SUMMARY_CSV = SIM_DIR / "sorting_state_machine_summary_v1.csv"

FINAL_STATUSES = {
    "completed_output",
    "completed_manual_review",
    "pending_waiting_resume",
    "skipped_empty",
    "pick_failed_retried_completed",
    "pick_failed_needs_operator_check",
    "paused_manual_review_full",
    "error",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    issues: list[str] = []
    occupancy = read_csv(INPUT_OCCUPANCY_CSV)
    tasks = read_csv(TASK_MANIFEST_CSV)
    events = read_csv(EVENT_LOG_CSV)
    results = read_csv(TASK_RESULT_CSV)
    output_timeline = read_csv(OUTPUT_TIMELINE_CSV)
    manual_timeline = read_csv(MANUAL_TIMELINE_CSV)
    hold_resume = read_csv(HOLD_RESUME_CSV)
    pending = read_csv(PENDING_QUEUE_CSV)
    abnormal = read_csv(ABNORMAL_LOG_CSV)
    pick_failure = read_csv(PICK_FAILURE_CSV)
    summary = read_csv(SUMMARY_CSV)

    scenario_ids = sorted({row["scenario_id"] for row in results})
    task_ids = {row["task_id"] for row in tasks}
    occupied_tubes = {row["tube_id"] for row in occupancy if row["tube_present"] == "true"}
    empty_tubes = {row["tube_id"] for row in occupancy if row["tube_present"] == "false" and row["tube_id"]}

    for scenario_id in scenario_ids:
        scenario_results = [row for row in results if row["scenario_id"] == scenario_id]
        if len(scenario_results) != len(tasks):
            issues.append(f"{scenario_id}: not all generated tasks have final_status")
        if any(row["final_status"] not in FINAL_STATUSES for row in scenario_results):
            issues.append(f"{scenario_id}: invalid final_status found")
        if any(row["task_id"] not in task_ids for row in scenario_results):
            issues.append(f"{scenario_id}: unknown task_id in results")
        if any(row["tube_id"] in empty_tubes for row in scenario_results):
            issues.append(f"{scenario_id}: empty slot entered state machine")
        if any(row["abnormal_flag"] == "false" and row["went_to_manual_review"] == "true" for row in scenario_results):
            issues.append(f"{scenario_id}: normal sample entered manual_review")

    abnormal_task_ids = {row["task_id"] for row in tasks if row["abnormal_flag"] == "true"}
    for scenario_id in scenario_ids:
        scenario_results = [row for row in results if row["scenario_id"] == scenario_id]
        for row in scenario_results:
            if row["task_id"] in abnormal_task_ids and row["final_status"] not in {
                "completed_manual_review",
                "paused_manual_review_full",
                "pick_failed_needs_operator_check",
            }:
                issues.append(f"{scenario_id}: abnormal sample not handled or paused")

    normal_manual_in_abnormal_log = [
        row for row in abnormal if row["task_id"] in {task["task_id"] for task in tasks if task["abnormal_flag"] == "false"}
    ]
    if normal_manual_in_abnormal_log:
        issues.append("normal sample appears in abnormal_handling_log")
    if any(row["abnormal_reason"] == "output_box_full" for row in abnormal):
        issues.append("output full appears as abnormal_reason")

    forced_events = [row for row in hold_resume if row["scenario_id"] == "forced_category_A_full"]
    if not any(row["event_type"] == "category_hold" for row in forced_events):
        issues.append("forced_category_A_full did not emit category_hold")
    if not any(row["event_type"] == "category_resume" for row in forced_events):
        issues.append("forced_category_A_full did not emit category_resume")

    forced_pending = [row for row in pending if row["scenario_id"] == "forced_category_A_full"]
    if not forced_pending:
        issues.append("forced_category_A_full has no pending queue entries")
    if any(row["sample_category"] != "category_A" for row in forced_pending):
        issues.append("forced_category_A_full pending queue contains non-category_A sample")

    forced_results = [row for row in results if row["scenario_id"] == "forced_category_A_full"]
    if any(
        row["sample_category"] == "category_A"
        and row["abnormal_flag"] == "false"
        and row["entered_pending_queue"] != "true"
        for row in forced_results
    ):
        issues.append("category_A normal sample did not enter pending queue in forced full scenario")
    if any(
        row["sample_category"] == "category_A"
        and row["abnormal_flag"] == "false"
        and row["resumed_from_pending"] != "true"
        for row in forced_results
    ):
        issues.append("category_A pending sample did not resume")

    hold_indices = [
        int(row["event_index"])
        for row in events
        if row["scenario_id"] == "forced_category_A_full" and row["event"] == "category_hold"
    ]
    resume_indices = [
        int(row["event_index"])
        for row in events
        if row["scenario_id"] == "forced_category_A_full" and row["event"] == "place_output_box" and row["sample_category"] == "category_A"
    ]
    if hold_indices and resume_indices:
        first_hold = min(hold_indices)
        first_a_resume_place = min(resume_indices)
        other_category_between = any(
            row["scenario_id"] == "forced_category_A_full"
            and row["event"] in {"place_output_box", "place_manual_review"}
            and row["sample_category"] != "category_A"
            and first_hold < int(row["event_index"]) < first_a_resume_place
            for row in events
        )
        if not other_category_between:
            issues.append("other categories did not continue between hold and resume")

    if any(int(row["occupied_slots"]) > 24 for row in output_timeline):
        issues.append("output box capacity exceeds 24")
    if any(int(row["occupied_slots"]) > int(row["capacity_slots"]) for row in manual_timeline):
        issues.append("manual review occupied exceeds scenario capacity")
    if any(int(row["capacity_slots"]) > 6 for row in manual_timeline):
        issues.append("manual review capacity exceeds 6")

    pick_task_ids = {row["task_id"] for row in pick_failure}
    if not pick_task_ids:
        issues.append("pick_failure_log is empty")
    result_by_task_scenario = {(row["scenario_id"], row["task_id"]): row for row in results}
    for row in pick_failure:
        result = result_by_task_scenario.get((row["scenario_id"], row["task_id"]))
        if result is None:
            issues.append("pick failure missing matching task result")
        elif result["abnormal_flag"] == "true":
            issues.append("pick_failed task was treated as abnormal")
        elif result["went_to_manual_review"] == "true":
            issues.append("pick_failed normal sample went to manual_review")

    validation_status = "PASS" if not issues else "FAIL"
    manual_review_normal_sample_count = sum(
        1 for row in results if row["abnormal_flag"] == "false" and row["went_to_manual_review"] == "true"
    )
    baseline_completed_count = sum(
        1
        for row in results
        if row["scenario_id"] == "baseline"
        and row["final_status"] in {"completed_output", "completed_manual_review", "pick_failed_retried_completed"}
    )
    forced_hold_count = sum(
        1 for row in hold_resume if row["scenario_id"] == "forced_category_A_full" and row["event_type"] == "category_hold"
    )
    forced_resume_count = sum(
        1 for row in hold_resume if row["scenario_id"] == "forced_category_A_full" and row["event_type"] == "category_resume"
    )
    pending_enqueue_count = sum(1 for row in pending if row["queue_action"] == "enqueue")
    abnormal_handled_count = sum(1 for row in abnormal if row["manual_review_status"] == "completed_manual_review")

    print(f"validation_status={validation_status}")
    print(f"scenario_count={len(scenario_ids)}")
    print(f"generated_task_count={len(tasks)}")
    print(f"baseline_completed_count={baseline_completed_count}")
    print(f"forced_category_A_full_hold_count={forced_hold_count}")
    print(f"forced_category_A_full_resume_count={forced_resume_count}")
    print(f"pending_queue_count={pending_enqueue_count}")
    print(f"abnormal_sample_handled_count={abnormal_handled_count}")
    print(f"manual_review_normal_sample_count={manual_review_normal_sample_count}")
    print(f"pick_failed_count={len(pick_failure)}")
    if issues:
        for issue in issues:
            print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
