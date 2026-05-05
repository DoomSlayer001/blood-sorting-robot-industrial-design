from __future__ import annotations

import csv
import shutil
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = ROOT / "04_simulation" / "task_planning"
FIGURE_DIR = TASK_DIR / "figures"
REPORT_DIR = ROOT / "reports"

TRAJECTORY_CSV = TASK_DIR / "multi_box_pick_scan_place_trajectory_v1.csv"
MOTION_SUMMARY_CSV = TASK_DIR / "multi_box_motion_summary_v1.csv"
EVENT_SUMMARY_CSV = TASK_DIR / "multi_box_trajectory_event_summary_v1.csv"
SLOT_CSV = TASK_DIR / "multi_box_slot_coordinates_v1.csv"
MANIFEST_CSV = TASK_DIR / "multi_box_sample_manifest_v1.csv"
PENDING_QUEUE_CSV = TASK_DIR / "multi_box_pending_queue_v1.csv"
OPERATOR_EVENTS_CSV = TASK_DIR / "multi_box_operator_events_v1.csv"
CYCLE_TIME_CSV = TASK_DIR / "multi_box_cycle_time_estimate_v1.csv"
BATCH_SUMMARY_CSV = TASK_DIR / "multi_box_batch_throughput_summary_v1.csv"

BASELINE_GIF = FIGURE_DIR / "multi_box_baseline_sorting_animation_v1.gif"
HOLD_RESUME_GIF = FIGURE_DIR / "multi_box_hold_resume_animation_v1.gif"
MANUAL_ALARM_GIF = FIGURE_DIR / "multi_box_manual_review_alarm_animation_v1.gif"
BASELINE_FRAME_DIR = FIGURE_DIR / "multi_box_baseline_sorting_animation_frames_v1"
HOLD_FRAME_DIR = FIGURE_DIR / "multi_box_hold_resume_animation_frames_v1"
ALARM_FRAME_DIR = FIGURE_DIR / "multi_box_manual_review_alarm_animation_frames_v1"

KEY_FRAMES = {
    "layout_overview": FIGURE_DIR / "multi_box_frame_layout_overview_v1.png",
    "scan_event": FIGURE_DIR / "multi_box_frame_scan_event_v1.png",
    "normal_output": FIGURE_DIR / "multi_box_frame_normal_output_v1.png",
    "manual_review": FIGURE_DIR / "multi_box_frame_manual_review_v1.png",
    "category_hold": FIGURE_DIR / "multi_box_frame_category_hold_v1.png",
    "pending_queue": FIGURE_DIR / "multi_box_frame_pending_queue_v1.png",
    "category_resume": FIGURE_DIR / "multi_box_frame_category_resume_v1.png",
    "pause_alarm": FIGURE_DIR / "multi_box_frame_pause_alarm_v1.png",
}

ANIMATION_EVENT_SUMMARY_CSV = TASK_DIR / "multi_box_sorting_animation_event_summary_v1.csv"
REPORT_PATH = REPORT_DIR / "stage_7f_multi_box_sorting_animation_report.md"

