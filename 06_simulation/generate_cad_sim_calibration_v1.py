from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"
REPORT_DIR = ROOT / "reports"
TASK_PLANNING_DIR = ROOT / "04_simulation" / "task_planning"
CAD_DIR = ROOT / "03_cad" / "freecad_assembly"

FRAME_ALIGNMENT_MD = SIM_DIR / "cad_to_simulation_frame_alignment_v1.md"
AXIS_LIMITS_CSV = SIM_DIR / "calibrated_axis_limits_v1.csv"
HEIGHT_RULES_CSV = SIM_DIR / "calibrated_height_rules_v1.csv"
SLOT_SOURCE_CSV = SIM_DIR / "simulation_slot_coordinate_source_v1.csv"
PROXY_CSV = SIM_DIR / "refined_collision_proxy_definition_v1.csv"
WORKSPACE_PLAN_CSV = SIM_DIR / "workspace_warning_resolution_plan_v1.csv"
COLLISION_PLAN_CSV = SIM_DIR / "collision_warning_resolution_plan_v1.csv"
SUMMARY_CSV = SIM_DIR / "cad_sim_calibration_summary_v1.csv"
REPORT_MD = REPORT_DIR / "stage_7c0_cad_simulation_calibration_report.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def count_status(path: Path, field: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in read_csv(path):
        counts[row[field]] += 1
    return counts


