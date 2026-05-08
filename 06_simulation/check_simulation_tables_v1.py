from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"

TUBE_TABLE = SIM_DIR / "tube_occupancy_input_table_schema_v1.csv"
INTERFACE_TABLE = SIM_DIR / "simulation_interface_table_v1.csv"
COLLISION_TABLE = SIM_DIR / "collision_envelope_definition_v1.csv"

REQUIRED_TUBE_FIELDS = {
    "rack_id",
    "rack_type",
    "slot_row",
    "slot_col",
    "slot_id",
    "x_mm",
    "y_mm",
    "z_pick_mm",
    "tube_present",
    "tube_id",
    "barcode_status",
    "sample_category",
    "priority",
    "abnormal_flag",
    "target_output_box",
    "notes",
}

REQUIRED_INTERFACE_FIELDS = {
    "command_id",
    "task_id",
    "tube_id",
    "source_rack_id",
    "source_slot_id",
    "target_box_id",
    "target_slot_id",
    "x_target_mm",
    "y_target_mm",
    "z_target_mm",
    "gripper_action",
    "expected_state",
    "status",
}

REQUIRED_COLLISION_FIELDS = {
    "object_name",
    "envelope_type",
    "x_min",
    "x_max",
    "y_min",
    "y_max",
    "z_min",
    "z_max",
    "collision_priority",
    "notes",
}

BOOLEAN_VALUES = {"TRUE", "FALSE"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def require_fields(name: str, fields: list[str], required: set[str], errors: list[str]) -> None:
    missing = sorted(required - set(fields))
    if missing:
        errors.append(f"{name}: missing fields {', '.join(missing)}")


def validate_tube_table(errors: list[str]) -> None:
    fields, rows = read_csv(TUBE_TABLE)
    require_fields(TUBE_TABLE.name, fields, REQUIRED_TUBE_FIELDS, errors)
    seen_slots: set[tuple[str, str]] = set()
    for index, row in enumerate(rows, start=2):
        key = (row.get("rack_id", ""), row.get("slot_id", ""))
        if key in seen_slots:
            errors.append(f"{TUBE_TABLE.name}:{index}: duplicate rack_id + slot_id {key}")
        seen_slots.add(key)
        if row.get("tube_present", "") not in BOOLEAN_VALUES:
            errors.append(f"{TUBE_TABLE.name}:{index}: tube_present must be TRUE or FALSE")
        if row.get("abnormal_flag", "") not in BOOLEAN_VALUES:
            errors.append(f"{TUBE_TABLE.name}:{index}: abnormal_flag must be TRUE or FALSE")
        if row.get("target_output_box", "") == "" and row.get("tube_present") == "TRUE" and row.get("abnormal_flag") == "FALSE":
            errors.append(f"{TUBE_TABLE.name}:{index}: normal present tube should have target_output_box")


def validate_simple_table(path: Path, required: set[str], errors: list[str]) -> None:
    fields, _ = read_csv(path)
    require_fields(path.name, fields, required, errors)


def main() -> int:
    errors: list[str] = []
    for path in [TUBE_TABLE, INTERFACE_TABLE, COLLISION_TABLE]:
        if not path.exists():
            errors.append(f"missing file: {path}")
    if not errors:
        validate_tube_table(errors)
        validate_simple_table(INTERFACE_TABLE, REQUIRED_INTERFACE_FIELDS, errors)
        validate_simple_table(COLLISION_TABLE, REQUIRED_COLLISION_FIELDS, errors)

    if errors:
        print("validation_status=FAIL")
        for error in errors:
            print(error)
        return 1

    print("validation_status=PASS")
    print(f"checked={TUBE_TABLE.name},{INTERFACE_TABLE.name},{COLLISION_TABLE.name}")
    print("target_output_box_empty_allowed=yes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