CATEGORY_COLORS = {
    "Category A": "#7b3294",
    "Category B": "#d8b365",
    "Category C": "#4393c3",
    "Category D": "#d6604d",
    "unknown": "#666666",
    "manual_review": "#b2182b",
}
ZONE_COLORS = {
    "input": "#377eb8",
    "output_A": "#7b3294",
    "output_B": "#d8b365",
    "output_C": "#4393c3",
    "output_D": "#d6604d",
    "manual_review": "#666666",
    "scan_station": "#111111",
}
ANIMATION_RUNS = {
    "baseline_multi_box_sorting": ("baseline_multi_box_run", BASELINE_GIF, BASELINE_FRAME_DIR, 8),
    "category_hold_resume": ("forced_category_A_full", HOLD_RESUME_GIF, HOLD_FRAME_DIR, 6),
    "manual_review_pause_alarm": ("forced_manual_review_full", MANUAL_ALARM_GIF, ALARM_FRAME_DIR, 3),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_inputs() -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    trajectory_rows = read_csv(TRAJECTORY_CSV)
    slot_rows = read_csv(SLOT_CSV)
    motion_by_key = {(row["run_id"], row["sample_id"]): row for row in read_csv(MOTION_SUMMARY_CSV)}
    manifest_by_sample = {row["sample_id"]: row for row in read_csv(MANIFEST_CSV)}
    pending_rows = read_csv(PENDING_QUEUE_CSV)
    operator_rows = read_csv(OPERATOR_EVENTS_CSV)
    return trajectory_rows, slot_rows, motion_by_key, manifest_by_sample, pending_rows, operator_rows


def grouped_trajectory(trajectory_rows: list[dict[str, str]]) -> dict[tuple[str, str], list[dict[str, str]]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in trajectory_rows:
        grouped[(row["run_id"], row["trajectory_id"])].append(row)
    for rows in grouped.values():
        rows.sort(key=lambda item: int(item["step_order"]))
    return grouped


def category_for(row: dict[str, str], manifest_by_sample: dict[str, dict[str, str]]) -> str:
    if row.get("sample_id") and row["sample_id"] in manifest_by_sample:
        category = manifest_by_sample[row["sample_id"]]["category"]
        if category.startswith("Category "):
            return category
    if row.get("target_zone", "").startswith("output_"):
        return f"Category {row['target_zone'][-1]}"
    return "manual_review" if row.get("target_box_id") == "manual_review_bin" else "unknown"


def event_type_for(row: dict[str, str]) -> str:
    state = row["state"]
    if state == "MOVE_SAFE_ABOVE_INPUT":
        return "move_to_input"
    if state == "PICK_TUBE":
        return "pick"
    if state == "MOVE_SAFE_ABOVE_SCAN":
        return "move_to_scan"
    if state == "SCAN_BARCODE":
        return "scan"
    if state == "CLASSIFY_SAMPLE":
        return "classify"
    if state == "MOVE_SAFE_ABOVE_TARGET":
        return "move_to_output"
    if state == "PLACE_TUBE" and row["target_box_id"] == "manual_review_bin":
        return "place_to_manual_review"
    if state == "PLACE_TUBE":
        return "place_to_output"
    if state == "HOLD_CATEGORY":
        return "category_hold"
    if state == "SKIP_HELD_CATEGORY":
        return "pending_queue"
    if state == "PAUSE_ALARM":
        return "pause_alarm"
    if row.get("pending_queue_action") == "released":
        return "released_pending"
    return "trajectory"


def event_label(event_type: str, row: dict[str, str], category: str) -> str:
    labels = {
        "move_to_input": "move to input",
        "pick": "pick tube",
        "move_to_scan": "move to scan",
        "scan": "scan barcode",
        "classify": "classify sample",
        "move_to_output": "move to target",
        "place_to_output": f"place to {category}",
        "place_to_manual_review": "place to manual review",
        "category_hold": f"{category} HOLD",
        "pending_queue": "queued pending sample",
        "operator_clear": "operator clear output box",
        "category_resume": f"{category} RESUME",
        "released_pending": "released pending sample",
        "pause_alarm": "PAUSE_ALARM",
    }
    return labels.get(event_type, row["state"])


def build_raw_frame_events(
    trajectory_rows: list[dict[str, str]],
    manifest_by_sample: dict[str, dict[str, str]],
    operator_rows: list[dict[str, str]],
) -> dict[str, list[dict[str, object]]]:
    frames_by_animation: dict[str, list[dict[str, object]]] = {key: [] for key in ANIMATION_RUNS}
    animation_by_run = {run_id: animation_id for animation_id, (run_id, _, _, _) in ANIMATION_RUNS.items()}

    for row in trajectory_rows:
        animation_id = animation_by_run.get(row["run_id"])
        if not animation_id:
            continue
        event_type = event_type_for(row)
        category = category_for(row, manifest_by_sample)
        if row["state"] == "SCAN_BARCODE":
            frames_by_animation[animation_id].append(frame_from_row(animation_id, row, category, "scan"))
            classify_frame = dict(row)
            classify_frame["state"] = "CLASSIFY_SAMPLE"
            frames_by_animation[animation_id].append(frame_from_row(animation_id, classify_frame, category, "classify"))
        else:
            frames_by_animation[animation_id].append(frame_from_row(animation_id, row, category, event_type))

    for event in operator_rows:
        animation_id = animation_by_run.get(event["run_id"])
        if not animation_id:
            continue
        if event["event_type"] == "clear_or_replace_category_A_output_box":
            event_type = "operator_clear"
        elif event["event_type"] == "resume_category_A":
            event_type = "category_resume"
        elif event["event_type"] == "manual_review_full_alarm":
            event_type = "pause_alarm"
        else:
            event_type = "category_hold"
        category = f"Category {event['related_category']}" if event["related_category"] in {"A", "B", "C", "D"} else "manual_review"
        x, y = ("90.000", "212.000") if event["related_category"] == "A" else ("-140.000", "60.000")
        frames_by_animation[animation_id].append(
            {
                "animation_id": animation_id,
                "run_id": event["run_id"],
                "sample_id": "",
                "state": event["system_response"],
                "category": category,
                "x_mm": x,
                "y_mm": y,
                "target_zone": "",
                "event_type": event_type,
                "event_label": event_label(event_type, {"state": event["system_response"]}, category),
                "notes": event["notes"],
            }
        )

    for frames in frames_by_animation.values():
        for index, frame in enumerate(frames, start=1):
            frame["raw_index"] = index
    return frames_by_animation


def frame_from_row(animation_id: str, row: dict[str, str], category: str, event_type: str) -> dict[str, object]:
    return {
        "animation_id": animation_id,
        "run_id": row["run_id"],
        "sample_id": row["sample_id"],
        "state": row["state"],
        "category": category,
        "x_mm": row["x_mm"],
        "y_mm": row["y_mm"],
        "target_zone": row["target_zone"],
        "event_type": event_type,
        "event_label": event_label(event_type, row, category),
        "notes": row["notes"],
    }


def select_frames(raw_frames: list[dict[str, object]], stride: int) -> list[dict[str, object]]:
    required_types = {
        "move_to_input",
        "pick",
        "move_to_scan",
        "scan",
        "classify",
        "move_to_output",
        "place_to_output",
        "place_to_manual_review",
        "category_hold",
        "pending_queue",
        "operator_clear",
        "category_resume",
        "released_pending",
        "pause_alarm",
    }
    selected_indices: set[int] = {0, len(raw_frames) - 1}
    seen_types: set[str] = set()
    for index, frame in enumerate(raw_frames):
        event_type = str(frame["event_type"])
        if event_type in required_types and event_type not in seen_types:
            selected_indices.add(index)
            seen_types.add(event_type)
        if event_type in {"category_hold", "pending_queue", "operator_clear", "category_resume", "released_pending", "pause_alarm", "place_to_manual_review"}:
            selected_indices.add(index)
        if index % stride == 0:
            selected_indices.add(index)
    selected = [raw_frames[index] for index in sorted(selected_indices)]
    for frame_id, frame in enumerate(selected, start=1):
        frame["frame_id"] = frame_id
    return selected


def all_selected_frames(frames_by_animation: dict[str, list[dict[str, object]]]) -> dict[str, list[dict[str, object]]]:
    selected = {}
    for animation_id, (_, _, _, stride) in ANIMATION_RUNS.items():
        selected[animation_id] = select_frames(frames_by_animation[animation_id], stride)
    return selected


def write_animation_event_summary(selected_frames: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows = []
    for animation_id, frames in selected_frames.items():
        for frame in frames:
            rows.append(
                {
                    "animation_id": animation_id,
                    "frame_id": frame["frame_id"],
                    "run_id": frame["run_id"],
                    "sample_id": frame["sample_id"],
                    "state": frame["state"],
                    "category": frame["category"],
                    "x_mm": frame["x_mm"],
                    "y_mm": frame["y_mm"],
                    "target_zone": frame["target_zone"],
                    "event_type": frame["event_type"],
                    "event_label": frame["event_label"],
                    "notes": frame["notes"],
                }
            )
    write_csv(
        ANIMATION_EVENT_SUMMARY_CSV,
        rows,
        ["animation_id", "frame_id", "run_id", "sample_id", "state", "category", "x_mm", "y_mm", "target_zone", "event_type", "event_label", "notes"],
    )
    return rows


def slot_groups(slot_rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in slot_rows:
        groups[row["box_id"]].append(row)
    return groups


def draw_layout(ax, slot_rows: list[dict[str, str]], held_category: str | None = None) -> None:
    from matplotlib.patches import Rectangle

    ax.set_xlim(-470, 520)
    ax.set_ylim(-360, 360)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.3, alpha=0.35)
    ax.set_xlabel("X mm")
    ax.set_ylabel("Y mm")

    for box_id, rows in slot_groups(slot_rows).items():
        xs = [float(row["x_mm"]) for row in rows]
        ys = [float(row["y_mm"]) for row in rows]
        zone = rows[0]["zone"]
        color = ZONE_COLORS.get(zone, "#555555")
        pad_x = 18.0
        pad_y = 18.0
        ax.add_patch(
            Rectangle(
                (min(xs) - pad_x, min(ys) - pad_y),
                max(xs) - min(xs) + 2 * pad_x,
                max(ys) - min(ys) + 2 * pad_y,
                fill=held_category is not None and box_id == f"category_{held_category[-1]}_output_box",
                facecolor="#ffcccc" if held_category and box_id == f"category_{held_category[-1]}_output_box" else "none",
                edgecolor="red" if held_category and box_id == f"category_{held_category[-1]}_output_box" else color,
                linewidth=2.0 if held_category and box_id == f"category_{held_category[-1]}_output_box" else 0.9,
                alpha=0.32 if held_category and box_id == f"category_{held_category[-1]}_output_box" else 1.0,
            )
        )
        ax.scatter(xs, ys, s=14, color=color, alpha=0.75)
        label = box_id.replace("_output_box", "").replace("_", " ")
        ax.text(sum(xs) / len(xs), max(ys) + 30, label, fontsize=7, ha="center")
    ax.scatter([-140], [60], marker="*", s=120, c="#111111", label="scan station")
    ax.legend(loc="upper right", fontsize=7)


def draw_frame(ax, frame: dict[str, object], prior_frames: list[dict[str, object]], slot_rows: list[dict[str, str]]) -> None:
    ax.clear()
    held_category = "Category A" if frame["event_type"] in {"category_hold", "pending_queue", "operator_clear", "category_resume", "released_pending"} and frame["run_id"] == "forced_category_A_full" else None
    draw_layout(ax, slot_rows, held_category)

    completed = [item for item in prior_frames if item["event_type"] in {"place_to_output", "place_to_manual_review", "released_pending"}]
    for item in completed[-80:]:
        color = CATEGORY_COLORS.get(str(item["category"]), "#444444")
        marker = "X" if item["event_type"] == "place_to_manual_review" else "o"
        ax.scatter(float(item["x_mm"]), float(item["y_mm"]), s=40, color=color, marker=marker, alpha=0.75, edgecolor="white", linewidth=0.4)

    color = CATEGORY_COLORS.get(str(frame["category"]), "#222222")
    marker = "^" if frame["event_type"] == "pending_queue" else "X" if frame["event_type"] == "pause_alarm" else "*"
    size = 150 if frame["event_type"] == "pause_alarm" else 115
    ax.scatter(float(frame["x_mm"]), float(frame["y_mm"]), s=size, color="red" if frame["event_type"] == "pause_alarm" else color, marker=marker, edgecolor="black", linewidth=0.7, zorder=8)
    if frame["event_type"] == "pause_alarm":
        ax.text(-430, -330, "PAUSE_ALARM", color="red", fontsize=18, weight="bold")
    if frame["event_type"] == "pending_queue":
        ax.text(float(frame["x_mm"]) + 12, float(frame["y_mm"]) + 12, "PENDING", color="#d95f02", fontsize=9, weight="bold")
    if frame["event_type"] == "category_resume":
        ax.text(80, 280, "CATEGORY A RESUME", color="#1b9e77", fontsize=12, weight="bold")
    if frame["event_type"] == "operator_clear":
        ax.text(60, 280, "OPERATOR CLEAR A", color="#984ea3", fontsize=12, weight="bold")

    ax.set_title(
        f"{frame['animation_id']} | frame {frame['frame_id']} | {frame['run_id']}\n"
        f"{frame['sample_id']} | {frame['state']} | {frame['category']} | {frame['event_label']}",
        fontsize=10,
    )


def save_static_frame(path: Path, frame: dict[str, object], prior_frames: list[dict[str, object]], slot_rows: list[dict[str, str]]) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 7))
    draw_frame(ax, frame, prior_frames, slot_rows)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_animation(animation_id: str, frames: list[dict[str, object]], slot_rows: list[dict[str, str]], out_path: Path, frame_dir: Path) -> tuple[str, str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter

    fig, ax = plt.subplots(figsize=(8, 6))

    def update(index: int):
        draw_frame(ax, frames[index], frames[:index], slot_rows)
        return []

    animation = FuncAnimation(fig, update, frames=len(frames), interval=300, blit=False)
    try:
        animation.save(out_path, writer=PillowWriter(fps=3), dpi=110)
        plt.close(fig)
        return ("gif", out_path.relative_to(ROOT).as_posix())
    except Exception as gif_exc:
        mp4_path = out_path.with_suffix(".mp4")
        try:
            animation.save(mp4_path, writer=FFMpegWriter(fps=3), dpi=110)
            plt.close(fig)
            return ("mp4", mp4_path.relative_to(ROOT).as_posix())
        except Exception as mp4_exc:
            plt.close(fig)
            if frame_dir.exists():
                shutil.rmtree(frame_dir)
            frame_dir.mkdir(parents=True, exist_ok=True)
            for index, frame in enumerate(frames, start=1):
                save_static_frame(frame_dir / f"{animation_id}_frame_{index:04d}.png", frame, frames[: index - 1], slot_rows)
            return ("frames", f"{frame_dir.relative_to(ROOT).as_posix()} (GIF failed: {gif_exc}; MP4 failed: {mp4_exc})")


def first_frame(frames: list[dict[str, object]], event_type: str) -> tuple[dict[str, object], list[dict[str, object]]]:
    for index, frame in enumerate(frames):
        if frame["event_type"] == event_type:
            return frame, frames[:index]
    return frames[0], []


def save_key_frames(selected_frames: dict[str, list[dict[str, object]]], slot_rows: list[dict[str, str]]) -> list[str]:
    outputs: list[str] = []
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 7))
    draw_layout(ax, slot_rows)
    ax.set_title("Stage 7F Multi-box Layout Overview")
    fig.tight_layout()
    fig.savefig(KEY_FRAMES["layout_overview"], dpi=180)
    plt.close(fig)
    outputs.append(KEY_FRAMES["layout_overview"].relative_to(ROOT).as_posix())

    key_specs = [
        ("scan_event", "baseline_multi_box_sorting", "scan"),
        ("normal_output", "baseline_multi_box_sorting", "place_to_output"),
        ("manual_review", "baseline_multi_box_sorting", "place_to_manual_review"),
        ("category_hold", "category_hold_resume", "category_hold"),
        ("pending_queue", "category_hold_resume", "pending_queue"),
        ("category_resume", "category_hold_resume", "category_resume"),
        ("pause_alarm", "manual_review_pause_alarm", "pause_alarm"),
    ]
    for key, animation_id, event_type in key_specs:
        frame, prior = first_frame(selected_frames[animation_id], event_type)
        save_static_frame(KEY_FRAMES[key], frame, prior, slot_rows)
        outputs.append(KEY_FRAMES[key].relative_to(ROOT).as_posix())
    return outputs


