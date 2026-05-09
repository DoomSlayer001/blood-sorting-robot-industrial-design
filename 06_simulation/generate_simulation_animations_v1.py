from __future__ import annotations

import csv
import shutil
from collections import Counter, defaultdict
from datetime import datetime
from importlib.util import find_spec
from pathlib import Path

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"
FIG_DIR = SIM_DIR / "figures"
ANIM_DIR = SIM_DIR / "animations"
FRAME_DIR = ANIM_DIR / "frames"
REPORT_DIR = ROOT / "reports"

INPUT_FILES = [
    "input_box_occupancy_map_v1.csv",
    "tube_sample_manifest_v1.csv",
    "sorting_task_manifest_v1.csv",
    "sorting_state_machine_event_log_v1.csv",
    "sorting_state_machine_task_result_v1.csv",
    "output_box_occupancy_timeline_v1.csv",
    "manual_review_occupancy_timeline_v1.csv",
    "category_hold_resume_events_v1.csv",
    "pending_queue_log_v1.csv",
    "trajectory_waypoints_v1.csv",
    "trajectory_segments_v1.csv",
    "time_stepped_motion_trace_v1.csv",
    "time_stepped_motion_summary_v1.csv",
    "axis_servo_tracking_trace_v1.csv",
    "servo_robustness_error_summary_v1.csv",
    "simulation_chain_key_metrics_v1.csv",
    "simulation_chain_acceptance_status_v1.csv",
]

MANIFEST_CSV = SIM_DIR / "animation_manifest_v1.csv"
FRAME_SUMMARY_CSV = SIM_DIR / "animation_frame_summary_v1.csv"
EVENT_OVERLAY_CSV = SIM_DIR / "animation_event_overlay_v1.csv"
DASHBOARD_PNG = FIG_DIR / "simulation_animation_dashboard_v1.png"
REPORT_MD = REPORT_DIR / "stage_7b9_python_simulation_animation_package_report.md"

TOP_GIF = ANIM_DIR / "top_view_sorting_animation_v1.gif"
XYZ_GIF = ANIM_DIR / "xyz_motion_trajectory_animation_v1.gif"
TIMELINE_GIF = ANIM_DIR / "output_pending_timeline_animation_v1.gif"

FPS = 8
NO_CAMERA_LOGIC_USED = True


