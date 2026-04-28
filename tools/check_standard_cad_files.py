from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SCAN_DIR = ROOT / "03_cad" / "standard_parts" / "downloaded"
REPORT_DIR = ROOT / "reports"
REPORT_PATH = REPORT_DIR / "cad_file_check_report.md"
ALLOWED_EXTENSIONS = {".step", ".stp", ".sldprt", ".sldasm", ".x_t", ".igs", ".iges"}
CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")


def is_real_candidate(path: Path) -> bool:
    return path.is_file() and path.name != ".gitkeep"


def check_file(path: Path) -> list[str]:
    issues: list[str] = []
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        issues.append(f"extension `{path.suffix}` is not allowed")
    if CHINESE_RE.search(path.name):
        issues.append("file name contains Chinese characters")
    if " " in path.name:
        issues.append("file name contains spaces")
    if path.stat().st_size <= 0:
        issues.append("file size is zero")
    return issues


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in SCAN_DIR.rglob("*") if is_real_candidate(p))
    rows = []
    valid_count = 0

    for path in files:
        issues = check_file(path)
        if not issues:
            valid_count += 1
        rel = path.relative_to(ROOT).as_posix()
        rows.append((rel, path.stat().st_size, "OK" if not issues else "; ".join(issues)))

    lines = [
        "# CAD File Check Report",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"- Scan directory: `{SCAN_DIR.relative_to(ROOT).as_posix()}`",
        f"- Real CAD file count: {len(files)}",
        f"- Valid CAD file count: {valid_count}",
        "",
    ]

    if not files:
        lines.extend([
            "## Status",
            "",
            "当前尚未导入真实 CAD。",
            "",
            "No CAD files were found under the downloaded standard-parts directory. This is expected for Stage 3A.",
            "",
        ])
    else:
        lines.extend([
            "## File Results",
            "",
            "| file | size_bytes | status |",
            "|---|---:|---|",
        ])
        for rel, size, status in rows:
            lines.append(f"| `{rel}` | {size} | {status} |")
        lines.append("")

    lines.extend([
        "## Rules",
        "",
        "- This script does not modify CAD files.",
        "- This script does not mark any file as downloaded in BOM or CAD status tables.",
        "- Allowed extensions: `.step`, `.stp`, `.sldprt`, `.sldasm`, `.x_t`, `.igs`, `.iges`.",
        "- File names must not contain Chinese characters or spaces.",
    ])

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"CAD file check complete: {REPORT_PATH}")
    print(f"Real CAD file count: {len(files)}")
    print(f"Valid CAD file count: {valid_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
