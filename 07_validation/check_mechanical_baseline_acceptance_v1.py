from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
CAD_DIR = ROOT / "03_cad" / "freecad_assembly"
VALIDATION_DIR = ROOT / "07_validation"


REQUIRED_FILES = [
    REPORT_DIR / "stage_7a3f_v1_7_accepted_baseline_status.md",
    REPORT_DIR / "stage_7a3f_v1_8_rejected_status.md",
    CAD_DIR / "current_mechanical_baseline_manifest_v1.csv",
    VALIDATION_DIR / "deferred_mechanical_issue_register_v2.csv",
    VALIDATION_DIR / "final_cad_acceptance_criteria_v2.csv",
    VALIDATION_DIR / "isaac_sim_readiness_gate_v2.csv",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    issues: list[str] = []

    for path in REQUIRED_FILES:
        if not path.exists():
            issues.append(f"missing: {path.relative_to(ROOT).as_posix()}")

    accepted_report = REPORT_DIR / "stage_7a3f_v1_7_accepted_baseline_status.md"
    if accepted_report.exists() and "Status: ACCEPTED_AS_CURRENT_MECHANICAL_BASELINE" not in accepted_report.read_text(encoding="utf-8"):
        issues.append("v1.7 accepted status report does not contain accepted baseline status")

    rejected_report = REPORT_DIR / "stage_7a3f_v1_8_rejected_status.md"
    if rejected_report.exists() and "Status: NOT_ACCEPTED_FOR_FINAL_MECHANICAL_VALIDATION" not in rejected_report.read_text(encoding="utf-8"):
        issues.append("v1.8 rejected status report does not contain not accepted status")

    manifest_path = CAD_DIR / "current_mechanical_baseline_manifest_v1.csv"
    if manifest_path.exists():
        rows = read_csv(manifest_path)
        if not rows:
            issues.append("baseline manifest is empty")
        if not any(row.get("selected_version") == "v1.7" and row.get("used_for_downstream") == "yes" for row in rows):
            issues.append("baseline manifest does not clearly select v1.7 for downstream use")
        if not any(row.get("baseline_item") == "rejected_version_v1_8" and row.get("status") == "NOT_ACCEPTED" for row in rows):
            issues.append("baseline manifest does not clearly mark v1.8 not accepted")
        preview = CAD_DIR / "blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_7.step"
        module = CAD_DIR / "blood_sorting_robot_gantry_joint_adapter_module_v1_7.step"
        if not preview.exists():
            issues.append("selected v1.7 preview STEP is missing")
        if not module.exists():
            issues.append("selected v1.7 module STEP is missing")

    validation_status = "PASS" if not issues else "FAIL"
    print(f"validation_status={validation_status}")
    for path in REQUIRED_FILES:
        print(f"{path.name}_exists={'yes' if path.exists() else 'no'}")
    if manifest_path.exists():
        rows = read_csv(manifest_path)
        print(f"baseline_manifest_rows={len(rows)}")
        selected = [row for row in rows if row.get("selected_version") == "v1.7" and row.get("used_for_downstream") == "yes"]
        rejected = [row for row in rows if row.get("baseline_item") == "rejected_version_v1_8" and row.get("status") == "NOT_ACCEPTED"]
        print(f"selected_version_v1_7_rows={len(selected)}")
        print(f"v1_8_not_accepted_rows={len(rejected)}")
    for issue in issues:
        print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