def read_csv(name: str) -> list[dict[str, str]]:
    path = SIM_DIR / name
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def as_float(value: str | float | int, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: str | float | int, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def is_true(value: str) -> bool:
    return str(value).strip().lower() == "true"


def task_sort_key(task_id: str) -> int:
    return as_int(task_id.rsplit("-", 1)[-1])


def source_list(names: list[str]) -> str:
    return ";".join(names)


def capture_frame(fig: plt.Figure) -> np.ndarray:
    fig.canvas.draw()
    rgba = np.asarray(fig.canvas.buffer_rgba())
    return rgba[:, :, :3].copy()


def save_animation(
    animation_id: str,
    frames: list[np.ndarray],
    gif_path: Path,
    source_files: list[str],
    manifest_rows: list[dict[str, object]],
    frame_summary_rows: list[dict[str, object]],
    duration_note: str,
) -> None:
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    imageio.mimsave(gif_path, frames, duration=1 / FPS, loop=0)
    duration_s = round(len(frames) / FPS, 3)
    manifest_rows.append(
        {
            "animation_id": animation_id,
            "animation_name": gif_path.stem,
            "output_path": gif_path.relative_to(ROOT).as_posix(),
            "format": "gif",
            "frame_count": len(frames),
            "duration_s": duration_s,
            "source_files": source_list(source_files),
            "generation_status": "success",
            "notes": duration_note,
        }
    )
    frame_summary_rows.append(
        {
            "animation_id": animation_id,
            "output_path": gif_path.relative_to(ROOT).as_posix(),
            "frame_count": len(frames),
            "fps": FPS,
            "duration_s": duration_s,
            "representative_frames_saved": save_representative_frames(animation_id, frames),
            "notes": duration_note,
        }
    )
    maybe_write_mp4(animation_id, frames, gif_path.with_suffix(".mp4"), source_files, manifest_rows, duration_note)


def save_representative_frames(animation_id: str, frames: list[np.ndarray]) -> int:
    indexes = sorted({0, len(frames) // 2, len(frames) - 1})
    saved = 0
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    for index in indexes:
        if 0 <= index < len(frames):
            imageio.imwrite(FRAME_DIR / f"{animation_id}_frame_{index:04d}.png", frames[index])
            saved += 1
    return saved


def maybe_write_mp4(
    animation_id: str,
    frames: list[np.ndarray],
    mp4_path: Path,
    source_files: list[str],
    manifest_rows: list[dict[str, object]],
    base_note: str,
) -> None:
    duration_s = round(len(frames) / FPS, 3)
    ffmpeg_available = shutil.which("ffmpeg") is not None or find_spec("imageio_ffmpeg") is not None
    if not ffmpeg_available:
        manifest_rows.append(
            {
                "animation_id": animation_id,
                "animation_name": mp4_path.stem,
                "output_path": mp4_path.relative_to(ROOT).as_posix(),
                "format": "mp4",
                "frame_count": len(frames),
                "duration_s": duration_s,
                "source_files": source_list(source_files),
                "generation_status": "warning",
                "notes": "MP4 skipped: ffmpeg/imageio-ffmpeg not available. GIF is the accepted output. " + base_note,
            }
        )
        return

    try:
        imageio.mimsave(mp4_path, frames, fps=FPS, codec="libx264", quality=8)
        status = "success"
        note = "MP4 generated successfully. " + base_note
    except Exception as exc:  # MP4 is optional for this stage.
        status = "warning"
        note = f"MP4 generation failed without failing the package: {exc}. GIF is the accepted output. {base_note}"

    manifest_rows.append(
        {
            "animation_id": animation_id,
            "animation_name": mp4_path.stem,
            "output_path": mp4_path.relative_to(ROOT).as_posix(),
            "format": "mp4",
            "frame_count": len(frames),
            "duration_s": duration_s,
            "source_files": source_list(source_files),
            "generation_status": status,
            "notes": note,
        }
    )


def load_data() -> dict[str, list[dict[str, str]]]:
    return {name: read_csv(name) for name in INPUT_FILES}


def build_waypoint_maps(waypoints: list[dict[str, str]]) -> tuple[dict[tuple[str, str], list[dict[str, str]]], dict[str, tuple[float, float]]]:
    by_key: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    destinations: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in waypoints:
        by_key[(row["scenario_id"], row["task_id"])].append(row)
        if row["waypoint_name"] == "descend_to_place":
            destinations[row["target_box_id"]].append((as_float(row["x_mm"]), as_float(row["y_mm"])))
    for rows in by_key.values():
        rows.sort(key=lambda r: as_int(r["waypoint_index"]))
    return by_key, {key: tuple(np.mean(value, axis=0)) for key, value in destinations.items()}


def draw_static_layout(
    ax: plt.Axes,
    input_rows: list[dict[str, str]],
    destination_xy: dict[str, tuple[float, float]],
    output_counts: Counter[str],
    manual_count: int,
    remaining_tubes: set[str],
) -> None:
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-470, 310)
    ax.set_ylim(-230, 325)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.grid(True, alpha=0.18)

    occupied_x, occupied_y, empty_x, empty_y = [], [], [], []
    for row in input_rows:
        x, y = as_float(row["x_mm"]), as_float(row["y_mm"])
        if row["tube_id"] and row["tube_id"] in remaining_tubes:
            occupied_x.append(x)
            occupied_y.append(y)
        else:
            empty_x.append(x)
            empty_y.append(y)
    ax.scatter(empty_x, empty_y, s=32, facecolors="none", edgecolors="#9aa0a6", linewidths=0.8, label="empty/picked slot")
    ax.scatter(occupied_x, occupied_y, s=38, color="#2f6fdd", label="tube in input slot")
    ax.add_patch(plt.Rectangle((-255, -190), 185, 145, fill=False, edgecolor="#4b5563", linewidth=1.4))
    ax.text(-252, -42, "input rack\ninternal occupancy table", fontsize=8, va="bottom")

    colors = {
        "output_box_A": "#2ca02c",
        "output_box_B": "#17becf",
        "output_box_C": "#9467bd",
        "output_box_D": "#ff7f0e",
        "manual_review_01": "#d62728",
    }
    for box_id, (x, y) in sorted(destination_xy.items()):
        width, height = (86, 60) if box_id.startswith("output") else (96, 52)
        ax.add_patch(
            plt.Rectangle((x - width / 2, y - height / 2), width, height, fill=False, edgecolor=colors.get(box_id, "#111827"), linewidth=1.6)
        )
        label = box_id.replace("output_box_", "out ").replace("manual_review_01", "manual review")
        count = manual_count if box_id == "manual_review_01" else output_counts[box_id]
        ax.text(x, y, f"{label}\n{count}", ha="center", va="center", fontsize=8, color=colors.get(box_id, "#111827"))

    ax.scatter([0], [20], marker="s", s=80, color="#111827", label="scan align")
    ax.text(8, 30, "scan align\nno camera recognition", fontsize=8)


def generate_top_view_animation(data: dict[str, list[dict[str, str]]], manifest_rows: list[dict[str, object]], frame_rows: list[dict[str, object]], overlay_rows: list[dict[str, object]]) -> None:
    input_rows = data["input_box_occupancy_map_v1.csv"]
    task_manifest = data["sorting_task_manifest_v1.csv"]
    results = [row for row in data["sorting_state_machine_task_result_v1.csv"] if row["scenario_id"] == "baseline"]
    waypoints_by_key, destination_xy = build_waypoint_maps(data["trajectory_waypoints_v1.csv"])

    task_by_id = {row["task_id"]: row for row in task_manifest}
    results.sort(key=lambda r: task_sort_key(r["task_id"]))
    remaining = {row["tube_id"] for row in input_rows if row.get("tube_id") and is_true(row.get("tube_present", ""))}
    output_counts: Counter[str] = Counter()
    manual_count = 0
    frame_specs: list[dict[str, object]] = []
    hold_events = data["category_hold_resume_events_v1.csv"]
    hold_note = "category_A hold/resume overlay from forced_category_A_full" if hold_events else "no hold/resume events present"

    for result in results:
        task = task_by_id[result["task_id"]]
        task_waypoints = waypoints_by_key.get(("baseline", result["task_id"]), [])
        place = next((w for w in task_waypoints if w["waypoint_name"] == "descend_to_place"), None)
        if not place:
            continue
        source = (as_float(task["source_x_mm"]), as_float(task["source_y_mm"]))
        scan = (0.0, 20.0)
        dest = (as_float(place["x_mm"]), as_float(place["y_mm"]))
        target_box = result["target_box_id"]
        abnormal = is_true(result["abnormal_flag"])

        for phase, position, picked in [
            ("pick from input", source, False),
            ("carry through scan align", scan, True),
            ("move to destination", ((scan[0] + dest[0]) / 2, (scan[1] + dest[1]) / 2), True),
        ]:
            if picked and result["tube_id"] in remaining:
                remaining.remove(result["tube_id"])
            frame_specs.append(
                {
                    "task_id": result["task_id"],
                    "tube_id": result["tube_id"],
                    "phase": phase,
                    "tcp": position,
                    "tube": position if picked else source,
                    "source": source,
                    "dest": dest,
                    "target_box": target_box,
                    "abnormal": abnormal,
                    "remaining": set(remaining),
                    "output_counts": Counter(output_counts),
                    "manual_count": manual_count,
                    "hold_note": hold_note,
                }
            )

        if abnormal:
            manual_count += 1
        else:
            output_counts[target_box] += 1
        frame_specs.append(
            {
                "task_id": result["task_id"],
                "tube_id": result["tube_id"],
                "phase": "place to manual review" if abnormal else "place to output",
                "tcp": dest,
                "tube": dest,
                "source": source,
                "dest": dest,
                "target_box": target_box,
                "abnormal": abnormal,
                "remaining": set(remaining),
                "output_counts": Counter(output_counts),
                "manual_count": manual_count,
                "hold_note": hold_note,
            }
        )

    frames: list[np.ndarray] = []
    total = len(frame_specs)
    for index, spec in enumerate(frame_specs):
        fig, ax = plt.subplots(figsize=(9.5, 6.2), dpi=110)
        draw_static_layout(ax, input_rows, destination_xy, spec["output_counts"], int(spec["manual_count"]), spec["remaining"])
        source = spec["source"]
        dest = spec["dest"]
        tcp = spec["tcp"]
        tube = spec["tube"]
        color = "#d62728" if spec["abnormal"] else "#111827"
        ax.plot([source[0], 0, dest[0]], [source[1], 20, dest[1]], color="#6b7280", linewidth=1.0, alpha=0.5)
        ax.scatter([tcp[0]], [tcp[1]], marker="x", s=100, color="#111827", linewidths=2.0, label="TCP/gripper")
        ax.scatter([tube[0]], [tube[1]], s=95, color=color, edgecolor="white", linewidth=1.0, label="active tube")
        if spec["abnormal"]:
            ax.text(dest[0] + 15, dest[1] - 28, "abnormal -> manual review", color="#d62728", fontsize=8)
        ax.set_title(f"Top-view sorting animation | frame {index + 1}/{total} | {spec['task_id']} {spec['phase']}", fontsize=11)
        ax.text(-455, 295, "No camera logic: input state comes from internal tube occupancy table.", fontsize=8, color="#374151")
        ax.text(-455, 272, spec["hold_note"], fontsize=8, color="#b45309")
        ax.legend(loc="lower right", fontsize=7, framealpha=0.9)
        frames.append(capture_frame(fig))
        plt.close(fig)

    overlay_rows.extend(
        [
            {
                "animation_id": "top_view_sorting_animation_v1",
                "overlay_type": "manual_review_route",
                "scenario_id": "baseline",
                "event_ref": "abnormal_flag=true",
                "display_text": "Abnormal samples are placed in manual_review_01.",
                "source_file": "sorting_state_machine_task_result_v1.csv",
                "notes": f"manual_review_count={manual_count}",
            },
            {
                "animation_id": "top_view_sorting_animation_v1",
                "overlay_type": "category_hold_resume",
                "scenario_id": "forced_category_A_full",
                "event_ref": "category_hold/category_resume",
                "display_text": "Output category full creates a pending queue, then resumes after operator service.",
                "source_file": "category_hold_resume_events_v1.csv",
                "notes": f"hold_resume_events={len(hold_events)}",
            },
            {
                "animation_id": "top_view_sorting_animation_v1",
                "overlay_type": "no_camera_logic",
                "scenario_id": "all",
                "event_ref": "input_box_occupancy_map_v1.csv",
                "display_text": "Input occupancy is table-driven; no camera recognition is used.",
                "source_file": "input_box_occupancy_map_v1.csv",
                "notes": "NO_CAMERA_LOGIC_USED=True",
            },
        ]
    )
    save_animation(
        "top_view_sorting_animation_v1",
        frames,
        TOP_GIF,
        [
            "input_box_occupancy_map_v1.csv",
            "sorting_task_manifest_v1.csv",
            "sorting_state_machine_task_result_v1.csv",
            "trajectory_waypoints_v1.csv",
            "category_hold_resume_events_v1.csv",
        ],
        manifest_rows,
        frame_rows,
        "Top-view animation shows input rack, TCP/gripper, tube movement, output boxes, manual review, and hold/resume overlay.",
    )


def generate_xyz_animation(data: dict[str, list[dict[str, str]]], manifest_rows: list[dict[str, object]], frame_rows: list[dict[str, object]], overlay_rows: list[dict[str, object]]) -> None:
    trace = [row for row in data["time_stepped_motion_trace_v1.csv"] if row["scenario_id"] == "baseline"]
    trace.sort(key=lambda r: (as_float(r["time_s"]), r["task_id"], as_int(r["segment_index"])))
    sample_count = min(1100, len(trace))
    indexes = np.linspace(0, len(trace) - 1, sample_count, dtype=int)
    sampled = [trace[i] for i in indexes]
    time = np.array([as_float(row["time_s"]) for row in sampled])
    x = np.array([as_float(row["x_mm"]) for row in sampled])
    y = np.array([as_float(row["y_mm"]) for row in sampled])
    z = np.array([as_float(row["z_mm"]) for row in sampled])
    frame_indexes = np.linspace(1, len(sampled), 90, dtype=int)

    safe_z = 190.0
    pick_z = 145.0
    place_z = 135.0
    scan_z = 155.0
    low_z_mask = z < safe_z - 1e-6

    frames: list[np.ndarray] = []
    for frame_no, end in enumerate(frame_indexes, start=1):
        fig, axes = plt.subplots(3, 1, figsize=(9.2, 7.0), dpi=110, sharex=True)
        for ax, values, label, color in [
            (axes[0], x, "X (mm)", "#2f6fdd"),
            (axes[1], y, "Y (mm)", "#2ca02c"),
            (axes[2], z, "Z (mm)", "#d62728"),
        ]:
            ax.plot(time, values, color="#c7cdd6", linewidth=0.9)
            ax.plot(time[:end], values[:end], color=color, linewidth=1.8)
            ax.axvline(time[end - 1], color="#111827", linewidth=0.8, alpha=0.6)
            ax.set_ylabel(label)
            ax.grid(True, alpha=0.22)
        axes[2].axhline(safe_z, color="#111827", linestyle="--", linewidth=1.0, label="safe_z 190")
        axes[2].axhline(pick_z, color="#9467bd", linestyle=":", linewidth=1.0, label="pick_z 145")
        axes[2].axhline(place_z, color="#ff7f0e", linestyle=":", linewidth=1.0, label="place_z 135")
        axes[2].axhline(scan_z, color="#17becf", linestyle=":", linewidth=1.0, label="scan_z 155")
        axes[2].scatter(time[low_z_mask], z[low_z_mask], s=4, color="#d62728", alpha=0.25, label="low-Z samples")
        axes[2].set_xlabel("Time (s)")
        axes[2].legend(loc="upper right", fontsize=7, ncol=5)
        fig.suptitle(f"XYZ motion trajectory | frame {frame_no}/{len(frame_indexes)} | low Z constrained to pick/place/scan zones", fontsize=11)
        frames.append(capture_frame(fig))
        plt.close(fig)

    overlay_rows.append(
        {
            "animation_id": "xyz_motion_trajectory_animation_v1",
            "overlay_type": "safe_z_pick_place_scan",
            "scenario_id": "baseline",
            "event_ref": "time_stepped_motion_trace_v1.csv",
            "display_text": "safe_z=190, pick_z=145, place_z=135, scan_z=155; low-Z points are highlighted.",
            "source_file": "time_stepped_motion_trace_v1.csv",
            "notes": f"low_z_sample_count={int(np.sum(low_z_mask))}",
        }
    )
    save_animation(
        "xyz_motion_trajectory_animation_v1",
        frames,
        XYZ_GIF,
        ["time_stepped_motion_trace_v1.csv", "trajectory_waypoints_v1.csv", "trajectory_segments_v1.csv"],
        manifest_rows,
        frame_rows,
        "XYZ animation plots X/Y/Z versus time and highlights safe_z, pick_z, place_z, and scan_z.",
    )


def timeline_series(rows: list[dict[str, str]], scenario_id: str, box_id: str) -> tuple[list[int], list[int]]:
    filtered = [r for r in rows if r["scenario_id"] == scenario_id and r["output_box_id"] == box_id]
    filtered.sort(key=lambda r: as_int(r["timestamp_step"]))
    return [as_int(r["timestamp_step"]) for r in filtered], [as_int(r["occupied_slots"]) for r in filtered]


def generate_timeline_animation(data: dict[str, list[dict[str, str]]], manifest_rows: list[dict[str, object]], frame_rows: list[dict[str, object]], overlay_rows: list[dict[str, object]]) -> None:
    scenario = "forced_category_A_full"
    output_rows = data["output_box_occupancy_timeline_v1.csv"]
    event_rows = [r for r in data["sorting_state_machine_event_log_v1.csv"] if r["scenario_id"] == scenario]
    event_rows.sort(key=lambda r: as_int(r["timestamp_step"]))
    times = np.array([as_int(r["timestamp_step"]) for r in event_rows])
    pending = np.array([as_int(r["pending_queue_size"]) for r in event_rows])
    frame_times = np.linspace(int(times.min()), int(times.max()), 92, dtype=int)
    hold_time = next((as_int(r["timestamp_step"]) for r in event_rows if r["event"] == "category_hold"), int(times.min()))
    resume_time = next((as_int(r["timestamp_step"]) for r in reversed(event_rows) if as_int(r["pending_queue_size"]) == 0), int(times.max()))
    box_ids = sorted({r["output_box_id"] for r in output_rows if r["scenario_id"] == scenario})
    colors = ["#2ca02c", "#17becf", "#9467bd", "#ff7f0e"]

    frames: list[np.ndarray] = []
    for frame_no, current_time in enumerate(frame_times, start=1):
        fig, axes = plt.subplots(2, 1, figsize=(9.2, 6.6), dpi=110, sharex=True)
        for color, box_id in zip(colors, box_ids):
            tx, values = timeline_series(output_rows, scenario, box_id)
            tx_arr = np.array(tx)
            val_arr = np.array(values)
            mask = tx_arr <= current_time
            axes[0].step(tx_arr, val_arr, where="post", color="#c7cdd6", linewidth=0.8)
            axes[0].step(tx_arr[mask], val_arr[mask], where="post", color=color, linewidth=1.8, label=box_id)
        axes[0].axhline(24, color="#111827", linestyle="--", linewidth=0.9, label="capacity 24")
        axes[0].set_ylabel("Occupied slots")
        axes[0].grid(True, alpha=0.22)
        axes[0].legend(loc="upper left", fontsize=7, ncol=3)

        visible = times <= current_time
        axes[1].plot(times, pending, color="#c7cdd6", linewidth=0.8)
        axes[1].plot(times[visible], pending[visible], color="#b45309", linewidth=2.0, label="pending queue")
        axes[1].set_ylabel("Pending queue size")
        axes[1].set_xlabel("State-machine timestamp step")
        axes[1].grid(True, alpha=0.22)
        axes[1].legend(loc="upper left", fontsize=8)

        for ax in axes:
            ax.axvline(hold_time, color="#d62728", linestyle=":", linewidth=1.3)
            ax.axvline(resume_time, color="#2ca02c", linestyle=":", linewidth=1.3)
            ax.axvline(current_time, color="#111827", linewidth=0.8, alpha=0.55)
        axes[0].text(hold_time + 1, 22, "category hold", color="#d62728", fontsize=8)
        axes[0].text(resume_time - 23, 20, "resume/drain", color="#2ca02c", fontsize=8)
        fig.suptitle(f"Output boxes and pending queue | frame {frame_no}/{len(frame_times)} | {scenario}", fontsize=11)
        frames.append(capture_frame(fig))
        plt.close(fig)

    overlay_rows.append(
        {
            "animation_id": "output_pending_timeline_animation_v1",
            "overlay_type": "hold_resume_markers",
            "scenario_id": scenario,
            "event_ref": "category_hold/category_resume",
            "display_text": "Hold starts when output_box_A is full; pending queue drains after resume.",
            "source_file": "sorting_state_machine_event_log_v1.csv;category_hold_resume_events_v1.csv;pending_queue_log_v1.csv",
            "notes": f"hold_time={hold_time};resume_time={resume_time};max_pending={int(pending.max())}",
        }
    )
    save_animation(
        "output_pending_timeline_animation_v1",
        frames,
        TIMELINE_GIF,
        [
            "output_box_occupancy_timeline_v1.csv",
            "pending_queue_log_v1.csv",
            "category_hold_resume_events_v1.csv",
            "sorting_state_machine_event_log_v1.csv",
        ],
        manifest_rows,
        frame_rows,
        "Timeline animation shows output box capacity, pending queue size, and hold/resume markers.",
    )


def metric_value(metrics: list[dict[str, str]], name: str, default: str = "") -> str:
    for row in metrics:
        if row["metric_name"] == name:
            return row["value"]
    return default


def generate_dashboard(data: dict[str, list[dict[str, str]]]) -> dict[str, str]:
    metrics = data["simulation_chain_key_metrics_v1.csv"]
    axis_summary = read_csv("axis_tracking_error_summary_v1.csv")
    robustness = data["servo_robustness_error_summary_v1.csv"]
    throughput = read_csv("throughput_summary_v1.csv")
    scenario_batch = read_csv("scenario_batch_time_summary_v1.csv")

    baseline_throughput = next(
        (row["value"] for row in throughput if row["scenario_id"] == "baseline" and row["throughput_metric"] == "baseline_samples_per_hour_elapsed"),
        metric_value(metrics, "baseline samples_per_hour_elapsed", "n/a"),
    )
    total_samples = metric_value(metrics, "occupied slots", "n/a")
    abnormal_samples = metric_value(metrics, "abnormal sample count", "n/a")
    bottleneck_stage = next((row["bottleneck_stage"] for row in scenario_batch if row["scenario_id"] == "baseline"), "n/a")
    balanced_rmse = [as_float(row["rmse_mm"]) for row in axis_summary if row["parameter_set_id"] == "balanced_pid"]
    robustness_rmse = [as_float(row["rmse_mean_mm"]) for row in robustness]
    tracking_rmse = round(max(balanced_rmse), 3) if balanced_rmse else "n/a"
    robust_rmse = round(max(robustness_rmse), 3) if robustness_rmse else "n/a"

    values = {
        "baseline throughput": f"{baseline_throughput} samples/hour",
        "total samples": f"{total_samples}",
        "abnormal samples": f"{abnormal_samples}",
        "bottleneck stage": bottleneck_stage,
        "7B-6 tracking RMSE": f"{tracking_rmse} mm max axis, balanced_pid",
        "7B-7 robustness RMSE": f"{robust_rmse} mm max axis mean",
        "mechanical baseline": "Stage 7A-3f v1.7 accepted; v1.8 rejected",
    }

    fig, ax = plt.subplots(figsize=(10.0, 5.8), dpi=150)
    ax.axis("off")
    fig.patch.set_facecolor("#f8fafc")
    ax.set_title("Stage 7B-9 Python Simulation Animation Dashboard", fontsize=15, loc="left", pad=18)
    ax.text(0.0, 0.88, "Python animation package, not Isaac Sim. No camera logic; input occupancy is table-driven.", fontsize=9, color="#374151")
    y_positions = [0.72, 0.56, 0.40, 0.24]
    cards = [
        ("baseline throughput", values["baseline throughput"], "#2f6fdd"),
        ("total samples", values["total samples"], "#111827"),
        ("abnormal samples", values["abnormal samples"], "#d62728"),
        ("bottleneck stage", values["bottleneck stage"], "#b45309"),
        ("7B-6 tracking RMSE", values["7B-6 tracking RMSE"], "#2ca02c"),
        ("7B-7 robustness RMSE", values["7B-7 robustness RMSE"], "#9467bd"),
        ("selected mechanical baseline", values["mechanical baseline"], "#0f766e"),
    ]
    for idx, (label, value, color) in enumerate(cards):
        row = idx // 2
        col = idx % 2
        x0 = 0.02 + col * 0.48
        y0 = y_positions[row] if row < len(y_positions) else 0.08
        width = 0.44 if idx < 6 else 0.92
        ax.add_patch(plt.Rectangle((x0, y0), width, 0.11, facecolor="white", edgecolor="#d1d5db", linewidth=0.8))
        ax.text(x0 + 0.02, y0 + 0.071, label, fontsize=8, color="#4b5563")
        ax.text(x0 + 0.02, y0 + 0.029, value, fontsize=11, color=color, weight="bold")
    ax.text(0.02, 0.03, f"Generated: {datetime.now().isoformat(timespec='seconds')}", fontsize=7.5, color="#6b7280")
    DASHBOARD_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(DASHBOARD_PNG, bbox_inches="tight")
    plt.close(fig)
    return values


def write_event_overlay(rows: list[dict[str, object]]) -> None:
    write_csv(
        EVENT_OVERLAY_CSV,
        ["animation_id", "overlay_type", "scenario_id", "event_ref", "display_text", "source_file", "notes"],
        rows,
    )


def write_report(manifest_rows: list[dict[str, object]], dashboard_values: dict[str, str]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    gif_success = [row for row in manifest_rows if row["format"] == "gif" and row["generation_status"] == "success"]
    mp4_rows = [row for row in manifest_rows if row["format"] == "mp4"]
    mp4_status = "; ".join(f"{row['animation_name']}={row['generation_status']}" for row in mp4_rows) or "not attempted"
    lines = [
        "# Stage 7B-9 Python Simulation Animation Package Report",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "- Stage scope: Python animation package, not Isaac Sim.",
        "- Camera status: no camera logic is used.",
        "- Input occupancy source: internal tube occupancy table.",
        "- Data basis: Stage 7B state machine, trajectory waypoints/segments, and time-stepped Cartesian motion trace.",
        "- Mechanical baseline: Stage 7A-3f v1.7 is the accepted current baseline; v1.8 is rejected.",
        "",
        "## Generated animation logic",
        "",
        "- Top-view animation shows the input rack, output boxes, manual review area, TCP/gripper XY motion, tube pick/place movement, abnormal samples routed to manual review, and category hold/resume overlay.",
        "- XYZ animation shows X/Y/Z over time, safe_z, pick_z, place_z, scan_z, and low-Z samples constrained to pick/place/scan zones.",
        "- Output/pending timeline animation shows output box occupancy, capacity, pending queue size, and hold/resume scheduling markers.",
        "- Dashboard summarizes baseline throughput, total samples, abnormal samples, bottleneck stage, 7B-6 tracking RMSE, 7B-7 robustness RMSE, and selected mechanical baseline v1.7.",
        "",
        "## Successful GIF outputs",
        "",
    ]
    lines.extend(f"- `{row['output_path']}` ({row['frame_count']} frames)" for row in gif_success)
    lines.extend(
        [
            "",
            "## MP4 status",
            "",
            f"- {mp4_status}",
            "- MP4 generation failure or absence is only a warning and does not affect GIF acceptance.",
            "",
            "## Dashboard metrics",
            "",
        ]
    )
    lines.extend(f"- {key}: {value}" for key, value in dashboard_values.items())
    lines.extend(
        [
            "",
            "## Intended use and next stages",
            "",
            "- These animations are for course presentation and report explanation.",
            "- A future stage may still prepare SolidWorks presentation screenshots or Isaac Sim high-quality display simulation.",
            "- This stage does not automatically enter the next stage.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ANIM_DIR.mkdir(parents=True, exist_ok=True)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    data = load_data()
    manifest_rows: list[dict[str, object]] = []
    frame_rows: list[dict[str, object]] = []
    overlay_rows: list[dict[str, object]] = []

    generate_top_view_animation(data, manifest_rows, frame_rows, overlay_rows)
    generate_xyz_animation(data, manifest_rows, frame_rows, overlay_rows)
    generate_timeline_animation(data, manifest_rows, frame_rows, overlay_rows)
    dashboard_values = generate_dashboard(data)

    write_csv(
        MANIFEST_CSV,
        ["animation_id", "animation_name", "output_path", "format", "frame_count", "duration_s", "source_files", "generation_status", "notes"],
        manifest_rows,
    )
    write_csv(
        FRAME_SUMMARY_CSV,
        ["animation_id", "output_path", "frame_count", "fps", "duration_s", "representative_frames_saved", "notes"],
        frame_rows,
    )
    write_event_overlay(overlay_rows)
    write_report(manifest_rows, dashboard_values)

    print("generation_status=PASS")
    print(f"gif_success_count={sum(1 for row in manifest_rows if row['format'] == 'gif' and row['generation_status'] == 'success')}")
    print(f"mp4_success_count={sum(1 for row in manifest_rows if row['format'] == 'mp4' and row['generation_status'] == 'success')}")
    print(f"mp4_warning_count={sum(1 for row in manifest_rows if row['format'] == 'mp4' and row['generation_status'] == 'warning')}")
    print(f"manifest={MANIFEST_CSV.relative_to(ROOT).as_posix()}")
    print(f"report={REPORT_MD.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
