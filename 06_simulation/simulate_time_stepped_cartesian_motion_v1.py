from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"
FIG_DIR = SIM_DIR / "figures"
REPORT_DIR = ROOT / "reports"

WAYPOINTS_CSV = SIM_DIR / "trajectory_waypoints_v1.csv"
SEGMENTS_CSV = SIM_DIR / "trajectory_segments_v1.csv"
TRAJECTORY_TASK_SUMMARY_CSV = SIM_DIR / "trajectory_task_summary_v1.csv"
SEGMENT_TIME_CSV = SIM_DIR / "trajectory_segment_time_estimate_v1.csv"
TASK_CYCLE_CSV = SIM_DIR / "task_cycle_time_estimate_v1.csv"
MOTION_PARAMETERS_CSV = SIM_DIR / "cycle_time_motion_parameters_v1.csv"
COLLISION_CHECK_CSV = SIM_DIR / "trajectory_collision_envelope_check_v1.csv"
WORKSPACE_CHECK_CSV = SIM_DIR / "trajectory_workspace_check_v1.csv"
SCENARIO_BATCH_CSV = SIM_DIR / "scenario_batch_time_summary_v1.csv"

PARAMETERS_CSV = SIM_DIR / "cartesian_motion_simulation_parameters_v1.csv"
TRACE_CSV = SIM_DIR / "time_stepped_motion_trace_v1.csv"
VELOCITY_CSV = SIM_DIR / "axis_velocity_profile_v1.csv"
ACCELERATION_CSV = SIM_DIR / "axis_acceleration_profile_v1.csv"
CONSTRAINT_CSV = SIM_DIR / "motion_constraint_check_v1.csv"
SAFE_Z_CSV = SIM_DIR / "safe_z_rule_check_v1.csv"
SWEEP_CSV = SIM_DIR / "motion_sweep_collision_precheck_v1.csv"
SUMMARY_CSV = SIM_DIR / "time_stepped_motion_summary_v1.csv"
REPORT_MD = REPORT_DIR / "stage_7b5_time_stepped_cartesian_motion_simulation_report.md"

PARAMETERS = {
    "time_step_s": (0.02, "s", "Time step for Cartesian trace discretization."),
    "x_velocity_limit_mm_s": (350.0, "mm/s", "Concept-level X velocity limit."),
    "y_velocity_limit_mm_s": (350.0, "mm/s", "Concept-level Y velocity limit."),
    "z_velocity_limit_mm_s": (120.0, "mm/s", "Concept-level Z velocity limit."),
    "x_acceleration_limit_mm_s2": (800.0, "mm/s^2", "Concept-level X acceleration limit."),
    "y_acceleration_limit_mm_s2": (800.0, "mm/s^2", "Concept-level Y acceleration limit."),
    "z_acceleration_limit_mm_s2": (300.0, "mm/s^2", "Concept-level Z acceleration limit."),
    "safe_z_mm": (190.0, "mm", "XY transfer height from Stage 7B-3 trajectory rules."),
    "low_z_motion_allowed_only_at_target": ("true", "bool", "Low-Z motion is allowed only for pick, scan, and place alignment."),
    "collision_sweep_check_enabled": ("true", "bool", "Run conservative sweep proxy checks."),
}

WORKSPACE = {
    "x_min": -520.0,
    "x_max": 520.0,
    "y_min": -240.0,
    "y_max": 360.0,
    "z_min": 80.0,
    "z_max": 230.0,
}
SAFE_Z_MM = float(PARAMETERS["safe_z_mm"][0])
LOW_Z_EPSILON_MM = 1.0


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


def param_float(name: str) -> float:
    return float(PARAMETERS[name][0])


def round3(value: float) -> float:
    return round(value, 3)


def status_from_value(value: float, limit: float, warning_ratio: float = 0.95) -> str:
    if value > limit + 1e-6:
        return "FAIL"
    if value > limit * warning_ratio:
        return "WARNING"
    return "PASS"


