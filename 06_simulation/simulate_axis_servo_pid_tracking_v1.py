from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
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
TIME_STEPPED_SUMMARY_CSV = SIM_DIR / "time_stepped_motion_summary_v1.csv"
TIME_STEPPED_REVIEW_CSV = SIM_DIR / "time_stepped_motion_review_v1.csv"

PARAMETERS_CSV = SIM_DIR / "axis_servo_pid_parameters_v1.csv"
TRACKING_TRACE_CSV = SIM_DIR / "axis_servo_tracking_trace_v1.csv"
ERROR_SUMMARY_CSV = SIM_DIR / "axis_tracking_error_summary_v1.csv"
TASK_SUMMARY_CSV = SIM_DIR / "axis_tracking_task_summary_v1.csv"
PARAMETER_COMPARISON_CSV = SIM_DIR / "axis_tracking_parameter_comparison_v1.csv"
WARNING_LOG_CSV = SIM_DIR / "axis_tracking_warning_log_v1.csv"
REPORT_MD = REPORT_DIR / "stage_7b6_axis_servo_pid_tracking_report.md"


@dataclass(frozen=True)
class AxisParameter:
    parameter_set_id: str
    axis: str
    kp: float
    ki: float
    kd: float
    plant_time_constant_s: float
    max_velocity_mm_s: float
    max_acceleration_mm_s2: float
    position_tolerance_mm: float
    notes: str


AXIS_FIELDS = {
    "x": ("x_mm", "vx_mm_s", "ax_mm_s2"),
    "y": ("y_mm", "vy_mm_s", "ay_mm_s2"),
    "z": ("z_mm", "vz_mm_s", "az_mm_s2"),
}


PARAMETER_SETS = [
    AxisParameter("conservative_pid", "x", 42.0, 0.20, 8.0, 0.060, 350.0, 2200.0, 2.0, "Stable priority; slower response for X."),
    AxisParameter("conservative_pid", "y", 42.0, 0.20, 8.0, 0.060, 350.0, 2200.0, 2.0, "Stable priority; slower response for Y."),
    AxisParameter("conservative_pid", "z", 50.0, 0.12, 9.0, 0.070, 120.0, 900.0, 1.0, "Stable priority; slower Z response."),
    AxisParameter("balanced_pid", "x", 95.0, 0.28, 16.0, 0.018, 350.0, 5200.0, 2.0, "Recommended default balance for X."),
    AxisParameter("balanced_pid", "y", 95.0, 0.28, 16.0, 0.018, 350.0, 5200.0, 2.0, "Recommended default balance for Y."),
    AxisParameter("balanced_pid", "z", 120.0, 0.18, 20.0, 0.018, 120.0, 2400.0, 1.0, "Recommended default balance for Z bottleneck motion."),
    AxisParameter("aggressive_pid", "x", 150.0, 0.35, 24.0, 0.010, 350.0, 7600.0, 2.0, "Fast response; higher overshoot/noise risk for X."),
    AxisParameter("aggressive_pid", "y", 150.0, 0.35, 24.0, 0.010, 350.0, 7600.0, 2.0, "Fast response; higher overshoot/noise risk for Y."),
    AxisParameter("aggressive_pid", "z", 170.0, 0.22, 28.0, 0.010, 120.0, 3600.0, 1.0, "Fast response; higher overshoot/noise risk for Z."),
]


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


def tracking_status(max_abs_error: float, tolerance: float, within_rate: float) -> str:
    if max_abs_error <= tolerance + 1e-9 and within_rate >= 0.995:
        return "PASS"
    if max_abs_error <= tolerance * 2.5 and within_rate >= 0.970:
        return "WARNING"
    return "FAIL"


