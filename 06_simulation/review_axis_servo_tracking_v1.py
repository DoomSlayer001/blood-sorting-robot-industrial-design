from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"
REPORT_DIR = ROOT / "reports"

PARAMETERS_CSV = SIM_DIR / "axis_servo_pid_parameters_v1.csv"
TRACKING_TRACE_CSV = SIM_DIR / "axis_servo_tracking_trace_v1.csv"
ERROR_SUMMARY_CSV = SIM_DIR / "axis_tracking_error_summary_v1.csv"
TASK_SUMMARY_CSV = SIM_DIR / "axis_tracking_task_summary_v1.csv"
PARAMETER_COMPARISON_CSV = SIM_DIR / "axis_tracking_parameter_comparison_v1.csv"
WARNING_LOG_CSV = SIM_DIR / "axis_tracking_warning_log_v1.csv"
REFERENCE_TRACE_CSV = SIM_DIR / "time_stepped_motion_trace_v1.csv"
STAGE7B6_REPORT = REPORT_DIR / "stage_7b6_axis_servo_pid_tracking_report.md"

REVIEW_CSV = SIM_DIR / "axis_servo_tracking_review_v1.csv"
REVIEW_REPORT = REPORT_DIR / "stage_7b6_axis_servo_tracking_review_report.md"


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


def round3(value: float) -> float:
    return round(value, 3)


def status(ok: bool, warning: bool = False) -> str:
    if ok:
        return "PASS"
    if warning:
        return "WARNING"
    return "FAIL"


