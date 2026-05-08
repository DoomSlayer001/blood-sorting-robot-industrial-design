from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"
FIG_DIR = SIM_DIR / "figures"
REPORT_DIR = ROOT / "reports"

OCCUPANCY_CSV = SIM_DIR / "input_box_occupancy_map_v1.csv"
TASK_MANIFEST_CSV = SIM_DIR / "sorting_task_manifest_v1.csv"
TASK_RESULT_CSV = SIM_DIR / "sorting_state_machine_task_result_v1.csv"
EVENT_LOG_CSV = SIM_DIR / "sorting_state_machine_event_log_v1.csv"
HOLD_EVENTS_CSV = SIM_DIR / "category_hold_resume_events_v1.csv"
PENDING_LOG_CSV = SIM_DIR / "pending_queue_log_v1.csv"
ABNORMAL_LOG_CSV = SIM_DIR / "abnormal_handling_log_v1.csv"
COLLISION_ENV_CSV = SIM_DIR / "collision_envelope_definition_v1.csv"
SIM_INTERFACE_CSV = SIM_DIR / "simulation_interface_table_v1.csv"

WAYPOINTS_CSV = SIM_DIR / "trajectory_waypoints_v1.csv"
SEGMENTS_CSV = SIM_DIR / "trajectory_segments_v1.csv"
TASK_SUMMARY_CSV = SIM_DIR / "trajectory_task_summary_v1.csv"
WORKSPACE_CSV = SIM_DIR / "trajectory_workspace_check_v1.csv"
COLLISION_CSV = SIM_DIR / "trajectory_collision_envelope_check_v1.csv"
SCENARIO_SUMMARY_CSV = SIM_DIR / "trajectory_scenario_summary_v1.csv"
WARNING_LOG_CSV = SIM_DIR / "trajectory_warning_log_v1.csv"
REPORT_MD = REPORT_DIR / "stage_7b3_trajectory_collision_precheck_report.md"

SAFE_Z_MM = 190.0
PICK_Z_MM = 145.0
SCAN_Z_MM = 155.0
PLACE_Z_MM = 135.0
MANUAL_REVIEW_PLACE_Z_MM = 135.0
GRIPPER_CLEARANCE_Z_MM = 55.0
TUBE_TOP_Z_MM = 125.0
RACK_TOP_Z_MM = 90.0
SCAN_X_MM = 0.0
SCAN_Y_MM = 20.0

WORKSPACE = {
    "x_min": -520.0,
    "x_max": 520.0,
    "y_min": -240.0,
    "y_max": 360.0,
    "z_min": 80.0,
    "z_max": 230.0,
}

OUTPUT_BOX_ORIGINS = {
    "output_box_A": (180.0, -170.0),
    "output_box_B": (330.0, -170.0),
    "output_box_C": (180.0, 10.0),
    "output_box_D": (330.0, 10.0),
}
MANUAL_REVIEW_ORIGIN = (-420.0, 275.0)
SLOT_PITCH_MM = 25.0

