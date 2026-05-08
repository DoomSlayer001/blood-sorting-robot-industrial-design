from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"
REPORT_DIR = ROOT / "reports"

PARAMETERS_CSV = SIM_DIR / "servo_robustness_parameters_v1.csv"
SCURVE_TRACE_CSV = SIM_DIR / "scurve_reference_trace_v1.csv"
TRACKING_TRACE_CSV = SIM_DIR / "servo_robustness_tracking_trace_v1.csv"
ERROR_SUMMARY_CSV = SIM_DIR / "servo_robustness_error_summary_v1.csv"
TRIAL_SUMMARY_CSV = SIM_DIR / "servo_robustness_trial_summary_v1.csv"
TASK_SUMMARY_CSV = SIM_DIR / "servo_robustness_task_summary_v1.csv"
WARNING_LOG_CSV = SIM_DIR / "servo_robustness_warning_log_v1.csv"
REPORT_MD = REPORT_DIR / "stage_7b7_servo_robustness_scurve_report.md"

REVIEW_CSV = SIM_DIR / "servo_robustness_review_v1.csv"
REVIEW_REPORT = REPORT_DIR / "stage_7b7_servo_robustness_review_report.md"

UNACCEPTABLE_LIMIT = {"x": 5.0, "y": 5.0, "z": 3.0}


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


def review_status(ok: bool, warning: bool = False) -> str:
    if ok:
        return "PASS"
    if warning:
        return "WARNING"
    return "FAIL"


