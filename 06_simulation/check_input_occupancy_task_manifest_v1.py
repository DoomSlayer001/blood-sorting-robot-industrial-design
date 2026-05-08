from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"

INPUT_OCCUPANCY_CSV = SIM_DIR / "input_box_occupancy_map_v1.csv"
TUBE_MANIFEST_CSV = SIM_DIR / "tube_sample_manifest_v1.csv"
TASK_MANIFEST_CSV = SIM_DIR / "sorting_task_manifest_v1.csv"
OUTPUT_BOX_STATE_CSV = SIM_DIR / "output_box_capacity_state_v1.csv"
MANUAL_REVIEW_STATE_CSV = SIM_DIR / "manual_review_capacity_state_v1.csv"
CATEGORY_MAPPING_CSV = SIM_DIR / "category_mapping_v1.csv"

REQUIRED_OCCUPANCY_FIELDS = {
    "input_box_id",
    "rack_type",
    "slot_row",
    "slot_col",
    "slot_id",
    "tube_present",
    "tube_id",
    "x_mm",
    "y_mm",
    "z_pick_mm",
    "slot_status",
    "notes",
}
REQUIRED_MANIFEST_FIELDS = {
    "tube_id",
    "input_box_id",
    "source_slot_id",
    "tube_present",
    "barcode_status",
    "sample_category",
    "abnormal_flag",
    "abnormal_reason",
    "target_output_box",
    "priority",
    "sample_status",
    "notes",
}
REQUIRED_TASK_FIELDS = {
    "task_id",
    "tube_id",
    "source_input_box_id",
    "source_slot_id",
    "source_x_mm",
    "source_y_mm",
    "source_z_pick_mm",
    "requires_scan",
    "scan_station_id",
    "barcode_status",
    "sample_category",
    "abnormal_flag",
    "target_type",
    "target_box_id",
    "target_slot_id",
    "task_priority",
    "initial_task_status",
    "notes",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require_fields(path: Path, rows: list[dict[str, str]], required: set[str], issues: list[str]) -> None:
    if not rows:
        issues.append(f"{path.name} has no rows")
        return
    missing = required.difference(rows[0].keys())
    if missing:
        issues.append(f"{path.name} missing fields: {', '.join(sorted(missing))}")


def main() -> int:
    issues: list[str] = []
    occupancy = read_csv(INPUT_OCCUPANCY_CSV)
    manifest = read_csv(TUBE_MANIFEST_CSV)
    tasks = read_csv(TASK_MANIFEST_CSV)
    output_state = read_csv(OUTPUT_BOX_STATE_CSV)
    manual_review = read_csv(MANUAL_REVIEW_STATE_CSV)
    category_mapping = read_csv(CATEGORY_MAPPING_CSV)

    require_fields(INPUT_OCCUPANCY_CSV, occupancy, REQUIRED_OCCUPANCY_FIELDS, issues)
    require_fields(TUBE_MANIFEST_CSV, manifest, REQUIRED_MANIFEST_FIELDS, issues)
    require_fields(TASK_MANIFEST_CSV, tasks, REQUIRED_TASK_FIELDS, issues)

    if len(occupancy) != 96:
        issues.append(f"input slot total expected 96, got {len(occupancy)}")

    input_box_counts = Counter(row["input_box_id"] for row in occupancy)
    if len(input_box_counts) != 4:
        issues.append(f"input box count expected 4, got {len(input_box_counts)}")
    for input_box_id, count in sorted(input_box_counts.items()):
        if count != 24:
            issues.append(f"{input_box_id} expected 24 slots, got {count}")

    valid_bool = {"true", "false"}
    if any(row["tube_present"] not in valid_bool for row in occupancy):
        issues.append("tube_present contains value outside true/false")
    if any(row["abnormal_flag"] not in valid_bool for row in manifest):
        issues.append("abnormal_flag contains value outside true/false")

    occupancy_keys = [(row["input_box_id"], row["slot_id"]) for row in occupancy]
    if len(occupancy_keys) != len(set(occupancy_keys)):
        issues.append("input_box_id + slot_id is not globally unique")

    for input_box_id in input_box_counts:
        slot_ids = [row["slot_id"] for row in occupancy if row["input_box_id"] == input_box_id]
        if len(slot_ids) != len(set(slot_ids)):
            issues.append(f"slot_id is not unique within {input_box_id}")

    occupied_rows = [row for row in occupancy if row["tube_present"] == "true"]
    empty_rows = [row for row in occupancy if row["tube_present"] == "false"]
    if any(not row["tube_id"] for row in occupied_rows):
        issues.append("occupied slot missing tube_id")
    if any(row["tube_id"] for row in empty_rows):
        issues.append("empty slot has tube_id")

    manifest_tube_ids = [row["tube_id"] for row in manifest]
    if len(manifest_tube_ids) != len(set(manifest_tube_ids)):
        issues.append("tube_id is not unique in tube_sample_manifest")
    if len(manifest) != len(occupied_rows):
        issues.append("tube_sample_manifest row count does not match occupied slots")

    task_tube_ids = {row["tube_id"] for row in tasks}
    empty_tube_ids = {row["tube_id"] for row in empty_rows if row["tube_id"]}
    if task_tube_ids.intersection(empty_tube_ids):
        issues.append("empty slot generated pick task")
    if len(tasks) != len(occupied_rows):
        issues.append("sorting_task_manifest row count does not match occupied slots")

    category_to_box = {row["sample_category"]: row["target_output_box"] for row in category_mapping}
    task_by_tube = {row["tube_id"]: row for row in tasks}
    for sample in manifest:
        task = task_by_tube.get(sample["tube_id"])
        if task is None:
            issues.append(f"missing task for tube {sample['tube_id']}")
            continue
        if sample["abnormal_flag"] == "true":
            if task["target_type"] != "manual_review":
                issues.append(f"abnormal sample not routed to manual_review: {sample['tube_id']}")
            if task["target_box_id"] != "manual_review_01":
                issues.append(f"abnormal sample target_box_id mismatch: {sample['tube_id']}")
        else:
            if task["target_type"] != "output_box":
                issues.append(f"normal sample not routed to output_box: {sample['tube_id']}")
            expected_box = category_to_box.get(sample["sample_category"])
            if task["target_box_id"] != expected_box:
                issues.append(f"target output box mismatch for {sample['tube_id']}")

    normal_in_manual_review = [
        row for row in tasks if row["abnormal_flag"] == "false" and row["target_type"] == "manual_review"
    ]
    if normal_in_manual_review:
        issues.append("manual_review contains normal sample task")

    for row in output_state:
        if int(row["capacity_slots"]) != 24:
            issues.append(f"output box capacity is not 24: {row['output_box_id']}")
    if len(output_state) != 4:
        issues.append("output box count is not 4")

    if len(manual_review) != 1:
        issues.append("manual review state should contain one box")
    for row in manual_review:
        if int(row["capacity_slots"]) != 6:
            issues.append("manual review capacity is not 6")

    validation_status = "PASS" if not issues else "FAIL"
    print(f"validation_status={validation_status}")
    print(f"total_input_slots={len(occupancy)}")
    print(f"input_box_count={len(input_box_counts)}")
    print(f"occupied_slots={len(occupied_rows)}")
    print(f"empty_slots={len(empty_rows)}")
    print(f"generated_task_count={len(tasks)}")
    print(f"manual_review_has_normal_samples={'yes' if normal_in_manual_review else 'no'}")
    if issues:
        for issue in issues:
            print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