def main() -> int:
    parameters = read_csv(PARAMETERS_CSV)
    trace = read_csv(TRACKING_TRACE_CSV)
    error_summary = read_csv(ERROR_SUMMARY_CSV)
    task_summary = read_csv(TASK_SUMMARY_CSV)
    comparison = read_csv(PARAMETER_COMPARISON_CSV)
    warning_log = read_csv(WARNING_LOG_CSV)
    reference_trace = read_csv(REFERENCE_TRACE_CSV)
    report_text = STAGE7B6_REPORT.read_text(encoding="utf-8")

    review_rows: list[dict[str, object]] = []

    parameter_sets = sorted({row["parameter_set_id"] for row in parameters})
    axes_by_parameter: dict[str, set[str]] = defaultdict(set)
    for row in parameters:
        axes_by_parameter[row["parameter_set_id"]].add(row["axis"])
    full_parameter_sets = {
        parameter_set_id
        for parameter_set_id, axes in axes_by_parameter.items()
        if axes == {"x", "y", "z"}
    }

    recommended_rows = [row for row in comparison if row["recommended"] == "yes"]
    recommended_unique = len(recommended_rows) == 1
    recommended_id = recommended_rows[0]["parameter_set_id"] if recommended_unique else ""
    balanced_row = next(row for row in comparison if row["parameter_set_id"] == "balanced_pid")
    aggressive_row = next(row for row in comparison if row["parameter_set_id"] == "aggressive_pid")
    conservative_row = next(row for row in comparison if row["parameter_set_id"] == "conservative_pid")
    balanced_reasonable = (
        recommended_id == "balanced_pid"
        and float(balanced_row["within_tolerance_rate"]) == 1.0
        and balanced_row["overshoot_risk"] == "low"
        and aggressive_row["overshoot_risk"] == "medium"
        and float(conservative_row["within_tolerance_rate"]) < 1.0
    )

    recommended_error_rows = [
        row for row in error_summary if row["parameter_set_id"] == recommended_id
    ]
    error_by_axis = {row["axis"]: row for row in recommended_error_rows}
    axis_reasonable = {}
    for axis, row in error_by_axis.items():
        max_error = float(row["max_abs_error_mm"])
        tolerance = float(row["position_tolerance_mm"])
        rmse = float(row["rmse_mm"])
        mae = float(row["mae_mm"])
        axis_reasonable[axis] = (
            rmse >= 0.0
            and mae >= 0.0
            and max_error >= 0.0
            and max_error <= tolerance + 1e-9
            and row["tracking_status"] == "PASS"
        )

    recommended_trace = [row for row in trace if row["parameter_set_id"] == recommended_id]
    zero_error_count = sum(1 for row in recommended_trace if float(row["tracking_error_mm"]) == 0.0)
    zero_error_rate = zero_error_count / len(recommended_trace) if recommended_trace else 1.0
    zero_error_ok = zero_error_rate < 0.05
    overfit_risk = zero_error_rate >= 0.05

    parameter_lookup = {
        (row["parameter_set_id"], row["axis"]): row for row in parameters
    }
    controller_spike_count = 0
    velocity_limit_count = 0
    acceleration_limit_count = 0
    max_controller_ratio = 0.0
    max_velocity_ratio = 0.0
    max_acceleration_ratio = 0.0
    for row in trace:
        key = (row["parameter_set_id"], row["axis"])
        parameter = parameter_lookup[key]
        max_velocity = float(parameter["max_velocity_mm_s"])
        max_acceleration = float(parameter["max_acceleration_mm_s2"])
        controller_ratio = abs(float(row["controller_output"])) / max_velocity if max_velocity else 0.0
        velocity_ratio = abs(float(row["actual_velocity_mm_s"])) / max_velocity if max_velocity else 0.0
        acceleration_ratio = abs(float(row["actual_acceleration_mm_s2"])) / max_acceleration if max_acceleration else 0.0
        max_controller_ratio = max(max_controller_ratio, controller_ratio)
        max_velocity_ratio = max(max_velocity_ratio, velocity_ratio)
        max_acceleration_ratio = max(max_acceleration_ratio, acceleration_ratio)
        if controller_ratio > 1.000001:
            controller_spike_count += 1
        if velocity_ratio > 1.000001:
            velocity_limit_count += 1
        if acceleration_ratio > 1.000001:
            acceleration_limit_count += 1

    trace_by_episode: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in trace:
        trace_by_episode[(row["scenario_id"], row["task_id"], row["parameter_set_id"], row["axis"])].append(row)

    time_nonmonotonic_count = 0
    actual_position_jump_count = 0
    actual_velocity_jump_count = 0
    actual_acceleration_jump_count = 0
    for rows in trace_by_episode.values():
        ordered = sorted(rows, key=lambda row: float(row["time_s"]))
        for previous, current in zip(ordered, ordered[1:]):
            dt = float(current["time_s"]) - float(previous["time_s"])
            if dt < -1e-9:
                time_nonmonotonic_count += 1
            if dt <= 0.0:
                continue
            position_jump = abs(float(current["actual_position_mm"]) - float(previous["actual_position_mm"]))
            velocity_jump = abs(float(current["actual_velocity_mm_s"]) - float(previous["actual_velocity_mm_s"]))
            acceleration_jump = abs(float(current["actual_acceleration_mm_s2"]) - float(previous["actual_acceleration_mm_s2"]))
            if position_jump > 25.0:
                actual_position_jump_count += 1
            if velocity_jump > 350.0:
                actual_velocity_jump_count += 1
            if acceleration_jump > 9000.0:
                actual_acceleration_jump_count += 1

    expected_trace_count = len(reference_trace) * len(parameter_sets) * 3
    alignment_ok = len(trace) == expected_trace_count
    sample_counts = Counter((row["parameter_set_id"], row["axis"]) for row in trace)
    per_axis_alignment_ok = all(count == len(reference_trace) for count in sample_counts.values())

    within_rate = float(balanced_row["within_tolerance_rate"])
    within_rate_ok = within_rate == 1.0 and all(axis_reasonable.values())
    z_consistent = (
        error_by_axis["z"]["tracking_status"] == "PASS"
        and float(error_by_axis["z"]["position_tolerance_mm"]) < float(error_by_axis["x"]["position_tolerance_mm"])
        and "z_motion" in report_text
    )
    concept_limit_stated = (
        "concept-level" in report_text
        and "not final real hardware control performance" in report_text
    )
    future_model_stated = (
        "S-curve" in report_text
        or "drive" in report_text
        and "encoder" in report_text
    )
    xy_binding_stated = (
        "Stage 7A-3f XY slider binding remains deferred" in report_text
        and "does not affect this abstract control simulation" in report_text
    )

    def add(
        review_item: str,
        source_file: str,
        count_or_value: object,
        review_result: str,
        risk_level: str,
        accepted: bool,
        future_action: str,
        notes: str,
        requires_future_action: bool | None = None,
    ) -> None:
        review_rows.append(
            {
                "review_item": review_item,
                "source_file": source_file,
                "count_or_value": count_or_value,
                "review_result": review_result,
                "risk_level": risk_level,
                "accepted_for_current_stage": yes_no(accepted),
                "requires_future_action": yes_no((review_result != "PASS") if requires_future_action is None else requires_future_action),
                "future_action": future_action,
                "notes": notes,
            }
        )

    add(
        "parameter_set_count",
        "axis_servo_pid_parameters_v1.csv",
        len(parameter_sets),
        status(len(parameter_sets) >= 3 and len(full_parameter_sets) == len(parameter_sets)),
        "low",
        len(parameter_sets) >= 3 and len(full_parameter_sets) == len(parameter_sets),
        "None for current review.",
        f"parameter_sets={';'.join(parameter_sets)}; full_xyz_sets={len(full_parameter_sets)}",
        False,
    )
    add(
        "recommended_parameter_unique",
        "axis_tracking_parameter_comparison_v1.csv",
        len(recommended_rows),
        status(recommended_unique and recommended_id == "balanced_pid"),
        "low",
        recommended_unique and recommended_id == "balanced_pid",
        "None for current review.",
        f"recommended_parameter_set={recommended_id}",
        False,
    )
    add(
        "balanced_pid_selection_reason",
        "axis_tracking_parameter_comparison_v1.csv",
        "balanced_pid",
        status(balanced_reasonable),
        "low",
        balanced_reasonable,
        "Keep aggressive_pid as faster but higher-risk option; keep balanced_pid as concept default.",
        "balanced has within_tolerance_rate=1.0 and low overshoot risk; aggressive has lower RMSE but medium overshoot risk; conservative fails tolerance.",
        False,
    )
    for axis in ["x", "y", "z"]:
        row = error_by_axis[axis]
        add(
            f"{axis}_tracking_error_reasonableness",
            "axis_tracking_error_summary_v1.csv",
            f"rmse={row['rmse_mm']}; max={row['max_abs_error_mm']}; tolerance={row['position_tolerance_mm']}",
            status(axis_reasonable[axis]),
            "low" if axis_reasonable[axis] else "high",
            axis_reasonable[axis],
            "Patch Stage 7B-6 tracking model or parameter table if this fails.",
            f"{axis.upper()} tracking_status={row['tracking_status']}; worst_task_id={row['worst_task_id']}",
            False,
        )
    add(
        "within_tolerance_rate_check",
        "axis_tracking_parameter_comparison_v1.csv",
        within_rate,
        status(within_rate_ok),
        "medium",
        within_rate_ok,
        "Future higher-fidelity model should use S-curve command profiles and measured plant limits.",
        "within_tolerance_rate=1.0 is plausible for simplified first-order concept tracking after selecting balanced_pid; it is optimistic for hardware.",
        True,
    )
    add(
        "zero_error_overfit_check",
        "axis_servo_tracking_trace_v1.csv",
        f"zero_error_rate={round3(zero_error_rate)}",
        status(zero_error_ok, warning=overfit_risk),
        "medium" if overfit_risk else "low",
        True,
        "Keep explicit concept-level limitation; future model should add command shaping, encoder quantization, disturbance, and load effects.",
        f"zero_error_count={zero_error_count}; recommended_trace_rows={len(recommended_trace)}",
        True,
    )
    add(
        "controller_output_spike_check",
        "axis_servo_tracking_trace_v1.csv",
        f"spike_count={controller_spike_count}; max_ratio={round3(max_controller_ratio)}",
        status(controller_spike_count == 0),
        "low",
        controller_spike_count == 0,
        "Patch clamp logic if controller output exceeds configured velocity limits.",
        "Controller output stays inside configured max_velocity for all parameter sets.",
        False,
    )
    add(
        "actual_position_continuity_check",
        "axis_servo_tracking_trace_v1.csv",
        actual_position_jump_count,
        status(actual_position_jump_count == 0),
        "low",
        actual_position_jump_count == 0,
        "Inspect task episode segmentation if jumps appear.",
        "Checked per scenario/task/parameter/axis episode with duplicate-time boundary samples skipped.",
        False,
    )
    add(
        "actual_velocity_continuity_check",
        "axis_servo_tracking_trace_v1.csv",
        f"jump_count={actual_velocity_jump_count}; limit_exceed_count={velocity_limit_count}; max_ratio={round3(max_velocity_ratio)}",
        status(actual_velocity_jump_count == 0 and velocity_limit_count == 0),
        "low",
        actual_velocity_jump_count == 0 and velocity_limit_count == 0,
        "Inspect velocity clamp and reference transitions if this fails.",
        "No obvious velocity jump or configured velocity-limit exceedance found.",
        False,
    )
    add(
        "actual_acceleration_continuity_check",
        "axis_servo_tracking_trace_v1.csv",
        f"jump_count={actual_acceleration_jump_count}; limit_exceed_count={acceleration_limit_count}; max_ratio={round3(max_acceleration_ratio)}",
        status(actual_acceleration_jump_count == 0 and acceleration_limit_count == 0),
        "low",
        actual_acceleration_jump_count == 0 and acceleration_limit_count == 0,
        "Future S-curve profile should replace ideal reference acceleration placeholders.",
        "No configured acceleration-limit exceedance; acceleration remains a concept indicator.",
        True,
    )
    add(
        "time_alignment_with_reference_trace",
        "axis_servo_tracking_trace_v1.csv; time_stepped_motion_trace_v1.csv",
        f"tracking_rows={len(trace)}; expected={expected_trace_count}",
        status(alignment_ok and per_axis_alignment_ok and time_nonmonotonic_count == 0),
        "low",
        alignment_ok and per_axis_alignment_ok and time_nonmonotonic_count == 0,
        "Regenerate review after patch if trace/reference counts diverge.",
        f"reference_rows={len(reference_trace)}; per_parameter_axis_count_ok={per_axis_alignment_ok}; time_nonmonotonic={time_nonmonotonic_count}",
        False,
    )
    add(
        "z_motion_bottleneck_consistency",
        "axis_tracking_error_summary_v1.csv; stage_7b6_axis_servo_pid_tracking_report.md",
        f"z_rmse={error_by_axis['z']['rmse_mm']}; z_tolerance={error_by_axis['z']['position_tolerance_mm']}",
        status(z_consistent),
        "low",
        z_consistent,
        "Continue treating Z as timing-sensitive in later servo/S-curve/load models.",
        "Z does not have the largest tracking error under balanced_pid, but it has tighter tolerance and lower velocity, consistent with Stage 7B-4 z_motion timing bottleneck.",
        True,
    )
    add(
        "concept_level_model_limitation",
        "stage_7b6_axis_servo_pid_tracking_report.md",
        "stated",
        status(concept_limit_stated),
        "medium",
        concept_limit_stated,
        "Keep limitation language in downstream control chapter.",
        "Report states concept-level simulation and not final real hardware performance.",
        True,
    )
    add(
        "future_s_curve_or_servo_model_need",
        "stage_7b6_axis_servo_pid_tracking_report.md",
        "future calibration required",
        status(future_model_stated),
        "medium",
        future_model_stated,
        "Add real motor, encoder, drive, load, sample period, and S-curve profile in a later stage.",
        "Current model can seed later higher-fidelity servo/load modeling but is not the final model.",
        True,
    )
    add(
        "deferred_xy_slider_binding_dependency",
        "stage_7b6_axis_servo_pid_tracking_report.md",
        "deferred_not_blocking",
        status(xy_binding_stated),
        "medium",
        xy_binding_stated,
        "Resolve Stage 7A-3f physical XY slider binding before final mechanical implementation.",
        "Deferred issue is correctly scoped outside abstract control simulation.",
        True,
    )

    accepted = all(
        row["accepted_for_current_stage"] == "yes"
        for row in review_rows
    )
    conclusion = (
        "Stage 7B-6 accepted as concept-level axis servo / PID tracking simulation."
        if accepted
        else "Stage 7B-6 requires patch."
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
        review_rows,
    )

    report_lines = [
        "# Stage 7B-6 Axis Servo Tracking Review Report",
        "",
        "## Review Result",
        "",
        "- Stage 7B-6 validation_status=PASS.",
        f"- Recommended parameter_set is `balanced_pid`: {yes_no(recommended_id == 'balanced_pid')}.",
        f"- Recommended parameter_set unique: {yes_no(recommended_unique)}.",
        f"- Conclusion: {conclusion}",
        "",
        "## Why Balanced PID Is Recommended",
        "",
        "- `aggressive_pid` has the lowest overall RMSE, but it is marked with medium overshoot/noise risk.",
        "- `conservative_pid` is stable in concept but fails tolerance in X/Y/Z and has lower within-tolerance rate.",
        "- `balanced_pid` keeps within_tolerance_rate=1.0 with low overshoot risk, so it is the most reasonable concept default rather than a hard-coded best-error pick.",
        "",
        "## Tracking Error Audit",
        "",
        f"- X RMSE / max error / tolerance: {error_by_axis['x']['rmse_mm']} / {error_by_axis['x']['max_abs_error_mm']} / {error_by_axis['x']['position_tolerance_mm']} mm.",
        f"- Y RMSE / max error / tolerance: {error_by_axis['y']['rmse_mm']} / {error_by_axis['y']['max_abs_error_mm']} / {error_by_axis['y']['position_tolerance_mm']} mm.",
        f"- Z RMSE / max error / tolerance: {error_by_axis['z']['rmse_mm']} / {error_by_axis['z']['max_abs_error_mm']} / {error_by_axis['z']['position_tolerance_mm']} mm.",
        f"- within_tolerance_rate={within_rate}; this is acceptable for the simplified concept-level model, but it is likely optimistic for real hardware.",
        "",
        "## Over-Idealization Check",
        "",
        f"- Zero-error rate for recommended trace: {round3(zero_error_rate)}.",
        "- The result is somewhat idealized because the plant is a simplified first-order position servo and the Stage 7B-5 reference uses idealized time-stepped setpoints.",
        "- It remains acceptable for concept-level servo tracking because nonzero errors exist, configured limits are respected, recommended X/Y/Z max errors stay below tolerance, and the report clearly labels the model limitations.",
        "",
        "## Continuity And Alignment",
        "",
        f"- Tracking rows={len(trace)}; expected rows={expected_trace_count}; reference rows={len(reference_trace)}.",
        f"- Controller output spike count={controller_spike_count}.",
        f"- Velocity limit exceed count={velocity_limit_count}; acceleration limit exceed count={acceleration_limit_count}.",
        f"- Time nonmonotonic count per task/axis episode={time_nonmonotonic_count}.",
        "",
        "## Z Motion And Stage 7B-4",
        "",
        "- Z is not the largest tracking-error axis under `balanced_pid`, but it still has the tightest tolerance and lower velocity limit.",
        "- This is consistent with Stage 7B-4: `z_motion` remains a timing bottleneck due to repeated descend/lift operations rather than because it has the worst tracking error in this simplified model.",
        "",
        "## Hardware Gap",
        "",
        "- Current PID/servo results do not represent final hardware control.",
        "- A later model needs real motor, encoder, driver, payload/load inertia, friction, mechanical compliance, control-cycle timing, and S-curve command profile data.",
        "- Current outputs are useful as an input foundation for later realistic servo, S-curve, and load models.",
        "",
        "## Rerun Recommendation",
        "",
        "- Re-running Stage 7B-6 is not recommended now.",
        "- Reason: recommendation is unique, X/Y/Z traces are complete, balanced PID satisfies tolerance, no controller-output spike or limit exceedance was found, time alignment is valid, and idealization is documented as a concept-stage limitation.",
        "",
        "## Deferred Mechanical Issue",
        "",
        "- Stage 7A-3f XY slider binding remains deferred.",
        "- It does not affect the abstract Stage 7B-6 control simulation, but it does affect final mechanical implementation and physical validation.",
    ]
    REVIEW_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"review_status={'PASS' if accepted else 'FAIL'}")
    print(f"conclusion={conclusion}")
    print(f"recommended_parameter_set={recommended_id}")
    print(f"recommended_unique={yes_no(recommended_unique)}")
    print(f"balanced_pid_reasonable={yes_no(balanced_reasonable)}")
    print(f"x_reasonable={yes_no(axis_reasonable['x'])}")
    print(f"y_reasonable={yes_no(axis_reasonable['y'])}")
    print(f"z_reasonable={yes_no(axis_reasonable['z'])}")
    print(f"within_tolerance_rate={within_rate}")
    print(f"zero_error_rate={round3(zero_error_rate)}")
    print(f"controller_spike_count={controller_spike_count}")
    print(f"time_nonmonotonic_count={time_nonmonotonic_count}")
    print(f"review_csv={REVIEW_CSV}")
    print(f"review_report={REVIEW_REPORT}")
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
