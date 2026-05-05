from __future__ import annotations

import csv
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = ROOT / "04_simulation" / "task_planning"
FIGURE_DIR = TASK_DIR / "figures"
REPORT_DIR = ROOT / "reports"

TRAJECTORY_CSV = TASK_DIR / "multi_box_pick_scan_place_trajectory_v1.csv"
MOTION_SUMMARY_CSV = TASK_DIR / "multi_box_motion_summary_v1.csv"
EVENT_SUMMARY_CSV = TASK_DIR / "multi_box_trajectory_event_summary_v1.csv"
POLICY_SIM_CSV = TASK_DIR / "multi_box_sorting_policy_simulation_v1.csv"
PENDING_QUEUE_CSV = TASK_DIR / "multi_box_pending_queue_v1.csv"
OPERATOR_EVENTS_CSV = TASK_DIR / "multi_box_operator_events_v1.csv"
POLICY_SUMMARY_CSV = TASK_DIR / "multi_box_sorting_policy_summary_v1.csv"

CYCLE_TIME_CSV = TASK_DIR / "multi_box_cycle_time_estimate_v1.csv"
BATCH_SUMMARY_CSV = TASK_DIR / "multi_box_batch_throughput_summary_v1.csv"
CATEGORY_SUMMARY_CSV = TASK_DIR / "multi_box_category_throughput_summary_v1.csv"
CYCLE_PER_SAMPLE_FIGURE = FIGURE_DIR / "multi_box_cycle_time_per_sample_v1.png"
CYCLE_BREAKDOWN_FIGURE = FIGURE_DIR / "multi_box_cycle_time_breakdown_v1.png"
THROUGHPUT_COMPARISON_FIGURE = FIGURE_DIR / "multi_box_batch_throughput_comparison_v1.png"
CATEGORY_CYCLE_FIGURE = FIGURE_DIR / "multi_box_category_cycle_time_v1.png"
HOLD_IMPACT_FIGURE = FIGURE_DIR / "multi_box_hold_impact_v1.png"
REPORT_PATH = REPORT_DIR / "stage_7e_multi_box_cycle_time_throughput_report.md"

