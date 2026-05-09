from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = ROOT / "07_validation"
REPORT_DIR = ROOT / "reports"

STATE_LOGIC_CSV = VALIDATION_DIR / "operator_feedback_state_logic_v1.csv"
IO_MAP_CSV = VALIDATION_DIR / "operator_feedback_io_map_v1.csv"
PRIORITY_CSV = VALIDATION_DIR / "operator_alarm_priority_table_v1.csv"
EVENT_MAPPING_CSV = VALIDATION_DIR / "operator_feedback_event_mapping_v1.csv"
SIM_INTERFACE_CSV = VALIDATION_DIR / "operator_feedback_simulation_interface_v1.csv"
REQUIREMENTS_MD = VALIDATION_DIR / "operator_feedback_hmi_requirements_v1.md"
REPORT_MD = REPORT_DIR / "stage_7c2_operator_feedback_hmi_alarm_logic_report.md"

REQUIRED_FILES = [
    REQUIREMENTS_MD,
    STATE_LOGIC_CSV,
    IO_MAP_CSV,
    PRIORITY_CSV,
    EVENT_MAPPING_CSV,
    SIM_INTERFACE_CSV,
    REPORT_MD,
]

REQUIRED_STATE_EVENTS = {
    "input_box_empty",
    "all_input_boxes_empty",
    "output_box_near_full",
    "output_box_full",
    "output_box_replaced",
    "category_hold",
    "category_resume",
    "manual_review_full",
    "barcode_missing_label",
    "invalid_barcode",
    "abnormal_sample_info",
    "pick_failed",
    "emergency_stop",
    "safety_door_open",
    "normal_running",
    "system_idle",
}

REQUIRED_MAPPING_EVENTS = {
    ("Stage 7B-2", "category_hold"),
    ("Stage 7B-2", "category_resume"),
    ("Stage 7B-2", "pending_queue"),
    ("Stage 7B-2", "abnormal_handling"),
    ("Stage 7B-2", "pick_failure"),
    ("Stage 7B-1", "empty slot"),
    ("Stage 7B-4", "operator wait time"),
}

STATE_FIELDS = [
    "system_event",
    "condition",
    "indicator_output",
    "light_color",
    "blink_pattern",
    "buzzer_pattern",
    "operator_action_required",
    "system_action",
    "cleared_by",
    "notes",
]

IO_FIELDS = [
    "io_id",
    "signal_name",
    "signal_type",
    "direction",
    "linked_event",
    "hardware_type",
    "default_state",
    "active_state",
    "priority",
    "notes",
]

PRIORITY_FIELDS = [
    "alarm_name",
    "priority_level",
    "visual_signal",
    "audio_signal",
    "robot_action",
    "operator_action",
    "auto_clear_allowed",
    "notes",
]

MAPPING_FIELDS = [
    "source_stage",
    "source_file",
    "event_name",
    "feedback_event",
    "indicator_signal",
    "buzzer_signal",
    "state_machine_effect",
    "notes",
]

SIM_FIELDS = [
    "timestamp_step",
    "scenario_id",
    "event_source",
    "event_name",
    "indicator_state",
    "buzzer_state",
    "operator_required",
    "system_state",
    "notes",
]

