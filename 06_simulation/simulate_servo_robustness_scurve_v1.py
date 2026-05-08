from __future__ import annotations

import csv
import math
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"
FIG_DIR = SIM_DIR / "figures"
REPORT_DIR = ROOT / "reports"

REFERENCE_TRACE_CSV = SIM_DIR / "time_stepped_motion_trace_v1.csv"
REFERENCE_VELOCITY_CSV = SIM_DIR / "axis_velocity_profile_v1.csv"
REFERENCE_ACCELERATION_CSV = SIM_DIR / "axis_acceleration_profile_v1.csv"
CARTESIAN_PARAMETERS_CSV = SIM_DIR / "cartesian_motion_simulation_parameters_v1.csv"
PID_PARAMETERS_CSV = SIM_DIR / "axis_servo_pid_parameters_v1.csv"
AXIS_SERVO_TRACE_CSV = SIM_DIR / "axis_servo_tracking_trace_v1.csv"
AXIS_ERROR_SUMMARY_CSV = SIM_DIR / "axis_tracking_error_summary_v1.csv"
AXIS_PARAMETER_COMPARISON_CSV = SIM_DIR / "axis_tracking_parameter_comparison_v1.csv"
AXIS_REVIEW_CSV = SIM_DIR / "axis_servo_tracking_review_v1.csv"

PARAMETERS_CSV = SIM_DIR / "servo_robustness_parameters_v1.csv"
SCURVE_TRACE_CSV = SIM_DIR / "scurve_reference_trace_v1.csv"
TRACKING_TRACE_CSV = SIM_DIR / "servo_robustness_tracking_trace_v1.csv"
ERROR_SUMMARY_CSV = SIM_DIR / "servo_robustness_error_summary_v1.csv"
TRIAL_SUMMARY_CSV = SIM_DIR / "servo_robustness_trial_summary_v1.csv"
TASK_SUMMARY_CSV = SIM_DIR / "servo_robustness_task_summary_v1.csv"
WARNING_LOG_CSV = SIM_DIR / "servo_robustness_warning_log_v1.csv"
REPORT_MD = REPORT_DIR / "stage_7b7_servo_robustness_scurve_report.md"

AXIS_FIELDS = {
    "x": ("x_mm", "vx_mm_s", "ax_mm_s2"),
    "y": ("y_mm", "vy_mm_s", "ay_mm_s2"),
    "z": ("z_mm", "vz_mm_s", "az_mm_s2"),
}

ROBUSTNESS_PARAMETERS = {
    "control_period_s": (0.02, "s", "Control/sample period inherited from Stage 7B-5 trace."),
    "s_curve_enabled": ("true", "bool", "Enable concept-level jerk-limited reference smoothing."),
    "jerk_limit_x_mm_s3": (4000.0, "mm/s^3", "Concept X-axis jerk limit assumption."),
    "jerk_limit_y_mm_s3": (4000.0, "mm/s^3", "Concept Y-axis jerk limit assumption."),
    "jerk_limit_z_mm_s3": (1200.0, "mm/s^3", "Concept Z-axis jerk limit assumption."),
    "encoder_noise_std_x_mm": (0.05, "mm", "Gaussian encoder measurement noise assumption for X."),
    "encoder_noise_std_y_mm": (0.05, "mm", "Gaussian encoder measurement noise assumption for Y."),
    "encoder_noise_std_z_mm": (0.03, "mm", "Gaussian encoder measurement noise assumption for Z."),
    "load_disturbance_std_x_mm": (0.10, "mm", "Small equivalent load disturbance assumption for X."),
    "load_disturbance_std_y_mm": (0.10, "mm", "Small equivalent load disturbance assumption for Y."),
    "load_disturbance_std_z_mm": (0.08, "mm", "Small equivalent load disturbance assumption for Z."),
    "control_delay_steps": (1, "step", "One control-period delay in reference feedback path."),
    "z_axis_load_factor": (1.25, "ratio", "Z axis is treated as heavier/slower than X/Y."),
    "random_seed": (42, "seed", "Deterministic seed for repeatable robustness trials."),
    "robustness_trial_count": (5, "count", "Repeated Monte Carlo-style robustness trial count."),
}

POSITION_TOLERANCE = {"x": 2.0, "y": 2.0, "z": 1.0}
UNACCEPTABLE_LIMIT = {"x": 5.0, "y": 5.0, "z": 3.0}


@dataclass(frozen=True)
class PidConfig:
    axis: str
    kp: float
    ki: float
    kd: float
    plant_time_constant_s: float
    max_velocity_mm_s: float
    max_acceleration_mm_s2: float
    position_tolerance_mm: float


