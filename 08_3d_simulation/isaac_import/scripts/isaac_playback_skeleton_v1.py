"""This script is an Isaac Sim playback skeleton and may require Isaac Sim Python environment.

It is intentionally pseudo-operational for Stage 7D-1. Stage 7D-2 can replace
the placeholder functions with concrete Isaac Sim API calls after USD import.
"""

from __future__ import annotations

import csv
from pathlib import Path
from time import sleep


ROOT = Path(__file__).resolve().parents[3]
IMPORT_DIR = ROOT / "08_3d_simulation" / "isaac_import"
USD_ASSET_PLACEHOLDER = IMPORT_DIR / "assets" / "blood_sorting_robot_v7_3f_v1_7.usd"
JOINT_COMMANDS_CSV = IMPORT_DIR / "isaac_joint_command_timeseries_v1.csv"
TUBE_EVENTS_CSV = IMPORT_DIR / "isaac_tube_attach_detach_events_v1.csv"
SCENE_HIERARCHY_CSV = IMPORT_DIR / "isaac_scene_hierarchy_v1.csv"
JOINT_CONFIG_CSV = IMPORT_DIR / "isaac_joint_config_v1.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_usd_asset() -> None:
    # Stage 7D-2 should replace this with an Isaac Sim stage/open reference call.
    print(f"load_usd_asset placeholder: {USD_ASSET_PLACEHOLDER.as_posix()}")


def resolve_joints(joint_config: list[dict[str, str]]) -> dict[str, str]:
    # Stage 7D-2 should resolve Articulation/Joint prim handles here.
    return {row["joint_name"]: row["child_prim"] for row in joint_config}


def apply_joint_commands(joints: dict[str, str], command: dict[str, str]) -> None:
    # Stage 7D-2 should set Isaac joint targets in meters.
    _ = {
        "joint_y_gantry": float(command["joint_y_gantry_m"]),
        "joint_x_slider": float(command["joint_x_slider_m"]),
        "joint_z_axis": float(command["joint_z_axis_m"]),
        "joint_gripper_left": float(command["gripper_left_m"]),
        "joint_gripper_right": float(command["gripper_right_m"]),
    }
    print(f"time={command['time_s']} task={command['active_task_id']} tube={command['active_tube_id']} joints={len(joints)}")


def apply_tube_event(event: dict[str, str]) -> None:
    # Stage 7D-2 should re-parent the tube visual or switch visible tube instances.
    print(
        "tube_event "
        f"{event['event_type']} {event['tube_id']} {event['from_parent']} -> {event['to_parent']} target={event['target_prim']}"
    )


def display_state_machine_overlay(command: dict[str, str], tube_events_by_time: dict[str, list[dict[str, str]]]) -> None:
    # Stage 7D-2 can show hold/resume/manual_review overlays using Stage 7B event tables.
    for event in tube_events_by_time.get(command["time_s"], []):
        apply_tube_event(event)


def main() -> int:
    scene_hierarchy = read_csv(SCENE_HIERARCHY_CSV)
    joint_config = read_csv(JOINT_CONFIG_CSV)
    commands = read_csv(JOINT_COMMANDS_CSV)
    tube_events = read_csv(TUBE_EVENTS_CSV)
    tube_events_by_time: dict[str, list[dict[str, str]]] = {}
    for event in tube_events:
        tube_events_by_time.setdefault(event["time_s"], []).append(event)

    load_usd_asset()
    print(f"scene prim count={len(scene_hierarchy)}")
    joints = resolve_joints(joint_config)

    previous_time = 0.0
    for command in commands[:20]:
        current_time = float(command["time_s"])
        sleep(max(0.0, min(current_time - previous_time, 0.02)))
        apply_joint_commands(joints, command)
        display_state_machine_overlay(command, tube_events_by_time)
        previous_time = current_time

    print("playback_skeleton_status=COMPLETE_PLACEHOLDER")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
