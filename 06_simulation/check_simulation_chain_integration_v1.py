from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"
REPORT_DIR = ROOT / "reports"

REQUIRED_OUTPUTS = [
    SIM_DIR / "simulation_chain_master_summary_v1.csv",
    SIM_DIR / "simulation_chain_traceability_matrix_v1.csv",
    SIM_DIR / "simulation_chain_consistency_audit_v1.csv",
    SIM_DIR / "simulation_chain_risk_register_v1.csv",
    SIM_DIR / "simulation_chain_acceptance_status_v1.csv",
    SIM_DIR / "simulation_chain_key_metrics_v1.csv",
    REPORT_DIR / "stage_7b8_simulation_chain_integration_acceptance_report.md",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    issues: list[str] = []
    missing = [path for path in REQUIRED_OUTPUTS if not path.exists()]
    if missing:
        issues.extend(f"missing output file: {path}" for path in missing)
        print("validation_status=FAIL")
        for issue in issues:
            print(f"issue={issue}")
        return 1

    master = read_csv(SIM_DIR / "simulation_chain_master_summary_v1.csv")
    traceability = read_csv(SIM_DIR / "simulation_chain_traceability_matrix_v1.csv")
    audit = read_csv(SIM_DIR / "simulation_chain_consistency_audit_v1.csv")
    risks = read_csv(SIM_DIR / "simulation_chain_risk_register_v1.csv")
    acceptance = read_csv(SIM_DIR / "simulation_chain_acceptance_status_v1.csv")
    metrics = read_csv(SIM_DIR / "simulation_chain_key_metrics_v1.csv")

    if len(master) < 7:
        issues.append("master summary does not contain all Stage 7B rows")
    if len(traceability) < 8:
        issues.append("traceability matrix does not contain required links")
    if any(row["status"] == "FAIL" for row in audit):
        issues.append("consistency audit contains FAIL")
    if not metrics:
        issues.append("key metrics could not be read")
    acceptance_statuses = {row["status"] for row in acceptance}
    if not {"accepted", "deferred", "future_validation_required"}.issubset(acceptance_statuses):
        issues.append("acceptance status does not clearly distinguish accepted/deferred/future validation")
    if not any("XY slider binding" in row["risk_name"] and row["current_status"] == "deferred" for row in risks):
        issues.append("risk register missing deferred XY slider binding risk")
    if not any(row["metric_name"] == "Stage 7B-7 within_tolerance_rate" for row in metrics):
        issues.append("key metrics missing Stage 7B-7 within_tolerance_rate")

    validation_status = "PASS" if not issues else "FAIL"
    print(f"validation_status={validation_status}")
    print(f"master_summary_rows={len(master)}")
    print(f"traceability_rows={len(traceability)}")
    print(f"consistency_audit_rows={len(audit)}")
    print(f"risk_register_rows={len(risks)}")
    print(f"acceptance_status_rows={len(acceptance)}")
    print(f"key_metrics_rows={len(metrics)}")
    print(f"consistency_FAIL={sum(1 for row in audit if row['status'] == 'FAIL')}")
    print(f"accepted_items={sum(1 for row in acceptance if row['status'] == 'accepted')}")
    print(f"deferred_items={sum(1 for row in acceptance if row['status'] == 'deferred')}")
    print(f"future_validation_items={sum(1 for row in acceptance if row['status'] == 'future_validation_required')}")
    if issues:
        for issue in issues:
            print(f"issue={issue}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
