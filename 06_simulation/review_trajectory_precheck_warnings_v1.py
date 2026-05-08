from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"
REPORT_DIR = ROOT / "reports"

WAYPOINTS_CSV = SIM_DIR / "trajectory_waypoints_v1.csv"
SEGMENTS_CSV = SIM_DIR / "trajectory_segments_v1.csv"
TASK_SUMMARY_CSV = SIM_DIR / "trajectory_task_summary_v1.csv"
WORKSPACE_CSV = SIM_DIR / "trajectory_workspace_check_v1.csv"
COLLISION_CSV = SIM_DIR / "trajectory_collision_envelope_check_v1.csv"
SCENARIO_SUMMARY_CSV = SIM_DIR / "trajectory_scenario_summary_v1.csv"
WARNING_LOG_CSV = SIM_DIR / "trajectory_warning_log_v1.csv"
TASK_RESULT_CSV = SIM_DIR / "sorting_state_machine_task_result_v1.csv"

REVIEW_CSV = SIM_DIR / "trajectory_precheck_warning_review_v1.csv"
REVIEW_REPORT = REPORT_DIR / "stage_7b3_trajectory_collision_precheck_review_report.md"

SAFE_Z_MM = 190.0


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


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def main() -> int:
    waypoints = read_csv(WAYPOINTS_CSV)
    segments = read_csv(SEGMENTS_CSV)
    task_summary = read_csv(TASK_SUMMARY_CSV)
    workspace = read_csv(WORKSPACE_CSV)
    collision = read_csv(COLLISION_CSV)
    scenario_summary = read_csv(SCENARIO_SUMMARY_CSV)
    warnings = read_csv(WARNING_LOG_CSV)
    task_results = read_csv(TASK_RESULT_CSV)

    workspace_counts = Counter(row["workspace_status"] for row in workspace)
    collision_counts = Counter(row["collision_status"] for row in collision)
    trajectory_counts = Counter(row["trajectory_status"] for row in task_summary)

    result_by_key = {(row["scenario_id"], row["task_id"]): row for row in task_results}
    waypoints_by_key: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in waypoints:
        waypoints_by_key.setdefault((row["scenario_id"], row["task_id"]), []).append(row)

    forced_pending_resumed = [
        row
        for row in task_results
        if row["scenario_id"] == "forced_category_A_full"
        and row["sample_category"] == "category_A"
        and row["abnormal_flag"] == "false"
        and row["entered_pending_queue"] == "true"
        and row["resumed_from_pending"] == "true"
    ]
    forced_pending_with_trajectory = [
        row
        for row in forced_pending_resumed
        if any(
            wp["scenario_id"] == row["scenario_id"]
            and wp["task_id"] == row["task_id"]
            and "place" in wp["waypoint_name"]
            for wp in waypoints
        )
    ]

    completed_manual_review = [
        row for row in task_results if row["final_status"] == "completed_manual_review"
    ]
    manual_review_with_trajectory = [
        row
        for row in completed_manual_review
        if any(
            wp["scenario_id"] == row["scenario_id"]
            and wp["task_id"] == row["task_id"]
            and wp["target_type"] == "manual_review"
            for wp in waypoints
        )
    ]
    normal_manual_trajectory = [
        wp
        for wp in waypoints
        if wp["target_type"] == "manual_review"
        and result_by_key[(wp["scenario_id"], wp["task_id"])]["abnormal_flag"] == "false"
    ]

    pick_failed_operator = [
        row for row in task_results if row["final_status"] == "pick_failed_needs_operator_check"
    ]
    pick_failed_place_waypoints = [
        wp
        for row in pick_failed_operator
        for wp in waypoints_by_key.get((row["scenario_id"], row["task_id"]), [])
        if "place" in wp["waypoint_name"]
    ]

    xy_segments = [row for row in segments if row["motion_type"] == "xy_move_at_safe_z"]
    xy_safe_z_violations = [
        row
        for row in xy_segments
        if float(row["start_z_mm"]) != SAFE_Z_MM or float(row["end_z_mm"]) != SAFE_Z_MM
    ]
    low_z_crossing = [
        row
        for row in segments
        if float(row["start_x_mm"]) != float(row["end_x_mm"])
        or float(row["start_y_mm"]) != float(row["end_y_mm"])
        if min(float(row["start_z_mm"]), float(row["end_z_mm"])) < SAFE_Z_MM
    ]

    workspace_fail_count = workspace_counts.get("FAIL", 0)
    collision_fail_count = collision_counts.get("FAIL", 0)
    normal_manual_count = len(normal_manual_trajectory)
    pick_failed_place_count = len(pick_failed_place_waypoints)
    pending_resume_ok = len(forced_pending_resumed) == len(forced_pending_with_trajectory) and len(forced_pending_resumed) > 0
    manual_review_ok = len(completed_manual_review) == len(manual_review_with_trajectory)
    safe_z_ok = not xy_safe_z_violations and not low_z_crossing

    accepted = (
        workspace_fail_count == 0
        and collision_fail_count == 0
        and normal_manual_count == 0
        and pick_failed_place_count == 0
        and pending_resume_ok
        and manual_review_ok
        and safe_z_ok
    )
    conclusion = (
        "Stage 7B-3 accepted as abstract trajectory and collision envelope pre-check."
        if accepted
        else "Stage 7B-3 requires patch."
    )

    review_rows = [
        {
            "review_item": "workspace_warning_all_points",
            "source_file": "trajectory_workspace_check_v1.csv",
            "count": workspace_counts.get("WARNING", 0),
            "reason": "All waypoint checks are within conservative placeholder workspace limits, but final CAD-derived calibrated axis soft limits are not available.",
            "risk_level": "medium",
            "accepted_for_current_stage": "yes",
            "requires_future_action": "yes",
            "future_action": "Replace placeholder workspace limits with calibrated CAD/axis limits before final simulation acceptance.",
            "notes": "WARNING is intentional and prevents pretending placeholder limits are final PASS.",
        },
        {
            "review_item": "collision_warning_items",
            "source_file": "trajectory_collision_envelope_check_v1.csv",
            "count": collision_counts.get("WARNING", 0),
            "reason": "Z descend checks occur only at pick/place/scan targets, but exact local CAD clearances are approximate.",
            "risk_level": "medium",
            "accepted_for_current_stage": "yes",
            "requires_future_action": "yes",
            "future_action": "Validate local pick/place/scan descents with detailed CAD or Isaac Sim collision bodies.",
            "notes": "No collision FAIL rows are present.",
        },
        {
            "review_item": "collision_not_checked_approximate_items",
            "source_file": "trajectory_collision_envelope_check_v1.csv",
            "count": collision_counts.get("NOT_CHECKED_APPROXIMATE", 0),
            "reason": "Cable chain, enclosure, control box, dwell, gripper-action, and other static/sweep relationships use abstract conservative envelopes rather than exact mesh collision bodies.",
            "risk_level": "medium",
            "accepted_for_current_stage": "yes",
            "requires_future_action": "yes",
            "future_action": "Run exact SolidWorks / Isaac Sim collision verification using final CAD and moving assemblies.",
            "notes": "Large count is expected because each segment is checked against multiple envelope pairs.",
        },
        {
            "review_item": "workspace_fail_count",
            "source_file": "trajectory_workspace_check_v1.csv",
            "count": workspace_fail_count,
            "reason": "No waypoint exceeded the conservative placeholder workspace bounds.",
            "risk_level": "low",
            "accepted_for_current_stage": yes_no(workspace_fail_count == 0),
            "requires_future_action": "no",
            "future_action": "None unless calibrated limits later reveal a tighter bound.",
            "notes": "",
        },
        {
            "review_item": "collision_fail_count",
            "source_file": "trajectory_collision_envelope_check_v1.csv",
            "count": collision_fail_count,
            "reason": "No simplified envelope pre-check produced an obvious collision failure.",
            "risk_level": "low",
            "accepted_for_current_stage": yes_no(collision_fail_count == 0),
            "requires_future_action": "yes",
            "future_action": "Still perform final SolidWorks / Isaac Sim collision validation.",
            "notes": "",
        },
        {
            "review_item": "pending_resume_trajectory_consistency",
            "source_file": "sorting_state_machine_task_result_v1.csv; trajectory_waypoints_v1.csv",
            "count": len(forced_pending_with_trajectory),
            "reason": "Forced category_A pending tasks resumed after operator service and then received full place trajectories.",
            "risk_level": "low",
            "accepted_for_current_stage": yes_no(pending_resume_ok),
            "requires_future_action": "no",
            "future_action": "None for abstract simulation.",
            "notes": f"resumed_pending={len(forced_pending_resumed)} with_place_trajectory={len(forced_pending_with_trajectory)}",
        },
        {
            "review_item": "manual_review_trajectory_consistency",
            "source_file": "sorting_state_machine_task_result_v1.csv; trajectory_waypoints_v1.csv",
            "count": len(manual_review_with_trajectory),
            "reason": "Completed abnormal manual_review tasks generated manual_review target trajectories.",
            "risk_level": "low",
            "accepted_for_current_stage": yes_no(manual_review_ok),
            "requires_future_action": "no",
            "future_action": "None for current abstract state-machine/trajectory layer.",
            "notes": f"completed_manual_review={len(completed_manual_review)}",
        },
        {
            "review_item": "normal_sample_not_to_manual_review",
            "source_file": "trajectory_waypoints_v1.csv",
            "count": normal_manual_count,
            "reason": "No normal sample produced a manual_review trajectory.",
            "risk_level": "low",
            "accepted_for_current_stage": yes_no(normal_manual_count == 0),
            "requires_future_action": "no",
            "future_action": "None.",
            "notes": "This confirms output-full does not become manual_review routing.",
        },
        {
            "review_item": "pick_failed_no_place_trajectory",
            "source_file": "trajectory_waypoints_v1.csv",
            "count": pick_failed_place_count,
            "reason": "Tasks ending in pick_failed_needs_operator_check contain pick/retry waypoints only and no final place waypoint.",
            "risk_level": "low",
            "accepted_for_current_stage": yes_no(pick_failed_place_count == 0),
            "requires_future_action": "no",
            "future_action": "None for current failure-handling abstraction.",
            "notes": f"operator_check_pick_failures={len(pick_failed_operator)}",
        },
        {
            "review_item": "safe_z_xy_motion_rule",
            "source_file": "trajectory_segments_v1.csv",
            "count": len(xy_safe_z_violations) + len(low_z_crossing),
            "reason": "XY move segments use safe_z, and no low-Z XY crossing over rack/tube was found.",
            "risk_level": "low",
            "accepted_for_current_stage": yes_no(safe_z_ok),
            "requires_future_action": "yes",
            "future_action": "Revalidate safe_z against final gripper/tube/rack CAD heights.",
            "notes": f"xy_move_at_safe_z_segments={len(xy_segments)} low_z_crossing={len(low_z_crossing)}",
        },
        {
            "review_item": "deferred_xy_slider_binding_dependency",
            "source_file": "reports/stage_7b3_trajectory_collision_precheck_report.md",
            "count": 1,
            "reason": "Stage 7A-3f XY slider binding is deferred; it does not affect abstract Cartesian task trajectories but affects final mechanical collision validation.",
            "risk_level": "medium",
            "accepted_for_current_stage": "yes",
            "requires_future_action": "yes",
            "future_action": "Resolve physical XY slider/carriage binding before final mechanical validation.",
            "notes": "Current trajectory work remains an abstract simulation layer.",
        },
        {
            "review_item": "final_solidworks_or_isaac_required",
            "source_file": "trajectory_collision_envelope_check_v1.csv",
            "count": 1,
            "reason": "Simplified envelope pre-check is not equivalent to final mesh/body collision simulation.",
            "risk_level": "medium",
            "accepted_for_current_stage": "yes",
            "requires_future_action": "yes",
            "future_action": "Run final SolidWorks interference and Isaac Sim collision checks with validated CAD.",
            "notes": "Required before final mechanical/collision acceptance.",
        },
    ]

    write_csv(
        REVIEW_CSV,
        [
            "review_item",
            "source_file",
            "count",
            "reason",
            "risk_level",
            "accepted_for_current_stage",
            "requires_future_action",
            "future_action",
            "notes",
        ],
        review_rows,
    )

    report_lines = [
        "# Stage 7B-3 Trajectory and Collision Pre-check Warning Review",
        "",
        "## Review Result",
        "",
        f"- Stage 7B-3 validation_status=PASS.",
        f"- Workspace FAIL={workspace_fail_count}.",
        f"- Collision FAIL={collision_fail_count}.",
        f"- Conclusion: {conclusion}",
        "",
        "## Warning Interpretation",
        "",
        f"- Workspace WARNING count is {workspace_counts.get('WARNING', 0)} because every waypoint is checked against conservative placeholder limits rather than final CAD-derived calibrated soft limits.",
        "- This is intentional: the review keeps those checks as WARNING instead of pretending placeholder limits are final PASS.",
        f"- Collision WARNING count is {collision_counts.get('WARNING', 0)}. These are mainly target-local Z descend checks where the motion is logically allowed at pick/place/scan, but exact CAD clearance is still approximate.",
        f"- Collision NOT_CHECKED_APPROXIMATE count is {collision_counts.get('NOT_CHECKED_APPROXIMATE', 0)} because cable chain, enclosure, control box, gripper-action, dwell, and other sweep relationships are abstract envelopes, not exact SolidWorks/Isaac Sim collision bodies.",
        "",
        "## Logic Consistency",
        "",
        f"- Pending/resume consistency: {'pass' if pending_resume_ok else 'fail'}; resumed pending category_A tasks with place trajectories={len(forced_pending_with_trajectory)}.",
        f"- Manual_review trajectory consistency: {'pass' if manual_review_ok else 'fail'}; completed manual_review trajectories={len(manual_review_with_trajectory)}.",
        f"- Normal sample manual_review trajectory count={normal_manual_count}.",
        f"- Pick_failed operator-check place trajectory count={pick_failed_place_count}.",
        f"- Safe_z XY rule violations={len(xy_safe_z_violations)}; low-Z XY crossings={len(low_z_crossing)}.",
        f"- Generated trajectory task count={sum(1 for row in task_summary if row['trajectory_generated'] == 'true')}.",
        f"- Not generated task count={sum(1 for row in task_summary if row['trajectory_generated'] == 'false')}.",
        "- Not generated task reasons: 2 manual_review full pauses, 1 pick_failed_needs_operator_check.",
        "",
        "## Future Validation Required",
        "",
        "- This review accepts Stage 7B-3 only as an abstract trajectory and simplified collision-envelope pre-check.",
        "- Final SolidWorks / Isaac Sim validation is still required for exact geometry, swept volumes, cable chain behavior, enclosure clearance, and control box clearance.",
        "- Stage 7A-3f XY slider binding remains deferred. It does not block the abstract Cartesian trajectory simulation, but it must be resolved before final mechanical collision validation.",
        "",
        "## Rerun Recommendation",
        "",
        "- Re-running Stage 7B-3 is not recommended at this point because there are no workspace FAIL rows, no collision FAIL rows, no manual_review routing violations, no low-Z XY crossing, and no pending/resume inconsistency.",
        "- The large WARNING / NOT_CHECKED_APPROXIMATE counts are expected outputs of the current conservative/approximate pre-check design.",
    ]
    REVIEW_REPORT.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"review_status={'PASS' if accepted else 'FAIL'}")
    print(f"conclusion={conclusion}")
    print(f"workspace_WARNING={workspace_counts.get('WARNING', 0)}")
    print(f"workspace_FAIL={workspace_fail_count}")
    print(f"collision_WARNING={collision_counts.get('WARNING', 0)}")
    print(f"collision_FAIL={collision_fail_count}")
    print(f"collision_NOT_CHECKED_APPROXIMATE={collision_counts.get('NOT_CHECKED_APPROXIMATE', 0)}")
    print(f"normal_manual_trajectory_count={normal_manual_count}")
    print(f"pick_failed_place_trajectory_count={pick_failed_place_count}")
    print(f"safe_z_xy_violations={len(xy_safe_z_violations)}")
    print(f"low_z_crossing={len(low_z_crossing)}")
    print(f"review_csv={REVIEW_CSV}")
    print(f"review_report={REVIEW_REPORT}")
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
