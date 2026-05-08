from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"

AXIS_LIMITS_CSV = SIM_DIR / "calibrated_axis_limits_v1.csv"
HEIGHT_RULES_CSV = SIM_DIR / "calibrated_height_rules_v1.csv"
PROXY_CSV = SIM_DIR / "refined_collision_proxy_definition_v1.csv"
WORKSPACE_PLAN_CSV = SIM_DIR / "workspace_warning_resolution_plan_v1.csv"
COLLISION_PLAN_CSV = SIM_DIR / "collision_warning_resolution_plan_v1.csv"
SUMMARY_CSV = SIM_DIR / "cad_sim_calibration_summary_v1.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    issues: list[str] = []
    required_files = [
        SIM_DIR / "cad_to_simulation_frame_alignment_v1.md",
        AXIS_LIMITS_CSV,
        HEIGHT_RULES_CSV,
        SIM_DIR / "simulation_slot_coordinate_source_v1.csv",
        PROXY_CSV,
        WORKSPACE_PLAN_CSV,
        COLLISION_PLAN_CSV,
        SUMMARY_CSV,
    ]
    for path in required_files:
        if not path.exists():
            issues.append(f"missing file: {path}")

    if not issues:
        axis_limits = read_csv(AXIS_LIMITS_CSV)
        heights = read_csv(HEIGHT_RULES_CSV)
        proxies = read_csv(PROXY_CSV)
        workspace = read_csv(WORKSPACE_PLAN_CSV)
        collision = read_csv(COLLISION_PLAN_CSV)
        summary = read_csv(SUMMARY_CSV)

        soft_axes = {row["axis"] for row in axis_limits if row["limit_type"] == "soft_limit_for_planning"}
        if soft_axes != {"X", "Y", "Z"}:
            issues.append(f"soft limits missing axes: {sorted({'X', 'Y', 'Z'} - soft_axes)}")

        height_names = {row["height_rule_name"] for row in heights}
        required_height_tokens = ["safe_z_mm", "pick_z_mm", "scan_z_mm", "output_place_z_mm", "manual_review_place_z_mm"]
        for name in required_height_tokens:
            if name not in height_names:
                issues.append(f"missing height rule: {name}")

        proxy_names = {row["proxy_name"] for row in proxies}
        for name in [
            "input_rack_proxy",
            "output_rack_proxy",
            "manual_review_proxy",
            "tube_proxy",
            "gripper_proxy",
            "z_axis_proxy",
            "x_beam_proxy",
            "enclosure_proxy",
            "cable_chain_proxy",
            "control_box_proxy",
        ]:
            if name not in proxy_names:
                issues.append(f"missing proxy: {name}")

        if not workspace:
            issues.append("workspace warning plan is empty")
        if not collision:
            issues.append("collision warning plan is empty")
        if any(not row.get("confidence_level", "") for row in axis_limits + heights + proxies + summary):
            issues.append("confidence_level contains empty values")
        if any(not row.get("future_validation_needed", "") for row in proxies):
            issues.append("future_validation_needed contains empty values")

    validation_status = "PASS" if not issues else "FAIL"
    print(f"validation_status={validation_status}")
    if not issues:
        print(f"axis_limit_rows={len(read_csv(AXIS_LIMITS_CSV))}")
        print(f"height_rule_rows={len(read_csv(HEIGHT_RULES_CSV))}")
        print(f"collision_proxy_rows={len(read_csv(PROXY_CSV))}")
        print(f"workspace_plan_rows={len(read_csv(WORKSPACE_PLAN_CSV))}")
        print(f"collision_plan_rows={len(read_csv(COLLISION_PLAN_CSV))}")
        print(f"summary_rows={len(read_csv(SUMMARY_CSV))}")
    else:
        for issue in issues:
            print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