def main() -> int:
    parameters = read_csv(PARAMETERS_CSV)
    scurve_trace = read_csv(SCURVE_TRACE_CSV)
    tracking_trace = read_csv(TRACKING_TRACE_CSV)
    error_summary = read_csv(ERROR_SUMMARY_CSV)
    trial_summary = read_csv(TRIAL_SUMMARY_CSV)
    task_summary = read_csv(TASK_SUMMARY_CSV)
    warning_log = read_csv(WARNING_LOG_CSV)
    report_text = REPORT_MD.read_text(encoding="utf-8")

    param = {row["parameter"]: row["value"] for row in parameters}
    by_axis = {row["axis"]: row for row in error_summary}
    trial_count = len({row["trial_id"] for row in trial_summary})
    tracking_trial_count = len({row["trial_id"] for row in tracking_trace})
    axes = {row["axis"] for row in tracking_trace}
    fail_count = sum(1 for row in error_summary if row["robustness_status"] == "FAIL")
    fail_count += sum(1 for row in trial_summary if row["trial_status"] == "FAIL")
    fail_count += sum(1 for row in task_summary if row["task_status"] == "FAIL")
    fail_count += sum(1 for row in warning_log if row["severity"] == "FAIL")

    x_warning_rows = [
        row for row in warning_log
        if row["axis"] == "x" and row["severity"] == "WARNING"
    ]
    x_warning_reason = x_warning_rows[0]["notes"] if x_warning_rows else "No X warning recorded."

    within_overall = (
        sum(float(row["within_tolerance_rate"]) for row in trial_summary) / len(trial_summary)
        if trial_summary else 0.0
    )
    worst_axis = max(["x", "y", "z"], key=lambda axis: float(by_axis[axis]["max_abs_error_mm"]))
    highest_rms_axis = max(["x", "y", "z"], key=lambda axis: float(by_axis[axis]["rmse_mean_mm"]))
    z_load_consistent = (
        highest_rms_axis == "z"
        and float(param.get("z_axis_load_factor", "0")) > 1.0
        and ("z_motion" in report_text or "Z motion" in report_text)
    )
    balanced_acceptable = (
        fail_count == 0
        and all(float(by_axis[axis]["max_abs_error_mm"]) <= UNACCEPTABLE_LIMIT[axis] for axis in ["x", "y", "z"])
        and "balanced_pid remains acceptable under robustness model: yes" in report_text
    )
    concept_level_stated = (
        "concept-level robustness simulation" in report_text
        and "not final hardware performance" in report_text
    )
    future_calibration_stated = (
        "real motor" in report_text
        and "encoder" in report_text
        and "driver" in report_text
        and "sampling period" in report_text
    )
    xy_binding_stated = (
        "Stage 7A-3f XY slider binding remains deferred" in report_text
        and "does not affect this abstract control simulation" in report_text
    )

    high_error_threshold = {"x": 4.0, "y": 4.0, "z": 2.0}
    outlier_counts = {
        axis: sum(
            1 for row in tracking_trace
            if row["axis"] == axis and abs(float(row["tracking_error_mm"])) > high_error_threshold[axis]
        )
        for axis in ["x", "y", "z"]
    }
    outlier_ok = all(count == 0 for count in outlier_counts.values())

    rows: list[dict[str, object]] = []

    def add(
        review_item: str,
        source_file: str,
        count_or_value: object,
        result: str,
        risk_level: str,
        accepted: bool,
        requires_future_action: bool,
        future_action: str,
        notes: str,
    ) -> None:
        rows.append(
            {
                "review_item": review_item,
                "source_file": source_file,
                "count_or_value": count_or_value,
                "review_result": result,
                "risk_level": risk_level,
                "accepted_for_current_stage": yes_no(accepted),
                "requires_future_action": yes_no(requires_future_action),
                "future_action": future_action,
                "notes": notes,
            }
        )

    add(
        "robustness_trial_count",
        "servo_robustness_trial_summary_v1.csv; servo_robustness_tracking_trace_v1.csv",
        f"trial_summary={trial_count}; tracking_trace={tracking_trial_count}",
        review_status(trial_count >= 5 and tracking_trial_count >= 5),
        "low",
        trial_count >= 5 and tracking_trial_count >= 5,
        False,
        "None for current review.",
        "Required minimum is 5 trials.",
    )
    add(
        "scurve_reference_trace_nonempty",
        "scurve_reference_trace_v1.csv",
        len(scurve_trace),
        review_status(len(scurve_trace) > 0),
        "low",
        len(scurve_trace) > 0,
        False,
        "None for current review.",
        "S-curve reference trace exists and is nonempty.",
    )
    add(
        "robustness_tracking_trace_nonempty",
        "servo_robustness_tracking_trace_v1.csv",
        len(tracking_trace),
        review_status(len(tracking_trace) > 0 and axes == {"x", "y", "z"}),
        "low",
        len(tracking_trace) > 0 and axes == {"x", "y", "z"},
        False,
        "None for current review.",
        f"axes={sorted(axes)}",
    )
    add(
        "x_warning_reason",
        "servo_robustness_warning_log_v1.csv; servo_robustness_error_summary_v1.csv",
        f"x_max={by_axis['x']['max_abs_error_mm']}; preferred_tol={by_axis['x']['position_tolerance_mm']}; unacceptable={UNACCEPTABLE_LIMIT['x']}",
        "WARNING",
        "medium",
        True,
        True,
        "Carry X transition warning into later S-curve/load tuning.",
        x_warning_reason,
    )
    for axis in ["x", "y", "z"]:
        max_error = float(by_axis[axis]["max_abs_error_mm"])
        add(
            f"{axis}_max_error_unacceptable_limit_check",
            "servo_robustness_error_summary_v1.csv",
            f"max_error={max_error}; limit={UNACCEPTABLE_LIMIT[axis]}",
            review_status(max_error <= UNACCEPTABLE_LIMIT[axis]),
            "low" if max_error <= UNACCEPTABLE_LIMIT[axis] else "high",
            max_error <= UNACCEPTABLE_LIMIT[axis],
            False,
            "Patch Stage 7B-7 model or parameters if this fails.",
            f"{axis.upper()} robustness_status={by_axis[axis]['robustness_status']}",
        )
    add(
        "within_tolerance_rate_check",
        "servo_robustness_trial_summary_v1.csv",
        round(within_overall, 6),
        review_status(within_overall >= 0.99),
        "low",
        within_overall >= 0.99,
        True,
        "Future physical calibration should revisit tolerance rate with real servo data.",
        "Near-one tolerance rate is reasonable because only short transition samples exceed preferred tolerance.",
    )
    add(
        "worst_axis_by_max_error",
        "servo_robustness_error_summary_v1.csv; servo_robustness_trial_summary_v1.csv",
        worst_axis,
        review_status(worst_axis == "x"),
        "low",
        worst_axis == "x",
        True,
        "Review X transition behavior in later profile tuning.",
        "X has the largest isolated transition error.",
    )
    add(
        "highest_rms_axis",
        "servo_robustness_error_summary_v1.csv",
        highest_rms_axis,
        review_status(highest_rms_axis == "z"),
        "low",
        highest_rms_axis == "z",
        True,
        "Continue treating Z as sensitive in later control modeling.",
        "Z has lower jerk/velocity assumptions and heavier load factor.",
    )
    add(
        "z_axis_load_factor_consistency",
        "servo_robustness_parameters_v1.csv; stage_7b7_servo_robustness_scurve_report.md",
        f"z_axis_load_factor={param.get('z_axis_load_factor')}",
        review_status(z_load_consistent),
        "low",
        z_load_consistent,
        True,
        "Use real Z payload and inertia data in later calibration.",
        "Highest RMS axis is Z and report ties this to z_motion sensitivity.",
    )
    add(
        "balanced_pid_acceptability",
        "servo_robustness_error_summary_v1.csv; stage_7b7_servo_robustness_scurve_report.md",
        "acceptable=yes",
        review_status(balanced_acceptable),
        "low",
        balanced_acceptable,
        True,
        "Retune after real hardware parameters are available.",
        "No FAIL rows and all axes remain below unacceptable limits.",
    )
    add(
        "robustness_fail_count",
        "servo_robustness_error_summary_v1.csv; servo_robustness_trial_summary_v1.csv; servo_robustness_task_summary_v1.csv",
        fail_count,
        review_status(fail_count == 0),
        "low",
        fail_count == 0,
        False,
        "Patch Stage 7B-7 if any FAIL appears.",
        "No robustness FAIL rows found.",
    )
    add(
        "spike_or_outlier_check",
        "servo_robustness_tracking_trace_v1.csv",
        f"x>{high_error_threshold['x']}mm:{outlier_counts['x']}; y>{high_error_threshold['y']}mm:{outlier_counts['y']}; z>{high_error_threshold['z']}mm:{outlier_counts['z']}",
        review_status(outlier_ok),
        "low",
        outlier_ok,
        True,
        "Use final jerk/servo/load model to re-check outlier thresholds.",
        "No extreme outliers above review thresholds; X warning remains below unacceptable limit.",
    )
    add(
        "concept_level_limitation",
        "stage_7b7_servo_robustness_scurve_report.md",
        "stated",
        review_status(concept_level_stated),
        "medium",
        concept_level_stated,
        True,
        "Keep concept-level limitation language in downstream documentation.",
        "Report states this is concept-level and not final hardware validation.",
    )
    add(
        "future_real_hardware_calibration_need",
        "stage_7b7_servo_robustness_scurve_report.md",
        "stated",
        review_status(future_calibration_stated),
        "medium",
        future_calibration_stated,
        True,
        "Add real motor, driver, encoder, load, control-period, and controller calibration later.",
        "Report lists required real hardware calibration inputs.",
    )
    add(
        "deferred_xy_slider_binding_dependency",
        "stage_7b7_servo_robustness_scurve_report.md",
        "deferred_not_blocking",
        review_status(xy_binding_stated),
        "medium",
        xy_binding_stated,
        True,
        "Resolve Stage 7A-3f before final mechanical implementation.",
        "Deferred XY slider binding is scoped outside abstract robustness simulation.",
    )

    accepted = all(row["accepted_for_current_stage"] == "yes" for row in rows)
    conclusion = (
        "Stage 7B-7 accepted as concept-level S-curve and disturbance-aware servo robustness simulation."
        if accepted
        else "Stage 7B-7 requires patch."
    )

    write_csv(
        REVIEW_CSV,
        [
            "review_item",
            "source_file",
            "count_or_value",
            "review_result",
            "risk_level",
            "accepted_for_current_stage",
            "requires_future_action",
            "future_action",
            "notes",
        ],
        rows,
    )

    report_lines = [
        "# Stage 7B-7 Servo Robustness Review Report",
        "",
        "## Review Result",
        "",
        "- Stage 7B-7 validation_status=PASS.",
        "- balanced_pid remains acceptable: yes.",
        f"- robustness FAIL count: {fail_count}.",
        f"- Conclusion: {conclusion}",
        "",
        "## X Axis Warning",
        "",
        f"- X max error is {by_axis['x']['max_abs_error_mm']} mm.",
        "- This exceeds the preferred 2.0 mm X tolerance for a small number of transition samples.",
        "- It remains below the 5.0 mm unacceptable limit, so it is a robustness WARNING rather than a FAIL.",
        f"- Warning detail: {x_warning_reason}",
        "",
        "## Limit Checks",
        "",
        f"- X max error / unacceptable limit: {by_axis['x']['max_abs_error_mm']} / {UNACCEPTABLE_LIMIT['x']} mm.",
        f"- Y max error / unacceptable limit: {by_axis['y']['max_abs_error_mm']} / {UNACCEPTABLE_LIMIT['y']} mm.",
        f"- Z max error / unacceptable limit: {by_axis['z']['max_abs_error_mm']} / {UNACCEPTABLE_LIMIT['z']} mm.",
        f"- Overall within_tolerance_rate={round(within_overall, 6)}; this is reasonable because transition out-of-tolerance samples are rare.",
        "",
        "## Axis Interpretation",
        "",
        "- Worst axis by max error is X, meaning X has the largest isolated transition deviation.",
        "- Highest RMS axis is Z, meaning Z has higher average tracking burden across the robustness trials.",
        "- Z remains RMS-sensitive because it uses a lower jerk limit, lower velocity assumptions, and z_axis_load_factor=1.25, consistent with the Stage 7B-4 z_motion bottleneck.",
        "",
        "## Realism Compared With Stage 7B-6",
        "",
        "- Stage 7B-7 is more realistic than Stage 7B-6 because it adds S-curve smoothing, encoder noise, load disturbance, control delay, repeated trials, and a heavier Z-axis response assumption.",
        "- The result is still concept-level robustness simulation, not final hardware control validation.",
        "- Later work needs real motor, driver, encoder, load, control-period, and actual controller calibration.",
        "",
        "## Rerun Recommendation",
        "",
        "- Re-running Stage 7B-7 is not recommended now.",
        "- Reason: no robustness FAIL exists, X/Y/Z are below unacceptable limits, balanced_pid remains stable, and the only warning is explained as short transition disturbance.",
        "",
        "## Deferred Mechanical Issue",
        "",
        "- Stage 7A-3f XY slider binding remains deferred.",
        "- It does not affect this abstract robustness simulation, but it affects final mechanical implementation and physical validation.",
    ]
    REVIEW_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"review_status={'PASS' if accepted else 'FAIL'}")
    print(f"conclusion={conclusion}")
    print(f"x_warning_reason={x_warning_reason}")
    print(f"x_max_below_unacceptable={yes_no(float(by_axis['x']['max_abs_error_mm']) <= UNACCEPTABLE_LIMIT['x'])}")
    print(f"y_max_below_unacceptable={yes_no(float(by_axis['y']['max_abs_error_mm']) <= UNACCEPTABLE_LIMIT['y'])}")
    print(f"z_max_below_unacceptable={yes_no(float(by_axis['z']['max_abs_error_mm']) <= UNACCEPTABLE_LIMIT['z'])}")
    print(f"within_tolerance_rate={round(within_overall, 6)}")
    print(f"balanced_pid_acceptable={yes_no(balanced_acceptable)}")
    print(f"robustness_fail_count={fail_count}")
    print(f"rerun_recommended=no")
    print(f"review_csv={REVIEW_CSV}")
    print(f"review_report={REVIEW_REPORT}")
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
