from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"

TRAJ_TASK_SUMMARY_CSV = SIM_DIR / "trajectory_task_summary_v1.csv"
TASK_RESULT_CSV = SIM_DIR / "sorting_state_machine_task_result_v1.csv"
SEGMENT_TIME_CSV = SIM_DIR / "trajectory_segment_time_estimate_v1.csv"
TASK_CYCLE_CSV = SIM_DIR / "task_cycle_time_estimate_v1.csv"
SCENARIO_BATCH_CSV = SIM_DIR / "scenario_batch_time_summary_v1.csv"
STAGE_BREAKDOWN_CSV = SIM_DIR / "cycle_time_stage_breakdown_v1.csv"

COMPLETED_STATUSES = {
    "completed_output",
    "completed_manual_review",
    "pick_failed_retried_completed",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    issues: list[str] = []
    traj_tasks = read_csv(TRAJ_TASK_SUMMARY_CSV)
    task_results = read_csv(TASK_RESULT_CSV)
    segment_time = read_csv(SEGMENT_TIME_CSV)
    task_cycle = read_csv(TASK_CYCLE_CSV)
    scenario_batch = read_csv(SCENARIO_BATCH_CSV)
    stage_breakdown = read_csv(STAGE_BREAKDOWN_CSV)

    cycle_keys = {(row["scenario_id"], row["task_id"]) for row in task_cycle}
    for row in traj_tasks:
        if row["trajectory_generated"] == "true" and (row["scenario_id"], row["task_id"]) not in cycle_keys:
            issues.append(f"generated trajectory task missing cycle time: {row['scenario_id']} {row['task_id']}")

    if any(float(row["segment_time_s"]) < 0 for row in segment_time):
        issues.append("segment_time_s contains negative value")

    completed_results = [
        row for row in task_results if row["final_status"] in COMPLETED_STATUSES
    ]
    completed_batch_count = sum(int(row["completed_sample_count"]) for row in scenario_batch)
    if completed_batch_count != len(completed_results):
        issues.append("completed_output / completed_manual_review not reflected in batch summary")

    for row in task_cycle:
        if row["state_machine_final_status"] == "pending_waiting_resume" and row["cycle_time_status"] != "not_generated_pending":
            issues.append("pending_waiting_resume task miscounted as completed")
        if row["state_machine_final_status"] == "pick_failed_needs_operator_check" and row["cycle_time_status"] != "not_generated_pick_failure":
            issues.append("pick_failed_needs_operator_check generated normal place cycle")

    if any(float(row["robot_active_time_s"]) <= 0 for row in scenario_batch):
        issues.append("robot_active_time_s is not positive")
    if any(float(row["total_elapsed_time_s"]) < float(row["robot_active_time_s"]) for row in scenario_batch):
        issues.append("total_elapsed_time_s is less than robot_active_time_s")
    if any(float(row["estimated_samples_per_hour_robot_active"]) <= 0 for row in scenario_batch):
        issues.append("samples_per_hour is not positive")

    for scenario_id in sorted({row["scenario_id"] for row in stage_breakdown}):
        rows = [row for row in stage_breakdown if row["scenario_id"] == scenario_id]
        robot_pct = sum(float(row["percentage_of_robot_active_time"]) for row in rows)
        elapsed_pct = sum(float(row["percentage_of_total_elapsed_time"]) for row in rows)
        if not 99.0 <= robot_pct <= 101.0:
            issues.append(f"robot active stage percentages not reasonable for {scenario_id}: {robot_pct}")
        if not 99.0 <= elapsed_pct <= 101.0:
            issues.append(f"elapsed stage percentages not reasonable for {scenario_id}: {elapsed_pct}")

    validation_status = "PASS" if not issues else "FAIL"
    baseline = next(row for row in scenario_batch if row["scenario_id"] == "baseline")
    forced = next(row for row in scenario_batch if row["scenario_id"] == "forced_category_A_full")
    baseline_elapsed = float(baseline["estimated_samples_per_hour_elapsed"])
    forced_impact = (
        (baseline_elapsed - float(forced["estimated_samples_per_hour_elapsed"])) / baseline_elapsed * 100
        if baseline_elapsed > 0
        else 0.0
    )
    print(f"validation_status={validation_status}")
    print(f"baseline_robot_active_time_s={baseline['robot_active_time_s']}")
    print(f"baseline_total_elapsed_time_s={baseline['total_elapsed_time_s']}")
    print(f"baseline_samples_per_hour_robot_active={baseline['estimated_samples_per_hour_robot_active']}")
    print(f"baseline_samples_per_hour_elapsed={baseline['estimated_samples_per_hour_elapsed']}")
    print(f"forced_category_A_full_throughput_impact_percent={round(forced_impact, 3)}")
    print(f"bottleneck_stage={baseline['bottleneck_stage']}")
    if issues:
        for issue in issues:
            print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
