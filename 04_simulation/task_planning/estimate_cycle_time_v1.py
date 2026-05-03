from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = ROOT / "04_simulation" / "task_planning"
REPORT_DIR = ROOT / "reports"
FIGURE_DIR = TASK_DIR / "figures"

TRAJECTORY_CSV = TASK_DIR / "pick_scan_place_trajectory_v1.csv"
MOTION_SUMMARY_CSV = TASK_DIR / "sorting_motion_summary_v1.csv"
WORKSPACE_CHECK_CSV = TASK_DIR / "trajectory_workspace_check_v1.csv"
HEIGHT_RULES_MD = TASK_DIR / "pick_place_height_rules_v1.md"

CYCLE_TIME_CSV = TASK_DIR / "cycle_time_estimate_v1.csv"
BATCH_SUMMARY_CSV = TASK_DIR / "batch_throughput_summary_v1.csv"
CYCLE_TIME_FIGURE = FIGURE_DIR / "cycle_time_per_sample_v1.png"
BREAKDOWN_FIGURE = FIGURE_DIR / "cycle_time_breakdown_v1.png"
REPORT_PATH = REPORT_DIR / "stage_6c_cycle_time_throughput_report.md"

MODEL = {
    "xy_speed_mm_s": 300.0,
    "z_speed_mm_s": 120.0,
    "gripper_close_s": 0.8,
    "gripper_open_s": 0.6,
    "barcode_scan_s": 1.2,
    "classify_decision_s": 0.2,
    "settle_time_per_pick_s": 0.3,
    "settle_time_per_place_s": 0.3,
    "manual_review_extra_s": 0.5,
}
ASSUMPTIONS_VERSION = "stage_6c_initial_v1"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def group_by_sample(trajectory_rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in trajectory_rows:
        grouped[row["sample_id"]].append(row)
    for rows in grouped.values():
        rows.sort(key=lambda item: int(item["step_order"]))
    return dict(grouped)


def distance_components(rows: list[dict[str, str]]) -> tuple[float, float]:
    xy_total = 0.0
    z_total = 0.0
    previous: tuple[float, float, float] | None = None
    for row in rows:
        current = (float(row["x_mm"]), float(row["y_mm"]), float(row["z_mm"]))
        if previous is not None:
            xy_total += math.dist(previous[:2], current[:2])
            z_total += abs(current[2] - previous[2])
        previous = current
    return xy_total, z_total


def motion_time_s(xy_distance_mm: float, z_distance_mm: float) -> float:
    return xy_distance_mm / MODEL["xy_speed_mm_s"] + z_distance_mm / MODEL["z_speed_mm_s"]


def gripper_time_s(rows: list[dict[str, str]]) -> float:
    close_count = sum(1 for row in rows if row["gripper_action"] == "close")
    open_place_count = sum(1 for row in rows if row["state"] == "PLACE_TUBE" and row["gripper_action"] == "open")
    return close_count * MODEL["gripper_close_s"] + open_place_count * MODEL["gripper_open_s"]


def scan_time_s(rows: list[dict[str, str]]) -> float:
    return sum(1 for row in rows if row["scanner_action"] == "trigger_scan") * MODEL["barcode_scan_s"]


def decision_time_s(rows: list[dict[str, str]]) -> float:
    return sum(1 for row in rows if row["state"] == "SCAN_BARCODE") * MODEL["classify_decision_s"]


def settle_time_s(rows: list[dict[str, str]]) -> float:
    pick_count = sum(1 for row in rows if row["state"] == "PICK_TUBE")
    place_count = sum(1 for row in rows if row["state"] == "PLACE_TUBE")
    return pick_count * MODEL["settle_time_per_pick_s"] + place_count * MODEL["settle_time_per_place_s"]


def estimate_cycles(grouped: dict[str, list[dict[str, str]]], motion_summary_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    summary_by_sample = {row["sample_id"]: row for row in motion_summary_rows}
    rows = []
    for sample_id, waypoints in grouped.items():
        summary = summary_by_sample[sample_id]
        xy_distance, z_distance = distance_components(waypoints)
        motion = motion_time_s(xy_distance, z_distance)
        gripper = gripper_time_s(waypoints)
        scan = scan_time_s(waypoints)
        decision = decision_time_s(waypoints)
        settle = settle_time_s(waypoints)
        manual_extra = MODEL["manual_review_extra_s"] if summary["uses_manual_review"] == "yes" else 0.0
        total = motion + gripper + scan + decision + settle + manual_extra
        rows.append(
            {
                "sample_id": sample_id,
                "input_slot": summary["input_slot"],
                "target_zone": summary["target_zone"],
                "target_slot": summary["target_slot"],
                "tube_height_mm": summary["tube_height_mm"],
                "barcode_status": summary["barcode_status"],
                "category": summary["category"],
                "num_waypoints": len(waypoints),
                "xy_distance_mm": f"{xy_distance:.3f}",
                "z_distance_mm": f"{z_distance:.3f}",
                "motion_time_s": f"{motion:.3f}",
                "gripper_time_s": f"{gripper:.3f}",
                "scan_time_s": f"{scan:.3f}",
                "decision_time_s": f"{decision:.3f}",
                "settle_time_s": f"{settle:.3f}",
                "manual_review_extra_s": f"{manual_extra:.3f}",
                "total_cycle_time_s": f"{total:.3f}",
                "notes": "manual review path includes extra handling time" if manual_extra else "normal category path",
            }
        )
    return rows


def bottleneck_action(cycle_rows: list[dict[str, object]]) -> str:
    totals = {
        "motion": sum(float(row["motion_time_s"]) for row in cycle_rows),
        "gripper": sum(float(row["gripper_time_s"]) for row in cycle_rows),
        "scan": sum(float(row["scan_time_s"]) for row in cycle_rows),
        "decision": sum(float(row["decision_time_s"]) for row in cycle_rows),
        "settle": sum(float(row["settle_time_s"]) for row in cycle_rows),
        "manual_review_extra": sum(float(row["manual_review_extra_s"]) for row in cycle_rows),
    }
    return max(totals, key=totals.get)


def batch_summary(cycle_rows: list[dict[str, object]], trajectory_rows: list[dict[str, str]], motion_summary_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    sample_count = len(cycle_rows)
    totals = [float(row["total_cycle_time_s"]) for row in cycle_rows]
    total_batch_time = sum(totals)
    manual_review_count = sum(1 for row in motion_summary_rows if row["uses_manual_review"] == "yes")
    normal_count = sample_count - manual_review_count
    samples_per_hour = sample_count / (total_batch_time / 3600.0) if total_batch_time else 0.0
    rows = [
        ("sample_count", sample_count, "samples", "number of manifest samples"),
        ("total_waypoints", len(trajectory_rows), "waypoints", "generated Stage 6B trajectory waypoints"),
        ("total_batch_time_s", f"{total_batch_time:.3f}", "s", "sum of estimated sample cycle times"),
        ("total_batch_time_min", f"{total_batch_time / 60.0:.3f}", "min", "sum of estimated sample cycle times"),
        ("average_cycle_time_s", f"{total_batch_time / sample_count:.3f}", "s/sample", "mean cycle time"),
        ("max_cycle_time_s", f"{max(totals):.3f}", "s", "slowest sample"),
        ("min_cycle_time_s", f"{min(totals):.3f}", "s", "fastest sample"),
        ("normal_sample_count", normal_count, "samples", "samples routed to category bins"),
        ("manual_review_sample_count", manual_review_count, "samples", "samples routed to manual review"),
        ("estimated_samples_per_hour", f"{samples_per_hour:.3f}", "samples/hour", "ideal continuous throughput estimate"),
        ("bottleneck_action", bottleneck_action(cycle_rows), "category", "largest aggregate time component"),
        ("assumptions_version", ASSUMPTIONS_VERSION, "version", "initial engineering estimate"),
    ]
    return [{"metric": metric, "value": value, "unit": unit, "notes": notes} for metric, value, unit, notes in rows]


def make_figures(cycle_rows: list[dict[str, object]]) -> tuple[bool, list[str], str]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        return False, [], f"matplotlib unavailable: {type(exc).__name__}: {exc}"

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    labels = [str(row["sample_id"]) for row in cycle_rows]
    totals = [float(row["total_cycle_time_s"]) for row in cycle_rows]

    fig, ax = plt.subplots(figsize=(12, 5))
    colors = ["#c0392b" if float(row["manual_review_extra_s"]) > 0 else "#2c7fb8" for row in cycle_rows]
    ax.bar(labels, totals, color=colors)
    ax.set_title("Stage 6C Cycle Time Per Sample")
    ax.set_xlabel("Sample")
    ax.set_ylabel("Estimated cycle time (s)")
    ax.tick_params(axis="x", rotation=75)
    ax.grid(axis="y", linestyle=":", linewidth=0.7)
    fig.tight_layout()
    fig.savefig(CYCLE_TIME_FIGURE, dpi=180)
    plt.close(fig)

    components = [
        ("motion_time_s", "motion"),
        ("gripper_time_s", "gripper"),
        ("scan_time_s", "scan"),
        ("decision_time_s", "decision"),
        ("settle_time_s", "settle"),
        ("manual_review_extra_s", "manual review"),
    ]
    bottoms = [0.0] * len(cycle_rows)
    fig, ax = plt.subplots(figsize=(12, 5))
    for key, label in components:
        values = [float(row[key]) for row in cycle_rows]
        ax.bar(labels, values, bottom=bottoms, label=label)
        bottoms = [bottom + value for bottom, value in zip(bottoms, values)]
    ax.set_title("Stage 6C Cycle Time Breakdown")
    ax.set_xlabel("Sample")
    ax.set_ylabel("Estimated time (s)")
    ax.tick_params(axis="x", rotation=75)
    ax.legend(fontsize=8)
    ax.grid(axis="y", linestyle=":", linewidth=0.7)
    fig.tight_layout()
    fig.savefig(BREAKDOWN_FIGURE, dpi=180)
    plt.close(fig)

    return True, [CYCLE_TIME_FIGURE.relative_to(ROOT).as_posix(), BREAKDOWN_FIGURE.relative_to(ROOT).as_posix()], "generated"


def write_report(cycle_rows: list[dict[str, object]], batch_rows: list[dict[str, object]], figure_result: tuple[bool, list[str], str]) -> None:
    metrics = {row["metric"]: row["value"] for row in batch_rows}
    figure_ok, figure_paths, figure_note = figure_result
    params = ", ".join(f"{key}={value:g}" for key, value in MODEL.items())
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Stage 6C Cycle Time And Throughput Report",
                "",
                "## Inputs",
                "",
                f"- `{TRAJECTORY_CSV.relative_to(ROOT).as_posix()}`",
                f"- `{MOTION_SUMMARY_CSV.relative_to(ROOT).as_posix()}`",
                f"- `{WORKSPACE_CHECK_CSV.relative_to(ROOT).as_posix()}`",
                f"- `{HEIGHT_RULES_MD.relative_to(ROOT).as_posix()}`",
                "",
                "## Time Model",
                "",
                f"- Parameters: {params}",
                "- These are initial engineering estimates, not final controller or vendor timing values.",
                "",
                "## Results",
                "",
                f"- Sample count: {metrics['sample_count']}",
                f"- Total sorting time: {metrics['total_batch_time_s']} s ({metrics['total_batch_time_min']} min)",
                f"- Average cycle time: {metrics['average_cycle_time_s']} s/sample",
                f"- Estimated throughput: {metrics['estimated_samples_per_hour']} samples/hour",
                f"- Manual review samples: {metrics['manual_review_sample_count']}",
                f"- Main bottleneck: {metrics['bottleneck_action']}",
                f"- Figures: {', '.join(figure_paths) if figure_ok else figure_note}",
                "",
                "## Limits",
                "",
                "- Ignores acceleration, jerk, gripper compliance, controller blending, and real scanner retry behavior.",
                "- Assumes each sample is handled sequentially without parallel prefetching.",
                "",
                "## Next",
                "",
                "- 6D: exception handling logic simulation.",
                "- 6E: action animation or visualization demo.",
                "- 6F: control-system interface and pseudocode.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    trajectory_rows = read_csv(TRAJECTORY_CSV)
    motion_summary_rows = read_csv(MOTION_SUMMARY_CSV)
    grouped = group_by_sample(trajectory_rows)
    cycle_rows = estimate_cycles(grouped, motion_summary_rows)
    batch_rows = batch_summary(cycle_rows, trajectory_rows, motion_summary_rows)
    figure_result = make_figures(cycle_rows)

    write_csv(
        CYCLE_TIME_CSV,
        cycle_rows,
        [
            "sample_id",
            "input_slot",
            "target_zone",
            "target_slot",
            "tube_height_mm",
            "barcode_status",
            "category",
            "num_waypoints",
            "xy_distance_mm",
            "z_distance_mm",
            "motion_time_s",
            "gripper_time_s",
            "scan_time_s",
            "decision_time_s",
            "settle_time_s",
            "manual_review_extra_s",
            "total_cycle_time_s",
            "notes",
        ],
    )
    write_csv(BATCH_SUMMARY_CSV, batch_rows, ["metric", "value", "unit", "notes"])
    write_report(cycle_rows, batch_rows, figure_result)

    metrics = {row["metric"]: row["value"] for row in batch_rows}
    print(f"sample_count={metrics['sample_count']}")
    print(f"total_batch_time_s={metrics['total_batch_time_s']}")
    print(f"average_cycle_time_s={metrics['average_cycle_time_s']}")
    print(f"estimated_samples_per_hour={metrics['estimated_samples_per_hour']}")
    print(f"manual_review_sample_count={metrics['manual_review_sample_count']}")
    print(f"bottleneck_action={metrics['bottleneck_action']}")
    print(f"figures={';'.join(figure_result[1]) if figure_result[0] else figure_result[2]}")
    print(f"report={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
