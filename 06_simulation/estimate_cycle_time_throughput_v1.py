from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"
FIG_DIR = SIM_DIR / "figures"
REPORT_DIR = ROOT / "reports"

WAYPOINTS_CSV = SIM_DIR / "trajectory_waypoints_v1.csv"
SEGMENTS_CSV = SIM_DIR / "trajectory_segments_v1.csv"
TRAJ_TASK_SUMMARY_CSV = SIM_DIR / "trajectory_task_summary_v1.csv"
TRAJ_SCENARIO_SUMMARY_CSV = SIM_DIR / "trajectory_scenario_summary_v1.csv"
TASK_RESULT_CSV = SIM_DIR / "sorting_state_machine_task_result_v1.csv"
EVENT_LOG_CSV = SIM_DIR / "sorting_state_machine_event_log_v1.csv"
HOLD_EVENTS_CSV = SIM_DIR / "category_hold_resume_events_v1.csv"
PENDING_LOG_CSV = SIM_DIR / "pending_queue_log_v1.csv"
MANUAL_TIMELINE_CSV = SIM_DIR / "manual_review_occupancy_timeline_v1.csv"
OUTPUT_TIMELINE_CSV = SIM_DIR / "output_box_occupancy_timeline_v1.csv"
WARNING_REVIEW_CSV = SIM_DIR / "trajectory_precheck_warning_review_v1.csv"

PARAMETERS_CSV = SIM_DIR / "cycle_time_motion_parameters_v1.csv"
SEGMENT_TIME_CSV = SIM_DIR / "trajectory_segment_time_estimate_v1.csv"
TASK_CYCLE_CSV = SIM_DIR / "task_cycle_time_estimate_v1.csv"
SCENARIO_BATCH_CSV = SIM_DIR / "scenario_batch_time_summary_v1.csv"
THROUGHPUT_CSV = SIM_DIR / "throughput_summary_v1.csv"
STAGE_BREAKDOWN_CSV = SIM_DIR / "cycle_time_stage_breakdown_v1.csv"
CATEGORY_THROUGHPUT_CSV = SIM_DIR / "category_throughput_summary_v1.csv"
PENDING_IMPACT_CSV = SIM_DIR / "pending_resume_time_impact_v1.csv"
PICK_FAILURE_IMPACT_CSV = SIM_DIR / "pick_failure_time_impact_v1.csv"
REPORT_MD = REPORT_DIR / "stage_7b4_cycle_time_throughput_report.md"

PARAMETERS = {
    "xy_nominal_speed_mm_s": (350.0, "mm/s", "Concept-level XY speed assumption."),
    "z_nominal_speed_mm_s": (120.0, "mm/s", "Concept-level Z speed assumption."),
    "xy_accel_allowance_s": (0.20, "s", "Simple allowance for acceleration/deceleration per XY move."),
    "z_accel_allowance_s": (0.15, "s", "Simple allowance for acceleration/deceleration per Z move."),
    "grip_close_time_s": (0.60, "s", "Concept-level gripper close time."),
    "grip_open_time_s": (0.50, "s", "Concept-level gripper open time."),
    "scan_wait_time_s": (1.00, "s", "Concept-level scan dwell time; no camera localization."),
    "pick_settle_time_s": (0.30, "s", "Settling allowance at pick."),
    "place_settle_time_s": (0.30, "s", "Settling allowance at place."),
    "category_hold_operator_service_time_s": (20.00, "s", "Operator clear/replace time for full output category."),
    "manual_review_alarm_pause_time_s": (10.00, "s", "Operator pause time when manual_review is full."),
    "pick_retry_time_s": (2.00, "s", "Retry handling allowance for injected pick failure."),
    "home_return_time_s": (1.00, "s", "Concept-level service/home return allowance; not applied to every task."),
}

COMPLETED_STATUSES = {
    "completed_output",
    "completed_manual_review",
    "pick_failed_retried_completed",
}


def param(name: str) -> float:
    return PARAMETERS[name][0]


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


def round3(value: float) -> float:
    return round(value, 3)