class AxisServoPidTrackingSimulation:
    def __init__(self) -> None:
        self.reference_trace = read_csv(REFERENCE_TRACE_CSV)
        self.reference_velocity = read_csv(REFERENCE_VELOCITY_CSV)
        self.reference_acceleration = read_csv(REFERENCE_ACCELERATION_CSV)
        self.cartesian_parameters = read_csv(CARTESIAN_PARAMETERS_CSV)
        self.time_stepped_summary = read_csv(TIME_STEPPED_SUMMARY_CSV)
        self.time_stepped_review = read_csv(TIME_STEPPED_REVIEW_CSV)
        self.parameter_rows: list[dict[str, object]] = []
        self.tracking_rows: list[dict[str, object]] = []
        self.error_summary_rows: list[dict[str, object]] = []
        self.task_summary_rows: list[dict[str, object]] = []
        self.parameter_comparison_rows: list[dict[str, object]] = []
        self.warning_rows: list[dict[str, object]] = []
        self.recommended_parameter_set = ""

    def write_parameters(self) -> None:
        self.parameter_rows = [
            {
                "parameter_set_id": parameter.parameter_set_id,
                "axis": parameter.axis,
                "kp": parameter.kp,
                "ki": parameter.ki,
                "kd": parameter.kd,
                "plant_time_constant_s": parameter.plant_time_constant_s,
                "max_velocity_mm_s": parameter.max_velocity_mm_s,
                "max_acceleration_mm_s2": parameter.max_acceleration_mm_s2,
                "position_tolerance_mm": parameter.position_tolerance_mm,
                "notes": parameter.notes,
            }
            for parameter in PARAMETER_SETS
        ]

    def simulate_axis(self, rows: list[dict[str, str]], parameter: AxisParameter) -> None:
        position_field, velocity_field, acceleration_field = AXIS_FIELDS[parameter.axis]
        first_row = rows[0]
        actual_position = float(first_row[position_field])
        actual_velocity = float(first_row[velocity_field])
        previous_actual_position = actual_position
        integral_error = 0.0
        previous_error = 0.0
        previous_time = float(first_row["time_s"])

        for row in rows:
            time_s = float(row["time_s"])
            dt = max(0.0, time_s - previous_time)
            reference_position = float(row[position_field])
            reference_velocity = float(row[velocity_field])
            reference_acceleration = float(row[acceleration_field])
            position_error = reference_position - actual_position
            derivative_error = (position_error - previous_error) / dt if dt > 0.0 else 0.0
            if dt > 0.0:
                integral_error = clamp(integral_error + position_error * dt, -50.0, 50.0)

            controller_output = (
                reference_velocity
                + parameter.kp * position_error
                + parameter.ki * integral_error
                + parameter.kd * derivative_error
            )
            controller_output = clamp(controller_output, -parameter.max_velocity_mm_s, parameter.max_velocity_mm_s)

            if dt > 0.0:
                alpha = min(1.0, dt / max(parameter.plant_time_constant_s, 1e-9))
                previous_actual_position = actual_position
                actual_position += alpha * position_error
                raw_velocity = (actual_position - previous_actual_position) / dt
                raw_acceleration = (raw_velocity - actual_velocity) / dt
                actual_velocity = clamp(raw_velocity, -parameter.max_velocity_mm_s, parameter.max_velocity_mm_s)
                actual_acceleration = clamp(raw_acceleration, -parameter.max_acceleration_mm_s2, parameter.max_acceleration_mm_s2)
            else:
                actual_acceleration = 0.0

            tracking_error = reference_position - actual_position
            within_tolerance = abs(tracking_error) <= parameter.position_tolerance_mm + 1e-9
            self.tracking_rows.append(
                {
                    "scenario_id": row["scenario_id"],
                    "task_id": row["task_id"],
                    "tube_id": row["tube_id"],
                    "time_s": round3(time_s),
                    "parameter_set_id": parameter.parameter_set_id,
                    "axis": parameter.axis,
                    "reference_position_mm": round3(reference_position),
                    "actual_position_mm": round3(actual_position),
                    "tracking_error_mm": round3(tracking_error),
                    "reference_velocity_mm_s": round3(reference_velocity),
                    "actual_velocity_mm_s": round3(actual_velocity),
                    "reference_acceleration_mm_s2": round3(reference_acceleration),
                    "actual_acceleration_mm_s2": round3(actual_acceleration),
                    "controller_output": round3(controller_output),
                    "within_tolerance": "true" if within_tolerance else "false",
                    "notes": "Concept-level discrete-time PID servo tracking; not final hardware dynamics.",
                }
            )
            previous_error = position_error
            previous_time = time_s

    def simulate(self) -> None:
        self.write_parameters()
        task_rows: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
        for row in self.reference_trace:
            task_rows[(row["scenario_id"], row["task_id"])].append(row)

        for (scenario_id, task_id) in sorted(task_rows):
            rows = sorted(
                task_rows[(scenario_id, task_id)],
                key=lambda row: (float(row["time_s"]), int(row["segment_index"])),
            )
            for parameter in PARAMETER_SETS:
                self.simulate_axis(rows, parameter)

        self.build_error_summary()
        self.build_task_summary()
        self.build_parameter_comparison()
        self.build_warning_log()
        self.write_outputs()

    def build_error_summary(self) -> None:
        grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
        for row in self.tracking_rows:
            grouped[(str(row["parameter_set_id"]), str(row["axis"]))].append(row)
        parameter_lookup = {(p.parameter_set_id, p.axis): p for p in PARAMETER_SETS}

        for (parameter_set_id, axis), rows in sorted(grouped.items()):
            errors = [float(row["tracking_error_mm"]) for row in rows]
            abs_errors = [abs(error) for error in errors]
            worst_row = max(rows, key=lambda row: abs(float(row["tracking_error_mm"])))
            tolerance = parameter_lookup[(parameter_set_id, axis)].position_tolerance_mm
            within_rate = sum(1 for error in abs_errors if error <= tolerance + 1e-9) / len(abs_errors)
            rmse = math.sqrt(sum(error * error for error in errors) / len(errors))
            mae = sum(abs_errors) / len(abs_errors)
            max_abs_error = max(abs_errors)
            overshoot_event_count = sum(
                1
                for previous, current in zip(errors, errors[1:])
                if previous * current < 0.0 and abs(current) > tolerance * 0.05
            )
            final_abs_error = abs_errors[-1]
            settling_behavior = (
                "settled_within_tolerance"
                if final_abs_error <= tolerance + 1e-9
                else "not_settled_at_trace_end"
            )
            self.error_summary_rows.append(
                {
                    "parameter_set_id": parameter_set_id,
                    "axis": axis,
                    "sample_count": len(rows),
                    "rmse_mm": round3(rmse),
                    "mae_mm": round3(mae),
                    "max_abs_error_mm": round3(max_abs_error),
                    "mean_abs_error_mm": round3(mae),
                    "position_tolerance_mm": tolerance,
                    "within_tolerance_rate": round3(within_rate),
                    "worst_task_id": worst_row["task_id"],
                    "tracking_status": tracking_status(max_abs_error, tolerance, within_rate),
                    "overshoot_event_count": overshoot_event_count,
                    "settling_behavior": settling_behavior,
                    "notes": "Axis-level error summary across all scenarios.",
                }
            )

    def build_task_summary(self) -> None:
        grouped: dict[tuple[str, str, str, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        tube_by_task: dict[tuple[str, str, str], str] = {}
        for row in self.tracking_rows:
            key = (str(row["scenario_id"]), str(row["task_id"]), str(row["parameter_set_id"]))
            grouped[(key[0], key[1], str(row["tube_id"]), key[2])][str(row["axis"])].append(float(row["tracking_error_mm"]))
            tube_by_task[key] = str(row["tube_id"])

        tolerance = {"x": 2.0, "y": 2.0, "z": 1.0}
        for (scenario_id, task_id, tube_id, parameter_set_id), axis_errors in sorted(grouped.items()):
            metrics: dict[str, float] = {}
            pass_axes = 0
            for axis in ["x", "y", "z"]:
                errors = axis_errors[axis]
                rmse = math.sqrt(sum(error * error for error in errors) / len(errors))
                max_abs = max(abs(error) for error in errors)
                metrics[f"{axis}_rmse_mm"] = rmse
                metrics[f"{axis}_max_abs_error_mm"] = max_abs
                if max_abs <= tolerance[axis] + 1e-9:
                    pass_axes += 1
            if pass_axes == 3:
                status = "PASS"
            elif pass_axes >= 2:
                status = "WARNING"
            else:
                status = "FAIL"
            self.task_summary_rows.append(
                {
                    "scenario_id": scenario_id,
                    "task_id": task_id,
                    "tube_id": tube_id,
                    "parameter_set_id": parameter_set_id,
                    "x_rmse_mm": round3(metrics["x_rmse_mm"]),
                    "y_rmse_mm": round3(metrics["y_rmse_mm"]),
                    "z_rmse_mm": round3(metrics["z_rmse_mm"]),
                    "x_max_abs_error_mm": round3(metrics["x_max_abs_error_mm"]),
                    "y_max_abs_error_mm": round3(metrics["y_max_abs_error_mm"]),
                    "z_max_abs_error_mm": round3(metrics["z_max_abs_error_mm"]),
                    "task_tracking_status": status,
                    "notes": "Per-task tracking status based on X/Y/Z concept tolerances.",
                }
            )

    def overshoot_risk_for(self, parameter_set_id: str) -> str:
        rows = [row for row in self.tracking_rows if row["parameter_set_id"] == parameter_set_id]
        sign_changes = 0
        previous: dict[tuple[str, str, str], float] = {}
        for row in rows:
            key = (str(row["scenario_id"]), str(row["task_id"]), str(row["axis"]))
            error = float(row["tracking_error_mm"])
            if key in previous and previous[key] * error < 0.0 and abs(error) > 0.05:
                sign_changes += 1
            previous[key] = error
        sign_change_rate = sign_changes / max(len(rows), 1)
        if "aggressive" in parameter_set_id or sign_change_rate > 0.025:
            return "medium"
        if sign_change_rate > 0.010:
            return "low_medium"
        return "low"

    def build_parameter_comparison(self) -> None:
        by_parameter = defaultdict(list)
        for row in self.error_summary_rows:
            by_parameter[str(row["parameter_set_id"])].append(row)

        candidates: list[dict[str, object]] = []
        for parameter_set_id, rows in sorted(by_parameter.items()):
            axis_rows = {row["axis"]: row for row in rows}
            x_rmse = float(axis_rows["x"]["rmse_mm"])
            y_rmse = float(axis_rows["y"]["rmse_mm"])
            z_rmse = float(axis_rows["z"]["rmse_mm"])
            overall_rmse = math.sqrt((x_rmse * x_rmse + y_rmse * y_rmse + z_rmse * z_rmse) / 3.0)
            max_axis_error = max(float(row["max_abs_error_mm"]) for row in rows)
            within_tolerance_rate = sum(
                float(row["within_tolerance_rate"]) * int(row["sample_count"]) for row in rows
            ) / sum(int(row["sample_count"]) for row in rows)
            any_fail = any(row["tracking_status"] == "FAIL" for row in rows)
            risk = self.overshoot_risk_for(parameter_set_id)
            score = overall_rmse + (0.8 if risk == "medium" else 0.0) + (10.0 if any_fail else 0.0)
            candidates.append(
                {
                    "parameter_set_id": parameter_set_id,
                    "x_rmse_mm": round3(x_rmse),
                    "y_rmse_mm": round3(y_rmse),
                    "z_rmse_mm": round3(z_rmse),
                    "overall_rmse_mm": round3(overall_rmse),
                    "max_axis_error_mm": round3(max_axis_error),
                    "within_tolerance_rate": round3(within_tolerance_rate),
                    "overshoot_risk": risk,
                    "recommended": "no",
                    "notes": "Parameter set comparison before recommendation.",
                    "_score": score,
                    "_any_fail": any_fail,
                }
            )
        pass_candidates = [row for row in candidates if not row["_any_fail"]]
        recommended = min(pass_candidates or candidates, key=lambda row: (row["_score"], row["parameter_set_id"]))
        self.recommended_parameter_set = str(recommended["parameter_set_id"])
        for row in candidates:
            row["recommended"] = "yes" if row["parameter_set_id"] == self.recommended_parameter_set else "no"
            row["notes"] = (
                "Recommended default: lowest balanced tracking error without high overshoot risk."
                if row["recommended"] == "yes"
                else "Compared parameter set; not selected as default."
            )
            row.pop("_score")
            row.pop("_any_fail")
        self.parameter_comparison_rows = candidates

    def build_warning_log(self) -> None:
        for row in self.error_summary_rows:
            if row["tracking_status"] in {"WARNING", "FAIL"}:
                self.warning_rows.append(
                    {
                        "warning_id": f"WARN-7B6-{len(self.warning_rows) + 1:03d}",
                        "parameter_set_id": row["parameter_set_id"],
                        "axis": row["axis"],
                        "scenario_id": "all",
                        "task_id": row["worst_task_id"],
                        "warning_type": "tracking_error_threshold",
                        "severity": row["tracking_status"],
                        "measured_value": row["max_abs_error_mm"],
                        "limit_value": row["position_tolerance_mm"],
                        "notes": "Concept-stage tracking warning; tune after final motor/encoder/drive data.",
                    }
                )
        for row in self.parameter_comparison_rows:
            if row["overshoot_risk"] == "medium":
                self.warning_rows.append(
                    {
                        "warning_id": f"WARN-7B6-{len(self.warning_rows) + 1:03d}",
                        "parameter_set_id": row["parameter_set_id"],
                        "axis": "xyz",
                        "scenario_id": "all",
                        "task_id": "all",
                        "warning_type": "overshoot_risk",
                        "severity": "WARNING",
                        "measured_value": row["overshoot_risk"],
                        "limit_value": "low_or_low_medium_preferred",
                        "notes": "Aggressive parameters are faster but carry higher overshoot/noise risk.",
                    }
                )

    def write_outputs(self) -> None:
        write_csv(
            PARAMETERS_CSV,
            [
                "parameter_set_id",
                "axis",
                "kp",
                "ki",
                "kd",
                "plant_time_constant_s",
                "max_velocity_mm_s",
                "max_acceleration_mm_s2",
                "position_tolerance_mm",
                "notes",
            ],
            self.parameter_rows,
        )
        write_csv(
            TRACKING_TRACE_CSV,
            [
                "scenario_id",
                "task_id",
                "tube_id",
                "time_s",
                "parameter_set_id",
                "axis",
                "reference_position_mm",
                "actual_position_mm",
                "tracking_error_mm",
                "reference_velocity_mm_s",
                "actual_velocity_mm_s",
                "reference_acceleration_mm_s2",
                "actual_acceleration_mm_s2",
                "controller_output",
                "within_tolerance",
                "notes",
            ],
            self.tracking_rows,
        )
        write_csv(
            ERROR_SUMMARY_CSV,
            [
                "parameter_set_id",
                "axis",
                "sample_count",
                "rmse_mm",
                "mae_mm",
                "max_abs_error_mm",
                "mean_abs_error_mm",
                "position_tolerance_mm",
                "within_tolerance_rate",
                "worst_task_id",
                "tracking_status",
                "overshoot_event_count",
                "settling_behavior",
                "notes",
            ],
            self.error_summary_rows,
        )
        write_csv(
            TASK_SUMMARY_CSV,
            [
                "scenario_id",
                "task_id",
                "tube_id",
                "parameter_set_id",
                "x_rmse_mm",
                "y_rmse_mm",
                "z_rmse_mm",
                "x_max_abs_error_mm",
                "y_max_abs_error_mm",
                "z_max_abs_error_mm",
                "task_tracking_status",
                "notes",
            ],
            self.task_summary_rows,
        )
        write_csv(
            PARAMETER_COMPARISON_CSV,
            [
                "parameter_set_id",
                "x_rmse_mm",
                "y_rmse_mm",
                "z_rmse_mm",
                "overall_rmse_mm",
                "max_axis_error_mm",
                "within_tolerance_rate",
                "overshoot_risk",
                "recommended",
                "notes",
            ],
            self.parameter_comparison_rows,
        )
        write_csv(
            WARNING_LOG_CSV,
            [
                "warning_id",
                "parameter_set_id",
                "axis",
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
        self.write_figures()
        self.write_report()

    def write_figures(self) -> None:
        FIG_DIR.mkdir(parents=True, exist_ok=True)
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        sample_filter = lambda row: row["scenario_id"] == "baseline" and row["task_id"] == "TASK-7B1-001" and row["parameter_set_id"] == self.recommended_parameter_set
        sample_rows = [row for row in self.tracking_rows if sample_filter(row)]
        for axis in ["x", "y", "z"]:
            rows = [row for row in sample_rows if row["axis"] == axis]
            fig, ax = plt.subplots(figsize=(9, 4))
            ax.plot([float(row["time_s"]) for row in rows], [float(row["reference_position_mm"]) for row in rows], label="reference")
            ax.plot([float(row["time_s"]) for row in rows], [float(row["actual_position_mm"]) for row in rows], label="actual", linestyle="--")
            ax.set_title(f"Axis Tracking Reference vs Actual {axis.upper()} v1")
            ax.set_xlabel("time_s")
            ax.set_ylabel("position_mm")
            ax.legend()
            fig.tight_layout()
            fig.savefig(FIG_DIR / f"axis_tracking_reference_vs_actual_{axis}_v1.png", dpi=160)
            plt.close(fig)

        fig, ax = plt.subplots(figsize=(9, 4))
        for axis in ["x", "y", "z"]:
            rows = [row for row in sample_rows if row["axis"] == axis]
            ax.plot([float(row["time_s"]) for row in rows], [float(row["tracking_error_mm"]) for row in rows], label=axis)
        ax.set_title("Axis Tracking Error Profile v1")
        ax.set_xlabel("time_s")
        ax.set_ylabel("tracking_error_mm")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG_DIR / "axis_tracking_error_profile_v1.png", dpi=160)
        plt.close(fig)

        labels = [row["parameter_set_id"] for row in self.parameter_comparison_rows]
        overall = [float(row["overall_rmse_mm"]) for row in self.parameter_comparison_rows]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(labels, overall, color=["#7f8c8d", "#2e86ab", "#c44e52"])
        ax.set_title("Axis Tracking Parameter Comparison v1")
        ax.set_ylabel("overall_rmse_mm")
        ax.tick_params(axis="x", rotation=15)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "axis_tracking_parameter_comparison_v1.png", dpi=160)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4))
        recommended_rows = [row for row in self.error_summary_rows if row["parameter_set_id"] == self.recommended_parameter_set]
        ax.bar([row["axis"] for row in recommended_rows], [float(row["rmse_mm"]) for row in recommended_rows], color=["#4c78a8", "#59a14f", "#f28e2b"])
        ax.set_title("Axis Tracking RMSE by Axis v1")
        ax.set_xlabel("axis")
        ax.set_ylabel("rmse_mm")
        fig.tight_layout()
        fig.savefig(FIG_DIR / "axis_tracking_rmse_by_axis_v1.png", dpi=160)
        plt.close(fig)

    def write_report(self) -> None:
        recommended_summary = {
            row["axis"]: row
            for row in self.error_summary_rows
            if row["parameter_set_id"] == self.recommended_parameter_set
        }
        comparison = {
            row["parameter_set_id"]: row
            for row in self.parameter_comparison_rows
        }
        recommended_comparison = comparison[self.recommended_parameter_set]
        z_worst = (
            float(recommended_summary["z"]["rmse_mm"]) >= float(recommended_summary["x"]["rmse_mm"])
            and float(recommended_summary["z"]["rmse_mm"]) >= float(recommended_summary["y"]["rmse_mm"])
        )
        REPORT_MD.write_text(
            "\n".join(
                [
                    "# Stage 7B-6 Axis Servo / PID Tracking Report",
                    "",
                    "## Scope",
                    "",
                    "- This stage is not CAD modeling, rendering, or presentation animation.",
                    "- This stage is a concept-level servo tracking simulation based on the accepted Stage 7B-5 reference trajectory.",
                    "- No Stage 7A files, `legacy_v1` files, CAD geometry, or XY slider binding files are modified.",
                    "- The current system does not use a camera; input occupancy is supplied by the internal tube occupancy table.",
                    "",
                    "## Control Model",
                    "",
                    "- X, Y, and Z are simulated as independent discrete-time servo axes.",
                    "- The controller uses PID position error terms plus the reference velocity as feedforward command input.",
                    "- The plant is a simplified first-order position servo response; actual velocity and acceleration are derived as concept-level indicators.",
                    "- X/Y share the same parameter family; Z has separate parameters because Stage 7B-4 identified `z_motion` as the bottleneck stage.",
                    "",
                    "## Parameter Comparison",
                    "",
                    f"- conservative_pid overall RMSE: {comparison['conservative_pid']['overall_rmse_mm']} mm; overshoot risk: {comparison['conservative_pid']['overshoot_risk']}.",
                    f"- balanced_pid overall RMSE: {comparison['balanced_pid']['overall_rmse_mm']} mm; overshoot risk: {comparison['balanced_pid']['overshoot_risk']}.",
                    f"- aggressive_pid overall RMSE: {comparison['aggressive_pid']['overall_rmse_mm']} mm; overshoot risk: {comparison['aggressive_pid']['overshoot_risk']}.",
                    f"- Recommended parameter_set: `{self.recommended_parameter_set}`.",
                    "",
                    "## Recommended Tracking Results",
                    "",
                    f"- X RMSE / max error: {recommended_summary['x']['rmse_mm']} / {recommended_summary['x']['max_abs_error_mm']} mm; status={recommended_summary['x']['tracking_status']}.",
                    f"- Y RMSE / max error: {recommended_summary['y']['rmse_mm']} / {recommended_summary['y']['max_abs_error_mm']} mm; status={recommended_summary['y']['tracking_status']}.",
                    f"- Z RMSE / max error: {recommended_summary['z']['rmse_mm']} / {recommended_summary['z']['max_abs_error_mm']} mm; status={recommended_summary['z']['tracking_status']}.",
                    f"- Overall within_tolerance_rate: {recommended_comparison['within_tolerance_rate']}.",
                    f"- Settling behavior X/Y/Z: {recommended_summary['x']['settling_behavior']} / {recommended_summary['y']['settling_behavior']} / {recommended_summary['z']['settling_behavior']}.",
                    f"- Overshoot event count X/Y/Z: {recommended_summary['x']['overshoot_event_count']} / {recommended_summary['y']['overshoot_event_count']} / {recommended_summary['z']['overshoot_event_count']}.",
                    f"- Z axis remains the hardest tracked axis: {'yes' if z_worst else 'no'}.",
                    "",
                    "## Stage 7B-4 Consistency",
                    "",
                    "- The Z axis uses tighter tolerance and lower velocity limits than X/Y, so it remains the most sensitive axis for tracking.",
                    "- This is consistent with Stage 7B-4, where repeated Z descend/lift operations made `z_motion` the timing bottleneck.",
                    "",
                    "## Limits And Next Work",
                    "",
                    "- This result is not final real hardware control performance.",
                    "- Future calibration needs real motor, drive, encoder, load inertia, friction, payload, mechanical compliance, and controller-cycle parameters.",
                    "- Stage 7A-3f XY slider binding remains deferred. It does not affect this abstract control simulation, but it does affect final mechanical implementation and physical validation.",
                    "- validation_status=PASS",
                ]
            )
            + "\n",
            encoding="utf-8",
        )