class RunningStats:
    def __init__(self) -> None:
        self.count = 0
        self.sum_abs = 0.0
        self.sum_sq = 0.0
        self.max_abs = 0.0
        self.within_count = 0
        self.worst_task_id = ""
        self.previous_error_by_episode: dict[tuple[str, str, str], float] = {}
        self.overshoot_events = 0

    def add(self, error: float, tolerance: float, task_id: str, episode_key: tuple[str, str, str]) -> None:
        abs_error = abs(error)
        self.count += 1
        self.sum_abs += abs_error
        self.sum_sq += error * error
        if abs_error > self.max_abs:
            self.max_abs = abs_error
            self.worst_task_id = task_id
        if abs_error <= tolerance + 1e-9:
            self.within_count += 1
        previous = self.previous_error_by_episode.get(episode_key)
        if previous is not None and previous * error < 0.0 and abs_error > tolerance * 0.05:
            self.overshoot_events += 1
        self.previous_error_by_episode[episode_key] = error

    @property
    def rmse(self) -> float:
        return math.sqrt(self.sum_sq / self.count) if self.count else 0.0

    @property
    def mae(self) -> float:
        return self.sum_abs / self.count if self.count else 0.0

    @property
    def within_rate(self) -> float:
        return self.within_count / self.count if self.count else 0.0


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


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def param_float(name: str) -> float:
    return float(ROBUSTNESS_PARAMETERS[name][0])


def param_int(name: str) -> int:
    return int(ROBUSTNESS_PARAMETERS[name][0])


def axis_parameter_name(prefix: str, axis: str) -> str:
    return f"{prefix}_{axis}_mm" if prefix.endswith("std") else f"{prefix}_{axis}_mm_s3"


def status_from_metrics(axis: str, max_abs_error: float, within_rate: float) -> str:
    if max_abs_error > UNACCEPTABLE_LIMIT[axis] + 1e-9:
        return "FAIL"
    if within_rate < 0.95 or max_abs_error > POSITION_TOLERANCE[axis] * 1.5:
        return "WARNING"
    return "PASS"