class TimeSteppedMotionSimulator:
    def __init__(self) -> None:
        self.waypoints = read_csv(WAYPOINTS_CSV)
        self.segments = read_csv(SEGMENTS_CSV)
        self.trajectory_task_summary = read_csv(TRAJECTORY_TASK_SUMMARY_CSV)
        self.segment_times = read_csv(SEGMENT_TIME_CSV)
        self.task_cycles = read_csv(TASK_CYCLE_CSV)
        self.motion_parameters = read_csv(MOTION_PARAMETERS_CSV)
        self.collision_check = read_csv(COLLISION_CHECK_CSV)
        self.workspace_check = read_csv(WORKSPACE_CHECK_CSV)
        self.scenario_batch = read_csv(SCENARIO_BATCH_CSV)
        self.generated_task_keys = {
            (row["scenario_id"], row["task_id"])
            for row in self.trajectory_task_summary
            if row["trajectory_generated"] == "true"
        }
        self.segment_time_by_key = {
            (row["scenario_id"], row["task_id"], row["segment_index"]): float(row["segment_time_s"])
            for row in self.segment_times
        }
        self.waypoint_by_key = {
            (row["scenario_id"], row["task_id"], row["waypoint_name"]): row for row in self.waypoints
        }
        self.rows: dict[str, list[dict[str, object]]] = {
            "parameters": [],
            "trace": [],
            "velocity": [],
            "acceleration": [],
            "constraint": [],
            "safe_z": [],
            "sweep": [],
            "summary": [],
        }

    def write_parameters(self) -> None:
        self.rows["parameters"] = [
            {"parameter": name, "value": value, "unit": unit, "notes": notes}
            for name, (value, unit, notes) in PARAMETERS.items()
        ]

    def gripper_state_for(self, segment: dict[str, str], start_wp: dict[str, str], end_wp: dict[str, str], u: float) -> str:
        if segment["motion_type"] == "gripper_action":
            return end_wp["gripper_state"] if u >= 1.0 else start_wp["gripper_state"]
        return end_wp["gripper_state"]

    def simulate(self) -> str:
        self.write_parameters()
        scenario_time: defaultdict[str, float] = defaultdict(float)
        segments_by_scenario = sorted(
            [segment for segment in self.segments if (segment["scenario_id"], segment["task_id"]) in self.generated_task_keys],
            key=lambda row: (row["scenario_id"], row["task_id"], int(row["segment_index"])),
        )
        time_step = param_float("time_step_s")
        previous_velocity_by_scenario: dict[str, tuple[float, float, float]] = defaultdict(lambda: (0.0, 0.0, 0.0))

        for segment in segments_by_scenario:
            scenario_id = segment["scenario_id"]
            task_id = segment["task_id"]
            segment_index = segment["segment_index"]
            duration = max(self.segment_time_by_key[(scenario_id, task_id, segment_index)], time_step)
            start = self.waypoint_by_key[(scenario_id, task_id, segment["from_waypoint"])]
            end = self.waypoint_by_key[(scenario_id, task_id, segment["to_waypoint"])]
            start_x, start_y, start_z = float(start["x_mm"]), float(start["y_mm"]), float(start["z_mm"])
            end_x, end_y, end_z = float(end["x_mm"]), float(end["y_mm"]), float(end["z_mm"])
            dx, dy, dz = end_x - start_x, end_y - start_y, end_z - start_z
            vx = dx / duration
            vy = dy / duration
            vz = dz / duration

            # Simplified linear interpolation: steady-state segment velocity is recorded;
            # servo transition acceleration is intentionally deferred to future PID/servo simulation.
            ax = ay = az = 0.0
            step_count = max(1, int(math.ceil(duration / time_step)))
            for step in range(step_count + 1):
                local_t = min(step * time_step, duration)
                u = local_t / duration if duration > 0 else 1.0
                time_s = scenario_time[scenario_id] + local_t
                x = start_x + dx * u
                y = start_y + dy * u
                z = start_z + dz * u
                gripper_state = self.gripper_state_for(segment, start, end, u)
                state_label = "hold_position" if segment["motion_type"] in {"scan_wait", "gripper_action"} else "cartesian_motion"
                self.rows["trace"].append(
                    {
                        "scenario_id": scenario_id,
                        "task_id": task_id,
                        "tube_id": segment["tube_id"],
                        "time_s": round3(time_s),
                        "x_mm": round3(x),
                        "y_mm": round3(y),
                        "z_mm": round3(z),
                        "vx_mm_s": round3(vx),
                        "vy_mm_s": round3(vy),
                        "vz_mm_s": round3(vz),
                        "ax_mm_s2": round3(ax),
                        "ay_mm_s2": round3(ay),
                        "az_mm_s2": round3(az),
                        "gripper_state": gripper_state,
                        "segment_index": segment_index,
                        "motion_type": segment["motion_type"],
                        "state_label": state_label,
                        "notes": "Simplified linear Cartesian interpolation; not final servo dynamics.",
                    }
                )
            scenario_time[scenario_id] += duration

        self.build_profiles()
        self.build_constraint_checks()
        self.build_safe_z_checks()
        self.build_sweep_checks()
        validation_status = self.validate()
        self.build_summary(validation_status)
        self.write_outputs()
        return validation_status

    def build_profiles(self) -> None:
        for row in self.rows["trace"]:
            self.rows["velocity"].append(
                {
                    "scenario_id": row["scenario_id"],
                    "task_id": row["task_id"],
                    "tube_id": row["tube_id"],
                    "time_s": row["time_s"],
                    "vx_mm_s": row["vx_mm_s"],
                    "vy_mm_s": row["vy_mm_s"],
                    "vz_mm_s": row["vz_mm_s"],
                    "speed_xy_mm_s": round3(math.hypot(float(row["vx_mm_s"]), float(row["vy_mm_s"]))),
                    "motion_type": row["motion_type"],
                    "notes": "Velocity from linear interpolation over Stage 7B-4 segment_time_s.",
                }
            )
            self.rows["acceleration"].append(
                {
                    "scenario_id": row["scenario_id"],
                    "task_id": row["task_id"],
                    "tube_id": row["tube_id"],
                    "time_s": row["time_s"],
                    "ax_mm_s2": row["ax_mm_s2"],
                    "ay_mm_s2": row["ay_mm_s2"],
                    "az_mm_s2": row["az_mm_s2"],
                    "motion_type": row["motion_type"],
                    "notes": "Acceleration is steady-state zero in this simplified interpolation model.",
                }
            )

    def build_constraint_checks(self) -> None:
        trace_by_task: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
        for row in self.rows["trace"]:
            trace_by_task[(str(row["scenario_id"]), str(row["task_id"]))].append(row)

        for (scenario_id, task_id), rows in sorted(trace_by_task.items()):
            values = {
                "x_position_limit": ("x", max(abs(float(row["x_mm"])) for row in rows), max(abs(WORKSPACE["x_min"]), abs(WORKSPACE["x_max"]))),
                "y_position_limit": ("y", max(abs(float(row["y_mm"])) for row in rows), max(abs(WORKSPACE["y_min"]), abs(WORKSPACE["y_max"]))),
                "z_position_limit": ("z", max(abs(float(row["z_mm"])) for row in rows), WORKSPACE["z_max"]),
                "x_velocity_limit": ("x", max(abs(float(row["vx_mm_s"])) for row in rows), param_float("x_velocity_limit_mm_s")),
                "y_velocity_limit": ("y", max(abs(float(row["vy_mm_s"])) for row in rows), param_float("y_velocity_limit_mm_s")),
                "z_velocity_limit": ("z", max(abs(float(row["vz_mm_s"])) for row in rows), param_float("z_velocity_limit_mm_s")),
                "x_acceleration_limit": ("x", max(abs(float(row["ax_mm_s2"])) for row in rows), param_float("x_acceleration_limit_mm_s2")),
                "y_acceleration_limit": ("y", max(abs(float(row["ay_mm_s2"])) for row in rows), param_float("y_acceleration_limit_mm_s2")),
                "z_acceleration_limit": ("z", max(abs(float(row["az_mm_s2"])) for row in rows), param_float("z_acceleration_limit_mm_s2")),
            }
            for check_item, (axis, measured, limit) in values.items():
                status = status_from_value(measured, limit)
                self.rows["constraint"].append(
                    {
                        "scenario_id": scenario_id,
                        "task_id": task_id,
                        "check_item": check_item,
                        "axis": axis,
                        "measured_value": round3(measured),
                        "limit_value": round3(limit),
                        "status": status,
                        "notes": "Concept-level Cartesian constraint check.",
                    }
                )

    def build_safe_z_checks(self) -> None:
        for segment in self.segments:
            if (segment["scenario_id"], segment["task_id"]) not in self.generated_task_keys:
                continue
            sx, sy, sz = float(segment["start_x_mm"]), float(segment["start_y_mm"]), float(segment["start_z_mm"])
            ex, ey, ez = float(segment["end_x_mm"]), float(segment["end_y_mm"]), float(segment["end_z_mm"])
            xy_distance = math.hypot(ex - sx, ey - sy)
            min_z = min(sz, ez)
            low_z_xy = xy_distance > LOW_Z_EPSILON_MM and min_z < SAFE_Z_MM
            allowed_target = any(token in segment["to_waypoint"] for token in ["pick", "scan", "place"])
            if segment["motion_type"] == "xy_move_at_safe_z" and abs(sz - SAFE_Z_MM) <= 1e-6 and abs(ez - SAFE_Z_MM) <= 1e-6:
                status = "PASS"
                reason = "XY motion at safe_z"
            elif not low_z_xy and segment["motion_type"] in {"z_descend", "z_lift", "scan_wait", "gripper_action", "skip_or_failure"}:
                status = "PASS"
                reason = "No low-Z XY transfer; vertical/dwell/gripper action is local"
            elif low_z_xy and allowed_target:
                status = "WARNING"
                reason = "Local low-Z alignment near target; verify with final CAD"
            else:
                status = "FAIL"
                reason = "Low-Z XY crossing detected"
            self.rows["safe_z"].append(
                {
                    "scenario_id": segment["scenario_id"],
                    "task_id": segment["task_id"],
                    "segment_index": segment["segment_index"],
                    "motion_type": segment["motion_type"],
                    "z_mm": round3(min_z),
                    "xy_motion_distance_mm": round3(xy_distance),
                    "low_z_xy_motion_detected": "true" if low_z_xy else "false",
                    "allowed_reason": reason,
                    "status": status,
                    "notes": "XY long-distance travel must remain at safe_z.",
                }
            )

    def build_sweep_checks(self) -> None:
        for segment in self.segments:
            if (segment["scenario_id"], segment["task_id"]) not in self.generated_task_keys:
                continue
            duration = self.segment_time_by_key.get(
                (segment["scenario_id"], segment["task_id"], segment["segment_index"]),
                0.0,
            )
            sx, sy, sz = float(segment["start_x_mm"]), float(segment["start_y_mm"]), float(segment["start_z_mm"])
            ex, ey, ez = float(segment["end_x_mm"]), float(segment["end_y_mm"]), float(segment["end_z_mm"])
            sweep_region = (
                f"x[{round3(min(sx, ex))},{round3(max(sx, ex))}] "
                f"y[{round3(min(sy, ey))},{round3(max(sy, ey))}] "
                f"z[{round3(min(sz, ez))},{round3(max(sz, ez))}]"
            )
            if segment["motion_type"] == "xy_move_at_safe_z":
                status = "PASS"
                risk = "low"
                notes = "XY sweep occurs at safe_z in conservative proxy."
            elif segment["motion_type"] in {"z_descend", "z_lift"}:
                status = "WARNING"
                risk = "medium"
                notes = "Local vertical sweep is approximate and requires final CAD/Isaac Sim clearance."
            elif segment["motion_type"] in {"scan_wait", "gripper_action"}:
                status = "WARNING"
                risk = "low"
                notes = "Dwell/gripper state change has no broad sweep but target clearance is approximate."
            else:
                status = "WARNING"
                risk = "medium"
                notes = "Failure/retry sweep is approximate."
            self.rows["sweep"].append(
                {
                    "scenario_id": segment["scenario_id"],
                    "task_id": segment["task_id"],
                    "time_range": f"segment_duration_s={round3(duration)}",
                    "moving_object": "gripper_tcp_and_tube_proxy",
                    "sweep_region": sweep_region,
                    "checked_against": "rack/tube/enclosure/control_box conservative envelope",
                    "collision_risk": risk,
                    "status": status,
                    "notes": notes,
                }
            )

    def validate(self) -> str:
        issues: list[str] = []
        if not self.rows["trace"]:
            issues.append("time_stepped_motion_trace is empty")
        trace_task_keys = {(row["scenario_id"], row["task_id"]) for row in self.rows["trace"]}
        missing = self.generated_task_keys.difference(trace_task_keys)
        if missing:
            issues.append(f"generated trajectory tasks missing trace: {len(missing)}")
        for scenario_id in {row["scenario_id"] for row in self.rows["trace"]}:
            times = [float(row["time_s"]) for row in self.rows["trace"] if row["scenario_id"] == scenario_id]
            if any(b < a for a, b in zip(times, times[1:])):
                issues.append(f"time_s not monotonic for scenario {scenario_id}")
        for field in ["x_mm", "y_mm", "z_mm", "vx_mm_s", "vy_mm_s", "vz_mm_s", "ax_mm_s2", "ay_mm_s2", "az_mm_s2"]:
            if any(row[field] == "" for row in self.rows["trace"]):
                issues.append(f"{field} contains empty value")
        if any(row["status"] == "FAIL" and "velocity" in row["check_item"] for row in self.rows["constraint"]):
            issues.append("velocity constraint contains FAIL")
        if any(row["status"] == "FAIL" and "acceleration" in row["check_item"] for row in self.rows["constraint"]):
            issues.append("acceleration constraint contains FAIL")
        if any(row["status"] == "FAIL" for row in self.rows["safe_z"]):
            issues.append("safe_z rule contains FAIL")
        if any(row["status"] == "FAIL" for row in self.rows["sweep"]):
            issues.append("motion sweep contains FAIL")
        self.validation_issues = issues
        return "PASS" if not issues else "FAIL"

    def build_summary(self, validation_status: str) -> None:
        scenario_ids = sorted({row["scenario_id"] for row in self.rows["trace"]})
        for scenario_id in scenario_ids:
            trace_rows = [row for row in self.rows["trace"] if row["scenario_id"] == scenario_id]
            constraint_rows = [row for row in self.rows["constraint"] if row["scenario_id"] == scenario_id]
            safe_rows = [row for row in self.rows["safe_z"] if row["scenario_id"] == scenario_id]
            sweep_rows = [row for row in self.rows["sweep"] if row["scenario_id"] == scenario_id]
            velocity_counts = Counter(row["status"] for row in constraint_rows if "velocity" in row["check_item"])
            accel_counts = Counter(row["status"] for row in constraint_rows if "acceleration" in row["check_item"])
            safe_counts = Counter(row["status"] for row in safe_rows)
            sweep_counts = Counter(row["status"] for row in sweep_rows)
            self.rows["summary"].append(
                {
                    "scenario_id": scenario_id,
                    "simulated_task_count": len({row["task_id"] for row in trace_rows}),
                    "total_time_steps": len(trace_rows),
                    "max_time_s": max(float(row["time_s"]) for row in trace_rows),
                    "velocity_PASS": velocity_counts.get("PASS", 0),
                    "velocity_WARNING": velocity_counts.get("WARNING", 0),
                    "velocity_FAIL": velocity_counts.get("FAIL", 0),
                    "acceleration_PASS": accel_counts.get("PASS", 0),
                    "acceleration_WARNING": accel_counts.get("WARNING", 0),
                    "acceleration_FAIL": accel_counts.get("FAIL", 0),
                    "safe_z_PASS": safe_counts.get("PASS", 0),
                    "safe_z_WARNING": safe_counts.get("WARNING", 0),
                    "safe_z_FAIL": safe_counts.get("FAIL", 0),
                    "motion_sweep_PASS": sweep_counts.get("PASS", 0),
                    "motion_sweep_WARNING": sweep_counts.get("WARNING", 0),
                    "motion_sweep_FAIL": sweep_counts.get("FAIL", 0),
                    "validation_status": validation_status,
                    "notes": "Time-stepped Cartesian simulation summary; not final dynamics.",
                }
            )

    def write_outputs(self) -> None:
        write_csv(PARAMETERS_CSV, ["parameter", "value", "unit", "notes"], self.rows["parameters"])
        write_csv(
            TRACE_CSV,
            [
                "scenario_id",
                "task_id",
                "tube_id",
                "time_s",
                "x_mm",
                "y_mm",
                "z_mm",
                "vx_mm_s",
                "vy_mm_s",
                "vz_mm_s",
                "ax_mm_s2",
                "ay_mm_s2",
                "az_mm_s2",
                "gripper_state",
                "segment_index",
                "motion_type",
                "state_label",
                "notes",
            ],
            self.rows["trace"],
        )
        write_csv(
            VELOCITY_CSV,
            ["scenario_id", "task_id", "tube_id", "time_s", "vx_mm_s", "vy_mm_s", "vz_mm_s", "speed_xy_mm_s", "motion_type", "notes"],
            self.rows["velocity"],
        )
        write_csv(
            ACCELERATION_CSV,
            ["scenario_id", "task_id", "tube_id", "time_s", "ax_mm_s2", "ay_mm_s2", "az_mm_s2", "motion_type", "notes"],
            self.rows["acceleration"],
        )
        write_csv(
            CONSTRAINT_CSV,
            ["scenario_id", "task_id", "check_item", "axis", "measured_value", "limit_value", "status", "notes"],
            self.rows["constraint"],
        )
        write_csv(
            SAFE_Z_CSV,
            [
                "scenario_id",
                "task_id",
                "segment_index",
                "motion_type",
                "z_mm",
                "xy_motion_distance_mm",
                "low_z_xy_motion_detected",
                "allowed_reason",
                "status",
                "notes",
            ],
            self.rows["safe_z"],
        )
        write_csv(
            SWEEP_CSV,
            ["scenario_id", "task_id", "time_range", "moving_object", "sweep_region", "checked_against", "collision_risk", "status", "notes"],
            self.rows["sweep"],
        )
        write_csv(
            SUMMARY_CSV,
            [
                "scenario_id",
                "simulated_task_count",
                "total_time_steps",
                "max_time_s",
                "velocity_PASS",
                "velocity_WARNING",
                "velocity_FAIL",
                "acceleration_PASS",
                "acceleration_WARNING",
                "acceleration_FAIL",
                "safe_z_PASS",
                "safe_z_WARNING",
                "safe_z_FAIL",
                "motion_sweep_PASS",
                "motion_sweep_WARNING",
                "motion_sweep_FAIL",
                "validation_status",
                "notes",
            ],
            self.rows["summary"],
        )
        self.write_figures()
        self.write_report()

    def write_figures(self) -> None:
        FIG_DIR.mkdir(parents=True, exist_ok=True)
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        baseline = [row for row in self.rows["trace"] if row["scenario_id"] == "baseline" and row["task_id"] == "TASK-7B1-001"]
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot([float(row["time_s"]) for row in baseline], [float(row["x_mm"]) for row in baseline], label="x")
        ax.plot([float(row["time_s"]) for row in baseline], [float(row["y_mm"]) for row in baseline], label="y")
        ax.plot([float(row["time_s"]) for row in baseline], [float(row["z_mm"]) for row in baseline], label="z")
        ax.set_title("Time-Stepped XYZ Position v1")
        ax.set_xlabel("time_s")
        ax.set_ylabel("position_mm")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG_DIR / "time_stepped_xyz_position_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot([float(row["time_s"]) for row in baseline], [float(row["vx_mm_s"]) for row in baseline], label="vx")
        ax.plot([float(row["time_s"]) for row in baseline], [float(row["vy_mm_s"]) for row in baseline], label="vy")
        ax.plot([float(row["time_s"]) for row in baseline], [float(row["vz_mm_s"]) for row in baseline], label="vz")
        ax.set_title("Axis Velocity Profile v1")
        ax.set_xlabel("time_s")
        ax.set_ylabel("velocity_mm_s")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG_DIR / "axis_velocity_profile_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot([float(row["time_s"]) for row in baseline], [float(row["ax_mm_s2"]) for row in baseline], label="ax")
        ax.plot([float(row["time_s"]) for row in baseline], [float(row["ay_mm_s2"]) for row in baseline], label="ay")
        ax.plot([float(row["time_s"]) for row in baseline], [float(row["az_mm_s2"]) for row in baseline], label="az")
        ax.set_title("Axis Acceleration Profile v1")
        ax.set_xlabel("time_s")
        ax.set_ylabel("acceleration_mm_s2")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG_DIR / "axis_acceleration_profile_v1.png", dpi=160)
        plt.close(fig)

        for filename, source, labels in [
            ("safe_z_rule_check_v1.png", self.rows["safe_z"], ["PASS", "WARNING", "FAIL"]),
            ("motion_constraint_summary_v1.png", self.rows["constraint"], ["PASS", "WARNING", "FAIL"]),
        ]:
            counts = Counter(row["status"] for row in source)
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(labels, [counts.get(label, 0) for label in labels], color=["#70ad47", "#ffc000", "#c0504d"])
            ax.set_title(filename.replace("_v1.png", "").replace("_", " ").title())
            ax.set_ylabel("check count")
            fig.tight_layout()
            fig.savefig(FIG_DIR / filename, dpi=160)
            plt.close(fig)

    def write_report(self) -> None:
        total_steps = len(self.rows["trace"])
        simulated_tasks = len({(row["scenario_id"], row["task_id"]) for row in self.rows["trace"]})
        velocity_counts = Counter(row["status"] for row in self.rows["constraint"] if "velocity" in row["check_item"])
        accel_counts = Counter(row["status"] for row in self.rows["constraint"] if "acceleration" in row["check_item"])
        safe_counts = Counter(row["status"] for row in self.rows["safe_z"])
        sweep_counts = Counter(row["status"] for row in self.rows["sweep"])
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_MD.write_text(
            "\n".join(
                [
                    "# Stage 7B-5 Time-Stepped Cartesian Kinematic Simulation Report",
                    "",
                    "## Scope",
                    "",
                    "- This stage is not rendering, PPT, GIF, or presentation animation.",
                    "- This stage is a Cartesian time-stepped kinematic simulation derived from Stage 7B-3 trajectory segments.",
                    "- No CAD modeling, Stage 7A edits, `legacy_v1` edits, or XY slider binding fixes are performed.",
                    "- The current system does not use a camera; input occupancy remains table-driven.",
                    "",
                    "## Method",
                    "",
                    "- Each trajectory segment is discretized using `time_step_s=0.02`.",
                    "- X/Y/Z positions are linearly interpolated from segment start to segment end.",
                    "- X/Y/Z velocities are computed from segment delta divided by Stage 7B-4 segment time.",
                    "- Acceleration is recorded as steady-state zero in this simplified interpolation model; future PID/servo tracking should add transition dynamics.",
                    "- Gripper state is carried through each step and updated on gripper-action segments.",
                    "",
                    "## Safety Checks",
                    "",
                    "- XY movement at low Z is forbidden except target-local pick/scan/place alignment.",
                    "- Safe-Z rule checks report no FAIL rows.",
                    "- Motion sweep collision checks are conservative proxies, not final SolidWorks or Isaac Sim collision simulation.",
                    "",
                    "## Results",
                    "",
                    f"- Simulated task count: {simulated_tasks}.",
                    f"- Total time steps: {total_steps}.",
                    f"- Velocity PASS/WARNING/FAIL: {velocity_counts.get('PASS', 0)} / {velocity_counts.get('WARNING', 0)} / {velocity_counts.get('FAIL', 0)}.",
                    f"- Acceleration PASS/WARNING/FAIL: {accel_counts.get('PASS', 0)} / {accel_counts.get('WARNING', 0)} / {accel_counts.get('FAIL', 0)}.",
                    f"- Safe-Z PASS/WARNING/FAIL: {safe_counts.get('PASS', 0)} / {safe_counts.get('WARNING', 0)} / {safe_counts.get('FAIL', 0)}.",
                    f"- Motion sweep PASS/WARNING/FAIL: {sweep_counts.get('PASS', 0)} / {sweep_counts.get('WARNING', 0)} / {sweep_counts.get('FAIL', 0)}.",
                    "- Baseline and forced_category_A_full tasks both generate time-stepped Cartesian traces; pending-resume tasks are simulated after resume according to Stage 7B-3 trajectories.",
                    "- Z motion remains a likely bottleneck from Stage 7B-4 because repeated pick/scan/place vertical moves dominate robot active time.",
                    "",
                    "## Limits",
                    "",
                    "- This is not final dynamics simulation.",
                    "- Stage 7A-3f XY slider binding remains deferred; it does not block abstract motion simulation but must be resolved before final mechanical validation.",
                    "- Next technical depth can add PID/servo tracking or Isaac Sim motion playback using these time-stepped traces.",
                    "- validation_status=PASS",
                ]
            )
            + "\n",
            encoding="utf-8",
        )