FULL_PLACE_STATUSES = {
    "completed_output",
    "completed_manual_review",
    "pick_failed_retried_completed",
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


def distance(a: dict[str, object], b: dict[str, object]) -> float:
    return math.sqrt(
        (float(a["x_mm"]) - float(b["x_mm"])) ** 2
        + (float(a["y_mm"]) - float(b["y_mm"])) ** 2
        + (float(a["z_mm"]) - float(b["z_mm"])) ** 2
    )


def target_slot_index(target_slot_id: str) -> int:
    digits = "".join(ch for ch in target_slot_id if ch.isdigit())
    return max(int(digits or "1") - 1, 0)


def slot_xy_from_index(origin: tuple[float, float], index: int, cols: int = 6) -> tuple[float, float]:
    row = index // cols
    col = index % cols
    return origin[0] + col * SLOT_PITCH_MM, origin[1] + row * SLOT_PITCH_MM


class TrajectoryGenerator:
    def __init__(self) -> None:
        self.occupancy = read_csv(OCCUPANCY_CSV)
        self.task_manifest = read_csv(TASK_MANIFEST_CSV)
        self.task_results = read_csv(TASK_RESULT_CSV)
        self.events = read_csv(EVENT_LOG_CSV)
        self.hold_events = read_csv(HOLD_EVENTS_CSV)
        self.pending_log = read_csv(PENDING_LOG_CSV)
        self.abnormal_log = read_csv(ABNORMAL_LOG_CSV)
        self.collision_env = read_csv(COLLISION_ENV_CSV)
        self.sim_interface = read_csv(SIM_INTERFACE_CSV)
        self.manifest_by_task = {row["task_id"]: row for row in self.task_manifest}
        self.output_slot_counter: defaultdict[tuple[str, str], int] = defaultdict(int)
        self.manual_slot_counter: defaultdict[str, int] = defaultdict(int)
        self.rows: dict[str, list[dict[str, object]]] = {
            "waypoints": [],
            "segments": [],
            "workspace": [],
            "collision": [],
            "task_summary": [],
            "scenario_summary": [],
            "warnings": [],
        }

    def add_warning(self, scenario_id: str, task_id: str, warning_type: str, notes: str) -> None:
        self.rows["warnings"].append(
            {
                "scenario_id": scenario_id,
                "task_id": task_id,
                "warning_type": warning_type,
                "severity": "WARNING",
                "notes": notes,
            }
        )

    def make_waypoint(
        self,
        result: dict[str, str],
        index: int,
        name: str,
        x: float,
        y: float,
        z: float,
        gripper_state: str,
        notes: str,
    ) -> dict[str, object]:
        waypoint = {
            "scenario_id": result["scenario_id"],
            "task_id": result["task_id"],
            "tube_id": result["tube_id"],
            "waypoint_index": index,
            "waypoint_name": name,
            "x_mm": round(x, 3),
            "y_mm": round(y, 3),
            "z_mm": round(z, 3),
            "gripper_state": gripper_state,
            "sample_category": result["sample_category"],
            "target_type": result["target_type"],
            "target_box_id": result["target_box_id"],
            "source_slot_id": result["source_slot_id"],
            "state_machine_status": result["final_status"],
            "notes": notes,
        }
        self.rows["waypoints"].append(waypoint)
        self.add_workspace_check(waypoint)
        return waypoint

    def add_workspace_check(self, waypoint: dict[str, object]) -> None:
        x = float(waypoint["x_mm"])
        y = float(waypoint["y_mm"])
        z = float(waypoint["z_mm"])
        x_ok = WORKSPACE["x_min"] <= x <= WORKSPACE["x_max"]
        y_ok = WORKSPACE["y_min"] <= y <= WORKSPACE["y_max"]
        z_ok = WORKSPACE["z_min"] <= z <= WORKSPACE["z_max"]
        if not (x_ok and y_ok and z_ok):
            status = "FAIL"
            notes = "waypoint exceeds conservative soft limit"
        else:
            status = "WARNING"
            notes = "within conservative placeholder workspace; final calibrated soft limits are not yet available"
        self.rows["workspace"].append(
            {
                "scenario_id": waypoint["scenario_id"],
                "task_id": waypoint["task_id"],
                "waypoint_name": waypoint["waypoint_name"],
                "x_mm": waypoint["x_mm"],
                "y_mm": waypoint["y_mm"],
                "z_mm": waypoint["z_mm"],
                "x_in_range": "true" if x_ok else "false",
                "y_in_range": "true" if y_ok else "false",
                "z_in_range": "true" if z_ok else "false",
                "workspace_status": status,
                "notes": notes,
            }
        )
        if status == "WARNING":
            self.add_warning(
                str(waypoint["scenario_id"]),
                str(waypoint["task_id"]),
                "workspace_limit_approximate",
                notes,
            )

    def target_xyz(self, result: dict[str, str]) -> tuple[float, float, float]:
        if result["final_status"] == "completed_manual_review":
            index = self.manual_slot_counter[result["scenario_id"]]
            self.manual_slot_counter[result["scenario_id"]] += 1
            x, y = slot_xy_from_index(MANUAL_REVIEW_ORIGIN, index, cols=3)
            return x, y, MANUAL_REVIEW_PLACE_Z_MM
        output_box = result["target_box_id"]
        key = (result["scenario_id"], output_box)
        index = self.output_slot_counter[key]
        self.output_slot_counter[key] += 1
        x, y = slot_xy_from_index(OUTPUT_BOX_ORIGINS.get(output_box, (260.0, 0.0)), index)
        return x, y, PLACE_Z_MM

    def build_full_waypoints(self, result: dict[str, str], retry_success: bool = False) -> list[dict[str, object]]:
        source_x = float(result["source_input_box_id"] and self.manifest_by_task[result["task_id"]]["source_x_mm"])
        source_y = float(self.manifest_by_task[result["task_id"]]["source_y_mm"])
        pick_z = float(self.manifest_by_task[result["task_id"]]["source_z_pick_mm"] or PICK_Z_MM)
        target_x, target_y, target_z = self.target_xyz(result)
        waypoints: list[dict[str, object]] = []
        idx = 1

        def add(name: str, x: float, y: float, z: float, grip: str, notes: str) -> None:
            nonlocal idx
            waypoints.append(self.make_waypoint(result, idx, name, x, y, z, grip, notes))
            idx += 1

        add("home_safe", 0.0, 0.0, SAFE_Z_MM, "open", "safe home above rack/tube top")
        add("move_xy_above_pick", source_x, source_y, SAFE_Z_MM, "open", "XY move only at safe_z")
        add("descend_to_pick", source_x, source_y, pick_z, "open", "Z descend allowed at pick target")
        add("grip_close", source_x, source_y, pick_z, "closed", "gripper action")
        if retry_success:
            add("lift_check_retry_required", source_x, source_y, SAFE_Z_MM, "closed", "first pick attempt failed; retry once")
            add("descend_to_pick_retry", source_x, source_y, pick_z, "open", "retry descend at same pick target")
            add("grip_close_retry", source_x, source_y, pick_z, "closed", "retry grip succeeded")
        add("lift_to_safe_z", source_x, source_y, SAFE_Z_MM, "closed", "lift before XY travel")
        add("move_xy_above_scan", SCAN_X_MM, SCAN_Y_MM, SAFE_Z_MM, "closed", "scan is table-driven, no camera recognition")
        add("descend_or_align_to_scan", SCAN_X_MM, SCAN_Y_MM, SCAN_Z_MM, "closed", "scan alignment placeholder")
        add("scan_wait", SCAN_X_MM, SCAN_Y_MM, SCAN_Z_MM, "closed", "barcode/status wait; no vision localization")
        add("lift_to_safe_z_after_scan", SCAN_X_MM, SCAN_Y_MM, SAFE_Z_MM, "closed", "lift before place XY")
        add("move_xy_above_place", target_x, target_y, SAFE_Z_MM, "closed", "XY place move at safe_z")
        add("descend_to_place", target_x, target_y, target_z, "closed", "Z descend allowed at place target")
        add("grip_open", target_x, target_y, target_z, "open", "release tube")
        add("lift_to_safe_z_after_place", target_x, target_y, SAFE_Z_MM, "open", "return to safe_z after place")
        return waypoints

    def build_pick_failure_waypoints(self, result: dict[str, str]) -> list[dict[str, object]]:
        source = self.manifest_by_task[result["task_id"]]
        source_x = float(source["source_x_mm"])
        source_y = float(source["source_y_mm"])
        pick_z = float(source["source_z_pick_mm"] or PICK_Z_MM)
        waypoints: list[dict[str, object]] = []
        idx = 1

        def add(name: str, z: float, grip: str, notes: str) -> None:
            nonlocal idx
            waypoints.append(self.make_waypoint(result, idx, name, source_x, source_y, z, grip, notes))
            idx += 1

        add("home_safe", SAFE_Z_MM, "open", "safe home above rack/tube top")
        add("move_xy_above_pick", SAFE_Z_MM, "open", "XY move to pick at safe_z")
        add("descend_to_pick", pick_z, "open", "first pick attempt")
        add("grip_close", pick_z, "closed", "pick attempt failed")
        add("lift_check", SAFE_Z_MM, "closed", "lift check detects pick_failed")
        add("descend_to_pick_retry", pick_z, "open", "retry once")
        add("grip_close_retry", pick_z, "closed", "retry failed")
        add("lift_check_retry_failed", SAFE_Z_MM, "closed", "operator check required; no place trajectory generated")
        return waypoints

    def motion_type(self, a: dict[str, object], b: dict[str, object]) -> tuple[str, str, bool]:
        if a["gripper_state"] != b["gripper_state"] and a["x_mm"] == b["x_mm"] and a["y_mm"] == b["y_mm"] and a["z_mm"] == b["z_mm"]:
            return "gripper_action", "gripper", False
        if "scan_wait" in str(b["waypoint_name"]):
            return "scan_wait", "dwell", False
        if float(a["z_mm"]) != float(b["z_mm"]) and float(a["x_mm"]) == float(b["x_mm"]) and float(a["y_mm"]) == float(b["y_mm"]):
            return ("z_lift" if float(b["z_mm"]) > float(a["z_mm"]) else "z_descend", "z_axis", True)
        if float(a["z_mm"]) == SAFE_Z_MM and float(b["z_mm"]) == SAFE_Z_MM:
            return "xy_move_at_safe_z", "xy_axes", True
        return "skip_or_failure", "mixed", True

    def add_segments(self, result: dict[str, str], waypoints: list[dict[str, object]]) -> None:
        for index, (a, b) in enumerate(zip(waypoints, waypoints[1:]), start=1):
            motion_type, axis_mode, requires_safe_z = self.motion_type(a, b)
            segment = {
                "scenario_id": result["scenario_id"],
                "task_id": result["task_id"],
                "tube_id": result["tube_id"],
                "segment_index": index,
                "from_waypoint": a["waypoint_name"],
                "to_waypoint": b["waypoint_name"],
                "motion_type": motion_type,
                "axis_mode": axis_mode,
                "start_x_mm": a["x_mm"],
                "start_y_mm": a["y_mm"],
                "start_z_mm": a["z_mm"],
                "end_x_mm": b["x_mm"],
                "end_y_mm": b["y_mm"],
                "end_z_mm": b["z_mm"],
                "segment_distance_mm": round(distance(a, b), 3),
                "requires_safe_z": "true" if requires_safe_z else "false",
                "collision_check_required": "true" if motion_type not in {"scan_wait", "gripper_action"} else "false",
                "notes": "XY travel is constrained to safe_z" if motion_type == "xy_move_at_safe_z" else "",
            }
            self.rows["segments"].append(segment)
            self.add_collision_checks(segment, result)

    def add_collision_checks(self, segment: dict[str, object], result: dict[str, str]) -> None:
        motion_type = str(segment["motion_type"])
        checks = [
            ("gripper_envelope", "tube_envelope"),
            ("gripper_envelope", "rack_envelope"),
            ("z_axis_module_envelope", "rack_envelope"),
            ("x_axis_beam_envelope", "tube_envelope"),
            ("x_axis_beam_envelope", "rack_envelope"),
            ("cable_chain_envelope", "gantry_envelope"),
            ("enclosure_frame_envelope", "moving_gantry_envelope"),
            ("control_box_envelope", "motion_envelope"),
        ]
        if motion_type == "xy_move_at_safe_z":
            clearance = SAFE_Z_MM - TUBE_TOP_Z_MM
            status = "PASS" if clearance >= GRIPPER_CLEARANCE_Z_MM else "WARNING"
            risk = "low" if status == "PASS" else "medium"
            notes = "safe_z travel remains above tube/rack top envelope"
        elif motion_type == "z_descend":
            target_name = str(segment["to_waypoint"])
            allowed = any(token in target_name for token in ["pick", "scan", "place"])
            clearance = 15.0 if allowed else -1.0
            status = "WARNING" if allowed else "FAIL"
            risk = "medium" if allowed else "high"
            notes = "Z descend occurs only at pick/place/scan target; exact CAD clearance approximate" if allowed else "Z descend outside allowed target"
        elif motion_type == "skip_or_failure":
            clearance = ""
            status = "NOT_CHECKED_APPROXIMATE"
            risk = "medium"
            notes = "partial pick-failure segment; no final place sweep"
        else:
            clearance = ""
            status = "NOT_CHECKED_APPROXIMATE"
            risk = "low"
            notes = "gripper/dwell segment has no sweep envelope in this simplified check"

        for moving, checked in checks:
            row_status = status
            row_notes = notes
            row_clearance = clearance
            if moving in {"cable_chain_envelope", "enclosure_frame_envelope", "control_box_envelope"}:
                row_status = "NOT_CHECKED_APPROXIMATE"
                row_notes = "static/sweep relationship is approximate until CAD/Isaac Sim collision model"
                row_clearance = ""
            self.rows["collision"].append(
                {
                    "scenario_id": segment["scenario_id"],
                    "task_id": segment["task_id"],
                    "segment_index": segment["segment_index"],
                    "segment_type": motion_type,
                    "moving_object": moving,
                    "checked_against": checked,
                    "collision_status": row_status,
                    "estimated_clearance_mm": row_clearance,
                    "risk_level": risk if row_status != "NOT_CHECKED_APPROXIMATE" else "medium",
                    "notes": row_notes,
                }
            )
            if row_status in {"WARNING", "NOT_CHECKED_APPROXIMATE"}:
                self.add_warning(
                    str(segment["scenario_id"]),
                    str(segment["task_id"]),
                    f"collision_{row_status.lower()}",
                    row_notes,
                )

    def run(self) -> str:
        for result in self.task_results:
            final_status = result["final_status"]
            if final_status in FULL_PLACE_STATUSES:
                retry_success = final_status == "pick_failed_retried_completed"
                waypoints = self.build_full_waypoints(result, retry_success=retry_success)
                self.add_segments(result, waypoints)
                self.add_task_summary(result, waypoints, "generated_ok" if not retry_success else "generated_with_warning")
            elif final_status == "pick_failed_needs_operator_check":
                waypoints = self.build_pick_failure_waypoints(result)
                self.add_segments(result, waypoints)
                self.add_task_summary(result, waypoints, "not_generated_pick_failure")
            elif final_status == "pending_waiting_resume":
                self.add_task_summary(result, [], "not_generated_pending")
            elif final_status == "paused_manual_review_full":
                self.add_task_summary(result, [], "not_generated_manual_review_full_pause")
            else:
                self.add_task_summary(result, [], "error")

        validation_status = self.internal_validation()
        self.write_outputs(validation_status)
        return validation_status

    def add_task_summary(self, result: dict[str, str], waypoints: list[dict[str, object]], trajectory_status: str) -> None:
        task_segments = [
            row
            for row in self.rows["segments"]
            if row["scenario_id"] == result["scenario_id"] and row["task_id"] == result["task_id"]
        ]
        workspace_rows = [
            row
            for row in self.rows["workspace"]
            if row["scenario_id"] == result["scenario_id"] and row["task_id"] == result["task_id"]
        ]
        collision_rows = [
            row
            for row in self.rows["collision"]
            if row["scenario_id"] == result["scenario_id"] and row["task_id"] == result["task_id"]
        ]
        workspace_status = "NOT_CHECKED" if not workspace_rows else self.rollup_status(
            [str(row["workspace_status"]) for row in workspace_rows], warning_label="WARNING"
        )
        collision_status = "NOT_CHECKED" if not collision_rows else self.rollup_status(
            [str(row["collision_status"]) for row in collision_rows],
            warning_label="WARNING",
            approximate_label="NOT_CHECKED_APPROXIMATE",
        )
        if trajectory_status == "generated_ok" and (workspace_status != "PASS" or collision_status != "PASS"):
            trajectory_status = "generated_with_warning"
        self.rows["task_summary"].append(
            {
                "scenario_id": result["scenario_id"],
                "task_id": result["task_id"],
                "tube_id": result["tube_id"],
                "state_machine_final_status": result["final_status"],
                "trajectory_generated": "true"
                if waypoints and not trajectory_status.startswith("not_generated")
                else "false",
                "waypoint_count": len(waypoints),
                "segment_count": len(task_segments),
                "total_path_length_mm": round(sum(float(row["segment_distance_mm"]) for row in task_segments), 3),
                "workspace_status": workspace_status,
                "collision_status": collision_status,
                "trajectory_status": trajectory_status,
                "notes": "simplified Cartesian trajectory; final CAD/Isaac Sim collision verification still required",
            }
        )

    @staticmethod
    def rollup_status(statuses: list[str], warning_label: str, approximate_label: str = "") -> str:
        if "FAIL" in statuses:
            return "FAIL"
        if warning_label in statuses:
            return "WARNING"
        if approximate_label and approximate_label in statuses:
            return approximate_label
        if "NOT_CHECKED_APPROXIMATE" in statuses:
            return "NOT_CHECKED_APPROXIMATE"
        return "PASS"

    def internal_validation(self) -> str:
        issues: list[str] = []
        summary_by_key = {(row["scenario_id"], row["task_id"]): row for row in self.rows["task_summary"]}
        for result in self.task_results:
            key = (result["scenario_id"], result["task_id"])
            summary = summary_by_key.get(key)
            if summary is None:
                issues.append(f"missing trajectory summary for {key}")
                continue
            if result["final_status"] in FULL_PLACE_STATUSES and summary["trajectory_generated"] != "true":
                issues.append(f"completed task missing trajectory: {key}")
            if result["final_status"] == "pick_failed_needs_operator_check":
                place_waypoints = [
                    row
                    for row in self.rows["waypoints"]
                    if row["scenario_id"] == result["scenario_id"]
                    and row["task_id"] == result["task_id"]
                    and "place" in str(row["waypoint_name"])
                ]
                if place_waypoints:
                    issues.append(f"pick failure generated place waypoint: {key}")
            if result["abnormal_flag"] == "false":
                manual_waypoints = [
                    row
                    for row in self.rows["waypoints"]
                    if row["scenario_id"] == result["scenario_id"]
                    and row["task_id"] == result["task_id"]
                    and row["target_type"] == "manual_review"
                ]
                if manual_waypoints:
                    issues.append(f"normal sample generated manual_review trajectory: {key}")
        if any(row["workspace_status"] == "FAIL" for row in self.rows["workspace"]):
            issues.append("workspace check contains FAIL")
        if any(row["collision_status"] == "FAIL" for row in self.rows["collision"]):
            issues.append("collision check contains FAIL")
        self.validation_issues = issues
        return "PASS" if not issues else "FAIL"

    def write_outputs(self, validation_status: str) -> None:
        write_csv(
            WAYPOINTS_CSV,
            [
                "scenario_id",
                "task_id",
                "tube_id",
                "waypoint_index",
                "waypoint_name",
                "x_mm",
                "y_mm",
                "z_mm",
                "gripper_state",
                "sample_category",
                "target_type",
                "target_box_id",
                "source_slot_id",
                "state_machine_status",
                "notes",
            ],
            self.rows["waypoints"],
        )
        write_csv(
            SEGMENTS_CSV,
            [
                "scenario_id",
                "task_id",
                "tube_id",
                "segment_index",
                "from_waypoint",
                "to_waypoint",
                "motion_type",
                "axis_mode",
                "start_x_mm",
                "start_y_mm",
                "start_z_mm",
                "end_x_mm",
                "end_y_mm",
                "end_z_mm",
                "segment_distance_mm",
                "requires_safe_z",
                "collision_check_required",
                "notes",
            ],
            self.rows["segments"],
        )
        write_csv(
            TASK_SUMMARY_CSV,
            [
                "scenario_id",
                "task_id",
                "tube_id",
                "state_machine_final_status",
                "trajectory_generated",
                "waypoint_count",
                "segment_count",
                "total_path_length_mm",
                "workspace_status",
                "collision_status",
                "trajectory_status",
                "notes",
            ],
            self.rows["task_summary"],
        )
        write_csv(
            WORKSPACE_CSV,
            [
                "scenario_id",
                "task_id",
                "waypoint_name",
                "x_mm",
                "y_mm",
                "z_mm",
                "x_in_range",
                "y_in_range",
                "z_in_range",
                "workspace_status",
                "notes",
            ],
            self.rows["workspace"],
        )
        write_csv(
            COLLISION_CSV,
            [
                "scenario_id",
                "task_id",
                "segment_index",
                "segment_type",
                "moving_object",
                "checked_against",
                "collision_status",
                "estimated_clearance_mm",
                "risk_level",
                "notes",
            ],
            self.rows["collision"],
        )
        write_csv(
            WARNING_LOG_CSV,
            ["scenario_id", "task_id", "warning_type", "severity", "notes"],
            self.rows["warnings"],
        )
        self.write_scenario_summary(validation_status)
        self.write_figures()
        self.write_report(validation_status)

    def write_scenario_summary(self, validation_status: str) -> None:
        scenario_ids = sorted({row["scenario_id"] for row in self.task_results})
        rows: list[dict[str, object]] = []
        for scenario_id in scenario_ids:
            task_rows = [row for row in self.rows["task_summary"] if row["scenario_id"] == scenario_id]
            workspace_counts = Counter(row["workspace_status"] for row in self.rows["workspace"] if row["scenario_id"] == scenario_id)
            collision_counts = Counter(row["collision_status"] for row in self.rows["collision"] if row["scenario_id"] == scenario_id)
            rows.append(
                {
                    "scenario_id": scenario_id,
                    "state_machine_task_count": sum(1 for row in self.task_results if row["scenario_id"] == scenario_id),
                    "generated_trajectory_task_count": sum(1 for row in task_rows if row["trajectory_generated"] == "true"),
                    "not_generated_task_count": sum(1 for row in task_rows if row["trajectory_generated"] == "false"),
                    "workspace_pass_count": workspace_counts.get("PASS", 0),
                    "workspace_warning_count": workspace_counts.get("WARNING", 0),
                    "workspace_fail_count": workspace_counts.get("FAIL", 0),
                    "collision_pass_count": collision_counts.get("PASS", 0),
                    "collision_warning_count": collision_counts.get("WARNING", 0),
                    "collision_fail_count": collision_counts.get("FAIL", 0),
                    "collision_not_checked_approximate_count": collision_counts.get("NOT_CHECKED_APPROXIMATE", 0),
                    "validation_status": validation_status,
                    "notes": "scenario trajectory summary",
                }
            )
        write_csv(
            SCENARIO_SUMMARY_CSV,
            [
                "scenario_id",
                "state_machine_task_count",
                "generated_trajectory_task_count",
                "not_generated_task_count",
                "workspace_pass_count",
                "workspace_warning_count",
                "workspace_fail_count",
                "collision_pass_count",
                "collision_warning_count",
                "collision_fail_count",
                "collision_not_checked_approximate_count",
                "validation_status",
                "notes",
            ],
            rows,
        )
        self.rows["scenario_summary"] = rows

    def write_figures(self) -> None:
        FIG_DIR.mkdir(parents=True, exist_ok=True)
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        for scenario_id, filename in [
            ("baseline", "trajectory_top_view_baseline_v1.png"),
            ("forced_category_A_full", "trajectory_top_view_forced_category_A_full_v1.png"),
        ]:
            fig, ax = plt.subplots(figsize=(7, 6))
            for task_id in sorted({row["task_id"] for row in self.rows["waypoints"] if row["scenario_id"] == scenario_id})[:20]:
                pts = [row for row in self.rows["waypoints"] if row["scenario_id"] == scenario_id and row["task_id"] == task_id]
                ax.plot([float(row["x_mm"]) for row in pts], [float(row["y_mm"]) for row in pts], alpha=0.45)
            ax.set_title(f"Trajectory Top View {scenario_id} v1")
            ax.set_xlabel("x_mm")
            ax.set_ylabel("y_mm")
            ax.grid(True, linewidth=0.3)
            fig.tight_layout()
            fig.savefig(FIG_DIR / filename, dpi=160)
            plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4))
        sample_waypoints = [row for row in self.rows["waypoints"] if row["scenario_id"] == "baseline" and row["task_id"] == "TASK-7B1-001"]
        ax.plot([int(row["waypoint_index"]) for row in sample_waypoints], [float(row["z_mm"]) for row in sample_waypoints], marker="o")
        ax.set_title("Trajectory Z Profile v1")
        ax.set_xlabel("waypoint index")
        ax.set_ylabel("z_mm")
        ax.grid(True, linewidth=0.3)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "trajectory_z_profile_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(7, 4))
        workspace_counts = Counter(row["workspace_status"] for row in self.rows["workspace"])
        ax.bar(["PASS", "WARNING", "FAIL"], [workspace_counts.get(k, 0) for k in ["PASS", "WARNING", "FAIL"]], color=["#70ad47", "#ffc000", "#c0504d"])
        ax.set_title("Trajectory Workspace Check v1")
        ax.set_ylabel("waypoint checks")
        fig.tight_layout()
        fig.savefig(FIG_DIR / "trajectory_workspace_check_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4))
        collision_counts = Counter(row["collision_status"] for row in self.rows["collision"])
        labels = ["PASS", "WARNING", "FAIL", "NOT_CHECKED_APPROXIMATE"]
        ax.bar(labels, [collision_counts.get(k, 0) for k in labels], color=["#70ad47", "#ffc000", "#c0504d", "#8064a2"])
        ax.set_title("Trajectory Collision Envelope Summary v1")
        ax.set_ylabel("segment-object checks")
        ax.tick_params(axis="x", rotation=15)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "trajectory_collision_envelope_summary_v1.png", dpi=160)
        plt.close(fig)

    def write_report(self, validation_status: str) -> None:
        task_counts = Counter(row["trajectory_status"] for row in self.rows["task_summary"])
        workspace_counts = Counter(row["workspace_status"] for row in self.rows["workspace"])
        collision_counts = Counter(row["collision_status"] for row in self.rows["collision"])
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_MD.write_text(
            "\n".join(
                [
                    "# Stage 7B-3 Trajectory Generation and Collision Envelope Pre-check Report",
                    "",
                    "## Scope",
                    "",
                    "- This stage does not use a camera.",
                    "- Input occupancy and task routing are driven by internal tables from Stage 7B-1 and state machine results from Stage 7B-2.",
                    "- No CAD modeling, rendering, Stage 7A edits, `legacy_v1` edits, or XY slider binding fixes are performed.",
                    "- Stage 7A-3f XY slider binding remains a deferred mechanical integration issue and does not block abstract trajectory simulation.",
                    "",
                    "## Waypoint Rules",
                    "",
                    "- Completed output tasks generate pick-scan-output place trajectories.",
                    "- Completed manual_review tasks generate pick-scan-manual_review place trajectories.",
                    "- Resumed pending tasks generate complete trajectories after category_resume.",
                    "- `pick_failed_needs_operator_check` tasks generate pick-attempt and retry waypoints only, with no output/manual_review place trajectory.",
                    "- Normal samples never generate manual_review trajectories.",
                    "",
                    "## Height Strategy",
                    "",
                    f"- safe_z_mm={SAFE_Z_MM}; pick_z_mm uses source `z_pick_mm`; scan_z_mm={SCAN_Z_MM}; place_z_mm={PLACE_Z_MM}; manual_review_place_z_mm={MANUAL_REVIEW_PLACE_Z_MM}.",
                    "- XY moves occur only at safe_z.",
                    "- Z descends are limited to pick, scan alignment, and place target waypoints.",
                    "- The safe_z strategy is conservative and remains above the tube top placeholder.",
                    "",
                    "## Scenario Summary",
                    "",
                    f"- Generated trajectory task count: {sum(1 for row in self.rows['task_summary'] if row['trajectory_generated'] == 'true')}.",
                    f"- Not generated task count: {sum(1 for row in self.rows['task_summary'] if row['trajectory_generated'] == 'false')}.",
                    f"- Trajectory status counts: {dict(task_counts)}.",
                    "",
                    "## Workspace Check",
                    "",
                    f"- Workspace PASS/WARNING/FAIL: {workspace_counts.get('PASS', 0)} / {workspace_counts.get('WARNING', 0)} / {workspace_counts.get('FAIL', 0)}.",
                    "- Warnings indicate conservative placeholder soft limits; final calibrated axis limits are not yet available.",
                    "",
                    "## Collision Envelope Pre-check",
                    "",
                    f"- Collision PASS/WARNING/FAIL/NOT_CHECKED_APPROXIMATE: {collision_counts.get('PASS', 0)} / {collision_counts.get('WARNING', 0)} / {collision_counts.get('FAIL', 0)} / {collision_counts.get('NOT_CHECKED_APPROXIMATE', 0)}.",
                    "- WARNING and NOT_CHECKED_APPROXIMATE rows are intentional where exact CAD/Isaac Sim collision geometry is unavailable.",
                    "- This is a simplified envelope pre-check, not final SolidWorks or Isaac Sim collision verification.",
                    "",
                    "## Downstream Use",
                    "",
                    "- This stage provides trajectory foundations for cycle time, animation, and later Isaac Sim visualization.",
                    f"- validation_status={validation_status}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )


def main() -> int:
    generator = TrajectoryGenerator()
    validation_status = generator.run()
    workspace_counts = Counter(row["workspace_status"] for row in generator.rows["workspace"])
    collision_counts = Counter(row["collision_status"] for row in generator.rows["collision"])
    print(f"validation_status={validation_status}")
    print(f"generated_trajectory_task_count={sum(1 for row in generator.rows['task_summary'] if row['trajectory_generated'] == 'true')}")
    print(f"not_generated_task_count={sum(1 for row in generator.rows['task_summary'] if row['trajectory_generated'] == 'false')}")
    print(
        "workspace_counts="
        + f"PASS:{workspace_counts.get('PASS', 0)},WARNING:{workspace_counts.get('WARNING', 0)},FAIL:{workspace_counts.get('FAIL', 0)}"
    )
    print(
        "collision_counts="
        + f"PASS:{collision_counts.get('PASS', 0)},WARNING:{collision_counts.get('WARNING', 0)},FAIL:{collision_counts.get('FAIL', 0)},NOT_CHECKED_APPROXIMATE:{collision_counts.get('NOT_CHECKED_APPROXIMATE', 0)}"
    )
    if generator.validation_issues:
        for issue in generator.validation_issues:
            print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
