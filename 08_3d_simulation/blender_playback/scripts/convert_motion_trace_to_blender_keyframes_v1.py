from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TRACE_CSV = ROOT / "06_simulation" / "time_stepped_motion_trace_v1.csv"
WAYPOINTS_CSV = ROOT / "06_simulation" / "trajectory_waypoints_v1.csv"
EVENT_LOG_CSV = ROOT / "06_simulation" / "sorting_state_machine_event_log_v1.csv"
OUTPUT_CSV = ROOT / "08_3d_simulation" / "blender_playback" / "blender_keyframe_commands_v1.csv"

MM_TO_M = 0.001
FPS = 50
GRIPPER_OPEN_M = 0.012
GRIPPER_CLOSED_M = 0.0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def to_float(value: str, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    return float(value)


def gripper_opening_m(state: str) -> float:
    return GRIPPER_CLOSED_M if state.strip().lower() == "closed" else GRIPPER_OPEN_M


def load_waypoint_metadata() -> dict[tuple[str, str, str], dict[str, str]]:
    metadata: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in read_csv(WAYPOINTS_CSV):
        key = (row["scenario_id"], row["task_id"], row["tube_id"])
        metadata.setdefault(
            key,
            {
                "sample_category": row.get("sample_category", ""),
                "target_type": row.get("target_type", ""),
                "target_box_id": row.get("target_box_id", ""),
                "state_machine_status": row.get("state_machine_status", ""),
            },
        )
    return metadata


def load_event_metadata() -> dict[tuple[str, str, str], dict[str, object]]:
    event_metadata: dict[tuple[str, str, str], dict[str, object]] = {}
    for row in read_csv(EVENT_LOG_CSV):
        key = (row["scenario_id"], row["task_id"], row["tube_id"])
        item = event_metadata.setdefault(
            key,
            {
                "events": set(),
                "pending_sizes": [],
                "notes": [],
            },
        )
        item["events"].add(row.get("event", ""))
        pending_size = row.get("pending_queue_size", "")
        if pending_size != "":
            item["pending_sizes"].append(int(pending_size))
        if row.get("notes"):
            item["notes"].append(row["notes"])
    return event_metadata


def infer_event_label(row: dict[str, str], events: set[str], pending_sizes: list[int]) -> str:
    motion_type = row.get("motion_type", "").lower()
    state_label = row.get("state_label", "").lower()
    segment_index = int(float(row.get("segment_index", "0") or 0))
    event_text = " ".join(events).lower()

    if "pick_failed" in events or "retry_failed" in events:
        return "pick_failed"
    if "category_hold" in events:
        return "hold"
    if pending_sizes and min(pending_sizes) < max(pending_sizes) and segment_index >= 9:
        return "resume"
    if "scan" in motion_type or "scan" in state_label or segment_index in {6, 7, 8}:
        return "scan"
    if "manual_review" in event_text and segment_index >= 9:
        return "manual_review"
    if "place" in motion_type or segment_index >= 9:
        return "place"
    if segment_index in {2, 3, 4} or "gripper_action" in motion_type:
        return "pick"
    return ""


def main() -> int:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    waypoint_metadata = load_waypoint_metadata()
    event_metadata = load_event_metadata()
    fieldnames = [
        "frame",
        "time_s",
        "object_group",
        "location_x_m",
        "location_y_m",
        "location_z_m",
        "rotation_x_deg",
        "rotation_y_deg",
        "rotation_z_deg",
        "gripper_opening_m",
        "active_task_id",
        "active_tube_id",
        "event_label",
        "notes",
    ]
    event_labels_seen: set[str] = set()
    row_count = 0
    with TRACE_CSV.open(newline="", encoding="utf-8") as source, OUTPUT_CSV.open("w", newline="", encoding="utf-8") as target:
        reader = csv.DictReader(source)
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            key = (row["scenario_id"], row["task_id"], row["tube_id"])
            metadata = waypoint_metadata.get(key, {})
            event_item = event_metadata.get(key, {"events": set(), "pending_sizes": [], "notes": []})
            events = event_item["events"]
            pending_sizes = event_item["pending_sizes"]
            event_label = infer_event_label(row, events, pending_sizes)
            if event_label:
                event_labels_seen.add(event_label)
            time_s = to_float(row["time_s"])
            notes = [
                f"scenario={row['scenario_id']}",
                f"motion_type={row.get('motion_type', '')}",
                f"sample_category={metadata.get('sample_category', '')}",
                f"target_type={metadata.get('target_type', '')}",
                "source_mm_converted_to_m",
            ]
            writer.writerow(
                {
                    "frame": int(round(time_s * FPS)),
                    "time_s": f"{time_s:.3f}",
                    "object_group": "robot_motion_stack",
                    "location_x_m": f"{to_float(row['x_mm']) * MM_TO_M:.6f}",
                    "location_y_m": f"{to_float(row['y_mm']) * MM_TO_M:.6f}",
                    "location_z_m": f"{to_float(row['z_mm']) * MM_TO_M:.6f}",
                    "rotation_x_deg": "0.0",
                    "rotation_y_deg": "0.0",
                    "rotation_z_deg": "0.0",
                    "gripper_opening_m": f"{gripper_opening_m(row.get('gripper_state', 'open')):.6f}",
                    "active_task_id": row["task_id"],
                    "active_tube_id": row["tube_id"],
                    "event_label": event_label,
                    "notes": "; ".join(notes),
                }
            )
            row_count += 1

    print("conversion_status=PASS")
    print(f"source={TRACE_CSV.relative_to(ROOT).as_posix()}")
    print(f"waypoints={WAYPOINTS_CSV.relative_to(ROOT).as_posix()}")
    print(f"event_log={EVENT_LOG_CSV.relative_to(ROOT).as_posix()}")
    print(f"output={OUTPUT_CSV.relative_to(ROOT).as_posix()}")
    print(f"rows={row_count}")
    print(f"fps={FPS}")
    print(f"event_labels_seen={','.join(sorted(label for label in event_labels_seen if label))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
