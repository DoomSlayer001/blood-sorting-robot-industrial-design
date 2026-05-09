from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SIM3D_DIR = REPO_ROOT / "08_3d_simulation"
IMPORT_DIR = SIM3D_DIR / "isaac_import"
REPORT_DIR = REPO_ROOT / "reports"

SCENE_HIERARCHY_CSV = IMPORT_DIR / "isaac_scene_hierarchy_v1.csv"
JOINT_CONFIG_CSV = IMPORT_DIR / "isaac_joint_config_v1.csv"
COLLISION_PROXY_CSV = IMPORT_DIR / "isaac_collision_proxy_config_v1.csv"
PLAYBACK_INPUT_CSV = IMPORT_DIR / "isaac_playback_input_manifest_v1.csv"
TUBE_EVENTS_CSV = IMPORT_DIR / "isaac_tube_attach_detach_events_v1.csv"
JOINT_COMMANDS_CSV = IMPORT_DIR / "isaac_joint_command_timeseries_v1.csv"
PLAYBACK_SKELETON = IMPORT_DIR / "scripts" / "isaac_playback_skeleton_v1.py"
CONVERT_SCRIPT = IMPORT_DIR / "scripts" / "convert_motion_trace_to_isaac_commands_v1.py"
ENV_CHECK_CSV = IMPORT_DIR / "isaac_import_environment_check_v1.csv"
BASELINE_MANIFEST_CSV = REPO_ROOT / "03_cad" / "freecad_assembly" / "current_mechanical_baseline_manifest_v1.csv"
BASELINE_STEP = REPO_ROOT / "03_cad" / "freecad_assembly" / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_7.step"
TRACE_CSV = REPO_ROOT / "06_simulation" / "time_stepped_motion_trace_v1.csv"
REPORT_MD = REPORT_DIR / "stage_7d1_isaac_sim_import_preparation_report.md"

REQUIRED_FILES = [
    SCENE_HIERARCHY_CSV,
    JOINT_CONFIG_CSV,
    COLLISION_PROXY_CSV,
    PLAYBACK_INPUT_CSV,
    TUBE_EVENTS_CSV,
    JOINT_COMMANDS_CSV,
    PLAYBACK_SKELETON,
    CONVERT_SCRIPT,
    ENV_CHECK_CSV,
    REPORT_MD,
]

REQUIRED_SCENE_PRIMS = {
    "/World/blood_sorting_robot",
    "/World/blood_sorting_robot/fixed_base",
    "/World/blood_sorting_robot/y_gantry_moving_group",
    "/World/blood_sorting_robot/y_gantry_moving_group/x_slider_moving_group",
    "/World/blood_sorting_robot/y_gantry_moving_group/x_slider_moving_group/z_axis_moving_group",
    "/World/blood_sorting_robot/y_gantry_moving_group/x_slider_moving_group/z_axis_moving_group/gripper_left_finger",
    "/World/blood_sorting_robot/y_gantry_moving_group/x_slider_moving_group/z_axis_moving_group/gripper_right_finger",
    "/World/blood_sorting_robot/tube_dynamic_group",
    "/World/blood_sorting_robot/cable_chain_visual_group",
}

REQUIRED_JOINTS = {
    "joint_y_gantry",
    "joint_x_slider",
    "joint_z_axis",
    "joint_gripper_left",
    "joint_gripper_right",
}

