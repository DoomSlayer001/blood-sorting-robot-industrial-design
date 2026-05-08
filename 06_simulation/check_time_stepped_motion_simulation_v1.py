from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"

TRACE_CSV = SIM_DIR / "time_stepped_motion_trace_v1.csv"
TRAJECTORY_TASK_SUMMARY_CSV = SIM_DIR / "trajectory_task_summary_v1.csv"
CONSTRAINT_CSV = SIM_DIR / "motion_constraint_check_v1.csv"
SAFE_Z_CSV = SIM_DIR / "safe_z_rule_check_v1.csv"
SWEEP_CSV = SIM_DIR / "motion_sweep_collision_precheck_v1.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    issues: list[str] = []
    trace = read_csv(TRACE_CSV)
    trajectory_tasks = read_csv(TRAJECTORY_TASK_SUMMARY_CSV)
    constraints = read_csv(CONSTRAINT_CSV)
    safe_z = read_csv(SAFE_Z_CSV)
    sweep = read_csv(SWEEP_CSV)

    if not trace:
        issues.append("time_stepped_motion_trace is empty")

    generated_keys = {
        (row["scenario_id"], row["task_id"])
        for row in trajectory_tasks
        if row["trajectory_generated"] == "true"
    }
    trace_keys = {(row["scenario_id"], row["task_id"]) for row in trace}
    missing = generated_keys.difference(trace_keys)
    if missing:
        issues.append(f"generated trajectory tasks missing trace: {len(missing)}")

    for scenario_id in sorted({row["scenario_id"] for row in trace}):
        times = [float(row["time_s"]) for row in trace if row["scenario_id"] == scenario_id]
        if any(b < a for a, b in zip(times, times[1:])):
            issues.append(f"time_s is not monotonic for {scenario_id}")

    for field in ["x_mm", "y_mm", "z_mm", "vx_mm_s", "vy_mm_s", "vz_mm_s", "ax_mm_s2", "ay_mm_s2", "az_mm_s2"]:
        if any(row[field] == "" for row in trace):
            issues.append(f"{field} contains empty value")

    velocity_fail = sum(1 for row in constraints if "velocity" in row["check_item"] and row["status"] == "FAIL")
    acceleration_fail = sum(1 for row in constraints if "acceleration" in row["check_item"] and row["status"] == "FAIL")
    safe_z_fail = sum(1 for row in safe_z if row["status"] == "FAIL")
    sweep_fail = sum(1 for row in sweep if row["status"] == "FAIL")
    if velocity_fail:
        issues.append("velocity constraint contains FAIL")
    if acceleration_fail:
        issues.append("acceleration constraint contains FAIL")
    if safe_z_fail:
        issues.append("safe_z rule contains FAIL")
    if sweep_fail:
        issues.append("motion sweep contains FAIL")

    velocity_counts = Counter(row["status"] for row in constraints if "velocity" in row["check_item"])
    accel_counts = Counter(row["status"] for row in constraints if "acceleration" in row["check_item"])
    safe_counts = Counter(row["status"] for row in safe_z)
    sweep_counts = Counter(row["status"] for row in sweep)
    validation_status = "PASS" if not issues else "FAIL"

    print(f"validation_status={validation_status}")
    print(f"simulated_task_count={len(trace_keys)}")
    print(f"total_time_steps={len(trace)}")
    print(f"velocity_PASS={velocity_counts.get('PASS', 0)}")
    print(f"velocity_WARNING={velocity_counts.get('WARNING', 0)}")
    print(f"velocity_FAIL={velocity_counts.get('FAIL', 0)}")
    print(f"acceleration_PASS={accel_counts.get('PASS', 0)}")
    print(f"acceleration_WARNING={accel_counts.get('WARNING', 0)}")
    print(f"acceleration_FAIL={accel_counts.get('FAIL', 0)}")
    print(f"safe_z_PASS={safe_counts.get('PASS', 0)}")
    print(f"safe_z_WARNING={safe_counts.get('WARNING', 0)}")
    print(f"safe_z_FAIL={safe_counts.get('FAIL', 0)}")
    print(f"motion_sweep_PASS={sweep_counts.get('PASS', 0)}")
    print(f"motion_sweep_WARNING={sweep_counts.get('WARNING', 0)}")
    print(f"motion_sweep_FAIL={sweep_counts.get('FAIL', 0)}")
    if issues:
        for issue in issues:
            print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
