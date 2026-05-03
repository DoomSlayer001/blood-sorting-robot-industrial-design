from __future__ import annotations

import csv
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = ROOT / "04_simulation" / "task_planning"
REPORT_DIR = ROOT / "reports"
FIGURE_DIR = TASK_DIR / "figures"
FRAME_DIR = FIGURE_DIR / "sorting_animation_frames_v1"

TRAJECTORY_CSV = TASK_DIR / "pick_scan_place_trajectory_v1.csv"
MOTION_SUMMARY_CSV = TASK_DIR / "sorting_motion_summary_v1.csv"
RACK_SLOT_CSV = TASK_DIR / "rack_slot_coordinates_v1.csv"
FAILURE_SIM_CSV = TASK_DIR / "failure_handling_simulation_v1.csv"
CYCLE_TIME_CSV = TASK_DIR / "cycle_time_estimate_v1.csv"

GIF_OUT = FIGURE_DIR / "sorting_process_top_view_v1.gif"
MP4_OUT = FIGURE_DIR / "sorting_process_top_view_v1.mp4"
FRAME_START = FIGURE_DIR / "sorting_animation_frame_start_v1.png"
FRAME_SCAN = FIGURE_DIR / "sorting_animation_frame_scan_v1.png"
FRAME_OUTPUT = FIGURE_DIR / "sorting_animation_frame_output_v1.png"
FRAME_REVIEW = FIGURE_DIR / "sorting_animation_frame_review_v1.png"
EVENT_SUMMARY_CSV = TASK_DIR / "sorting_animation_event_summary_v1.csv"
REPORT_PATH = REPORT_DIR / "stage_6e_sorting_animation_report.md"

ZONE_LABELS = {
    "input": "Input rack",
    "scan_station": "Scan station",
    "output_A": "Category A",
    "output_B": "Category B",
    "output_C": "Category C",
    "output_D": "Category D",
    "manual_review": "Manual review",
}

ZONE_COLORS = {
    "input": "#2f80ed",
    "scan_station": "#111111",
    "output_A": "#7b3fbb",
    "output_B": "#e0a800",
    "output_C": "#1f77b4",
    "output_D": "#d62728",
    "manual_review": "#666666",
}