VALID_SIGNAL_TYPES = {"digital_output", "digital_input", "status_signal", "alarm_signal"}
VALID_DIRECTIONS = {"input", "output", "internal"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def has_fields(path: Path, expected_fields: list[str], issues: list[str]) -> bool:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        actual = reader.fieldnames or []
    missing = [field for field in expected_fields if field not in actual]
    if missing:
        issues.append(f"{path.name} missing fields: {', '.join(missing)}")
        return False
    return True


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

    has_fields(STATE_LOGIC_CSV, STATE_FIELDS, issues)
    has_fields(IO_MAP_CSV, IO_FIELDS, issues)
    has_fields(PRIORITY_CSV, PRIORITY_FIELDS, issues)
    has_fields(EVENT_MAPPING_CSV, MAPPING_FIELDS, issues)
    has_fields(SIM_INTERFACE_CSV, SIM_FIELDS, issues)

    state_rows = read_csv(STATE_LOGIC_CSV)
    io_rows = read_csv(IO_MAP_CSV)
    priority_rows = read_csv(PRIORITY_CSV)
    mapping_rows = read_csv(EVENT_MAPPING_CSV)
    sim_rows = read_csv(SIM_INTERFACE_CSV)

    state_events = {row["system_event"] for row in state_rows}
    missing_events = sorted(REQUIRED_STATE_EVENTS - state_events)
    if missing_events:
        issues.append(f"state logic missing required events: {', '.join(missing_events)}")

    mapping_events = {(row["source_stage"], row["event_name"]) for row in mapping_rows}
    missing_mappings = sorted(REQUIRED_MAPPING_EVENTS - mapping_events)
    if missing_mappings:
        issues.append(f"event mapping missing required rows: {missing_mappings}")

    invalid_signal_rows = [
        row["signal_name"]
        for row in io_rows
        if row["signal_type"] not in VALID_SIGNAL_TYPES or row["direction"] not in VALID_DIRECTIONS
    ]
    if invalid_signal_rows:
        issues.append(f"I/O map contains invalid signal type or direction: {', '.join(invalid_signal_rows)}")

    output_full_state = [row for row in state_rows if row["system_event"] == "output_box_full"]
    output_full_mapping = [
        row
        for row in mapping_rows
        if row["feedback_event"] == "output_box_full" or row["event_name"] in {"category_hold", "pending_queue"}
    ]
    output_full_text = " ".join(
        [row["system_action"] + " " + row["notes"] for row in output_full_state]
        + [row["state_machine_effect"] + " " + row["notes"] for row in output_full_mapping]
    ).lower()
    if "category_hold" not in output_full_text:
        issues.append("output_box_full is not mapped to category_hold")
    if "manual_review" in output_full_text and "not manual_review" not in output_full_text and "not_manual_review" not in output_full_text:
        issues.append("output_box_full mapping appears to route to manual_review")

    input_empty_state = [row for row in state_rows if row["system_event"] in {"input_box_empty", "all_input_boxes_empty"}]
    input_empty_mapping = [row for row in mapping_rows if row["feedback_event"] in {"input_box_empty", "all_input_boxes_empty"}]
    input_empty_text = " ".join(
        [row["system_action"] + " " + row["notes"] for row in input_empty_state]
        + [row["state_machine_effect"] + " " + row["notes"] for row in input_empty_mapping]
    ).lower()
    if "manual_review" in input_empty_text and "no manual_review" not in input_empty_text and "not manual_review" not in input_empty_text:
        issues.append("input_box_empty mapping appears to route to manual_review")

    if not any(row["signal_name"] == "buzzer_short_beep" for row in io_rows):
        issues.append("buzzer_short_beep is missing from I/O map")
    if not any(row["signal_name"] == "buzzer_intermit" for row in io_rows):
        issues.append("buzzer_intermit is missing from I/O map")
    if not any(row["signal_name"] == "buzzer_continuous" for row in io_rows):
        issues.append("buzzer_continuous is missing from I/O map")
    if not any(row["alarm_name"] == "manual_review_full" and row["priority_level"] == "P1" for row in priority_rows):
        issues.append("manual_review_full P1 alarm priority is missing")
    if not any(row["event_name"] == "output_box_full" and "category_hold" in row["system_state"] for row in sim_rows):
        issues.append("simulation interface missing output_box_full category_hold row")

    report_text = REPORT_MD.read_text(encoding="utf-8")
    for required_phrase in [
        "not camera logic",
        "category_hold",
        "category_resume",
        "Manual review full",
        "Pick Failure Boundary",
    ]:
        if required_phrase not in report_text:
            issues.append(f"report missing required phrase: {required_phrase}")

    validation_status = "PASS" if not issues else "FAIL"
    print(f"validation_status={validation_status}")
    print(f"state_logic_rows={len(state_rows)}")
    print(f"io_map_rows={len(io_rows)}")
    print(f"alarm_priority_rows={len(priority_rows)}")
    print(f"event_mapping_rows={len(mapping_rows)}")
    print(f"simulation_interface_rows={len(sim_rows)}")
    print(f"input_box_empty_feedback_defined={'yes' if 'input_box_empty' in state_events else 'no'}")
    print(f"output_box_full_feedback_defined={'yes' if 'output_box_full' in state_events else 'no'}")
    print(f"buzzer_feedback_defined={'yes' if all(any(row['signal_name'] == name for row in io_rows) for name in ['buzzer_short_beep', 'buzzer_intermit', 'buzzer_continuous']) else 'no'}")
    print(f"output_full_category_hold_not_manual_review={'yes' if 'category_hold' in output_full_text and not ('route to manual_review' in output_full_text) else 'no'}")
    for issue in issues:
        print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
