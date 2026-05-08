from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"

SCURVE_TRACE_CSV = SIM_DIR / "scurve_reference_trace_v1.csv"
TRACKING_TRACE_CSV = SIM_DIR / "servo_robustness_tracking_trace_v1.csv"
ERROR_SUMMARY_CSV = SIM_DIR / "servo_robustness_error_summary_v1.csv"
TRIAL_SUMMARY_CSV = SIM_DIR / "servo_robustness_trial_summary_v1.csv"
TASK_SUMMARY_CSV = SIM_DIR / "servo_robustness_task_summary_v1.csv"
WARNING_LOG_CSV = SIM_DIR / "servo_robustness_warning_log_v1.csv"

UNACCEPTABLE_LIMIT = {"x": 5.0, "y": 5.0, "z": 3.0}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    issues: list[str] = []
    scurve_trace = read_csv(SCURVE_TRACE_CSV)
    tracking_trace = read_csv(TRACKING_TRACE_CSV)
    error_summary = read_csv(ERROR_SUMMARY_CSV)
    trial_summary = read_csv(TRIAL_SUMMARY_CSV)
    task_summary = read_csv(TASK_SUMMARY_CSV)
    warning_log = read_csv(WARNING_LOG_CSV)

    if not scurve_trace:
        issues.append("scurve_reference_trace is empty")
    if not tracking_trace:
        issues.append("servo_robustness_tracking_trace is empty")
    if len({row["trial_id"] for row in tracking_trace}) < 5:
        issues.append("fewer than 5 robustness trials")
    axes = {row["axis"] for row in tracking_trace}
    if axes != {"x", "y", "z"}:
        issues.append(f"X/Y/Z results incomplete: axes={sorted(axes)}")
    if any(row["tracking_error_mm"] == "" for row in tracking_trace):
        issues.append("tracking_error contains empty values")
    if any(float(row["rmse_mean_mm"]) < 0.0 or float(row["rmse_max_mm"]) < 0.0 for row in error_summary):
        issues.append("RMSE contains negative values")

    low_within_rows = [
        row for row in error_summary
        if float(row["within_tolerance_rate"]) < 0.90
    ]
    if low_within_rows:
        issues.append("within_tolerance_rate below 0.90 for one or more axes")

    unacceptable_rows = [
        row for row in error_summary
        if float(row["max_abs_error_mm"]) > UNACCEPTABLE_LIMIT[row["axis"]]
    ]
    if unacceptable_rows:
        issues.append("max_abs_error exceeds unacceptable limit")

    if not any(row["estimated_jerk_mm_s3"] != "" for row in scurve_trace):
        issues.append("S-curve jerk statistics missing")
    if not any(row["estimated_jerk_mm_s3"] != "" for row in tracking_trace):
        issues.append("tracking jerk statistics missing")

    fail_rows = [row for row in error_summary if row["robustness_status"] == "FAIL"]
    fail_trials = [row for row in trial_summary if row["trial_status"] == "FAIL"]
    if fail_rows or fail_trials:
        issues.append("balanced_pid is not acceptable under robustness model")

    validation_status = "PASS" if not issues else "FAIL"
    print(f"validation_status={validation_status}")
    print(f"scurve_reference_rows={len(scurve_trace)}")
    print(f"tracking_trace_rows={len(tracking_trace)}")
    print(f"trial_count={len({row['trial_id'] for row in tracking_trace})}")
    print(f"error_summary_rows={len(error_summary)}")
    print(f"trial_summary_rows={len(trial_summary)}")
    print(f"task_summary_rows={len(task_summary)}")
    print(f"warning_log_rows={len(warning_log)}")
    for row in error_summary:
        print(
            f"{row['axis']}_rmse_mean_mm={row['rmse_mean_mm']} "
            f"{row['axis']}_max_abs_error_mm={row['max_abs_error_mm']} "
            f"{row['axis']}_within_tolerance_rate={row['within_tolerance_rate']} "
            f"{row['axis']}_status={row['robustness_status']}"
        )
    if issues:
        for issue in issues:
            print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
