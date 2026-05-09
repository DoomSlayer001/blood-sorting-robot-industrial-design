from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM3D = ROOT / "08_3d_simulation"
SW = SIM3D / "solidworks_motion"
BL = SIM3D / "blender_playback"

REQUIRED_FILES = {
    "SolidWorks guide": SW / "solidworks_motion_execution_guide_v1.md",
    "SolidWorks group mapping": SW / "solidworks_motion_group_mapping_v1.csv",
    "SolidWorks mate plan": SW / "solidworks_motion_mate_plan_v1.csv",
    "SolidWorks driver plan": SW / "solidworks_motion_driver_plan_v1.csv",
    "SolidWorks collision check plan": SW / "solidworks_motion_collision_check_plan_v1.csv",
    "Blender guide": BL / "blender_playback_execution_guide_v1.md",
    "Blender scene hierarchy": BL / "blender_scene_hierarchy_v1.csv",
    "Blender group mapping": BL / "blender_group_mapping_v1.csv",
    "Blender keyframe manifest": BL / "blender_keyframe_input_manifest_v1.csv",
    "Blender keyframe conversion script": BL / "scripts" / "convert_motion_trace_to_blender_keyframes_v1.py",
    "Blender playback skeleton": BL / "scripts" / "blender_playback_skeleton_v1.py",
    "Blender material color map": BL / "blender_material_color_map_v1.csv",
    "Dual branch plan": SIM3D / "dual_branch_3d_simulation_plan_v1.csv",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def file_ok(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def text_contains(path: Path, terms: list[str]) -> bool:
    text = path.read_text(encoding="utf-8").lower() if path.exists() else ""
    return all(term.lower() in text for term in terms)


def main() -> int:
    issues: list[str] = []
    for label, path in REQUIRED_FILES.items():
        if not file_ok(path):
            issues.append(f"missing_or_empty={label}:{path.relative_to(ROOT).as_posix()}")

    sw_driver = REQUIRED_FILES["SolidWorks driver plan"]
    bl_mapping = REQUIRED_FILES["Blender group mapping"]
    sw_group = REQUIRED_FILES["SolidWorks group mapping"]

    sw_xyz_ok = text_contains(sw_driver, ["y_mm", "x_mm", "z_mm", "Y gantry", "X slider", "Z axis"])
    bl_xyz_ok = text_contains(bl_mapping, ["y_mm", "x_mm", "z_mm", "y_gantry_moving_group", "x_slider_moving_group", "z_axis_moving_group"])
    sw_gripper_ok = text_contains(sw_driver, ["gripper_state"]) and text_contains(sw_group, ["gripper_left_finger_group", "gripper_right_finger_group"])
    bl_gripper_ok = text_contains(bl_mapping, ["gripper_left_finger_group", "gripper_right_finger_group", "gripper_state"])

    if not sw_xyz_ok:
        issues.append("solidworks_xyz_motion_mapping_missing")
    if not bl_xyz_ok:
        issues.append("blender_xyz_motion_mapping_missing")
    if not sw_gripper_ok:
        issues.append("solidworks_gripper_mapping_missing")
    if not bl_gripper_ok:
        issues.append("blender_gripper_mapping_missing")

    keyframe_commands = BL / "blender_keyframe_commands_v1.csv"
    keyframe_rows = read_csv(keyframe_commands) if keyframe_commands.exists() else []
    if not keyframe_rows:
        issues.append("blender_keyframe_commands_missing_or_empty")
    else:
        required_fields = {
            "frame",
            "time_s",
            "object_group",
            "location_x_m",
            "location_y_m",
            "location_z_m",
            "gripper_opening_m",
            "event_label",
        }
        missing_fields = required_fields - set(keyframe_rows[0].keys())
        if missing_fields:
            issues.append(f"blender_keyframe_commands_missing_fields={','.join(sorted(missing_fields))}")

    validation_status = "PASS" if not issues else "FAIL"
    print(f"validation_status={validation_status}")
    print(f"solidworks_guide_exists={file_ok(REQUIRED_FILES['SolidWorks guide'])}")
    print(f"solidworks_group_mapping_exists={file_ok(REQUIRED_FILES['SolidWorks group mapping'])}")
    print(f"solidworks_mate_plan_exists={file_ok(REQUIRED_FILES['SolidWorks mate plan'])}")
    print(f"solidworks_driver_plan_exists={file_ok(REQUIRED_FILES['SolidWorks driver plan'])}")
    print(f"solidworks_collision_check_plan_exists={file_ok(REQUIRED_FILES['SolidWorks collision check plan'])}")
    print(f"blender_guide_exists={file_ok(REQUIRED_FILES['Blender guide'])}")
    print(f"blender_scene_hierarchy_exists={file_ok(REQUIRED_FILES['Blender scene hierarchy'])}")
    print(f"blender_group_mapping_exists={file_ok(REQUIRED_FILES['Blender group mapping'])}")
    print(f"blender_keyframe_manifest_exists={file_ok(REQUIRED_FILES['Blender keyframe manifest'])}")
    print(f"blender_keyframe_conversion_script_exists={file_ok(REQUIRED_FILES['Blender keyframe conversion script'])}")
    print(f"blender_playback_skeleton_exists={file_ok(REQUIRED_FILES['Blender playback skeleton'])}")
    print(f"blender_material_color_map_exists={file_ok(REQUIRED_FILES['Blender material color map'])}")
    print(f"dual_branch_plan_exists={file_ok(REQUIRED_FILES['Dual branch plan'])}")
    print(f"solidworks_xyz_motion_mapping={'PASS' if sw_xyz_ok else 'FAIL'}")
    print(f"blender_xyz_motion_mapping={'PASS' if bl_xyz_ok else 'FAIL'}")
    print(f"solidworks_gripper_mapping={'PASS' if sw_gripper_ok else 'FAIL'}")
    print(f"blender_gripper_mapping={'PASS' if bl_gripper_ok else 'FAIL'}")
    print(f"blender_keyframe_command_rows={len(keyframe_rows)}")
    for issue in issues:
        print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