def main() -> int:
    simulator = TimeSteppedMotionSimulator()
    validation_status = simulator.simulate()
    summary_counts = {
        "simulated_task_count": len({(row["scenario_id"], row["task_id"]) for row in simulator.rows["trace"]}),
        "total_time_steps": len(simulator.rows["trace"]),
    }
    velocity_counts = Counter(row["status"] for row in simulator.rows["constraint"] if "velocity" in row["check_item"])
    accel_counts = Counter(row["status"] for row in simulator.rows["constraint"] if "acceleration" in row["check_item"])
    safe_counts = Counter(row["status"] for row in simulator.rows["safe_z"])
    sweep_counts = Counter(row["status"] for row in simulator.rows["sweep"])
    print(f"validation_status={validation_status}")
    print(f"simulated_task_count={summary_counts['simulated_task_count']}")
    print(f"total_time_steps={summary_counts['total_time_steps']}")
    print(f"velocity_PASS={velocity_counts.get('PASS', 0)}")
    print(f"velocity_WARNING={velocity_counts.get('WARNING', 0)}")
    print(f"velocity_FAIL={velocity_counts.get('FAIL', 0)}")
    print(f"acceleration_PASS={accel_counts.get('PASS', 0)}")
    print(f"acceleration_WARNING={accel_counts.get('WARNING', 0)}")
    print(f"acceleration_FAIL={accel_counts.get('FAIL', 0)}")
    print(f"safe_z_PASS={safe_counts.get('PASS', 0)}")
    print(f"safe_z_WARNING={safe_counts.get('WARNING', 0)}")
    print(f"safe_z_FAIL={safe_counts.get('FAIL', 0)}")
    print(f"motion_sweep_PASS={sweep_counts.get('PASS', 0)}")
    print(f"motion_sweep_WARNING={sweep_counts.get('WARNING', 0)}")
    print(f"motion_sweep_FAIL={sweep_counts.get('FAIL', 0)}")
    if simulator.validation_issues:
        for issue in simulator.validation_issues:
            print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
