from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TRACE_CSV = ROOT / "06_simulation" / "time_stepped_motion_trace_v1.csv"
OUTPUT_CSV = ROOT / "08_3d_simulation" / "isaac_import" / "isaac_joint_command_timeseries_v1.csv"

MM_TO_M = 0.001
GRIPPER_OPEN_M = 0.012
GRIPPER_CLOSED_M = 0.0


def gripper_commands(state: str) -> tuple[float, float]:
    normalized = state.strip().lower()
    if normalized == "closed":
        return GRIPPER_CLOSED_M, GRIPPER_CLOSED_M
    return GRIPPER_OPEN_M, -GRIPPER_OPEN_M


def to_float(value: str) -> float:
    return float(value)


def main() -> int:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with TRACE_CSV.open(newline="", encoding="utf-8") as source, OUTPUT_CSV.open("w", newline="", encoding="utf-8") as target:
        reader = csv.DictReader(source)
        fieldnames = [
            "time_s",
            "joint_y_gantry_m",
            "joint_x_slider_m",
            "joint_z_axis_m",
            "gripper_left_m",
            "gripper_right_m",
            "active_task_id",
            "active_tube_id",
            "notes",
        ]
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        row_count = 0
        for row in reader:
            left_m, right_m = gripper_commands(row["gripper_state"])
            writer.writerow(
                {
                    "time_s": row["time_s"],
                    "joint_y_gantry_m": round(to_float(row["y_mm"]) * MM_TO_M, 6),
                    "joint_x_slider_m": round(to_float(row["x_mm"]) * MM_TO_M, 6),
                    "joint_z_axis_m": round(to_float(row["z_mm"]) * MM_TO_M, 6),
                    "gripper_left_m": round(left_m, 6),
                    "gripper_right_m": round(right_m, 6),
                    "active_task_id": row["task_id"],
                    "active_tube_id": row["tube_id"],
                    "notes": f"scenario={row['scenario_id']}; source mm converted to meters for Isaac playback",
                }
            )
            row_count += 1
    print("conversion_status=PASS")
    print(f"source={TRACE_CSV.relative_to(ROOT).as_posix()}")
    print(f"output={OUTPUT_CSV.relative_to(ROOT).as_posix()}")
    print(f"rows={row_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