REQUIRED_TUBE_EVENT_TYPES = {
    "before_pick",
    "attach_to_gripper",
    "scan_attached",
    "detach_to_output_box",
    "detach_to_manual_review",
    "pick_failed_no_attach",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def status_row(check_item: str, expected: str, observed: str, status: str, notes: str) -> dict[str, object]:
    return {
        "check_item": check_item,
        "expected": expected,
        "observed": observed,
        "status": status,
        "notes": notes,
    }


def isaac_module_available() -> bool:
    return importlib.util.find_spec("omni") is not None or importlib.util.find_spec("isaacsim") is not None


def update_environment_check() -> tuple[list[dict[str, object]], bool]:
    isaac_available = isaac_module_available()
    rows = [
        status_row("Python available", "python can run", sys.version.split()[0], "PASS", "Python runtime is available."),
        status_row(
            "repository paths valid",
            "required repo paths exist",
            f"repo={REPO_ROOT.exists()}, import_dir={IMPORT_DIR.exists()}",
            "PASS" if REPO_ROOT.exists() and IMPORT_DIR.exists() else "FAIL",
            "Repository and Isaac import directories are present.",
        ),
        status_row(
            "time-stepped trace exists",
            "06_simulation/time_stepped_motion_trace_v1.csv exists",
            f"exists={TRACE_CSV.exists()}",
            "PASS" if TRACE_CSV.exists() else "FAIL",
            "Trace drives X/Y/Z playback.",
        ),
        status_row(
            "current mechanical baseline STEP exists",
            "v1.7 STEP exists",
            f"exists={BASELINE_STEP.exists()}",
            "PASS" if BASELINE_STEP.exists() else "FAIL",
            "Accepted Stage 7A-3f v1.7 baseline.",
        ),
        status_row(
            "Isaac Sim Python module available or not",
            "availability recorded",
            f"available={isaac_available}",
            "PASS" if isaac_available else "WARNING",
            "Missing Isaac Sim is warning only for Stage 7D-1.",
        ),
        status_row("ffmpeg not relevant", "ffmpeg is not required", "not checked", "PASS", "This is not video rendering."),
        status_row("USD conversion not performed", "conversion remains pending", "pending", "PASS", "Stage 7D-1 prepares import only."),
        status_row("import validation pending", "final import validation remains pending", "pending", "PASS", "Stage 7D-2 may attempt import/playback."),
    ]
    write_csv(ENV_CHECK_CSV, ["check_item", "expected", "observed", "status", "notes"], rows)
    return rows, isaac_available


def main() -> int:
    issues: list[str] = []
    warnings: list[str] = []
    env_rows, isaac_available = update_environment_check()

    for path in REQUIRED_FILES:
        if not path.exists():
            issues.append(f"missing file: {path.relative_to(REPO_ROOT).as_posix()}")
        elif path.stat().st_size <= 0 and path.name != ".gitkeep":
            issues.append(f"empty file: {path.relative_to(REPO_ROOT).as_posix()}")

    scene_rows = read_csv(SCENE_HIERARCHY_CSV) if SCENE_HIERARCHY_CSV.exists() else []
    joint_rows = read_csv(JOINT_CONFIG_CSV) if JOINT_CONFIG_CSV.exists() else []
    collision_rows = read_csv(COLLISION_PROXY_CSV) if COLLISION_PROXY_CSV.exists() else []
    playback_inputs = read_csv(PLAYBACK_INPUT_CSV) if PLAYBACK_INPUT_CSV.exists() else []
    tube_events = read_csv(TUBE_EVENTS_CSV) if TUBE_EVENTS_CSV.exists() else []
    command_rows = read_csv(JOINT_COMMANDS_CSV) if JOINT_COMMANDS_CSV.exists() else []

    scene_prims = {row["prim_path"] for row in scene_rows}
    missing_prims = sorted(REQUIRED_SCENE_PRIMS - scene_prims)
    if missing_prims:
        issues.append(f"scene hierarchy missing prims: {', '.join(missing_prims)}")

    joint_names = {row["joint_name"] for row in joint_rows}
    missing_joints = sorted(REQUIRED_JOINTS - joint_names)
    if missing_joints:
        issues.append(f"joint config missing joints: {', '.join(missing_joints)}")
    xyz_ok = all(
        any(row["joint_name"] == name and row["joint_type"] == "prismatic" and "0.001" in row["notes"] for row in joint_rows)
        for name in ["joint_y_gantry", "joint_x_slider", "joint_z_axis"]
    )
    if not xyz_ok:
        issues.append("X/Y/Z joints must be prismatic and document mm-to-meter scale 0.001")
    gripper_ok = all(name in joint_names for name in ["joint_gripper_left", "joint_gripper_right"])
    if not gripper_ok:
        issues.append("gripper joints are incomplete")

    required_proxy_keywords = [
        "base",
        "input_rack",
        "output",
        "manual_review",
        "x_beam",
        "z_axis",
        "gripper",
        "tube",
        "enclosure",
        "control_box",
        "cable_chain",
    ]
    proxy_text = " ".join(row["proxy_id"] + " " + row["prim_path"] + " " + row["source_group"] for row in collision_rows).lower()
    missing_proxy_keywords = [keyword for keyword in required_proxy_keywords if keyword not in proxy_text]
    if missing_proxy_keywords:
        issues.append(f"collision proxy config missing proxy coverage: {', '.join(missing_proxy_keywords)}")

    required_inputs = {
        "06_simulation/time_stepped_motion_trace_v1.csv",
        "06_simulation/trajectory_waypoints_v1.csv",
        "06_simulation/sorting_state_machine_task_result_v1.csv",
        "08_3d_simulation/tube_attach_detach_event_logic_v1.csv",
        "06_simulation/category_hold_resume_events_v1.csv",
        "06_simulation/pending_queue_log_v1.csv",
        "06_simulation/abnormal_handling_log_v1.csv",
    }
    input_files = {row["source_file"] for row in playback_inputs}
    missing_inputs = sorted(required_inputs - input_files)
    if missing_inputs:
        issues.append(f"playback input manifest missing inputs: {', '.join(missing_inputs)}")

    tube_event_types = {row["event_type"] for row in tube_events}
    missing_tube_types = sorted(REQUIRED_TUBE_EVENT_TYPES - tube_event_types)
    if missing_tube_types:
        issues.append(f"tube attach/detach events missing event types: {', '.join(missing_tube_types)}")

    if len(command_rows) == 0:
        issues.append("joint command timeseries is empty")
    else:
        command_fields = set(command_rows[0].keys())
        required_command_fields = {
            "time_s",
            "joint_y_gantry_m",
            "joint_x_slider_m",
            "joint_z_axis_m",
            "gripper_left_m",
            "gripper_right_m",
            "active_task_id",
            "active_tube_id",
            "notes",
        }
        missing_command_fields = sorted(required_command_fields - command_fields)
        if missing_command_fields:
            issues.append(f"joint command timeseries missing fields: {', '.join(missing_command_fields)}")

    baseline_rows = read_csv(BASELINE_MANIFEST_CSV)
    v17_selected = any(
        row["selected_version"] == "v1.7"
        and row["selected_file"] == "03_cad/freecad_assembly/blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_7.step"
        and row["used_for_downstream"] == "yes"
        for row in baseline_rows
    )
    if not v17_selected:
        issues.append("current mechanical baseline is not clearly selected as v1.7 preview STEP")

    if not isaac_available:
        warnings.append("Isaac Sim Python module is not available in this environment; warning only.")
    for row in env_rows:
        if row["status"] == "FAIL":
            issues.append(f"environment check failed: {row['check_item']}")

    skeleton_text = PLAYBACK_SKELETON.read_text(encoding="utf-8") if PLAYBACK_SKELETON.exists() else ""
    if "This script is an Isaac Sim playback skeleton and may require Isaac Sim Python environment." not in skeleton_text:
        issues.append("playback skeleton missing required Isaac Sim environment notice")

    validation_status = "PASS" if not issues else "FAIL"
    print(f"validation_status={validation_status}")
    print(f"scene_hierarchy_rows={len(scene_rows)}")
    print(f"joint_config_rows={len(joint_rows)}")
    print(f"collision_proxy_rows={len(collision_rows)}")
    print(f"playback_input_rows={len(playback_inputs)}")
    print(f"tube_event_rows={len(tube_events)}")
    print(f"joint_command_rows={len(command_rows)}")
    print(f"xyz_joints_defined={'yes' if xyz_ok else 'no'}")
    print(f"gripper_joints_defined={'yes' if gripper_ok else 'no'}")
    print(f"current_mechanical_baseline={'v1.7 preview STEP' if v17_selected else 'not confirmed'}")
    print(f"isaac_sim_available={'yes' if isaac_available else 'warning'}")
    for warning in warnings:
        print(f"warning={warning}")
    for issue in issues:
        print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
