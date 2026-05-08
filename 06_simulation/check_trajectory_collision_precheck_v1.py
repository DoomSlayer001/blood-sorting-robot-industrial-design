from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"

OCCUPANCY_CSV = SIM_DIR / "input_box_occupancy_map_v1.csv"
TASK_RESULT_CSV = SIM_DIR / "sorting_state_machine_task_result_v1.csv"
WAYPOINTS_CSV = SIM_DIR / "trajectory_waypoints_v1.csv"
TASK_SUMMARY_CSV = SIM_DIR / "trajectory_task_summary_v1.csv"
WORKSPACE_CSV = SIM_DIR / "trajectory_workspace_check_v1.csv"
COLLISION_CSV = SIM_DIR / "trajectory_collision_envelope_check_v1.csv"

FULL_PLACE_STATUSES = {
    "completed_output",
    "completed_manual_review",
    "pick_failed_retried_completed",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    issues: list[str] = []
    occupancy = read_csv(OCCUPANCY_CSV)
    results = read_csv(TASK_RESULT_CSV)
    waypoints = read_csv(WAYPOINTS_CSV)
    task_summary = read_csv(TASK_SUMMARY_CSV)
    workspace = read_csv(WORKSPACE_CSV)
    collision = read_csv(COLLISION_CSV)

    summary_by_key = {(row["scenario_id"], row["task_id"]): row for row in task_summary}
    waypoints_by_key: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in waypoints:
        waypoints_by_key.setdefault((row["scenario_id"], row["task_id"]), []).append(row)

    empty_tubes = {row["tube_id"] for row in occupancy if row["tube_present"] == "false" and row["tube_id"]}

    for result in results:
        key = (result["scenario_id"], result["task_id"])
        summary = summary_by_key.get(key)
        if summary is None:
            issues.append(f"missing trajectory summary for {key}")
            continue
        if result["final_status"] in {"completed_output", "completed_manual_review"} and summary["trajectory_generated"] != "true":
            issues.append(f"completed task missing trajectory: {key}")
        if result["final_status"] == "pending_waiting_resume":
            place_points = [row for row in waypoints_by_key.get(key, []) if "place" in row["waypoint_name"]]
            if place_points:
                issues.append(f"pending task has final place trajectory before resume: {key}")
        if result["final_status"] == "pick_failed_needs_operator_check":
            place_points = [row for row in waypoints_by_key.get(key, []) if "place" in row["waypoint_name"]]
            if place_points:
                issues.append(f"pick failure generated place trajectory: {key}")
        if result["tube_id"] in empty_tubes:
            issues.append(f"empty slot generated trajectory: {key}")
        if result["abnormal_flag"] == "false":
            manual_points = [
                row for row in waypoints_by_key.get(key, []) if row["target_type"] == "manual_review"
            ]
            if manual_points:
                issues.append(f"normal sample generated manual_review trajectory: {key}")
        if result["abnormal_flag"] == "true" and result["final_status"] == "completed_manual_review":
            points = waypoints_by_key.get(key, [])
            if not points or not any(row["target_type"] == "manual_review" for row in points):
                issues.append(f"abnormal completed sample missing manual_review trajectory: {key}")

    for row in waypoints:
        if row["x_mm"] == "" or row["y_mm"] == "" or row["z_mm"] == "":
            issues.append(f"waypoint coordinate missing: {row['scenario_id']} {row['task_id']} {row['waypoint_name']}")

    if any(row["workspace_status"] == "FAIL" for row in workspace):
        issues.append("workspace check contains FAIL")
    if any(row["collision_status"] == "FAIL" for row in collision):
        issues.append("collision envelope check contains FAIL")

    generated_count = sum(1 for row in task_summary if row["trajectory_generated"] == "true")
    not_generated_count = sum(1 for row in task_summary if row["trajectory_generated"] == "false")
    workspace_pass = sum(1 for row in workspace if row["workspace_status"] == "PASS")
    workspace_warning = sum(1 for row in workspace if row["workspace_status"] == "WARNING")
    workspace_fail = sum(1 for row in workspace if row["workspace_status"] == "FAIL")
    collision_pass = sum(1 for row in collision if row["collision_status"] == "PASS")
    collision_warning = sum(1 for row in collision if row["collision_status"] == "WARNING")
    collision_fail = sum(1 for row in collision if row["collision_status"] == "FAIL")
    collision_not_checked = sum(1 for row in collision if row["collision_status"] == "NOT_CHECKED_APPROXIMATE")

    validation_status = "PASS" if not issues else "FAIL"
    print(f"validation_status={validation_status}")
    print(f"generated_trajectory_task_count={generated_count}")
    print(f"not_generated_task_count={not_generated_count}")
    print(f"workspace_PASS={workspace_pass}")
    print(f"workspace_WARNING={workspace_warning}")
    print(f"workspace_FAIL={workspace_fail}")
    print(f"collision_PASS={collision_pass}")
    print(f"collision_WARNING={collision_warning}")
    print(f"collision_FAIL={collision_fail}")
    print(f"collision_NOT_CHECKED_APPROXIMATE={collision_not_checked}")
    if issues:
        for issue in issues:
            print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
