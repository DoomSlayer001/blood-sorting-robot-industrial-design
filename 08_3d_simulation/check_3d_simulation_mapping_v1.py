from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM3D_DIR = ROOT / "08_3d_simulation"
REPORT_DIR = ROOT / "reports"

KINEMATIC_GROUP_CSV = SIM3D_DIR / "kinematic_group_definition_v1.csv"
JOINT_MAPPING_CSV = SIM3D_DIR / "joint_mapping_v1.csv"
TRAJECTORY_MAPPING_CSV = SIM3D_DIR / "trajectory_to_3d_motion_mapping_v1.csv"
TUBE_EVENT_CSV = SIM3D_DIR / "tube_attach_detach_event_logic_v1.csv"
ISAAC_MANIFEST_CSV = SIM3D_DIR / "isaac_sim_import_preparation_manifest_v1.csv"
SOLIDWORKS_MANIFEST_CSV = SIM3D_DIR / "solidworks_motion_preparation_manifest_v1.csv"
ACCEPTANCE_CSV = SIM3D_DIR / "three_d_simulation_acceptance_criteria_v1.csv"
PLATFORM_PLAN_MD = SIM3D_DIR / "three_d_simulation_platform_plan_v1.md"
REPORT_MD = REPORT_DIR / "stage_7d0_3d_simulation_kinematic_hierarchy_report.md"

REQUIRED_FILES = [
    KINEMATIC_GROUP_CSV,
    JOINT_MAPPING_CSV,
    TRAJECTORY_MAPPING_CSV,
    TUBE_EVENT_CSV,
    ISAAC_MANIFEST_CSV,
    SOLIDWORKS_MANIFEST_CSV,
    ACCEPTANCE_CSV,
    PLATFORM_PLAN_MD,
    REPORT_MD,
]

REQUIRED_GROUPS = {
    "fixed_base_group",
    "y_gantry_moving_group",
    "x_slider_moving_group",
    "z_axis_moving_group",
    "gripper_left_finger_group",
    "gripper_right_finger_group",
    "tube_dynamic_group",
    "cable_chain_visual_group",
}

REQUIRED_TUBE_EVENTS = {
    "before_pick",
    "grip_close_at_pick",
    "transport_to_scan",
    "scan_wait",
    "transport_to_place",
    "grip_open_at_output_place",
    "grip_open_at_manual_review_place",
    "pick_failed",
}

