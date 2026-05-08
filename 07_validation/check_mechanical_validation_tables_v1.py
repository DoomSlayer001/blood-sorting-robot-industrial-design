from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_DIR = ROOT / "07_validation"

FILES_AND_FIELDS = {
    "deferred_mechanical_issue_register_v1.csv": [
        "issue_id",
        "issue_name",
        "source_stage",
        "current_status",
        "severity",
        "blocks_final_cad",
        "blocks_abstract_simulation",
        "blocks_isaac_sim",
        "required_resolution",
        "validation_method",
        "notes",
    ],
    "solidworks_mate_checklist_v1.csv": [
        "check_id",
        "assembly_region",
        "component_a",
        "component_b",
        "mate_or_relationship",
        "expected_result",
        "manual_check_required",
        "status",
        "notes",
    ],
    "solidworks_collision_checklist_v1.csv": [
        "check_id",
        "moving_component",
        "static_component",
        "motion_case",
        "collision_type",
        "expected_result",
        "manual_check_required",
        "status",
        "notes",
    ],
    "solidworks_clearance_measurement_table_v1.csv": [
        "measurement_id",
        "region",
        "component_a",
        "component_b",
        "required_min_clearance_mm",
        "measured_clearance_mm",
        "measurement_method",
        "status",
        "notes",
    ],
    "final_cad_acceptance_criteria_v1.csv": [
        "criteria_id",
        "criteria_name",
        "acceptance_condition",
        "required_for_final_cad",
        "current_status",
        "evidence_file",
        "notes",
    ],
    "isaac_sim_readiness_gate_v1.csv": [
        "readiness_item",
        "status",
        "required_before_isaac",
        "current_blocker",
        "resolution_needed",
        "notes",
    ],
}

VALID_STATUSES = {
    "NOT_CHECKED",
    "PENDING_MEASUREMENT",
    "PASS",
    "FAIL",
    "DEFERRED",
    "BLOCKED",
    "PARTIAL",
    "READY",
    "OPEN",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    issues: list[str] = []
    for filename, fields in FILES_AND_FIELDS.items():
        path = VALIDATION_DIR / filename
        if not path.exists():
            issues.append(f"missing table: {filename}")
            continue
        rows = read_csv(path)
        if not rows:
            issues.append(f"empty table: {filename}")
            continue
        missing_fields = [field for field in fields if field not in rows[0]]
        if missing_fields:
            issues.append(f"{filename} missing fields: {missing_fields}")
        status_field = "status" if "status" in rows[0] else "current_status"
        if filename == "final_cad_acceptance_criteria_v1.csv":
            status_field = "current_status"
        if status_field in rows[0]:
            for row in rows:
                if row[status_field] not in VALID_STATUSES:
                    issues.append(f"{filename} invalid status: {row[status_field]}")

    for md_name in ["solidworks_mechanical_validation_plan_v1.md", "xy_slider_binding_closure_plan_v1.md"]:
        if not (VALIDATION_DIR / md_name).exists():
            issues.append(f"missing document: {md_name}")

    validation_status = "PASS" if not issues else "FAIL"
    print(f"validation_status={validation_status}")
    for filename in FILES_AND_FIELDS:
        path = VALIDATION_DIR / filename
        if path.exists():
            print(f"{filename}_rows={len(read_csv(path))}")
    if issues:
        for issue in issues:
            print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
