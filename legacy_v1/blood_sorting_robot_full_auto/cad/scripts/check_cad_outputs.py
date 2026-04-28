from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_CUSTOM = [
    "base_plate.step", "input_tube_rack.step", "output_tube_rack.step", "test_tube_set.step",
    "y_axis_mounting_blocks.step", "x_axis_beam.step", "z_axis_mounting_plate.step",
    "motor_mounting_plates.step", "gripper_adapter.step", "sensor_bracket.step", "control_box_mount.step",
]
REQUIRED_FALLBACK = [
    "fallback_nema17_motor.step", "fallback_mgn12_rail.step", "fallback_mgn12_slider.step",
    "fallback_t8_lead_screw.step", "fallback_gt2_belt.step", "fallback_coupling.step",
    "fallback_bearing_block.step", "fallback_2020_profile.step", "fallback_cable_chain.step",
    "fallback_limit_switch.step", "fallback_sensor_module.step", "fallback_emergency_stop.step",
    "fallback_control_box.step", "fallback_parallel_gripper.step", "fallback_fasteners.step",
]
REQUIRED_MATLAB = [
    "main.m", "config.m", "generate_rack_positions.m", "generate_sorting_tasks.m",
    "generate_waypoints.m", "trapezoid_trajectory.m", "simulate_pid_axis.m",
    "simulate_three_axis_robot.m", "plot_results.m", "animate_sorting_robot.m", "export_results.m",
]


def check_file(path: Path, errors: list[str]):
    if not path.exists():
        errors.append(f"Missing: {path}")
    elif path.is_file() and path.stat().st_size <= 0:
        errors.append(f"Empty: {path}")


def main():
    errors = []
    for f in REQUIRED_CUSTOM:
        check_file(ROOT / "cad/custom_parts/step" / f, errors)
    for f in REQUIRED_FALLBACK:
        check_file(ROOT / "cad/standard_parts/fallback_generated" / f, errors)
    check_file(ROOT / "cad/assembly/blood_sorting_robot_assembly.step", errors)
    check_file(ROOT / "cad/standard_parts/standard_parts_manifest.csv", errors)
    check_file(ROOT / "README.md", errors)
    for f in REQUIRED_MATLAB:
        check_file(ROOT / "simulation/matlab" / f, errors)
    check_file(ROOT / "simulation/python/simulate_pid_robot.py", errors)

    subprocess.run([sys.executable, str(ROOT / "simulation/python/simulate_pid_robot.py")], check=True)
    figures = list((ROOT / "results/figures").glob("*.png"))
    if not figures:
        errors.append("No result figures generated in results/figures")

    log_path = ROOT / "results/logs/project_build_log.txt"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if errors:
        log_path.write_text("QUALITY CHECK FAILED\n" + "\n".join(errors), encoding="utf-8")
        print("\n".join(errors))
        raise SystemExit(1)
    log_path.write_text("QUALITY CHECK PASSED\nGenerated files checked successfully.\n", encoding="utf-8")
    print(f"Quality check passed. Log: {log_path}")


if __name__ == "__main__":
    main()