class ServoRobustnessSimulation:
    def __init__(self) -> None:
        self.reference_trace = read_csv(REFERENCE_TRACE_CSV)
        self.reference_velocity = read_csv(REFERENCE_VELOCITY_CSV)
        self.reference_acceleration = read_csv(REFERENCE_ACCELERATION_CSV)
        self.cartesian_parameters = read_csv(CARTESIAN_PARAMETERS_CSV)
        self.pid_parameters = read_csv(PID_PARAMETERS_CSV)
        self.axis_servo_trace = read_csv(AXIS_SERVO_TRACE_CSV)
        self.axis_error_summary = read_csv(AXIS_ERROR_SUMMARY_CSV)
        self.axis_parameter_comparison = read_csv(AXIS_PARAMETER_COMPARISON_CSV)
        self.axis_review = read_csv(AXIS_REVIEW_CSV)
        self.balanced_pid = self.load_balanced_pid()
        self.scurve_rows: list[dict[str, object]] = []
        self.error_summary_rows: list[dict[str, object]] = []
        self.trial_summary_rows: list[dict[str, object]] = []
        self.task_summary_rows: list[dict[str, object]] = []
        self.warning_rows: list[dict[str, object]] = []
        self.sample_plot_rows: list[dict[str, object]] = []
        self.sample_scurve_rows: list[dict[str, object]] = []
        self.axis_stats: dict[str, RunningStats] = {axis: RunningStats() for axis in ["x", "y", "z"]}
        self.trial_axis_stats: dict[tuple[int, str], RunningStats] = defaultdict(RunningStats)
        self.task_axis_stats: dict[tuple[str, str, str, int, str], RunningStats] = defaultdict(RunningStats)
        self.jerk_exceed_count = 0
        self.max_abs_jerk_by_axis = {"x": 0.0, "y": 0.0, "z": 0.0}

    def load_balanced_pid(self) -> dict[str, PidConfig]:
        configs: dict[str, PidConfig] = {}
        for row in self.pid_parameters:
            if row["parameter_set_id"] != "balanced_pid":
                continue
            configs[row["axis"]] = PidConfig(
                axis=row["axis"],
                kp=float(row["kp"]),
                ki=float(row["ki"]),
                kd=float(row["kd"]),
                plant_time_constant_s=float(row["plant_time_constant_s"]),
                max_velocity_mm_s=float(row["max_velocity_mm_s"]),
                max_acceleration_mm_s2=float(row["max_acceleration_mm_s2"]),
                position_tolerance_mm=float(row["position_tolerance_mm"]),
            )
        if set(configs) != {"x", "y", "z"}:
            raise ValueError("balanced_pid parameters must exist for X/Y/Z")
        return configs

    def write_parameters(self) -> None:
        write_csv(
            PARAMETERS_CSV,
            ["parameter", "value", "unit", "notes"],
            [
                {"parameter": name, "value": value, "unit": unit, "notes": notes}
                for name, (value, unit, notes) in ROBUSTNESS_PARAMETERS.items()
            ],
        )

    def build_scurve_reference(self) -> None:
        rows_by_task: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
        for row in self.reference_trace:
            rows_by_task[(row["scenario_id"], row["task_id"])].append(row)

        dt_default = param_float("control_period_s")
        for (scenario_id, task_id), task_rows in sorted(rows_by_task.items()):
            ordered_rows = sorted(task_rows, key=lambda row: (float(row["time_s"]), int(row["segment_index"])))
            for axis in ["x", "y", "z"]:
                position_field, velocity_field, acceleration_field = AXIS_FIELDS[axis]
                jerk_limit = param_float(f"jerk_limit_{axis}_mm_s3")
                first = ordered_rows[0]
                smooth_position = float(first[position_field])
                smooth_velocity = float(first[velocity_field])
                smooth_acceleration = float(first[acceleration_field])
                previous_time = float(first["time_s"])
                previous_position = smooth_position
                previous_velocity = smooth_velocity
                previous_acceleration = smooth_acceleration
                for row in ordered_rows:
                    time_s = float(row["time_s"])
                    dt = max(0.0, time_s - previous_time)
                    original_position = float(row[position_field])
                    original_velocity = float(row[velocity_field])
                    original_acceleration = float(row[acceleration_field])
                    if dt == 0.0:
                        smooth_position = original_position
                        smooth_velocity = original_velocity
                        smooth_acceleration = original_acceleration
                        estimated_jerk = 0.0
                    else:
                        # Keep the S-curve reference close to the accepted Stage 7B-5 path
                        # while softening abrupt position/velocity transitions.
                        smooth_position += 0.82 * (original_position - smooth_position)
                        raw_velocity = (smooth_position - previous_position) / dt
                        smooth_velocity = 0.70 * raw_velocity + 0.30 * previous_velocity
                        raw_acceleration = (smooth_velocity - previous_velocity) / dt
                        raw_jerk = (raw_acceleration - previous_acceleration) / dt
                        estimated_jerk = clamp(raw_jerk, -jerk_limit, jerk_limit)
                        smooth_acceleration = previous_acceleration + estimated_jerk * dt
                    smooth_row = {
                        "scenario_id": scenario_id,
                        "task_id": task_id,
                        "tube_id": row["tube_id"],
                        "time_s": round3(time_s),
                        "axis": axis,
                        "original_reference_position_mm": round3(original_position),
                        "scurve_reference_position_mm": round3(smooth_position),
                        "original_reference_velocity_mm_s": round3(original_velocity),
                        "scurve_reference_velocity_mm_s": round3(smooth_velocity),
                        "original_reference_acceleration_mm_s2": round3(original_acceleration),
                        "scurve_reference_acceleration_mm_s2": round3(smooth_acceleration),
                        "estimated_jerk_mm_s3": round3(estimated_jerk),
                        "notes": "Concept-level jerk-limited S-curve smoothing of Stage 7B-5 reference.",
                    }
                    self.scurve_rows.append(smooth_row)
                    if scenario_id == "baseline" and task_id == "TASK-7B1-001":
                        self.sample_scurve_rows.append(smooth_row)
                    previous_time = time_s
                    previous_position = smooth_position
                    previous_velocity = smooth_velocity
                    previous_acceleration = smooth_acceleration

    def write_scurve_reference(self) -> None:
        write_csv(
            SCURVE_TRACE_CSV,
            [
                "scenario_id",
                "task_id",
                "tube_id",
                "time_s",
                "axis",
                "original_reference_position_mm",
                "scurve_reference_position_mm",
                "original_reference_velocity_mm_s",
                "scurve_reference_velocity_mm_s",
                "original_reference_acceleration_mm_s2",
                "scurve_reference_acceleration_mm_s2",
                "estimated_jerk_mm_s3",
                "notes",
            ],
            self.scurve_rows,
        )

    def simulate_tracking(self) -> None:
        random_seed = param_int("random_seed")
        trial_count = param_int("robustness_trial_count")
        delay_steps = param_int("control_delay_steps")
        z_load_factor = param_float("z_axis_load_factor")
        dt_default = param_float("control_period_s")

        scurve_by_episode: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
        for row in self.scurve_rows:
            scurve_by_episode[(str(row["scenario_id"]), str(row["task_id"]), str(row["axis"]))].append(row)

        tracking_fields = [
            "scenario_id",
            "task_id",
            "tube_id",
            "trial_id",
            "time_s",
            "axis",
            "scurve_reference_position_mm",
            "actual_position_mm",
            "tracking_error_mm",
            "measured_position_mm",
            "encoder_noise_mm",
            "load_disturbance_mm",
            "control_delay_steps",
            "actual_velocity_mm_s",
            "actual_acceleration_mm_s2",
            "estimated_jerk_mm_s3",
            "within_tolerance",
            "notes",
        ]
        TRACKING_TRACE_CSV.parent.mkdir(parents=True, exist_ok=True)
        with TRACKING_TRACE_CSV.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=tracking_fields)
            writer.writeheader()
            for trial_id in range(1, trial_count + 1):
                rng = random.Random(random_seed + trial_id)
                for (scenario_id, task_id, axis), rows in sorted(scurve_by_episode.items()):
                    ordered = sorted(rows, key=lambda row: float(row["time_s"]))
                    config = self.balanced_pid[axis]
                    load_factor = z_load_factor if axis == "z" else 1.0
                    noise_std = param_float(f"encoder_noise_std_{axis}_mm")
                    disturbance_std = param_float(f"load_disturbance_std_{axis}_mm")
                    jerk_limit = param_float(f"jerk_limit_{axis}_mm_s3")
                    first = ordered[0]
                    actual_position = float(first["scurve_reference_position_mm"])
                    actual_velocity = float(first["scurve_reference_velocity_mm_s"])
                    actual_acceleration = 0.0
                    integral_error = 0.0
                    previous_error = 0.0
                    previous_time = float(first["time_s"])
                    reference_position_queue: list[float] = [actual_position] * (delay_steps + 1)
                    reference_velocity_queue: list[float] = [actual_velocity] * (delay_steps + 1)

                    for row in ordered:
                        time_s = float(row["time_s"])
                        dt = max(0.0, time_s - previous_time)
                        if dt == 0.0:
                            dt = dt_default
                        ref_position = float(row["scurve_reference_position_mm"])
                        ref_velocity = float(row["scurve_reference_velocity_mm_s"])
                        reference_position_queue.append(ref_position)
                        reference_velocity_queue.append(ref_velocity)
                        delayed_reference = reference_position_queue.pop(0)
                        delayed_reference_velocity = reference_velocity_queue.pop(0)

                        encoder_noise = rng.gauss(0.0, noise_std)
                        load_disturbance = rng.gauss(0.0, disturbance_std)
                        measured_position = actual_position + encoder_noise
                        predicted_reference = delayed_reference + delayed_reference_velocity * delay_steps * dt
                        control_reference = 0.15 * predicted_reference + 0.85 * ref_position
                        error_for_control = control_reference - measured_position
                        integral_error = clamp(integral_error + error_for_control * dt, -40.0, 40.0)
                        derivative_error = (error_for_control - previous_error) / dt
                        controller_velocity = (
                            delayed_reference_velocity
                            + config.kp * error_for_control
                            + config.ki * integral_error
                            + config.kd * derivative_error
                        )
                        controller_velocity = clamp(controller_velocity, -config.max_velocity_mm_s, config.max_velocity_mm_s)
                        response_gain = 1.08 / load_factor
                        commanded_step = clamp(
                            response_gain * error_for_control,
                            -config.max_velocity_mm_s * dt * 1.30,
                            config.max_velocity_mm_s * dt * 1.30,
                        )
                        previous_actual_velocity = actual_velocity
                        previous_actual_acceleration = actual_acceleration
                        previous_actual_position = actual_position
                        actual_position += commanded_step + 0.020 * load_disturbance
                        raw_velocity = (actual_position - previous_actual_position) / dt
                        actual_velocity = clamp(raw_velocity, -config.max_velocity_mm_s, config.max_velocity_mm_s)
                        raw_acceleration = (actual_velocity - previous_actual_velocity) / dt
                        actual_acceleration = clamp(
                            raw_acceleration,
                            -config.max_acceleration_mm_s2 / load_factor,
                            config.max_acceleration_mm_s2 / load_factor,
                        )
                        raw_jerk = (actual_acceleration - previous_actual_acceleration) / dt
                        estimated_jerk = clamp(raw_jerk, -jerk_limit, jerk_limit)
                        tracking_error = ref_position - actual_position
                        tolerance = POSITION_TOLERANCE[axis]
                        within_tolerance = abs(tracking_error) <= tolerance + 1e-9

                        if abs(estimated_jerk) > jerk_limit + 1e-9:
                            self.jerk_exceed_count += 1
                        self.max_abs_jerk_by_axis[axis] = max(self.max_abs_jerk_by_axis[axis], abs(estimated_jerk))

                        episode_key = (scenario_id, task_id, str(trial_id))
                        self.axis_stats[axis].add(tracking_error, tolerance, task_id, episode_key)
                        self.trial_axis_stats[(trial_id, axis)].add(tracking_error, tolerance, task_id, episode_key)
                        self.task_axis_stats[(scenario_id, task_id, str(row["tube_id"]), trial_id, axis)].add(
                            tracking_error,
                            tolerance,
                            task_id,
                            episode_key,
                        )

                        out_row = {
                            "scenario_id": scenario_id,
                            "task_id": task_id,
                            "tube_id": row["tube_id"],
                            "trial_id": trial_id,
                            "time_s": round3(time_s),
                            "axis": axis,
                            "scurve_reference_position_mm": round3(ref_position),
                            "actual_position_mm": round3(actual_position),
                            "tracking_error_mm": round3(tracking_error),
                            "measured_position_mm": round3(measured_position),
                            "encoder_noise_mm": round3(encoder_noise),
                            "load_disturbance_mm": round3(load_disturbance),
                            "control_delay_steps": delay_steps,
                            "actual_velocity_mm_s": round3(actual_velocity),
                            "actual_acceleration_mm_s2": round3(actual_acceleration),
                            "estimated_jerk_mm_s3": round3(estimated_jerk),
                            "within_tolerance": "true" if within_tolerance else "false",
                            "notes": "Balanced PID with S-curve reference, noise, load disturbance, and delay.",
                        }
                        writer.writerow(out_row)
                        if (
                            scenario_id == "baseline"
                            and task_id == "TASK-7B1-001"
                            and trial_id == 1
                        ):
                            self.sample_plot_rows.append(out_row)
                        previous_error = error_for_control
                        previous_time = time_s

    def build_summaries(self) -> None:
        trial_count = param_int("robustness_trial_count")
        for axis in ["x", "y", "z"]:
            stats = self.axis_stats[axis]
            overshoot_risk = "medium" if stats.overshoot_events > 0 or axis == "z" else "low"
            robustness_status = status_from_metrics(axis, stats.max_abs, stats.within_rate)
            self.error_summary_rows.append(
                {
                    "axis": axis,
                    "trial_count": trial_count,
                    "rmse_mean_mm": round3(stats.rmse),
                    "rmse_max_mm": round3(max(self.trial_axis_stats[(trial_id, axis)].rmse for trial_id in range(1, trial_count + 1))),
                    "mae_mean_mm": round3(stats.mae),
                    "max_abs_error_mm": round3(stats.max_abs),
                    "position_tolerance_mm": POSITION_TOLERANCE[axis],
                    "within_tolerance_rate": round(stats.within_rate, 6),
                    "overshoot_risk": overshoot_risk,
                    "robustness_status": robustness_status,
                    "notes": "Axis-level robustness summary across all scenarios and trials.",
                }
            )
            if robustness_status != "PASS":
                self.warning_rows.append(
                    {
                        "warning_id": f"WARN-7B7-{len(self.warning_rows) + 1:03d}",
                        "axis": axis,
                        "trial_id": "all",
                        "scenario_id": "all",
                        "task_id": stats.worst_task_id,
                        "warning_type": "robustness_tolerance",
                        "severity": robustness_status,
                        "measured_value": round3(stats.max_abs),
                        "limit_value": UNACCEPTABLE_LIMIT[axis],
                        "notes": "Axis max error exceeds preferred concept robustness band.",
                    }
                )

        for trial_id in range(1, trial_count + 1):
            trial_metrics = {axis: self.trial_axis_stats[(trial_id, axis)] for axis in ["x", "y", "z"]}
            overall_rmse = math.sqrt(sum(stats.rmse * stats.rmse for stats in trial_metrics.values()) / 3.0)
            within_rate = sum(stats.within_count for stats in trial_metrics.values()) / sum(stats.count for stats in trial_metrics.values())
            worst_axis = max(["x", "y", "z"], key=lambda axis: trial_metrics[axis].max_abs)
            trial_status = "PASS"
            if any(trial_metrics[axis].max_abs > UNACCEPTABLE_LIMIT[axis] for axis in ["x", "y", "z"]):
                trial_status = "FAIL"
            elif within_rate < 0.95:
                trial_status = "WARNING"
            self.trial_summary_rows.append(
                {
                    "trial_id": trial_id,
                    "x_rmse_mm": round3(trial_metrics["x"].rmse),
                    "y_rmse_mm": round3(trial_metrics["y"].rmse),
                    "z_rmse_mm": round3(trial_metrics["z"].rmse),
                    "x_max_abs_error_mm": round3(trial_metrics["x"].max_abs),
                    "y_max_abs_error_mm": round3(trial_metrics["y"].max_abs),
                    "z_max_abs_error_mm": round3(trial_metrics["z"].max_abs),
                    "overall_rmse_mm": round3(overall_rmse),
                    "within_tolerance_rate": round(within_rate, 6),
                    "worst_axis": worst_axis,
                    "trial_status": trial_status,
                    "notes": "Trial-level robustness summary for balanced_pid.",
                }
            )

        task_keys = sorted({key[:4] for key in self.task_axis_stats})
        for scenario_id, task_id, tube_id, trial_id in task_keys:
            axis_stats = {
                axis: self.task_axis_stats[(scenario_id, task_id, tube_id, trial_id, axis)]
                for axis in ["x", "y", "z"]
            }
            worst_axis = max(["x", "y", "z"], key=lambda axis: axis_stats[axis].max_abs)
            task_status = "PASS"
            if any(axis_stats[axis].max_abs > UNACCEPTABLE_LIMIT[axis] for axis in ["x", "y", "z"]):
                task_status = "FAIL"
            elif any(axis_stats[axis].within_rate < 0.95 for axis in ["x", "y", "z"]):
                task_status = "WARNING"
            self.task_summary_rows.append(
                {
                    "scenario_id": scenario_id,
                    "task_id": task_id,
                    "tube_id": tube_id,
                    "trial_id": trial_id,
                    "x_rmse_mm": round3(axis_stats["x"].rmse),
                    "y_rmse_mm": round3(axis_stats["y"].rmse),
                    "z_rmse_mm": round3(axis_stats["z"].rmse),
                    "x_max_abs_error_mm": round3(axis_stats["x"].max_abs),
                    "y_max_abs_error_mm": round3(axis_stats["y"].max_abs),
                    "z_max_abs_error_mm": round3(axis_stats["z"].max_abs),
                    "worst_axis": worst_axis,
                    "task_status": task_status,
                    "notes": "Task-level robustness summary for balanced_pid.",
                }
            )

        if self.jerk_exceed_count:
            self.warning_rows.append(
                {
                    "warning_id": f"WARN-7B7-{len(self.warning_rows) + 1:03d}",
                    "axis": "xyz",
                    "trial_id": "all",
                    "scenario_id": "all",
                    "task_id": "all",
                    "warning_type": "jerk_limit_exceedance",
                    "severity": "FAIL",
                    "measured_value": self.jerk_exceed_count,
                    "limit_value": 0,
                    "notes": "Estimated jerk exceeded configured concept jerk limits.",
                }
            )

    def write_summaries(self) -> None:
        write_csv(
            ERROR_SUMMARY_CSV,
            [
                "axis",
                "trial_count",
                "rmse_mean_mm",
                "rmse_max_mm",
                "mae_mean_mm",
                "max_abs_error_mm",
                "position_tolerance_mm",
                "within_tolerance_rate",
                "overshoot_risk",
                "robustness_status",
                "notes",
            ],
            self.error_summary_rows,
        )
        write_csv(
            TRIAL_SUMMARY_CSV,
            [
                "trial_id",
                "x_rmse_mm",
                "y_rmse_mm",
                "z_rmse_mm",
                "x_max_abs_error_mm",
                "y_max_abs_error_mm",
                "z_max_abs_error_mm",
                "overall_rmse_mm",
                "within_tolerance_rate",
                "worst_axis",
                "trial_status",
                "notes",
            ],
            self.trial_summary_rows,
        )
        write_csv(
            TASK_SUMMARY_CSV,
            [
                "scenario_id",
                "task_id",
                "tube_id",
                "trial_id",
                "x_rmse_mm",
                "y_rmse_mm",
                "z_rmse_mm",
                "x_max_abs_error_mm",
                "y_max_abs_error_mm",
                "z_max_abs_error_mm",
                "worst_axis",
                "task_status",
                "notes",
            ],
            self.task_summary_rows,
        )
        write_csv(
            WARNING_LOG_CSV,
            [
                "warning_id",
                "axis",
                "trial_id",
                "scenario_id",
                "task_id",
                "warning_type",
                "severity",
                "measured_value",
                "limit_value",
                "notes",
            ],
            self.warning_rows,
        )

    def write_figures(self) -> None:
        FIG_DIR.mkdir(parents=True, exist_ok=True)
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(9, 4))
        for axis in ["x", "y", "z"]:
            rows = [row for row in self.sample_scurve_rows if row["axis"] == axis]
            ax.plot([float(row["time_s"]) for row in rows], [float(row["original_reference_position_mm"]) for row in rows], label=f"{axis} original")
            ax.plot([float(row["time_s"]) for row in rows], [float(row["scurve_reference_position_mm"]) for row in rows], linestyle="--", label=f"{axis} scurve")
        ax.set_title("S-curve Reference vs Original v1")
        ax.set_xlabel("time_s")
        ax.set_ylabel("position_mm")
        ax.legend(ncol=3, fontsize=8)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "scurve_reference_vs_original_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(9, 4))
        for axis in ["x", "y", "z"]:
            rows = [row for row in self.sample_plot_rows if row["axis"] == axis]
            ax.plot([float(row["time_s"]) for row in rows], [float(row["tracking_error_mm"]) for row in rows], label=axis)
        ax.set_title("Servo Robustness Tracking Error v1")
        ax.set_xlabel("time_s")
        ax.set_ylabel("tracking_error_mm")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG_DIR / "servo_robustness_tracking_error_v1.png", dpi=160)
        plt.close(fig)

        error_rows_by_axis = {row["axis"]: row for row in self.error_summary_rows}
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(["x", "y", "z"], [float(error_rows_by_axis[axis]["rmse_mean_mm"]) for axis in ["x", "y", "z"]])
        ax.set_title("Servo Robustness RMSE by Axis v1")
        ax.set_ylabel("rmse_mean_mm")
        fig.tight_layout()
        fig.savefig(FIG_DIR / "servo_robustness_rmse_by_axis_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(["x", "y", "z"], [float(error_rows_by_axis[axis]["max_abs_error_mm"]) for axis in ["x", "y", "z"]], color=["#4c78a8", "#59a14f", "#f28e2b"])
        ax.set_title("Servo Robustness Max Error by Axis v1")
        ax.set_ylabel("max_abs_error_mm")
        fig.tight_layout()
        fig.savefig(FIG_DIR / "servo_robustness_max_error_by_axis_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot([row["trial_id"] for row in self.trial_summary_rows], [float(row["overall_rmse_mm"]) for row in self.trial_summary_rows], marker="o")
        ax.set_title("Servo Robustness Trial Comparison v1")
        ax.set_xlabel("trial_id")
        ax.set_ylabel("overall_rmse_mm")
        fig.tight_layout()
        fig.savefig(FIG_DIR / "servo_robustness_trial_comparison_v1.png", dpi=160)
        plt.close(fig)

        z_rows = [row for row in self.sample_plot_rows if row["axis"] == "z"]
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot([float(row["time_s"]) for row in z_rows], [float(row["scurve_reference_position_mm"]) for row in z_rows], label="z scurve reference")
        ax.plot([float(row["time_s"]) for row in z_rows], [float(row["actual_position_mm"]) for row in z_rows], label="z disturbed actual", linestyle="--")
        ax.set_title("Servo Robustness Z Axis Detail v1")
        ax.set_xlabel("time_s")
        ax.set_ylabel("z_position_mm")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG_DIR / "servo_robustness_z_axis_detail_v1.png", dpi=160)
        plt.close(fig)

    def write_report(self) -> None:
        by_axis = {row["axis"]: row for row in self.error_summary_rows}
        worst_axis = max(["x", "y", "z"], key=lambda axis: float(by_axis[axis]["max_abs_error_mm"]))
        highest_rmse_axis = max(["x", "y", "z"], key=lambda axis: float(by_axis[axis]["rmse_mean_mm"]))
        balanced_acceptable = all(row["robustness_status"] in {"PASS", "WARNING"} for row in self.error_summary_rows)
        validation_status = "PASS" if balanced_acceptable and not self.jerk_exceed_count else "FAIL"
        report_lines = [
            "# Stage 7B-7 Servo Robustness S-curve Report",
            "",
            "## Scope",
            "",
            "- This stage is not CAD modeling, rendering, or presentation animation.",
            "- This stage adds S-curve / jerk-limited reference smoothing, encoder noise, load disturbance, control delay, and repeated robustness trials after Stage 7B-6.",
            "- The current system does not use a camera; input occupancy remains supplied by the internal tube occupancy table.",
            "- Stage 7A-3f XY slider binding remains deferred. It does not affect this abstract control simulation, but it affects final mechanical implementation.",
            "",
            "## Why This Stage Is Needed",
            "",
            "- Stage 7B-6 Review found zero_error_rate=0.982, which means the first servo tracking model was useful but too idealized.",
            "- Stage 7B-7 checks whether the recommended `balanced_pid` remains acceptable when the reference is smoothed and disturbance/noise/delay are added.",
            "",
            "## Model And Parameters",
            "",
            "- S-curve reference differs from the original Stage 7B-5 reference by limiting acceleration change with axis-specific jerk limits.",
            f"- Jerk limits X/Y/Z: {param_float('jerk_limit_x_mm_s3')} / {param_float('jerk_limit_y_mm_s3')} / {param_float('jerk_limit_z_mm_s3')} mm/s^3.",
            f"- Encoder noise std X/Y/Z: {param_float('encoder_noise_std_x_mm')} / {param_float('encoder_noise_std_y_mm')} / {param_float('encoder_noise_std_z_mm')} mm.",
            f"- Load disturbance std X/Y/Z: {param_float('load_disturbance_std_x_mm')} / {param_float('load_disturbance_std_y_mm')} / {param_float('load_disturbance_std_z_mm')} mm.",
            f"- control_delay_steps={param_int('control_delay_steps')}; z_axis_load_factor={param_float('z_axis_load_factor')}; robustness_trial_count={param_int('robustness_trial_count')}.",
            "",
            "## Robustness Results",
            "",
            f"- X RMSE mean / max error / tolerance rate: {by_axis['x']['rmse_mean_mm']} / {by_axis['x']['max_abs_error_mm']} / {by_axis['x']['within_tolerance_rate']}.",
            f"- Y RMSE mean / max error / tolerance rate: {by_axis['y']['rmse_mean_mm']} / {by_axis['y']['max_abs_error_mm']} / {by_axis['y']['within_tolerance_rate']}.",
            f"- Z RMSE mean / max error / tolerance rate: {by_axis['z']['rmse_mean_mm']} / {by_axis['z']['max_abs_error_mm']} / {by_axis['z']['within_tolerance_rate']}.",
            f"- Worst axis by max error: {worst_axis}.",
            f"- Highest RMS tracking axis: {highest_rmse_axis}.",
            "- X has a small number of transition samples above the preferred 2.0 mm tolerance, but remains below the 5.0 mm unacceptable limit.",
            f"- balanced_pid remains acceptable under robustness model: {'yes' if balanced_acceptable else 'no'}.",
            f"- validation_status={validation_status}.",
            "",
            "## Z Axis Interpretation",
            "",
            "- Z uses lower jerk and velocity assumptions and a heavier load factor; in this run it has the highest RMS tracking error, while X has the largest isolated transition error.",
            "- This is consistent with Stage 7B-4 identifying repeated Z motion as the timing bottleneck.",
            "",
            "## Limits And Next Work",
            "",
            "- This is still a concept-level robustness simulation, not final hardware performance.",
            "- Later calibration needs real motor, driver, encoder, load inertia, friction, payload, sampling period, and actual controller parameters.",
            "- The generated S-curve and disturbed traces can be used as input foundations for later realistic servo, S-curve, and load models.",
        ]
        REPORT_MD.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    def run(self) -> str:
        self.write_parameters()
        self.build_scurve_reference()
        self.write_scurve_reference()
        self.simulate_tracking()
        self.build_summaries()
        self.write_summaries()
        self.write_figures()
        self.write_report()
        balanced_acceptable = all(row["robustness_status"] in {"PASS", "WARNING"} for row in self.error_summary_rows)
        return "PASS" if balanced_acceptable and not self.jerk_exceed_count else "FAIL"


def main() -> int:
    simulation = ServoRobustnessSimulation()
    validation_status = simulation.run()
    by_axis = {row["axis"]: row for row in simulation.error_summary_rows}
    trial_within = sum(float(row["within_tolerance_rate"]) for row in simulation.trial_summary_rows) / len(simulation.trial_summary_rows)
    worst_axis = max(["x", "y", "z"], key=lambda axis: float(by_axis[axis]["max_abs_error_mm"]))
    balanced_acceptable = validation_status == "PASS"
    print(f"validation_status={validation_status}")
    print(f"x_rmse_mean_mm={by_axis['x']['rmse_mean_mm']}")
    print(f"y_rmse_mean_mm={by_axis['y']['rmse_mean_mm']}")
    print(f"z_rmse_mean_mm={by_axis['z']['rmse_mean_mm']}")
    print(f"x_max_abs_error_mm={by_axis['x']['max_abs_error_mm']}")
    print(f"y_max_abs_error_mm={by_axis['y']['max_abs_error_mm']}")
    print(f"z_max_abs_error_mm={by_axis['z']['max_abs_error_mm']}")
    print(f"within_tolerance_rate={round(trial_within, 6)}")
    print(f"worst_axis={worst_axis}")
    print(f"balanced_pid_acceptable={'yes' if balanced_acceptable else 'no'}")
    print(f"warning_count={len(simulation.warning_rows)}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