TARGET_COLORS = {
    "category_a_bin": "#7b3fbb",
    "category_b_bin": "#e0a800",
    "category_c_bin": "#1f77b4",
    "category_d_bin": "#d62728",
    "manual_review_bin": "#c0392b",
    "PAUSE_ALARM": "#000000",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_inputs() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    return (
        read_csv(TRAJECTORY_CSV),
        read_csv(MOTION_SUMMARY_CSV),
        read_csv(RACK_SLOT_CSV),
        read_csv(FAILURE_SIM_CSV),
        read_csv(CYCLE_TIME_CSV),
    )


def baseline_failure_by_sample(failure_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["sample_id"]: row for row in failure_rows if row["run_id"] == "baseline_manifest_failures"}


def summary_by_sample(summary_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["sample_id"]: row for row in summary_rows}


def group_trajectory(trajectory_rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in trajectory_rows:
        grouped.setdefault(row["sample_id"], []).append(row)
    for rows in grouped.values():
        rows.sort(key=lambda item: int(item["step_order"]))
    return grouped


def sample_event_label(sample_id: str, motion_summary: dict[str, dict[str, str]], failure_summary: dict[str, dict[str, str]]) -> str:
    summary = motion_summary[sample_id]
    failure = failure_summary.get(sample_id, {})
    if failure.get("failure_type") == "scan_failed":
        return "scan_failed / manual_review"
    if failure.get("failure_type") == "unknown_category":
        return "unknown_category / manual_review"
    if summary["target_zone"] == "manual_review_bin":
        return "manual_review"
    return summary["category"]


def build_event_summary(trajectory_rows: list[dict[str, str]], motion_summary: dict[str, dict[str, str]], failure_summary: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    rows = []
    for frame_id, row in enumerate(trajectory_rows, start=1):
        sample_id = row["sample_id"]
        summary = motion_summary[sample_id]
        rows.append(
            {
                "frame_id": frame_id,
                "sample_id": sample_id,
                "state": row["state"],
                "x_mm": row["x_mm"],
                "y_mm": row["y_mm"],
                "target_zone": summary["target_zone"],
                "event_label": sample_event_label(sample_id, motion_summary, failure_summary),
                "notes": row["notes"],
            }
        )
    return rows


def setup_axes(ax, slot_rows: list[dict[str, str]]) -> None:
    ax.set_xlim(-540, 540)
    ax.set_ylim(-440, 390)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.grid(True, linestyle=":", linewidth=0.7)
    for zone, label in ZONE_LABELS.items():
        points = [(float(row["x_mm"]), float(row["y_mm"])) for row in slot_rows if row["zone"] == zone]
        if not points:
            continue
        xs, ys = zip(*points)
        ax.scatter(xs, ys, s=28, color=ZONE_COLORS[zone], label=label, alpha=0.85, zorder=2)
    ax.legend(loc="upper right", fontsize=8)


def draw_completed_targets(ax, completed_samples: set[str], grouped: dict[str, list[dict[str, str]]], motion_summary: dict[str, dict[str, str]]) -> None:
    for sample_id in completed_samples:
        summary = motion_summary[sample_id]
        if summary["target_zone"] == "PAUSE_ALARM":
            continue
        place_rows = [row for row in grouped[sample_id] if row["state"] == "PLACE_TUBE"]
        if not place_rows:
            continue
        point = place_rows[0]
        color = TARGET_COLORS.get(summary["target_zone"], "#555555")
        marker = "X" if summary["target_zone"] == "manual_review_bin" else "o"
        ax.scatter(float(point["x_mm"]), float(point["y_mm"]), s=70, color=color, marker=marker, edgecolor="white", linewidth=0.7, zorder=5)


def draw_frame(ax, frame_index: int, trajectory_rows: list[dict[str, str]], slot_rows: list[dict[str, str]], grouped: dict[str, list[dict[str, str]]], motion_summary: dict[str, dict[str, str]], failure_summary: dict[str, dict[str, str]]) -> None:
    ax.clear()
    setup_axes(ax, slot_rows)
    current = trajectory_rows[frame_index]
    sample_id = current["sample_id"]
    current_order = int(current["step_order"])
    completed = {row["sample_id"] for row in trajectory_rows[:frame_index] if row["state"] == "RETREAT_TO_SAFE_Z"}
    draw_completed_targets(ax, completed, grouped, motion_summary)

    current_rows = [row for row in grouped[sample_id] if int(row["step_order"]) <= current_order]
    xs = [float(row["x_mm"]) for row in current_rows]
    ys = [float(row["y_mm"]) for row in current_rows]
    color = TARGET_COLORS.get(motion_summary[sample_id]["target_zone"], "#2c7fb8")
    ax.plot(xs, ys, color=color, linewidth=2.0, alpha=0.9, zorder=4)
    ax.scatter(float(current["x_mm"]), float(current["y_mm"]), s=110, color=color, edgecolor="black", marker="*", linewidth=0.7, zorder=6)
    label = sample_event_label(sample_id, motion_summary, failure_summary)
    ax.set_title(f"Stage 6E Sorting Animation | frame {frame_index + 1}/{len(trajectory_rows)} | {sample_id} | {current['state']}\n{label}")


def save_static_frame(path: Path, frame_index: int, trajectory_rows: list[dict[str, str]], slot_rows: list[dict[str, str]], grouped: dict[str, list[dict[str, str]]], motion_summary: dict[str, dict[str, str]], failure_summary: dict[str, dict[str, str]]) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 8))
    draw_frame(ax, frame_index, trajectory_rows, slot_rows, grouped, motion_summary, failure_summary)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def key_frame_indices(trajectory_rows: list[dict[str, str]], motion_summary: dict[str, dict[str, str]]) -> dict[str, int]:
    scan_index = next(index for index, row in enumerate(trajectory_rows) if row["state"] == "SCAN_BARCODE")
    output_index = next(index for index, row in enumerate(trajectory_rows) if row["state"] == "PLACE_TUBE" and motion_summary[row["sample_id"]]["target_zone"] != "manual_review_bin")
    review_index = next(index for index, row in enumerate(trajectory_rows) if row["state"] == "PLACE_TUBE" and motion_summary[row["sample_id"]]["target_zone"] == "manual_review_bin")
    return {"start": 0, "scan": scan_index, "output": output_index, "review": review_index}


def generate_animation(trajectory_rows: list[dict[str, str]], slot_rows: list[dict[str, str]], grouped: dict[str, list[dict[str, str]]], motion_summary: dict[str, dict[str, str]], failure_summary: dict[str, dict[str, str]]) -> tuple[str, str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6))
    frame_stride = 2
    frame_indices = list(range(0, len(trajectory_rows), frame_stride))
    if frame_indices[-1] != len(trajectory_rows) - 1:
        frame_indices.append(len(trajectory_rows) - 1)

    def update(frame_number: int):
        draw_frame(ax, frame_indices[frame_number], trajectory_rows, slot_rows, grouped, motion_summary, failure_summary)
        return []

    animation = FuncAnimation(fig, update, frames=len(frame_indices), interval=250, blit=False)
    try:
        animation.save(GIF_OUT, writer=PillowWriter(fps=4), dpi=120)
        plt.close(fig)
        return ("gif", GIF_OUT.relative_to(ROOT).as_posix())
    except Exception as gif_exc:
        try:
            animation.save(MP4_OUT, writer=FFMpegWriter(fps=4), dpi=120)
            plt.close(fig)
            return ("mp4", MP4_OUT.relative_to(ROOT).as_posix())
        except Exception as mp4_exc:
            plt.close(fig)
            if FRAME_DIR.exists():
                shutil.rmtree(FRAME_DIR)
            FRAME_DIR.mkdir(parents=True, exist_ok=True)
            for frame_id, source_index in enumerate(frame_indices, start=1):
                save_static_frame(FRAME_DIR / f"frame_{frame_id:04d}.png", source_index, trajectory_rows, slot_rows, grouped, motion_summary, failure_summary)
            return ("frames", f"{FRAME_DIR.relative_to(ROOT).as_posix()} (GIF failed: {gif_exc}; MP4 failed: {mp4_exc})")