XY_SPEED_MM_PER_S = 320.0
Z_SPEED_MM_PER_S = 180.0
PICK_ACTION_TIME_S = 0.8
PLACE_ACTION_TIME_S = 0.8
SCAN_ACTION_TIME_S = 0.55
GRIPPER_OPEN_CLOSE_TIME_S = 0.25
SETTLE_TIME_S = 0.15
CATEGORY_HOLD_DECISION_OVERHEAD_S = 0.10
PENDING_QUEUE_ENQUEUE_TIME_S = 0.05
PENDING_QUEUE_RELEASE_TIME_S = 0.05
OPERATOR_CLEAR_OUTPUT_BOX_TIME_S = 12.0
OPERATOR_CLEAR_MANUAL_REVIEW_TIME_S = 15.0
ALARM_RESPONSE_TIME_S = 20.0
TOTAL_MANIFEST_SAMPLES = 96


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def grouped_trajectory_rows() -> dict[tuple[str, str], list[dict[str, str]]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(TRAJECTORY_CSV):
        grouped[(row["run_id"], row["sample_id"])].append(row)
    return grouped


def manifest_info_from_motion_summary() -> dict[tuple[str, str], dict[str, str]]:
    info: dict[tuple[str, str], dict[str, str]] = {}
    for row in read_csv(MOTION_SUMMARY_CSV):
        key = (row["run_id"], row["sample_id"])
        current = info.get(key)
        if current is None or row["final_status"] != "queued_pending":
            info[key] = row
    return info


def distance_and_motion_time(rows: list[dict[str, str]]) -> tuple[float, float, float]:
    xy_distance = 0.0
    z_distance = 0.0
    motion_time = 0.0
    for previous, current in zip(rows, rows[1:]):
        dx = float(current["x_mm"]) - float(previous["x_mm"])
        dy = float(current["y_mm"]) - float(previous["y_mm"])
        dz = float(current["z_mm"]) - float(previous["z_mm"])
        xy = math.hypot(dx, dy)
        z = abs(dz)
        xy_distance += xy
        z_distance += z
        motion_time += max(xy / XY_SPEED_MM_PER_S, z / Z_SPEED_MM_PER_S)
    return xy_distance, z_distance, motion_time


def pending_release_counts() -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in read_csv(PENDING_QUEUE_CSV):
        if row["released_at_step"]:
            counts[row["run_id"]] += 1
    return counts


def cycle_rows() -> list[dict[str, object]]:
    grouped = grouped_trajectory_rows()
    info = manifest_info_from_motion_summary()
    release_counts = pending_release_counts()
    rows: list[dict[str, object]] = []

    for (run_id, sample_id), points in grouped.items():
        sample = info[(run_id, sample_id)]
        states = [row["state"] for row in points]
        expected_results = [row["expected_result"] for row in points]
        pending_actions = [row["pending_queue_action"] for row in points]
        xy_distance, z_distance, motion_time = distance_and_motion_time(points)

        pick_count = states.count("PICK_TUBE")
        place_count = states.count("PLACE_TUBE")
        scan_count = states.count("SCAN_BARCODE")
        pick_time = pick_count * (PICK_ACTION_TIME_S + GRIPPER_OPEN_CLOSE_TIME_S + SETTLE_TIME_S)
        scan_time = scan_count * SCAN_ACTION_TIME_S
        place_time = place_count * (PLACE_ACTION_TIME_S + GRIPPER_OPEN_CLOSE_TIME_S + SETTLE_TIME_S)

        is_queued = any(action == "queued" or result == "queued_pending" for action, result in zip(pending_actions, expected_results))
        is_resumed = any(action == "released" for action in pending_actions)
        is_paused = "PAUSE_ALARM" in states
        queue_wait_time = 0.0
        operator_wait_time = 0.0
        alarm_wait_time = 0.0
        notes = []

        if "HOLD_CATEGORY" in states:
            queue_wait_time += CATEGORY_HOLD_DECISION_OVERHEAD_S
            notes.append("category_hold decision")
        if is_queued:
            queue_wait_time += PENDING_QUEUE_ENQUEUE_TIME_S
            notes.append("queued")
        if is_resumed:
            queue_wait_time += PENDING_QUEUE_RELEASE_TIME_S
            count = max(1, release_counts[run_id])
            operator_wait_time += OPERATOR_CLEAR_OUTPUT_BOX_TIME_S / count
            notes.append("resumed; operator clear output wait distributed across pending samples")
        if is_paused:
            operator_wait_time += OPERATOR_CLEAR_MANUAL_REVIEW_TIME_S
            alarm_wait_time += ALARM_RESPONSE_TIME_S
            notes.append("paused at manual_review_full alarm")
        if sample["is_abnormal"] == "yes":
            notes.append("abnormal")

        total_cycle = motion_time + pick_time + scan_time + place_time + queue_wait_time + operator_wait_time + alarm_wait_time
        final_point = points[-1]
        rows.append(
            {
                "run_id": run_id,
                "sample_id": sample_id,
                "category": sample["category"],
                "barcode_status": sample["barcode_status"],
                "is_abnormal": sample["is_abnormal"],
                "input_box_id": sample["input_box_id"],
                "input_slot_id": sample["input_slot_id"],
                "target_zone": final_point["target_zone"],
                "target_box_id": final_point["target_box_id"],
                "target_slot_id": final_point["target_slot_id"],
                "num_waypoints": len(points),
                "xy_distance_mm": f"{xy_distance:.3f}",
                "z_distance_mm": f"{z_distance:.3f}",
                "motion_time_s": f"{motion_time:.3f}",
                "pick_time_s": f"{pick_time:.3f}",
                "scan_time_s": f"{scan_time:.3f}",
                "place_time_s": f"{place_time:.3f}",
                "queue_wait_time_s": f"{queue_wait_time:.3f}",
                "operator_wait_time_s": f"{operator_wait_time:.3f}",
                "alarm_wait_time_s": f"{alarm_wait_time:.3f}",
                "total_cycle_time_s": f"{total_cycle:.3f}",
                "final_status": "pause_alarm" if is_paused else final_point["expected_result"],
                "notes": "; ".join(notes) if notes else "normal completed trajectory",
            }
        )
    return rows


def float_field(row: dict[str, object], field: str) -> float:
    return float(row[field])


def bottleneck_stage(rows: list[dict[str, object]]) -> str:
    totals = {
        "motion": sum(float_field(row, "motion_time_s") for row in rows),
        "scan": sum(float_field(row, "scan_time_s") for row in rows),
        "operator_wait": sum(float_field(row, "operator_wait_time_s") for row in rows),
        "alarm_pause": sum(float_field(row, "alarm_wait_time_s") for row in rows),
    }
    return max(totals, key=totals.get)


def median(values: list[float]) -> float:
    return statistics.median(values) if values else 0.0


def batch_summary_rows(cycles: list[dict[str, object]]) -> list[dict[str, object]]:
    by_run: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in cycles:
        by_run[str(row["run_id"])].append(row)
    rows: list[dict[str, object]] = []
    for run_id in ["baseline_multi_box_run", "forced_category_A_full", "forced_manual_review_full"]:
        run_rows = by_run[run_id]
        completed_rows = [row for row in run_rows if row["final_status"] in {"placed_output", "placed_manual_review"}]
        paused_rows = [row for row in run_rows if row["final_status"] == "pause_alarm"]
        total_motion = sum(float_field(row, "motion_time_s") for row in run_rows)
        total_pick = sum(float_field(row, "pick_time_s") for row in run_rows)
        total_scan = sum(float_field(row, "scan_time_s") for row in run_rows)
        total_place = sum(float_field(row, "place_time_s") for row in run_rows)
        total_queue = sum(float_field(row, "queue_wait_time_s") for row in run_rows)
        total_operator = sum(float_field(row, "operator_wait_time_s") for row in run_rows)
        total_alarm = sum(float_field(row, "alarm_wait_time_s") for row in run_rows)
        total_batch = sum(float_field(row, "total_cycle_time_s") for row in run_rows)
        cycle_times = [float_field(row, "total_cycle_time_s") for row in run_rows]
        completed_count = len(completed_rows)
        estimated_sph = completed_count / total_batch * 3600.0 if total_batch else 0.0
        rows.append(
            {
                "run_id": run_id,
                "total_samples_in_manifest": TOTAL_MANIFEST_SAMPLES,
                "processed_sample_count": len(run_rows),
                "completed_sample_count": completed_count,
                "abnormal_sample_count": sum(1 for row in run_rows if row["is_abnormal"] == "yes"),
                "queued_sample_count": sum(1 for row in run_rows if "queued" in str(row["notes"])),
                "resumed_sample_count": sum(1 for row in run_rows if "resumed" in str(row["notes"])),
                "paused_sample_count": len(paused_rows),
                "total_waypoints": sum(int(row["num_waypoints"]) for row in run_rows),
                "total_motion_time_s": f"{total_motion:.3f}",
                "total_non_motion_time_s": f"{(total_pick + total_scan + total_place + total_queue + total_operator + total_alarm):.3f}",
                "total_operator_wait_time_s": f"{total_operator:.3f}",
                "total_alarm_wait_time_s": f"{total_alarm:.3f}",
                "total_batch_time_s": f"{total_batch:.3f}",
                "average_cycle_time_s": f"{(total_batch / len(run_rows) if run_rows else 0.0):.3f}",
                "median_cycle_time_s": f"{median(cycle_times):.3f}",
                "max_cycle_time_s": f"{(max(cycle_times) if cycle_times else 0.0):.3f}",
                "estimated_samples_per_hour": f"{estimated_sph:.3f}",
                "bottleneck_stage": bottleneck_stage(run_rows),
                "notes": notes_for_run(run_id),
            }
        )
    return rows


def notes_for_run(run_id: str) -> str:
    if run_id == "baseline_multi_box_run":
        return "full 96-sample baseline; no alarm"
    if run_id == "forced_category_A_full":
        return "includes Category A hold, pending queue, operator clear, and resume"
    return "stops at manual_review_full PAUSE_ALARM"


def category_summary_rows(cycles: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in cycles:
        category = str(row["category"])
        if category.startswith("Category ") and row["is_abnormal"] == "no":
            grouped[(str(row["run_id"]), category)].append(row)
    rows: list[dict[str, object]] = []
    for run_id in ["baseline_multi_box_run", "forced_category_A_full", "forced_manual_review_full"]:
        for category in ["Category A", "Category B", "Category C", "Category D"]:
            run_rows = grouped.get((run_id, category), [])
            total = sum(float_field(row, "total_cycle_time_s") for row in run_rows)
            rows.append(
                {
                    "run_id": run_id,
                    "category": category,
                    "sample_count": len(run_rows),
                    "completed_count": sum(1 for row in run_rows if row["final_status"] == "placed_output"),
                    "queued_count": sum(1 for row in run_rows if "queued" in str(row["notes"])),
                    "resumed_count": sum(1 for row in run_rows if "resumed" in str(row["notes"])),
                    "average_cycle_time_s": f"{(total / len(run_rows) if run_rows else 0.0):.3f}",
                    "total_processing_time_s": f"{total:.3f}",
                    "notes": "abnormal samples excluded from category throughput",
                }
            )
    return rows


def plot_figures(cycles: list[dict[str, object]], batch_rows: list[dict[str, object]], category_rows: list[dict[str, object]]) -> list[str]:
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        return [f"matplotlib unavailable: {exc}"]
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[str] = []

    baseline = [row for row in cycles if row["run_id"] == "baseline_multi_box_run"]
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(range(1, len(baseline) + 1), [float_field(row, "total_cycle_time_s") for row in baseline], color="#377eb8")
    ax.set_title("Baseline Multi-box Cycle Time per Sample")
    ax.set_xlabel("sample order")
    ax.set_ylabel("cycle time s")
    fig.tight_layout()
    fig.savefig(CYCLE_PER_SAMPLE_FIGURE, dpi=180)
    plt.close(fig)
    outputs.append(str(CYCLE_PER_SAMPLE_FIGURE))

    breakdown_fields = ["motion_time_s", "pick_time_s", "scan_time_s", "place_time_s"]
    breakdown_values = [sum(float_field(row, field) for row in baseline) for field in breakdown_fields]
    other = sum(float_field(row, "queue_wait_time_s") + float_field(row, "operator_wait_time_s") + float_field(row, "alarm_wait_time_s") for row in baseline)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(["motion", "pick", "scan", "place", "other"], breakdown_values + [other], color=["#4daf4a", "#984ea3", "#ff7f00", "#a65628", "#999999"])
    ax.set_title("Baseline Cycle Time Breakdown")
    ax.set_ylabel("total time s")
    fig.tight_layout()
    fig.savefig(CYCLE_BREAKDOWN_FIGURE, dpi=180)
    plt.close(fig)
    outputs.append(str(CYCLE_BREAKDOWN_FIGURE))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    run_labels = [row["run_id"] for row in batch_rows]
    axes[0].bar(run_labels, [float(row["total_batch_time_s"]) for row in batch_rows], color="#377eb8")
    axes[0].set_title("Batch Time")
    axes[0].set_ylabel("seconds")
    axes[0].tick_params(axis="x", rotation=20)
    axes[1].bar(run_labels, [float(row["estimated_samples_per_hour"]) for row in batch_rows], color="#4daf4a")
    axes[1].set_title("Estimated Throughput")
    axes[1].set_ylabel("samples/hour")
    axes[1].tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(THROUGHPUT_COMPARISON_FIGURE, dpi=180)
    plt.close(fig)
    outputs.append(str(THROUGHPUT_COMPARISON_FIGURE))

    baseline_categories = [row for row in category_rows if row["run_id"] == "baseline_multi_box_run"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([row["category"] for row in baseline_categories], [float(row["average_cycle_time_s"]) for row in baseline_categories], color=["#7b3294", "#d8b365", "#4393c3", "#d6604d"])
    ax.set_title("Baseline Category Average Cycle Time")
    ax.set_ylabel("seconds")
    fig.tight_layout()
    fig.savefig(CATEGORY_CYCLE_FIGURE, dpi=180)
    plt.close(fig)
    outputs.append(str(CATEGORY_CYCLE_FIGURE))

    forced = [row for row in cycles if row["run_id"] == "forced_category_A_full" and row["is_abnormal"] == "no"]
    queued = [float_field(row, "total_cycle_time_s") for row in forced if "resumed" in str(row["notes"])]
    nonqueued = [float_field(row, "total_cycle_time_s") for row in forced if "resumed" not in str(row["notes"]) and row["final_status"] == "placed_output"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(["non-queued", "queued/resumed"], [statistics.mean(nonqueued) if nonqueued else 0.0, statistics.mean(queued) if queued else 0.0], color=["#377eb8", "#d95f02"])
    ax.set_title("Category Hold Impact on Cycle Time")
    ax.set_ylabel("average cycle time s")
    fig.tight_layout()
    fig.savefig(HOLD_IMPACT_FIGURE, dpi=180)
    plt.close(fig)
    outputs.append(str(HOLD_IMPACT_FIGURE))
    return outputs


def write_report(batch_rows: list[dict[str, object]], category_rows: list[dict[str, object]], figures: list[str]) -> None:
    by_run = {row["run_id"]: row for row in batch_rows}
    baseline = by_run["baseline_multi_box_run"]
    forced_a = by_run["forced_category_A_full"]
    forced_alarm = by_run["forced_manual_review_full"]
    figure_text = ", ".join(Path(path).relative_to(ROOT).as_posix() if Path(path).is_file() else path for path in figures)
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Stage 7E Multi-box Cycle Time and Throughput Report",
                "",
                "- Goal: estimate multi-box cycle time and throughput from Stage 7D trajectories.",
                f"- Input files: `{TRAJECTORY_CSV.relative_to(ROOT).as_posix()}`, `{MOTION_SUMMARY_CSV.relative_to(ROOT).as_posix()}`, `{EVENT_SUMMARY_CSV.relative_to(ROOT).as_posix()}`, `{POLICY_SIM_CSV.relative_to(ROOT).as_posix()}`, `{OPERATOR_EVENTS_CSV.relative_to(ROOT).as_posix()}`.",
                "- Time model: XY speed 320 mm/s, Z speed 180 mm/s, pick 0.8 s, place 0.8 s, scan 0.55 s, gripper open/close 0.25 s, settle 0.15 s, operator output clear 12 s, manual-review clear 15 s, alarm response 20 s.",
                f"- Baseline: total_batch_time_s={baseline['total_batch_time_s']}, average_cycle_time_s={baseline['average_cycle_time_s']}, estimated_samples_per_hour={baseline['estimated_samples_per_hour']}, bottleneck={baseline['bottleneck_stage']}.",
                f"- Forced Category A full: total_batch_time_s={forced_a['total_batch_time_s']}, queued={forced_a['queued_sample_count']}, resumed={forced_a['resumed_sample_count']}; operator clear/resume adds 12 s total distributed across pending samples.",
                f"- Forced manual review full: processed={forced_alarm['processed_sample_count']}, completed={forced_alarm['completed_sample_count']}, paused={forced_alarm['paused_sample_count']}; PAUSE_ALARM adds manual-review clear and alarm response time.",
                "- Category-level comparison excludes abnormal samples from normal A/B/C/D throughput.",
                f"- Figures: {figure_text}",
                "",
                "## Bottleneck Analysis",
                "",
                f"- Baseline bottleneck: {baseline['bottleneck_stage']}.",
                f"- Category hold scenario bottleneck: {forced_a['bottleneck_stage']}.",
                f"- Manual review full scenario bottleneck: {forced_alarm['bottleneck_stage']}.",
                "",
                "## Limits",
                "",
                "- No dynamics, acceleration limits, or PID response are modeled yet.",
                "- Speeds and operator response times are engineering estimates.",
                "- No parallel handling, path optimization, or collision timing is included.",
                "",
                "## Next Steps",
                "",
                "- Stage 7F: Multi-box animation update.",
                "- Stage 8A: Kinematics and PID control simulation.",
                "- Stage 8B: Trajectory-to-control interface.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    cycles = cycle_rows()
    batch_rows = batch_summary_rows(cycles)
    category_rows = category_summary_rows(cycles)
    figures = plot_figures(cycles, batch_rows, category_rows)
    write_report(batch_rows, category_rows, figures)

    write_csv(
        CYCLE_TIME_CSV,
        cycles,
        ["run_id", "sample_id", "category", "barcode_status", "is_abnormal", "input_box_id", "input_slot_id", "target_zone", "target_box_id", "target_slot_id", "num_waypoints", "xy_distance_mm", "z_distance_mm", "motion_time_s", "pick_time_s", "scan_time_s", "place_time_s", "queue_wait_time_s", "operator_wait_time_s", "alarm_wait_time_s", "total_cycle_time_s", "final_status", "notes"],
    )
    write_csv(
        BATCH_SUMMARY_CSV,
        batch_rows,
        ["run_id", "total_samples_in_manifest", "processed_sample_count", "completed_sample_count", "abnormal_sample_count", "queued_sample_count", "resumed_sample_count", "paused_sample_count", "total_waypoints", "total_motion_time_s", "total_non_motion_time_s", "total_operator_wait_time_s", "total_alarm_wait_time_s", "total_batch_time_s", "average_cycle_time_s", "median_cycle_time_s", "max_cycle_time_s", "estimated_samples_per_hour", "bottleneck_stage", "notes"],
    )
    write_csv(
        CATEGORY_SUMMARY_CSV,
        category_rows,
        ["run_id", "category", "sample_count", "completed_count", "queued_count", "resumed_count", "average_cycle_time_s", "total_processing_time_s", "notes"],
    )

    by_run = {row["run_id"]: row for row in batch_rows}
    baseline = by_run["baseline_multi_box_run"]
    forced_a = by_run["forced_category_A_full"]
    forced_alarm = by_run["forced_manual_review_full"]
    print(f"baseline_total_batch_time_s={baseline['total_batch_time_s']}")
    print(f"baseline_average_cycle_time_s={baseline['average_cycle_time_s']}")
    print(f"baseline_estimated_samples_per_hour={baseline['estimated_samples_per_hour']}")
    print(f"forced_category_A_full_total_batch_time_s={forced_a['total_batch_time_s']}")
    print(f"forced_category_A_full_queued={forced_a['queued_sample_count']}")
    print(f"forced_category_A_full_resumed={forced_a['resumed_sample_count']}")
    print(f"forced_manual_review_full_processed={forced_alarm['processed_sample_count']}")
    print(f"forced_manual_review_full_paused={forced_alarm['paused_sample_count']}")
    print(f"baseline_bottleneck_stage={baseline['bottleneck_stage']}")
    print(f"cycle_time_csv={CYCLE_TIME_CSV}")
    print(f"batch_summary_csv={BATCH_SUMMARY_CSV}")
    print(f"category_summary_csv={CATEGORY_SUMMARY_CSV}")
    print(f"report={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
