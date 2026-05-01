"""
Create the SolidWorks 2026 rough assembly from the existing native CAD cache.

This migration-branch script intentionally uses only existing .SLDPRT/.SLDASM
files registered in native_file_mapping.csv. It never opens or converts STEP/STP
files and writes a separate 2026 rough assembly so the prior rough assembly is
not overwritten.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

import create_rough_assembly_v1 as rough


ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ASM_2026 = ROOT / "03_cad" / "solidworks" / "assembly" / "blood_sorting_robot_rough_layout_2026_v1.SLDASM"
LOG_2026 = ROOT / "03_cad" / "solidworks" / "assembly" / "rough_assembly_2026_v1_log.md"
REPORT_2026 = ROOT / "reports" / "stage_4c_2026_rough_assembly_generation_report.md"
NATIVE_MAPPING = ROOT / "03_cad" / "solidworks" / "converted_native" / "native_file_mapping.csv"
TEMPLATE_CONFIG = ROOT / "03_cad" / "solidworks" / "macros" / "solidworks_template_config.json"


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def count_log_value(lines: list[str], prefix: str, default: str = "unknown") -> str:
    for line in lines:
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return default


def template_summary() -> list[str]:
    import json

    try:
        config: dict[str, Any] = json.loads(TEMPLATE_CONFIG.read_text(encoding="utf-8"))
    except Exception:
        config = {}
    output = []
    for key in ["part_template_path", "assembly_template_path", "drawing_template_path"]:
        raw = str(config.get(key, ""))
        path = Path(raw) if raw else None
        output.append(f"- {key}: `{raw}`; exists={bool(path and path.exists())}")
    return output


def write_report(success: bool, log_lines: list[str]) -> None:
    mapping = read_csv(NATIVE_MAPPING) if NATIVE_MAPPING.exists() else []
    native_available = sum(1 for row in mapping if row.get("native_file_exists") == "true")
    missing = [row.get("component_name", "") for row in mapping if row.get("native_file_exists") != "true"]
    inserted = count_log_value(log_lines, "- Inserted rows")
    failed = count_log_value(log_lines, "- Insertion failed rows")
    skipped = count_log_value(log_lines, "- Skipped rows")
    manual_checks: list[str] = []
    in_manual_section = False
    for line in log_lines:
        if line.strip() == "## Manual Orientation Check Components":
            in_manual_section = True
            continue
        if in_manual_section and line.startswith("- "):
            manual_checks.append(line[2:])

    lines = [
        "# Stage 4C SolidWorks 2026 Rough Assembly Generation Report",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "- Branch purpose: controlled SolidWorks 2026 migration validation",
        "",
        "## 1. SolidWorks 2026 Template Paths",
        "",
        *template_summary(),
        "",
        "## 2. Native Cache Usage",
        "",
        f"- Native mapping file: `{rel(NATIVE_MAPPING)}`",
        f"- Native files mapped for placement: {native_available}",
        f"- Native mapping rows still missing files: {len(missing)}",
    ]
    for item in missing:
        lines.append(f"  - {item}")
    lines.extend(
        [
            "",
            "## 3. Rough Assembly Result",
            "",
            f"- Generated 2026 rough assembly: {success}",
            f"- Assembly path: `{rel(OUTPUT_ASM_2026)}`",
            f"- Assembly exists: {OUTPUT_ASM_2026.exists()}",
            f"- Assembly size bytes: {OUTPUT_ASM_2026.stat().st_size if OUTPUT_ASM_2026.exists() else 'N/A'}",
            f"- Inserted component rows: {inserted}",
            f"- Failed insertion rows: {failed}",
            f"- Skipped component rows: {skipped}",
            "",
            "## 4. Skipped Components",
            "",
        ]
    )
    if missing:
        lines.extend([f"- {item}" for item in missing])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## 5. Required Manual View Checks",
            "",
            "- Overall isometric view.",
            "- Top view.",
            "- Front view.",
            "- Side view.",
            "- Gripper and sample tube detail.",
            "- Scan station detail.",
            "- Output bin area detail.",
            "",
            "## 6. Manual Orientation Check Components",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in manual_checks] or ["- None recorded"])
    lines.extend(
        [
            "",
            "## 7. Notes",
            "",
            "- This assembly is a 2026 migration validation artifact, not the final engineering assembly.",
            "- The script used existing native `.SLDPRT/.SLDASM` files only and did not open or convert STEP/STP.",
            "- The existing `blood_sorting_robot_rough_layout_v1.SLDASM` was not overwritten.",
        ]
    )
    REPORT_2026.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rough.OUTPUT_ASM = OUTPUT_ASM_2026
    rough.LOG_PATH = LOG_2026
    success, log_lines = rough.run_solidworks_automation()
    write_report(success, log_lines)
    print(f"solidworks_2026_rough_assembly_generated={success}")
    print(f"assembly_path={OUTPUT_ASM_2026}")
    print(f"assembly_size={OUTPUT_ASM_2026.stat().st_size if OUTPUT_ASM_2026.exists() else 'N/A'}")
    print(f"log_path={LOG_2026}")
    print(f"report_path={REPORT_2026}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