def write_report(animation_result: tuple[str, str], static_paths: list[str]) -> None:
    output_kind, output_path = animation_result
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Stage 6E Sorting Animation Report",
                "",
                "## Inputs",
                "",
                f"- `{TRAJECTORY_CSV.relative_to(ROOT).as_posix()}`",
                f"- `{MOTION_SUMMARY_CSV.relative_to(ROOT).as_posix()}`",
                f"- `{RACK_SLOT_CSV.relative_to(ROOT).as_posix()}`",
                f"- `{FAILURE_SIM_CSV.relative_to(ROOT).as_posix()}`",
                f"- `{CYCLE_TIME_CSV.relative_to(ROOT).as_posix()}`",
                "",
                "## Outputs",
                "",
                f"- Animation output: {output_kind} `{output_path}`",
                f"- Static key frames: {', '.join(static_paths)}",
                f"- Event summary: `{EVENT_SUMMARY_CSV.relative_to(ROOT).as_posix()}`",
                "",
                "## Display Logic",
                "",
                "- The figure shows input rack, scan station, Category A/B/C/D bins, manual review, active sample position, active path segment, and completed target placements.",
                "- Category outputs use distinct colors; manual review / scan-failed / unknown-category samples use a red exception marker.",
                "",
                "## Limits",
                "",
                "- 2D top-view only.",
                "- Does not show real robot arm posture, gripper orientation, acceleration, or controller blending.",
                "- Intended for report/PPT visualization, not final control simulation.",
                "",
                "## Next",
                "",
                "- 6F: control-system pseudocode and interface definition.",
                "- 6G: final report / PPT organization.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    try:
        import matplotlib  # noqa: F401
    except Exception as exc:
        raise SystemExit(f"matplotlib is required for Stage 6E animation: {type(exc).__name__}: {exc}") from exc

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    trajectory_rows, summary_rows, slot_rows, failure_rows, _cycle_rows = load_inputs()
    motion_summary = summary_by_sample(summary_rows)
    failure_summary = baseline_failure_by_sample(failure_rows)
    grouped = group_trajectory(trajectory_rows)
    event_rows = build_event_summary(trajectory_rows, motion_summary, failure_summary)
    write_csv(EVENT_SUMMARY_CSV, event_rows, ["frame_id", "sample_id", "state", "x_mm", "y_mm", "target_zone", "event_label", "notes"])

    keys = key_frame_indices(trajectory_rows, motion_summary)
    static_specs = [
        (FRAME_START, keys["start"]),
        (FRAME_SCAN, keys["scan"]),
        (FRAME_OUTPUT, keys["output"]),
        (FRAME_REVIEW, keys["review"]),
    ]
    for path, index in static_specs:
        save_static_frame(path, index, trajectory_rows, slot_rows, grouped, motion_summary, failure_summary)
    static_paths = [path.relative_to(ROOT).as_posix() for path, _ in static_specs]

    animation_result = generate_animation(trajectory_rows, slot_rows, grouped, motion_summary, failure_summary)
    write_report(animation_result, static_paths)

    print(f"event_count={len(event_rows)}")
    print(f"animation_type={animation_result[0]}")
    print(f"animation_path={animation_result[1]}")
    print(f"static_frames={';'.join(static_paths)}")
    print(f"event_summary={EVENT_SUMMARY_CSV}")
    print(f"report={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