def write_report(animation_outputs: dict[str, tuple[str, str]], key_frame_paths: list[str]) -> None:
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Stage 7F Multi-box Sorting Animation Report",
                "",
                "- Goal: generate 2D top-view animations for the v7.1 multi-box sorting workflow.",
                f"- Input files: `{TRAJECTORY_CSV.relative_to(ROOT).as_posix()}`, `{SLOT_CSV.relative_to(ROOT).as_posix()}`, `{EVENT_SUMMARY_CSV.relative_to(ROOT).as_posix()}`, `{MANIFEST_CSV.relative_to(ROOT).as_posix()}`, `{PENDING_QUEUE_CSV.relative_to(ROOT).as_posix()}`, `{OPERATOR_EVENTS_CSV.relative_to(ROOT).as_posix()}`, `{CYCLE_TIME_CSV.relative_to(ROOT).as_posix()}`, `{BATCH_SUMMARY_CSV.relative_to(ROOT).as_posix()}`.",
                f"- Baseline animation: {animation_outputs['baseline_multi_box_sorting'][1]} shows input -> scan -> category output/manual_review flow.",
                f"- Hold/resume animation: {animation_outputs['category_hold_resume'][1]} highlights Category A hold, pending queue, operator clear, resume, and released pending samples.",
                f"- Manual-review alarm animation: {animation_outputs['manual_review_pause_alarm'][1]} shows true abnormal samples entering review and PAUSE_ALARM when review is full.",
                f"- Key frames: {', '.join(key_frame_paths)}",
                f"- Animation event summary: `{ANIMATION_EVENT_SUMMARY_CSV.relative_to(ROOT).as_posix()}`",
                "",
                "## Limits",
                "",
                "- The animation is a 2D top-view process visualization.",
                "- It does not show real gripper posture, acceleration, dynamics, or controller response.",
                "- The timing is PPT-oriented and compressed; it is not a real-time controller simulation.",
                "",
                "## Next Steps",
                "",
                "- Stage 8A: Kinematics and trajectory-to-control model.",
                "- Stage 8B: PID control and dynamics simulation.",
                "- Stage 9: Mechanical detail and engineering deliverables.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    trajectory_rows, slot_rows, _motion_by_key, manifest_by_sample, _pending_rows, operator_rows = load_inputs()
    raw_frames = build_raw_frame_events(trajectory_rows, manifest_by_sample, operator_rows)
    selected_frames = all_selected_frames(raw_frames)
    summary_rows = write_animation_event_summary(selected_frames)

    animation_outputs: dict[str, tuple[str, str]] = {}
    for animation_id, (_run_id, out_path, frame_dir, _stride) in ANIMATION_RUNS.items():
        animation_outputs[animation_id] = save_animation(animation_id, selected_frames[animation_id], slot_rows, out_path, frame_dir)
    key_frame_paths = save_key_frames(selected_frames, slot_rows)
    write_report(animation_outputs, key_frame_paths)

    print(f"baseline_animation={animation_outputs['baseline_multi_box_sorting'][1]}")
    print(f"hold_resume_animation={animation_outputs['category_hold_resume'][1]}")
    print(f"manual_review_alarm_animation={animation_outputs['manual_review_pause_alarm'][1]}")
    print(f"key_frame_count={len(key_frame_paths)}")
    print(f"animation_event_summary_count={len(summary_rows)}")
    print(f"event_summary_csv={ANIMATION_EVENT_SUMMARY_CSV}")
    print(f"report={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