class CycleTimeEstimator:
    def __init__(self) -> None:
        self.waypoints = read_csv(WAYPOINTS_CSV)
        self.segments = read_csv(SEGMENTS_CSV)
        self.trajectory_tasks = read_csv(TRAJ_TASK_SUMMARY_CSV)
        self.trajectory_scenarios = read_csv(TRAJ_SCENARIO_SUMMARY_CSV)
        self.task_results = read_csv(TASK_RESULT_CSV)
        self.events = read_csv(EVENT_LOG_CSV)
        self.hold_events = read_csv(HOLD_EVENTS_CSV)
        self.pending_log = read_csv(PENDING_LOG_CSV)
        self.manual_timeline = read_csv(MANUAL_TIMELINE_CSV)
        self.output_timeline = read_csv(OUTPUT_TIMELINE_CSV)
        self.warning_review = read_csv(WARNING_REVIEW_CSV)
        self.result_by_key = {(row["scenario_id"], row["task_id"]): row for row in self.task_results}
        self.traj_by_key = {(row["scenario_id"], row["task_id"]): row for row in self.trajectory_tasks}
        self.waypoints_by_key: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
        for waypoint in self.waypoints:
            self.waypoints_by_key[(waypoint["scenario_id"], waypoint["task_id"])].append(waypoint)
        self.rows: dict[str, list[dict[str, object]]] = {
            "parameters": [],
            "segment_time": [],
            "task_cycle": [],
            "scenario_batch": [],
            "throughput": [],
            "stage_breakdown": [],
            "category_throughput": [],
            "pending_impact": [],
            "pick_failure_impact": [],
        }

    def write_parameters(self) -> None:
        self.rows["parameters"] = [
            {
                "parameter": name,
                "value": value,
                "unit": unit,
                "notes": notes + " Not final hardware measured performance.",
            }
            for name, (value, unit, notes) in PARAMETERS.items()
        ]

    def estimate_segment_time(self, segment: dict[str, str]) -> dict[str, object]:
        motion_type = segment["motion_type"]
        distance = float(segment["segment_distance_mm"])
        delta_z = abs(float(segment["end_z_mm"]) - float(segment["start_z_mm"]))
        time_model = ""
        time_s = 0.0
        category = "not_applicable"
        notes = "Concept-level timing assumption."

        if motion_type == "xy_move_at_safe_z":
            time_s = distance / param("xy_nominal_speed_mm_s") + param("xy_accel_allowance_s")
            time_model = "distance / xy_nominal_speed_mm_s + xy_accel_allowance_s"
            category = "xy_motion"
        elif motion_type in {"z_descend", "z_lift"}:
            time_s = delta_z / param("z_nominal_speed_mm_s") + param("z_accel_allowance_s")
            time_model = "abs(delta_z) / z_nominal_speed_mm_s + z_accel_allowance_s"
            category = "z_motion"
        elif motion_type == "scan_wait":
            time_s = param("scan_wait_time_s")
            time_model = "scan_wait_time_s"
            category = "scan_wait"
        elif motion_type == "gripper_action":
            if "grip_open" in segment["to_waypoint"]:
                time_s = param("grip_open_time_s")
                time_model = "grip_open_time_s"
            elif "grip_close" in segment["to_waypoint"]:
                time_s = param("grip_close_time_s")
                time_model = "grip_close_time_s"
            else:
                time_s = 0.0
                time_model = "no gripper timing matched"
            category = "gripper_action"
        elif motion_type == "skip_or_failure":
            time_s = param("pick_retry_time_s") if "retry" in segment["to_waypoint"] else 0.0
            time_model = "pick_retry_time_s when retry-related"
            category = "retry" if time_s > 0 else "not_applicable"

        return {
            "scenario_id": segment["scenario_id"],
            "task_id": segment["task_id"],
            "tube_id": segment["tube_id"],
            "segment_index": segment["segment_index"],
            "motion_type": motion_type,
            "axis_mode": segment["axis_mode"],
            "segment_distance_mm": segment["segment_distance_mm"],
            "delta_z_mm": round3(delta_z),
            "time_model": time_model,
            "segment_time_s": round3(time_s),
            "time_category": category,
            "notes": notes,
        }

    def build_segment_times(self) -> None:
        self.rows["segment_time"] = [self.estimate_segment_time(segment) for segment in self.segments]

    def task_cycle_status(self, result: dict[str, str], traj: dict[str, str] | None) -> str:
        final_status = result["final_status"]
        if final_status in {"completed_output", "completed_manual_review"}:
            return "estimated_with_warning" if traj and traj.get("trajectory_status") == "generated_with_warning" else "estimated_ok"
        if final_status == "pick_failed_retried_completed":
            return "estimated_with_warning"
        if final_status == "pending_waiting_resume":
            return "not_generated_pending"
        if final_status == "pick_failed_needs_operator_check":
            return "not_generated_pick_failure"
        if final_status == "paused_manual_review_full":
            return "not_generated_pause"
        return "error"

    def build_task_cycles(self) -> None:
        segment_by_key: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
        for row in self.rows["segment_time"]:
            segment_by_key[(str(row["scenario_id"]), str(row["task_id"]))].append(row)

        for result in self.task_results:
            key = (result["scenario_id"], result["task_id"])
            traj = self.traj_by_key.get(key)
            segment_rows = segment_by_key.get(key, [])
            by_category = Counter()
            for row in segment_rows:
                by_category[str(row["time_category"])] += float(row["segment_time_s"])

            has_pick = bool(self.waypoints_by_key.get(key))
            has_place = result["final_status"] in COMPLETED_STATUSES
            settle_time = (param("pick_settle_time_s") if has_pick else 0.0) + (
                param("place_settle_time_s") if has_place else 0.0
            )
            retry_time = 0.0
            if result["pick_failed"] == "true" or result["final_status"] in {
                "pick_failed_retried_completed",
                "pick_failed_needs_operator_check",
            }:
                retry_time = param("pick_retry_time_s")

            operator_wait = 0.0
            if result["final_status"] == "paused_manual_review_full":
                operator_wait = param("manual_review_alarm_pause_time_s")

            robot_active = (
                by_category["xy_motion"]
                + by_category["z_motion"]
                + by_category["scan_wait"]
                + by_category["gripper_action"]
                + settle_time
                + retry_time
            )
            total_elapsed = robot_active + operator_wait
            self.rows["task_cycle"].append(
                {
                    "scenario_id": result["scenario_id"],
                    "task_id": result["task_id"],
                    "tube_id": result["tube_id"],
                    "state_machine_final_status": result["final_status"],
                    "trajectory_status": traj["trajectory_status"] if traj else "missing",
                    "sample_category": result["sample_category"],
                    "target_type": result["target_type"],
                    "target_box_id": result["target_box_id"],
                    "robot_active_time_s": round3(robot_active),
                    "operator_wait_time_s": round3(operator_wait),
                    "total_elapsed_time_s": round3(total_elapsed),
                    "xy_motion_time_s": round3(by_category["xy_motion"]),
                    "z_motion_time_s": round3(by_category["z_motion"]),
                    "scan_time_s": round3(by_category["scan_wait"]),
                    "gripper_time_s": round3(by_category["gripper_action"]),
                    "settle_time_s": round3(settle_time),
                    "retry_time_s": round3(retry_time),
                    "segment_count": len(segment_rows),
                    "waypoint_count": traj["waypoint_count"] if traj else 0,
                    "cycle_time_status": self.task_cycle_status(result, traj),
                    "notes": "Concept-level estimate from Stage 7B-3 trajectory segments.",
                }
            )

    def build_scenario_summaries(self) -> None:
        scenario_ids = sorted({row["scenario_id"] for row in self.task_results})
        for scenario_id in scenario_ids:
            task_rows = [row for row in self.rows["task_cycle"] if row["scenario_id"] == scenario_id]
            result_rows = [row for row in self.task_results if row["scenario_id"] == scenario_id]
            completed = [row for row in result_rows if row["final_status"] in COMPLETED_STATUSES]
            normal_completed = [row for row in completed if row["abnormal_flag"] == "false"]
            manual_completed = [row for row in completed if row["final_status"] == "completed_manual_review"]
            pending_count = sum(1 for row in result_rows if row["entered_pending_queue"] == "true")
            resumed_count = sum(1 for row in result_rows if row["resumed_from_pending"] == "true")
            pick_failed_count = sum(1 for row in result_rows if row["pick_failed"] == "true")
            robot_active = sum(float(row["robot_active_time_s"]) for row in task_rows)
            operator_wait = sum(float(row["operator_wait_time_s"]) for row in task_rows)

            hold_service_events = [
                row
                for row in self.hold_events
                if row["scenario_id"] == scenario_id and row["event_type"] == "operator_cleared_output_box"
            ]
            operator_wait += len(hold_service_events) * param("category_hold_operator_service_time_s")
            elapsed = robot_active + operator_wait
            completed_count = len(completed)
            avg_robot = robot_active / completed_count if completed_count else 0.0
            avg_elapsed = elapsed / completed_count if completed_count else 0.0
            sph_robot = completed_count / robot_active * 3600 if robot_active > 0 and completed_count else 0.0
            sph_elapsed = completed_count / elapsed * 3600 if elapsed > 0 and completed_count else 0.0
            stage_totals = self.stage_totals_for(scenario_id, operator_wait)
            bottleneck_stage = max(
                (key for key in stage_totals if key != "operator_wait"),
                key=lambda key: stage_totals[key],
            )
            if stage_totals["operator_wait"] > stage_totals[bottleneck_stage]:
                bottleneck_stage = "operator_wait"

            self.rows["scenario_batch"].append(
                {
                    "scenario_id": scenario_id,
                    "completed_sample_count": completed_count,
                    "normal_completed_count": len(normal_completed),
                    "manual_review_completed_count": len(manual_completed),
                    "pending_count": pending_count,
                    "resumed_pending_count": resumed_count,
                    "pick_failed_count": pick_failed_count,
                    "robot_active_time_s": round3(robot_active),
                    "operator_wait_time_s": round3(operator_wait),
                    "total_elapsed_time_s": round3(elapsed),
                    "average_cycle_time_robot_active_s": round3(avg_robot),
                    "average_cycle_time_elapsed_s": round3(avg_elapsed),
                    "estimated_samples_per_hour_robot_active": round3(sph_robot),
                    "estimated_samples_per_hour_elapsed": round3(sph_elapsed),
                    "bottleneck_stage": bottleneck_stage,
                    "notes": "Robot active excludes operator service delay; elapsed includes it.",
                }
            )
            self.add_stage_breakdown(scenario_id, stage_totals, robot_active, elapsed)

    def stage_totals_for(self, scenario_id: str, operator_wait: float) -> dict[str, float]:
        task_rows = [row for row in self.rows["task_cycle"] if row["scenario_id"] == scenario_id]
        return {
            "xy_motion": sum(float(row["xy_motion_time_s"]) for row in task_rows),
            "z_motion": sum(float(row["z_motion_time_s"]) for row in task_rows),
            "scan_wait": sum(float(row["scan_time_s"]) for row in task_rows),
            "gripper_action": sum(float(row["gripper_time_s"]) for row in task_rows),
            "settle_time": sum(float(row["settle_time_s"]) for row in task_rows),
            "operator_wait": operator_wait,
            "retry_time": sum(float(row["retry_time_s"]) for row in task_rows),
        }

    def add_stage_breakdown(
        self, scenario_id: str, stage_totals: dict[str, float], robot_active: float, elapsed: float
    ) -> None:
        for stage_name in [
            "xy_motion",
            "z_motion",
            "scan_wait",
            "gripper_action",
            "settle_time",
            "operator_wait",
            "retry_time",
        ]:
            total = stage_totals[stage_name]
            self.rows["stage_breakdown"].append(
                {
                    "scenario_id": scenario_id,
                    "stage_name": stage_name,
                    "total_time_s": round3(total),
                    "percentage_of_robot_active_time": round3((total / robot_active * 100) if robot_active > 0 and stage_name != "operator_wait" else 0.0),
                    "percentage_of_total_elapsed_time": round3((total / elapsed * 100) if elapsed > 0 else 0.0),
                    "notes": "Concept-level stage timing estimate.",
                }
            )

    def build_throughput_rows(self) -> None:
        batch_by_id = {row["scenario_id"]: row for row in self.rows["scenario_batch"]}
        for scenario_id, row in batch_by_id.items():
            for metric_name, value, unit, notes in [
                (
                    f"{scenario_id}_samples_per_hour_robot_active",
                    row["estimated_samples_per_hour_robot_active"],
                    "samples/hour",
                    "Excludes operator wait.",
                ),
                (
                    f"{scenario_id}_samples_per_hour_elapsed",
                    row["estimated_samples_per_hour_elapsed"],
                    "samples/hour",
                    "Includes operator wait.",
                ),
                (f"{scenario_id}_robot_active_time_s", row["robot_active_time_s"], "s", "Robot active batch time."),
                (f"{scenario_id}_total_elapsed_time_s", row["total_elapsed_time_s"], "s", "Elapsed batch time."),
            ]:
                self.rows["throughput"].append(
                    {
                        "scenario_id": scenario_id,
                        "throughput_metric": metric_name,
                        "value": value,
                        "unit": unit,
                        "notes": notes,
                    }
                )
        for scenario_id in ["manual_review_limited_capacity", "pick_failure_test"]:
            row = batch_by_id[scenario_id]
            self.rows["throughput"].append(
                {
                    "scenario_id": scenario_id,
                    "throughput_metric": f"{scenario_id}_samples_per_hour",
                    "value": row["estimated_samples_per_hour_elapsed"],
                    "unit": "samples/hour",
                    "notes": "Compatibility summary metric; uses elapsed throughput including operator wait when present.",
                }
            )

    def build_category_throughput(self) -> None:
        grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
        for row in self.rows["task_cycle"]:
            if row["state_machine_final_status"] in COMPLETED_STATUSES:
                grouped[(str(row["scenario_id"]), str(row["sample_category"]))].append(row)
        for (scenario_id, category), rows in sorted(grouped.items()):
            robot_active = sum(float(row["robot_active_time_s"]) for row in rows)
            count = len(rows)
            self.rows["category_throughput"].append(
                {
                    "scenario_id": scenario_id,
                    "sample_category": category,
                    "completed_sample_count": count,
                    "robot_active_time_s": round3(robot_active),
                    "estimated_samples_per_hour_robot_active": round3(count / robot_active * 3600 if robot_active > 0 else 0.0),
                    "notes": "Category throughput excludes operator wait allocation.",
                }
            )

    def build_pending_impact(self) -> None:
        scenario_ids = sorted({row["scenario_id"] for row in self.pending_log})
        baseline = next(
            row for row in self.rows["scenario_batch"] if row["scenario_id"] == "baseline"
        )
        baseline_elapsed_sph = float(baseline["estimated_samples_per_hour_elapsed"])
        for scenario_id in scenario_ids:
            if not any(row["queue_action"] == "enqueue" for row in self.pending_log if row["scenario_id"] == scenario_id):
                continue
            hold_events = [row for row in self.hold_events if row["scenario_id"] == scenario_id]
            categories = sorted({row["sample_category"] for row in self.pending_log if row["scenario_id"] == scenario_id})
            scenario_batch = next(row for row in self.rows["scenario_batch"] if row["scenario_id"] == scenario_id)
            scenario_elapsed_sph = float(scenario_batch["estimated_samples_per_hour_elapsed"])
            impact_pct = (
                (baseline_elapsed_sph - scenario_elapsed_sph) / baseline_elapsed_sph * 100
                if baseline_elapsed_sph > 0
                else 0.0
            )
            for category in categories:
                pending_rows = [
                    row for row in self.pending_log if row["scenario_id"] == scenario_id and row["sample_category"] == category
                ]
                output_box_id = pending_rows[0]["target_output_box"] if pending_rows else ""
                service_count = sum(
                    1
                    for row in hold_events
                    if row["sample_category"] == category and row["event_type"] == "operator_cleared_output_box"
                )
                self.rows["pending_impact"].append(
                    {
                        "scenario_id": scenario_id,
                        "sample_category": category,
                        "output_box_id": output_box_id,
                        "hold_event_count": sum(
                            1
                            for row in hold_events
                            if row["sample_category"] == category and row["event_type"] == "category_hold"
                        ),
                        "resume_event_count": sum(
                            1
                            for row in hold_events
                            if row["sample_category"] == category and row["event_type"] == "category_resume"
                        ),
                        "pending_task_count": sum(1 for row in pending_rows if row["queue_action"] == "enqueue"),
                        "resumed_task_count": sum(1 for row in pending_rows if row["queue_action"] == "dequeue_resume"),
                        "operator_wait_time_s": round3(service_count * param("category_hold_operator_service_time_s")),
                        "additional_elapsed_time_s": round3(service_count * param("category_hold_operator_service_time_s")),
                        "throughput_impact_percent": round3(impact_pct),
                        "notes": "Pending wait is tracked separately from robot active motion time.",
                    }
                )

    def build_pick_failure_impact(self) -> None:
        for row in self.rows["task_cycle"]:
            if row["retry_time_s"] and float(row["retry_time_s"]) > 0:
                self.rows["pick_failure_impact"].append(
                    {
                        "scenario_id": row["scenario_id"],
                        "task_id": row["task_id"],
                        "tube_id": row["tube_id"],
                        "sample_category": row["sample_category"],
                        "state_machine_final_status": row["state_machine_final_status"],
                        "retry_time_s": row["retry_time_s"],
                        "robot_active_time_s": row["robot_active_time_s"],
                        "operator_wait_time_s": row["operator_wait_time_s"],
                        "notes": "Pick failure is execution handling and not abnormal sample routing.",
                    }
                )

    def validate(self) -> str:
        issues: list[str] = []
        task_cycle_keys = {(row["scenario_id"], row["task_id"]) for row in self.rows["task_cycle"]}
        for row in self.trajectory_tasks:
            if row["trajectory_generated"] == "true" and (row["scenario_id"], row["task_id"]) not in task_cycle_keys:
                issues.append(f"generated trajectory missing cycle time: {row['scenario_id']} {row['task_id']}")
        if any(float(row["segment_time_s"]) < 0 for row in self.rows["segment_time"]):
            issues.append("negative segment_time_s")
        completed_in_batch = sum(int(row["completed_sample_count"]) for row in self.rows["scenario_batch"])
        completed_results = sum(1 for row in self.task_results if row["final_status"] in COMPLETED_STATUSES)
        if completed_in_batch != completed_results:
            issues.append("completed task count mismatch in batch summary")
        for row in self.rows["task_cycle"]:
            if row["state_machine_final_status"] == "pending_waiting_resume" and row["cycle_time_status"] != "not_generated_pending":
                issues.append("pending_waiting_resume misclassified")
            if row["state_machine_final_status"] == "pick_failed_needs_operator_check" and row["cycle_time_status"] != "not_generated_pick_failure":
                issues.append("pick_failed_needs_operator_check misclassified")
        if any(float(row["robot_active_time_s"]) <= 0 for row in self.rows["scenario_batch"]):
            issues.append("scenario robot_active_time_s is not positive")
        if any(float(row["total_elapsed_time_s"]) < float(row["robot_active_time_s"]) for row in self.rows["scenario_batch"]):
            issues.append("elapsed time is less than robot active time")
        if any(float(row["estimated_samples_per_hour_robot_active"]) <= 0 for row in self.rows["scenario_batch"]):
            issues.append("samples/hour robot active not positive")
        for scenario_id in {row["scenario_id"] for row in self.rows["stage_breakdown"]}:
            robot_pct = sum(
                float(row["percentage_of_robot_active_time"])
                for row in self.rows["stage_breakdown"]
                if row["scenario_id"] == scenario_id
            )
            elapsed_pct = sum(
                float(row["percentage_of_total_elapsed_time"])
                for row in self.rows["stage_breakdown"]
                if row["scenario_id"] == scenario_id
            )
            if not (99.0 <= robot_pct <= 101.0):
                issues.append(f"robot active stage percentage out of range: {scenario_id} {robot_pct}")
            if not (99.0 <= elapsed_pct <= 101.0):
                issues.append(f"elapsed stage percentage out of range: {scenario_id} {elapsed_pct}")
        self.validation_issues = issues
        return "PASS" if not issues else "FAIL"

    def write_outputs(self, validation_status: str) -> None:
        write_csv(PARAMETERS_CSV, ["parameter", "value", "unit", "notes"], self.rows["parameters"])
        write_csv(
            SEGMENT_TIME_CSV,
            [
                "scenario_id",
                "task_id",
                "tube_id",
                "segment_index",
                "motion_type",
                "axis_mode",
                "segment_distance_mm",
                "delta_z_mm",
                "time_model",
                "segment_time_s",
                "time_category",
                "notes",
            ],
            self.rows["segment_time"],
        )
        write_csv(
            TASK_CYCLE_CSV,
            [
                "scenario_id",
                "task_id",
                "tube_id",
                "state_machine_final_status",
                "trajectory_status",
                "sample_category",
                "target_type",
                "target_box_id",
                "robot_active_time_s",
                "operator_wait_time_s",
                "total_elapsed_time_s",
                "xy_motion_time_s",
                "z_motion_time_s",
                "scan_time_s",
                "gripper_time_s",
                "settle_time_s",
                "retry_time_s",
                "segment_count",
                "waypoint_count",
                "cycle_time_status",
                "notes",
            ],
            self.rows["task_cycle"],
        )
        write_csv(
            SCENARIO_BATCH_CSV,
            [
                "scenario_id",
                "completed_sample_count",
                "normal_completed_count",
                "manual_review_completed_count",
                "pending_count",
                "resumed_pending_count",
                "pick_failed_count",
                "robot_active_time_s",
                "operator_wait_time_s",
                "total_elapsed_time_s",
                "average_cycle_time_robot_active_s",
                "average_cycle_time_elapsed_s",
                "estimated_samples_per_hour_robot_active",
                "estimated_samples_per_hour_elapsed",
                "bottleneck_stage",
                "notes",
            ],
            self.rows["scenario_batch"],
        )
        write_csv(THROUGHPUT_CSV, ["scenario_id", "throughput_metric", "value", "unit", "notes"], self.rows["throughput"])
        write_csv(
            STAGE_BREAKDOWN_CSV,
            [
                "scenario_id",
                "stage_name",
                "total_time_s",
                "percentage_of_robot_active_time",
                "percentage_of_total_elapsed_time",
                "notes",
            ],
            self.rows["stage_breakdown"],
        )
        write_csv(
            CATEGORY_THROUGHPUT_CSV,
            [
                "scenario_id",
                "sample_category",
                "completed_sample_count",
                "robot_active_time_s",
                "estimated_samples_per_hour_robot_active",
                "notes",
            ],
            self.rows["category_throughput"],
        )
        write_csv(
            PENDING_IMPACT_CSV,
            [
                "scenario_id",
                "sample_category",
                "output_box_id",
                "hold_event_count",
                "resume_event_count",
                "pending_task_count",
                "resumed_task_count",
                "operator_wait_time_s",
                "additional_elapsed_time_s",
                "throughput_impact_percent",
                "notes",
            ],
            self.rows["pending_impact"],
        )
        write_csv(
            PICK_FAILURE_IMPACT_CSV,
            [
                "scenario_id",
                "task_id",
                "tube_id",
                "sample_category",
                "state_machine_final_status",
                "retry_time_s",
                "robot_active_time_s",
                "operator_wait_time_s",
                "notes",
            ],
            self.rows["pick_failure_impact"],
        )
        self.write_figures()
        self.write_report(validation_status)

    def write_figures(self) -> None:
        FIG_DIR.mkdir(parents=True, exist_ok=True)
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        completed_rows = [row for row in self.rows["task_cycle"] if row["state_machine_final_status"] in COMPLETED_STATUSES]
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.scatter(range(len(completed_rows)), [float(row["robot_active_time_s"]) for row in completed_rows], s=10, color="#4f81bd")
        ax.set_title("Cycle Time Per Completed Task v1")
        ax.set_xlabel("completed task index")
        ax.set_ylabel("robot_active_time_s")
        fig.tight_layout()
        fig.savefig(FIG_DIR / "cycle_time_per_task_v1.png", dpi=160)
        plt.close(fig)

        baseline_stage = [row for row in self.rows["stage_breakdown"] if row["scenario_id"] == "baseline"]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar([row["stage_name"] for row in baseline_stage], [float(row["total_time_s"]) for row in baseline_stage], color="#70ad47")
        ax.set_title("Cycle Time Stage Breakdown v1")
        ax.set_ylabel("total_time_s")
        ax.tick_params(axis="x", rotation=25)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "cycle_time_stage_breakdown_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(9, 4))
        labels = [row["scenario_id"] for row in self.rows["scenario_batch"]]
        active = [float(row["estimated_samples_per_hour_robot_active"]) for row in self.rows["scenario_batch"]]
        elapsed = [float(row["estimated_samples_per_hour_elapsed"]) for row in self.rows["scenario_batch"]]
        x = range(len(labels))
        ax.bar([i - 0.2 for i in x], active, width=0.4, label="robot_active")
        ax.bar([i + 0.2 for i in x], elapsed, width=0.4, label="elapsed")
        ax.set_xticks(list(x), labels, rotation=20)
        ax.set_ylabel("samples/hour")
        ax.set_title("Scenario Throughput Comparison v1")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG_DIR / "scenario_throughput_comparison_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(7, 4))
        pending = self.rows["pending_impact"] or [{"scenario_id": "none", "throughput_impact_percent": 0}]
        ax.bar([row["scenario_id"] for row in pending], [float(row["throughput_impact_percent"]) for row in pending], color="#c0504d")
        ax.set_title("Pending Resume Time Impact v1")
        ax.set_ylabel("throughput impact percent")
        fig.tight_layout()
        fig.savefig(FIG_DIR / "pending_resume_time_impact_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(10, 4))
        labels = [f"{row['scenario_id']}:{row['sample_category']}" for row in self.rows["category_throughput"]]
        ax.bar(labels, [float(row["estimated_samples_per_hour_robot_active"]) for row in self.rows["category_throughput"]], color="#8064a2")
        ax.set_title("Category Throughput Summary v1")
        ax.set_ylabel("samples/hour robot active")
        ax.tick_params(axis="x", rotation=70)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "category_throughput_summary_v1.png", dpi=160)
        plt.close(fig)

    def write_report(self, validation_status: str) -> None:
        batch_by_id = {row["scenario_id"]: row for row in self.rows["scenario_batch"]}
        baseline = batch_by_id["baseline"]
        forced = batch_by_id["forced_category_A_full"]
        manual = batch_by_id["manual_review_limited_capacity"]
        pick = batch_by_id["pick_failure_test"]
        baseline_elapsed = float(baseline["estimated_samples_per_hour_elapsed"])
        forced_impact = (
            (baseline_elapsed - float(forced["estimated_samples_per_hour_elapsed"])) / baseline_elapsed * 100
            if baseline_elapsed > 0
            else 0.0
        )
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_MD.write_text(
            "\n".join(
                [
                    "# Stage 7B-4 Trajectory-Based Cycle Time and Throughput Simulation Report",
                    "",
                    "## Scope",
                    "",
                    "- This stage does not use a camera.",
                    "- Cycle time is estimated from Stage 7B-3 trajectory segments and Stage 7B-2 state-machine outcomes.",
                    "- No CAD modeling, rendering, Stage 7A edits, `legacy_v1` edits, or XY slider binding fixes are performed.",
                    "- Stage 7A-3f XY slider binding remains deferred; it does not affect abstract cycle-time estimation but does affect final mechanical validation.",
                    "",
                    "## Timing Model",
                    "",
                    "- The timing model is concept-level and not final measured hardware performance.",
                    f"- XY speed={param('xy_nominal_speed_mm_s')} mm/s; Z speed={param('z_nominal_speed_mm_s')} mm/s.",
                    f"- Grip close/open={param('grip_close_time_s')} / {param('grip_open_time_s')} s.",
                    f"- Scan wait={param('scan_wait_time_s')} s.",
                    f"- Category hold operator service={param('category_hold_operator_service_time_s')} s; manual_review alarm pause={param('manual_review_alarm_pause_time_s')} s.",
                    "",
                    "## Scenario Results",
                    "",
                    f"- Baseline: robot_active_time_s={baseline['robot_active_time_s']}, total_elapsed_time_s={baseline['total_elapsed_time_s']}, robot_active throughput={baseline['estimated_samples_per_hour_robot_active']} samples/hour, elapsed throughput={baseline['estimated_samples_per_hour_elapsed']} samples/hour.",
                    f"- forced_category_A_full: operator_wait_time_s={forced['operator_wait_time_s']}, elapsed throughput={forced['estimated_samples_per_hour_elapsed']} samples/hour, throughput impact vs baseline elapsed={round3(forced_impact)}%.",
                    f"- manual_review_limited_capacity: completed_sample_count={manual['completed_sample_count']}, operator_wait_time_s={manual['operator_wait_time_s']}, elapsed throughput={manual['estimated_samples_per_hour_elapsed']} samples/hour.",
                    f"- pick_failure_test: completed_sample_count={pick['completed_sample_count']}, pick_failed_count={pick['pick_failed_count']}, elapsed throughput={pick['estimated_samples_per_hour_elapsed']} samples/hour.",
                    "",
                    "## Bottleneck",
                    "",
                    f"- Baseline bottleneck stage: {baseline['bottleneck_stage']}.",
                    "- Robot active throughput excludes operator service delay; elapsed throughput includes output service and manual_review alarm pauses.",
                    "",
                    "## Downstream Use",
                    "",
                    "- These estimates support report tables, animation timing, and later Isaac Sim presentation setup.",
                    "- Future calibration must use real motor speed/acceleration, Z-axis travel tuning, gripper timing, and scanner response measurements.",
                    f"- validation_status={validation_status}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    def run(self) -> str:
        self.write_parameters()
        self.build_segment_times()
        self.build_task_cycles()
        self.build_scenario_summaries()
        self.build_throughput_rows()
        self.build_category_throughput()
        self.build_pending_impact()
        self.build_pick_failure_impact()
        validation_status = self.validate()
        self.write_outputs(validation_status)
        return validation_status


def main() -> int:
    estimator = CycleTimeEstimator()
    validation_status = estimator.run()
    baseline = next(row for row in estimator.rows["scenario_batch"] if row["scenario_id"] == "baseline")
    forced = next(row for row in estimator.rows["scenario_batch"] if row["scenario_id"] == "forced_category_A_full")
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
    print(f"forced_category_A_full_throughput_impact_percent={round3(forced_impact)}")
    print(f"bottleneck_stage={baseline['bottleneck_stage']}")
    if estimator.validation_issues:
        for issue in estimator.validation_issues:
            print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