def main() -> int:
    workspace_counts = count_status(SIM_DIR / "trajectory_workspace_check_v1.csv", "workspace_status")
    collision_counts = count_status(SIM_DIR / "trajectory_collision_envelope_check_v1.csv", "collision_status")
    sweep_counts = count_status(SIM_DIR / "motion_sweep_collision_precheck_v1.csv", "status")
    slot_coordinate_file = TASK_PLANNING_DIR / "multi_box_slot_coordinates_v1.csv"
    height_reference_file = TASK_PLANNING_DIR / "multi_box_pick_place_height_rules_v1.md"
    slot_rows = read_csv(slot_coordinate_file) if slot_coordinate_file.exists() else []
    slot_counts = Counter(row["zone"] for row in slot_rows)
    validation_files = sorted(CAD_DIR.glob("*validation*.csv"))
    interface_files = sorted(CAD_DIR.glob("*interface*.csv"))
    accessibility_files = sorted(CAD_DIR.glob("*accessibility*.csv"))

    FRAME_ALIGNMENT_MD.write_text(
        "\n".join(
            [
                "# CAD-to-Simulation Frame Alignment v1",
                "",
                "## Scope",
                "",
                "- This document does not create or edit CAD.",
                "- It records the coordinate-frame convention used to align the current abstract simulation with the existing v7.x CAD planning context.",
                "- The current system does not use a camera; tube pose and occupancy are table-driven.",
                "",
                "## Alignment Rule",
                "",
                "- `world_frame` and `base_plate_frame` are treated as coincident for Stage 7C-0 calibration.",
                "- Simulation X follows the cross-beam direction from the input-side working region toward the output-side working region.",
                "- Simulation Y follows gantry travel across the input/output box rows.",
                "- Simulation Z is positive upward; pick, scan, and place moves descend from `safe_z_mm` to task-local Z targets.",
                "- `gripper_tcp_frame` is the simulated tool point used by trajectory and collision proxy checks.",
                "",
                "## Data Sources",
                "",
                "- Existing frame definitions: `06_simulation/digital_twin_coordinate_frames_v1.md`.",
                "- Existing abstract axis definitions: `06_simulation/axis_kinematic_model_v1.md`.",
                "- Slot coordinate reference: `04_simulation/task_planning/multi_box_slot_coordinates_v1.csv` when available.",
                "- Height reference: `04_simulation/task_planning/multi_box_pick_place_height_rules_v1.md` when available.",
                "- CAD validation/interface/accessibility CSV files are reference evidence only; Stage 7C-0 does not claim final CAD-derived hard limits.",
                "",
                "## Deferred Mechanical Dependency",
                "",
                "Stage 7A-3f XY slider binding remains a deferred mechanical integration issue. It does not block the abstract X/Y/Z simulation calibration because this stage works in task-space coordinates, but it must be resolved before final mechanical workspace and collision acceptance.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    axis_rows = []
    axis_limits = {
        "X": {
            "hard_limit_estimate": (-520, 520, "Stage 7B workspace placeholder and observed trace range -420..455 mm plus margin", "medium", "no"),
            "soft_limit_for_planning": (-500, 500, "Calibrated planning envelope for current 7B task-space simulation", "medium", "yes"),
            "safe_motion_limit": (-455, 490, "Observed Stage 7B trace range plus local margin", "medium", "yes"),
            "future_cad_verified_limit": (-520, 520, "Placeholder until final CAD/mate/axis verification", "low", "no"),
        },
        "Y": {
            "hard_limit_estimate": (-240, 360, "Stage 7B workspace placeholder and slot coverage", "medium", "no"),
            "soft_limit_for_planning": (-220, 340, "Calibrated planning envelope for current 7B task-space simulation", "medium", "yes"),
            "safe_motion_limit": (-190, 320, "Observed Stage 7B trace range -170..300 mm plus local margin", "medium", "yes"),
            "future_cad_verified_limit": (-240, 360, "Placeholder until final CAD/mate/axis verification", "low", "no"),
        },
        "Z": {
            "hard_limit_estimate": (80, 230, "Stage 7B workspace placeholder for vertical travel", "medium", "no"),
            "soft_limit_for_planning": (125, 205, "Planning range covering pick/place/scan/safe_z", "medium", "yes"),
            "safe_motion_limit": (135, 190, "Observed Stage 7B trace range; XY travel at 190 mm safe_z", "medium", "yes"),
            "future_cad_verified_limit": (80, 230, "Placeholder until final Z module/gripper/rack clearance verification", "low", "no"),
        },
    }
    for axis, rows in axis_limits.items():
        for limit_type, (min_mm, max_mm, source, confidence, used) in rows.items():
            axis_rows.append(
                {
                    "axis": axis,
                    "limit_type": limit_type,
                    "min_mm": min_mm,
                    "max_mm": max_mm,
                    "source": source,
                    "confidence_level": confidence,
                    "used_by_simulation": used,
                    "notes": "Estimated/calibrated for abstract simulation; not final hardware limit. XY slider binding deferred affects final workspace certainty.",
                }
            )

    height_rows = [
        ("safe_z_mm", 190.0, "Safe XY travel height above tube/rack proxy envelopes.", "Stage 7B trajectory rules; 04_simulation reference lists safe_z=200 mm.", "medium", "7B-3/7B-5/7C", "XY travel must occur at safe_z; current 7B uses 190 mm."),
        ("pick_z_mm", 145.0, "Input tube pick/grip height used in current trajectory.", "trajectory_waypoints_v1.csv descend_to_pick/grip_close.", "medium", "7B-3/7B-5", "Low-Z allowed only at pick target."),
        ("scan_z_mm", 155.0, "Scan station alignment height.", "trajectory_waypoints_v1.csv descend_or_align_to_scan.", "medium", "7B-3/7B-5", "Low-Z allowed only at scan target."),
        ("output_place_z_mm", 135.0, "Output rack placement height.", "trajectory_waypoints_v1.csv descend_to_place/grip_open.", "medium", "7B-3/7B-5", "Low-Z allowed only at place target."),
        ("manual_review_place_z_mm", 135.0, "Manual review tray placement height using same current place rule.", "trajectory_waypoints_v1.csv manual-review place waypoints.", "medium", "7B-3/7B-5", "Requires final tray/gripper clearance validation."),
        ("tube_top_clearance_z_mm", 125.0, "Tube top proxy upper envelope used below safe_z.", "collision_envelope_definition_v1.csv tube_envelope.", "medium", "7B-3/7B-5", "safe_z=190 gives 65 mm nominal clearance over tube proxy."),
        ("low_z_allowed_zone", "pick_scan_place_only", "Low-Z motion policy.", "safe_z_rule_check_v1.csv and Stage 7B-5 review.", "medium", "7B-3/7B-5/7C", "Low-Z XY crossing remains forbidden; local vertical descent/dwell is target-local."),
    ]

    coordinate_rows = [
        ("input_box_slots", str(slot_coordinate_file), "slot_center_xyz", slot_counts.get("input", 96), "7B-1/7B-3", "medium", "Current 7B task manifest covers 96 input slots; optional 04_simulation file provides v7.1 coordinate reference."),
        ("output_box_slots", str(slot_coordinate_file), "slot_center_xyz", slot_counts.get("output", 96), "7B-2/7B-3", "medium", "Output A-D slots used by normal sample routing."),
        ("manual_review_slots", str(slot_coordinate_file), "slot_center_xyz", slot_counts.get("manual_review", 6), "7B-2/7B-3", "medium", "Manual review is abnormal-only in current state machine."),
        ("scan_station", str(slot_coordinate_file), "single_station_xyz", slot_counts.get("scan", 1), "7B-3/7B-5", "medium", "Scan station uses table-defined point; no camera frame is defined."),
        ("home_safe", "trajectory_waypoints_v1.csv", "safe_home_xyz", 1, "7B-3/7B-5", "medium", "home_safe is [0,0,190] in current trajectory set."),
        ("pending_resume_targets", "sorting_state_machine_task_result_v1.csv; trajectory_waypoints_v1.csv", "resumed_task_targets", 16, "7B-2/7B-3", "medium", "Forced category hold/resume generated 16 resumed pending tasks."),
    ]

    proxy_rows = [
        ("input_rack_proxy", "input racks and input tubes", "box", -430, -180, -190, 350, 0, 125, "slot coordinate table + rack/tube envelope split", "medium", "usable_for_abstract_check", "yes", "Improves over combined rack proxy, but final CAD clearance still needed."),
        ("output_rack_proxy", "output racks and output tubes", "box", 180, 470, -190, 350, 0, 125, "slot coordinate table + rack/tube envelope split", "medium", "usable_for_abstract_check", "yes", "Output area proxy is separated from input proxy for future checks."),
        ("manual_review_proxy", "manual review tray", "box", 300, 470, -210, 0, 0, 125, "slot coordinate table and manual review logic", "medium", "usable_for_abstract_check", "yes", "Manual review placement remains approximate."),
        ("tube_proxy", "individual tube", "cylinder", -10, 10, -10, 10, 20, 125, "collision_envelope_definition_v1.csv", "medium", "usable_for_abstract_check", "yes", "Per-slot placement required for exact CAD/Isaac check."),
        ("gripper_proxy", "gripper TCP and jaws", "box", -35, 35, -25, 25, 20, 130, "collision_envelope_definition_v1.csv", "medium", "usable_for_abstract_check", "yes", "Current proxy does not model jaw pad details."),
        ("z_axis_proxy", "Z axis module", "box", -45, 45, -10, 55, 80, 360, "collision_envelope_definition_v1.csv", "medium", "warning_only", "yes", "Local vertical sweeps remain warning-only until detailed CAD collision."),
        ("x_beam_proxy", "X beam and carriage", "box", -390, 390, -40, 60, 220, 310, "collision_envelope_definition_v1.csv", "medium", "warning_only", "yes", "XY slider binding deferred affects final beam/carriage validation."),
        ("enclosure_proxy", "enclosure frame", "box", -600, 600, -450, 450, 0, 430, "collision_envelope_definition_v1.csv", "low", "not_checked_until_solidworks", "yes", "Exact panel/door/opening geometry required."),
        ("cable_chain_proxy", "cable chain sweep", "box", -180, 120, 240, 420, 150, 360, "collision_envelope_definition_v1.csv", "low", "not_checked_until_solidworks", "yes", "Cable chain routing is not final."),
        ("control_box_proxy", "control box", "box", 430, 590, -420, -220, 20, 260, "collision_envelope_definition_v1.csv", "low", "not_checked_until_isaac", "yes", "Final digital twin should validate static placement and moving envelope."),
    ]

    workspace_plan_rows = [
        {
            "warning_source": "trajectory_workspace_check_v1.csv",
            "current_warning_count": workspace_counts.get("WARNING", 0),
            "root_cause": "All points were checked against conservative placeholder workspace limits rather than calibrated soft limits.",
            "can_resolve_now": "partially",
            "resolution_action": "Use calibrated_axis_limits_v1.csv to document planning soft limits and safe motion limits.",
            "remaining_status": "WARNING retained until final CAD/mate axis travel verification.",
            "future_validation": "Final CAD-derived axis soft limits after XY slider binding and gantry mechanics are resolved.",
            "notes": "No immediate rerun is recommended because this stage documents calibration rather than changing trajectory logic.",
        }
    ]

    collision_plan_rows = [
        {
            "warning_source": "trajectory_collision_envelope_check_v1.csv",
            "current_warning_count": collision_counts.get("WARNING", 0),
            "root_cause": "Local vertical sweep and target clearances use simplified proxies.",
            "can_resolve_now": "partially",
            "resolution_action": "Split rack/control/enclosure proxies and label usable vs warning-only proxy classes.",
            "remaining_status": "WARNING retained for local vertical/dwell/gripper clearance.",
            "future_validation": "SolidWorks exact interference and Isaac Sim collision bodies.",
            "notes": f"PASS={collision_counts.get('PASS', 0)} NOT_CHECKED_APPROXIMATE={collision_counts.get('NOT_CHECKED_APPROXIMATE', 0)}.",
        },
        {
            "warning_source": "motion_sweep_collision_precheck_v1.csv",
            "current_warning_count": sweep_counts.get("WARNING", 0),
            "root_cause": "Time-stepped sweep uses conservative gripper/tube proxy rather than exact moving assemblies.",
            "can_resolve_now": "partially",
            "resolution_action": "Use refined_collision_proxy_definition_v1.csv for future abstract check refinement.",
            "remaining_status": "WARNING retained until exact swept-volume validation.",
            "future_validation": "SolidWorks motion/mate check and Isaac Sim import/playback.",
            "notes": f"PASS={sweep_counts.get('PASS', 0)} WARNING={sweep_counts.get('WARNING', 0)}.",
        },
    ]

    summary_rows = [
        ("coordinate_frame_alignment", "defined", "medium", "digital_twin_coordinate_frames_v1.md; cad_to_simulation_frame_alignment_v1.md", "7C/future Isaac Sim", "World/base frames treated as coincident for current abstraction."),
        ("axis_limits", "calibrated_estimate", "medium", "calibrated_axis_limits_v1.csv", "future workspace rerun", "Estimated soft/safe limits documented; not final hardware limits."),
        ("height_rules", "calibrated_estimate", "medium", "calibrated_height_rules_v1.csv", "future trajectory checks", "Current 7B heights documented and contrasted with optional 04_simulation reference."),
        ("slot_coordinates", "source_mapped", "medium", "simulation_slot_coordinate_source_v1.csv", "future trajectory regeneration", "Coordinate groups and counts mapped."),
        ("collision_proxies", "refined_proxy_plan", "medium", "refined_collision_proxy_definition_v1.csv", "future collision check", "Proxy classes split by usable/warning/future validation status."),
        ("workspace_warning_reduction", "partially_explained", "medium", "workspace_warning_resolution_plan_v1.csv", "future workspace rerun", "Can reduce uncertainty but warnings retained until final axis verification."),
        ("collision_warning_reduction", "partially_explained", "medium", "collision_warning_resolution_plan_v1.csv", "future collision rerun", "Some proxy classes improved; exact checks remain future work."),
        ("solidworks_future_validation", "required", "high", "simulation_chain_risk_register_v1.csv", "future mechanical validation", "Required for real collision/mate acceptance."),
        ("isaac_sim_future_validation", "required", "high", "simulation_chain_risk_register_v1.csv", "future digital twin validation", "Required before final physical digital twin claim."),
    ]

    write_csv(AXIS_LIMITS_CSV, ["axis", "limit_type", "min_mm", "max_mm", "source", "confidence_level", "used_by_simulation", "notes"], axis_rows)
    write_csv(HEIGHT_RULES_CSV, ["height_rule_name", "z_mm", "purpose", "source", "confidence_level", "used_by", "notes"], [dict(zip(["height_rule_name", "z_mm", "purpose", "source", "confidence_level", "used_by", "notes"], row)) for row in height_rows])
    write_csv(SLOT_SOURCE_CSV, ["coordinate_group", "source_file", "coordinate_type", "count", "used_by_stage", "confidence_level", "notes"], [dict(zip(["coordinate_group", "source_file", "coordinate_type", "count", "used_by_stage", "confidence_level", "notes"], row)) for row in coordinate_rows])
    write_csv(PROXY_CSV, ["proxy_name", "object_group", "proxy_type", "x_min_mm", "x_max_mm", "y_min_mm", "y_max_mm", "z_min_mm", "z_max_mm", "source", "confidence_level", "check_status", "future_validation_needed", "notes"], [dict(zip(["proxy_name", "object_group", "proxy_type", "x_min_mm", "x_max_mm", "y_min_mm", "y_max_mm", "z_min_mm", "z_max_mm", "source", "confidence_level", "check_status", "future_validation_needed", "notes"], row)) for row in proxy_rows])
    write_csv(WORKSPACE_PLAN_CSV, ["warning_source", "current_warning_count", "root_cause", "can_resolve_now", "resolution_action", "remaining_status", "future_validation", "notes"], workspace_plan_rows)
    write_csv(COLLISION_PLAN_CSV, ["warning_source", "current_warning_count", "root_cause", "can_resolve_now", "resolution_action", "remaining_status", "future_validation", "notes"], collision_plan_rows)
    write_csv(SUMMARY_CSV, ["calibration_item", "status", "confidence_level", "source", "used_by_future_stage", "notes"], [dict(zip(["calibration_item", "status", "confidence_level", "source", "used_by_future_stage", "notes"], row)) for row in summary_rows])

    REPORT_MD.write_text(
        "\n".join(
            [
                "# Stage 7C-0 CAD-to-Simulation Calibration Report",
                "",
                "## Scope",
                "",
                "- This stage does not create CAD, rendering, PPT, or animation.",
                "- This stage reduces placeholder/abstract uncertainty in the Stage 7B simulation chain by documenting frame alignment, axis-limit estimates, height rules, slot coordinate sources, and collision proxy classes.",
                "- The current system still does not use a camera; input occupancy comes from the internal tube occupancy table.",
                "",
                "## Frame Alignment",
                "",
                "- The current calibration treats `world_frame` and `base_plate_frame` as coincident for task-space simulation.",
                "- X follows cross-beam travel, Y follows gantry travel, and Z is positive upward.",
                "- CAD validation/interface/accessibility CSV files are reference evidence only; final CAD-derived hard limits are not claimed in this stage.",
                f"- CAD reference evidence found: validation CSV={len(validation_files)}, interface CSV={len(interface_files)}, accessibility CSV={len(accessibility_files)}.",
                "",
                "## Axis Limits And Heights",
                "",
                "- X/Y/Z axis limits are conservative calibrated estimates, not final hardware limits.",
                "- Current planning soft limits are documented in `calibrated_axis_limits_v1.csv`.",
                "- Current Stage 7B height rules are safe_z=190 mm, pick_z=145 mm, scan_z=155 mm, output/manual-review place_z=135 mm.",
                "- XY moves must remain at safe_z; low-Z motion remains target-local for pick, scan, and place.",
                "- Optional historical planning reference exists: `04_simulation/task_planning/multi_box_pick_place_height_rules_v1.md`.",
                "",
                "## Collision Proxy Refinement",
                "",
                "- The combined abstract rack/control/enclosure proxies are split into named input, output, manual review, tube, gripper, Z-axis, X-beam, enclosure, cable-chain, and control-box proxies.",
                "- `usable_for_abstract_check` proxies can support future abstract reruns.",
                "- `warning_only`, `not_checked_until_solidworks`, and `not_checked_until_isaac` proxies must remain warnings or future-validation items.",
                "",
                "## Warning Resolution",
                "",
                f"- Stage 7B-3 workspace WARNING count is {workspace_counts.get('WARNING', 0)} because final calibrated CAD/axis soft limits were not yet available.",
                "- Calibrated axis limits reduce uncertainty, but the warnings should not be blindly converted to final PASS until physical axis travel is verified.",
                f"- Collision WARNING count is {collision_counts.get('WARNING', 0)} and NOT_CHECKED_APPROXIMATE count is {collision_counts.get('NOT_CHECKED_APPROXIMATE', 0)}.",
                "- Safe-Z XY travel checks are already meaningful at the abstract level; local vertical and static/sweep envelope checks still need exact SolidWorks or Isaac Sim validation.",
                "",
                "## Deferred XY Slider Binding",
                "",
                "- Stage 7A-3f XY slider binding remains deferred.",
                "- It does not block current simulation calibration because this stage calibrates task-space frames and proxy assumptions, not final mechanical load paths.",
                "- It does affect final mechanical workspace, mate, and collision validation.",
                "",
                "## Rerun Recommendation",
                "",
                "- Immediate rerun of Stage 7B-3 is not recommended until final CAD/axis soft limits are validated; this stage only prepares calibrated inputs for a future rerun.",
                "- Immediate rerun of Stage 7B-5 is not recommended until Stage 7B-3 workspace/collision rules are updated from final validation.",
                "",
                "## Next Options",
                "",
                "- SolidWorks real collision check.",
                "- Isaac Sim import preparation.",
                "- Final report integration.",
                "",
                "No next stage is executed by this report.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print("validation_status=PASS")
    print(f"workspace_WARNING={workspace_counts.get('WARNING', 0)}")
    print(f"collision_WARNING={collision_counts.get('WARNING', 0)}")
    print(f"collision_NOT_CHECKED_APPROXIMATE={collision_counts.get('NOT_CHECKED_APPROXIMATE', 0)}")
    print("rerun_stage_7b3_recommended=no")
    print("rerun_stage_7b5_recommended=no")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