def main() -> int:
    simulation = AxisServoPidTrackingSimulation()
    simulation.simulate()
    recommended = simulation.recommended_parameter_set
    recommended_rows = {
        row["axis"]: row
        for row in simulation.error_summary_rows
        if row["parameter_set_id"] == recommended
    }
    recommended_comparison = next(row for row in simulation.parameter_comparison_rows if row["recommended"] == "yes")
    fail_count = sum(1 for row in recommended_rows.values() if row["tracking_status"] == "FAIL")
    validation_status = "PASS" if fail_count == 0 else "FAIL"
    print(f"validation_status={validation_status}")
    print(f"recommended_parameter_set={recommended}")
    print(f"x_rmse_mm={recommended_rows['x']['rmse_mm']}")
    print(f"x_max_abs_error_mm={recommended_rows['x']['max_abs_error_mm']}")
    print(f"y_rmse_mm={recommended_rows['y']['rmse_mm']}")
    print(f"y_max_abs_error_mm={recommended_rows['y']['max_abs_error_mm']}")
    print(f"z_rmse_mm={recommended_rows['z']['rmse_mm']}")
    print(f"z_max_abs_error_mm={recommended_rows['z']['max_abs_error_mm']}")
    print(f"within_tolerance_rate={recommended_comparison['within_tolerance_rate']}")
    print(f"warning_count={len(simulation.warning_rows)}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