REQUIRED_TRAJECTORY_FIELDS = {
    "time_s",
    "x_mm",
    "y_mm",
    "z_mm",
    "gripper_state",
    "tube_id",
    "task_id",
    "sample_category",
    "target_type",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    issues: list[str] = []

    for path in REQUIRED_FILES:
        if not path.exists():
            issues.append(f"missing file: {path.relative_to(ROOT).as_posix()}")
        elif path.stat().st_size <= 0:
            issues.append(f"empty file: {path.relative_to(ROOT).as_posix()}")

    if issues:
        print("validation_status=FAIL")
        for issue in issues:
            print(f"issue={issue}")
        return 1

    groups = read_csv(KINEMATIC_GROUP_CSV)
    joints = read_csv(JOINT_MAPPING_CSV)
    trajectory_map = read_csv(TRAJECTORY_MAPPING_CSV)
    tube_events = read_csv(TUBE_EVENT_CSV)
    isaac_manifest = read_csv(ISAAC_MANIFEST_CSV)
    solidworks_manifest = read_csv(SOLIDWORKS_MANIFEST_CSV)
    acceptance = read_csv(ACCEPTANCE_CSV)

    group_names = {row["group_name"] for row in groups}
    missing_groups = sorted(REQUIRED_GROUPS - group_names)
    if missing_groups:
        issues.append(f"missing required kinematic groups: {', '.join(missing_groups)}")

    prismatic_axes = {
        row["axis"]
        for row in joints
        if row["joint_type"] == "prismatic" and row["joint_name"] in {"joint_x_slider", "joint_y_gantry", "joint_z_axis"}
    }
    if prismatic_axes != {"X", "Y", "Z"}:
        issues.append(f"required X/Y/Z prismatic joints not complete: {sorted(prismatic_axes)}")

    gripper_joints = [row for row in joints if row["joint_name"] in {"joint_gripper_left", "joint_gripper_right"}]
    if len(gripper_joints) != 2 or not all(row["axis"] == "gripper_open_close" for row in gripper_joints):
        issues.append("gripper open/close joints are incomplete")

    tube_event_names = {row["event_name"] for row in tube_events}
    missing_tube_events = sorted(REQUIRED_TUBE_EVENTS - tube_event_names)
    if missing_tube_events:
        issues.append(f"missing tube attach/detach events: {', '.join(missing_tube_events)}")

    trajectory_fields = {row["source_field"] for row in trajectory_map}
    missing_trajectory_fields = sorted(REQUIRED_TRAJECTORY_FIELDS - trajectory_fields)
    if missing_trajectory_fields:
        issues.append(f"trajectory-to-3D mapping missing source fields: {', '.join(missing_trajectory_fields)}")

    baseline_manifest = read_csv(ROOT / "03_cad" / "freecad_assembly" / "current_mechanical_baseline_manifest_v1.csv")
    selected_v17 = any(
        row["selected_version"] == "v1.7"
        and row["status"] in {"ACCEPTED_AS_CURRENT_MECHANICAL_BASELINE", "BASELINE_SELECTED"}
        and row["used_for_downstream"] == "yes"
        for row in baseline_manifest
    )
    rejected_v18 = any(row["selected_version"] == "v1.8" and row["status"] == "NOT_ACCEPTED" for row in baseline_manifest)
    if not selected_v17:
        issues.append("current mechanical baseline manifest does not select v1.7 for downstream use")
    if not rejected_v18:
        issues.append("current mechanical baseline manifest does not mark v1.8 rejected")

    isaac_items = {row["item"]: row["current_status"] for row in isaac_manifest}
    required_isaac_items = {
        "CAD baseline STEP selected",
        "fixed vs moving groups defined",
        "X/Y/Z joints defined",
        "gripper joints defined",
        "trajectory input available",
        "time-stepped trace available",
        "tube attach/detach events defined",
        "collision proxies defined",
        "material assignment optional",
        "USD conversion not yet performed",
        "Isaac Sim playback script not yet created",
        "final import validation pending",
    }
    missing_isaac = sorted(required_isaac_items - set(isaac_items))
    if missing_isaac:
        issues.append(f"Isaac manifest missing items: {', '.join(missing_isaac)}")
    if isaac_items.get("USD conversion not yet performed") != "pending":
        issues.append("Isaac manifest should keep USD conversion pending")
    if isaac_items.get("final import validation pending") != "pending":
        issues.append("Isaac manifest should keep final import validation pending")

    required_solidworks_items = {
        "assembly baseline selected",
        "Y gantry mate needed",
        "X slider mate needed",
        "Z axis mate needed",
        "gripper open/close mate needed",
        "tube attach/detach not native / requires simplified handling",
        "motion path from time-stepped trace available",
        "manual setup required in SolidWorks",
    }
    solidworks_items = {row["item"] for row in solidworks_manifest}
    missing_solidworks = sorted(required_solidworks_items - solidworks_items)
    if missing_solidworks:
        issues.append(f"SolidWorks manifest missing items: {', '.join(missing_solidworks)}")

    if not any(row["criteria_name"] == "Isaac Sim import pending" and row["current_status"] == "PENDING" for row in acceptance):
        issues.append("acceptance criteria must keep Isaac Sim import pending")
    if not any(row["criteria_name"] == "final 3D playback pending" and row["current_status"] == "PENDING" for row in acceptance):
        issues.append("acceptance criteria must keep final 3D playback pending")

    report_text = REPORT_MD.read_text(encoding="utf-8")
    for phrase in [
        "not a 2D animation",
        "kinematic hierarchy",
        "STEP is a static geometry exchange",
        "Y axis",
        "X axis",
        "Z axis",
        "attach/detach",
        "Isaac Sim",
        "SolidWorks Motion",
        "does not automatically enter the next stage",
    ]:
        if phrase not in report_text:
            issues.append(f"report missing phrase: {phrase}")

    validation_status = "PASS" if not issues else "FAIL"
    print(f"validation_status={validation_status}")
    print(f"kinematic_group_rows={len(groups)}")
    print(f"joint_mapping_rows={len(joints)}")
    print(f"trajectory_mapping_rows={len(trajectory_map)}")
    print(f"tube_event_rows={len(tube_events)}")
    print(f"isaac_manifest_rows={len(isaac_manifest)}")
    print(f"solidworks_manifest_rows={len(solidworks_manifest)}")
    print(f"acceptance_criteria_rows={len(acceptance)}")
    print(f"xyz_moving_groups_defined={'yes' if {'y_gantry_moving_group', 'x_slider_moving_group', 'z_axis_moving_group'}.issubset(group_names) else 'no'}")
    print(f"gripper_joints_defined={'yes' if len(gripper_joints) == 2 else 'no'}")
    print(f"tube_attach_detach_defined={'yes' if REQUIRED_TUBE_EVENTS.issubset(tube_event_names) else 'no'}")
    print(f"isaac_import_preparation_ready={'yes' if validation_status == 'PASS' else 'no'}")
    for issue in issues:
        print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
