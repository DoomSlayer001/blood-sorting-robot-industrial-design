from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"

PARAMETERS_CSV = SIM_DIR / "axis_servo_pid_parameters_v1.csv"
TRACKING_TRACE_CSV = SIM_DIR / "axis_servo_tracking_trace_v1.csv"
ERROR_SUMMARY_CSV = SIM_DIR / "axis_tracking_error_summary_v1.csv"
TASK_SUMMARY_CSV = SIM_DIR / "axis_tracking_task_summary_v1.csv"
PARAMETER_COMPARISON_CSV = SIM_DIR / "axis_tracking_parameter_comparison_v1.csv"
WARNING_LOG_CSV = SIM_DIR / "axis_tracking_warning_log_v1.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    issues: list[str] = []
    parameters = read_csv(PARAMETERS_CSV)
    trace = read_csv(TRACKING_TRACE_CSV)
    error_summary = read_csv(ERROR_SUMMARY_CSV)
    task_summary = read_csv(TASK_SUMMARY_CSV)
    comparison = read_csv(PARAMETER_COMPARISON_CSV)
    warning_log = read_csv(WARNING_LOG_CSV)

    if not trace:
        issues.append("tracking trace is empty")
    if not error_summary:
        issues.append("error summary is empty")
    if not task_summary:
        issues.append("task summary is empty")
    if not comparison:
        issues.append("parameter comparison is empty")

    axes = {row["axis"] for row in trace}
    if axes != {"x", "y", "z"}:
        issues.append(f"X/Y/Z simulation incomplete: axes={sorted(axes)}")

    parameter_sets = {row["parameter_set_id"] for row in parameters}
    if len(parameter_sets) < 3:
        issues.append("fewer than 3 parameter_set values")

    if any(row["actual_position_mm"] == "" for row in trace):
        issues.append("actual_position_mm contains empty value")
    if any(row["tracking_error_mm"] == "" for row in trace):
        issues.append("tracking_error_mm contains empty value")
    if any(float(row["rmse_mm"]) < 0.0 for row in error_summary):
        issues.append("RMSE contains negative value")

    recommended = [row for row in comparison if row["recommended"] == "yes"]
    if len(recommended) != 1:
        issues.append(f"recommended parameter_set is not unique: count={len(recommended)}")
        recommended_id = ""
    else:
        recommended_id = recommended[0]["parameter_set_id"]

    balanced_or_recommended_ids = {"balanced_pid"}
    if recommended_id:
        balanced_or_recommended_ids.add(recommended_id)
    acceptable_rows = [
        row
        for row in error_summary
        if row["parameter_set_id"] in balanced_or_recommended_ids and row["tracking_status"] in {"PASS", "WARNING"}
    ]
    acceptable_axes_by_parameter: dict[str, set[str]] = {}
    for row in acceptable_rows:
        acceptable_axes_by_parameter.setdefault(row["parameter_set_id"], set()).add(row["axis"])
    if not any(axes == {"x", "y", "z"} for axes in acceptable_axes_by_parameter.values()):
        issues.append("neither balanced nor recommended parameters satisfy concept-level tolerance")

    validation_status = "PASS" if not issues else "FAIL"
    print(f"validation_status={validation_status}")
    print(f"parameter_set_count={len(parameter_sets)}")
    print(f"tracking_trace_rows={len(trace)}")
    print(f"error_summary_rows={len(error_summary)}")
    print(f"task_summary_rows={len(task_summary)}")
    print(f"warning_log_rows={len(warning_log)}")
    print(f"recommended_parameter_set={recommended_id}")
    if recommended_id:
        rec = recommended[0]
        print(f"recommended_overall_rmse_mm={rec['overall_rmse_mm']}")
        print(f"recommended_within_tolerance_rate={rec['within_tolerance_rate']}")
        print(f"recommended_max_axis_error_mm={rec['max_axis_error_mm']}")
    if issues:
        for issue in issues:
            print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
