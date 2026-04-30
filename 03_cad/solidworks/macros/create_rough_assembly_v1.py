"""
Create the first rough SolidWorks assembly from component_placement_table_v1.csv.

This script intentionally performs only coordinate placement. It does not create
mates, does not infer mounting faces, and does not select holes.
"""

from __future__ import annotations

import csv
import json
import math
import platform
import sys
import traceback
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PLACEMENT_CSV = ROOT / "03_cad" / "solidworks" / "component_placement_table_v1.csv"
INVENTORY_CSV = ROOT / "03_cad" / "solidworks" / "current_cad_inventory_for_assembly.csv"
ASSEMBLY_DIR = ROOT / "03_cad" / "solidworks" / "assembly"
LOG_PATH = ASSEMBLY_DIR / "rough_assembly_v1_log.md"
OUTPUT_ASM = ASSEMBLY_DIR / "blood_sorting_robot_rough_layout_v1.SLDASM"
TEMPLATE_CONFIG = ROOT / "03_cad" / "solidworks" / "macros" / "solidworks_template_config.json"


def md_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def parse_float(value: str | None, default: float = 0.0) -> float:
    if value is None or str(value).strip() == "":
        return default
    try:
        return float(str(value).strip())
    except ValueError:
        return default


def rotation_matrix_xyz(rx_deg: float, ry_deg: float, rz_deg: float) -> list[float]:
    rx = math.radians(rx_deg)
    ry = math.radians(ry_deg)
    rz = math.radians(rz_deg)

    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)

    # R = Rz * Ry * Rx
    return [
        cz * cy,
        cz * sy * sx - sz * cx,
        cz * sy * cx + sz * sx,
        sz * cy,
        sz * sy * sx + cz * cx,
        sz * sy * cx - cz * sx,
        -sy,
        cy * sx,
        cy * cx,
    ]


def transform_array(x_m: float, y_m: float, z_m: float, rx_deg: float, ry_deg: float, rz_deg: float) -> list[float]:
    rot = rotation_matrix_xyz(rx_deg, ry_deg, rz_deg)
    return rot + [x_m, y_m, z_m, 1.0, 0.0, 0.0, 0.0]


def read_rows() -> list[dict[str, str]]:
    with PLACEMENT_CSV.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def load_template_config() -> dict[str, str]:
    if not TEMPLATE_CONFIG.exists():
        return {}
    try:
        with TEMPLATE_CONFIG.open(encoding="utf-8") as fp:
            data = json.load(fp)
    except Exception:
        return {}
    return {str(k): str(v) for k, v in data.items()}


def resolve_assembly_template(sw_app, lines: list[str]) -> str | None:
    config = load_template_config()
    configured = config.get("assembly_template_path", "").strip()
    if configured:
        configured_path = Path(configured)
        if configured_path.exists() and configured_path.is_file():
            lines.append(f"- Assembly template from config: `{configured}`")
            return str(configured_path)
        lines.append(f"- Config assembly template missing or not a file: `{configured}`")
    else:
        lines.append("- Config assembly template: empty or not configured.")

    try:
        default_template = sw_app.GetUserPreferenceStringValue(2)  # swDefaultTemplateAssembly
    except Exception as exc:
        lines.append(f"- SolidWorks default assembly template lookup failed: {type(exc).__name__}: {exc}")
        return None

    if default_template and Path(default_template).exists():
        lines.append(f"- Assembly template from SolidWorks defaults: `{default_template}`")
        return str(default_template)

    if default_template:
        lines.append(f"- SolidWorks default assembly template path does not exist: `{default_template}`")
    else:
        lines.append("- SolidWorks default assembly template: not configured.")
    return None


def is_usable_cad_path(raw_path: str) -> tuple[bool, str, Path | None]:
    raw = (raw_path or "").strip()
    if not raw or raw.upper() == "TBD":
        return False, "missing_or_tbd_path", None
    if "*" in raw or "?" in raw:
        return False, "wildcard_path_not_expanded_in_4B", None
    path = ROOT / raw
    if not path.exists():
        return False, "file_not_found", path
    if not path.is_file():
        return False, "not_a_file", path
    return True, "ok", path


def write_log(lines: list[str]) -> None:
    ASSEMBLY_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def environment_lines() -> list[str]:
    lines = [
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"- Platform: {platform.platform()}",
        f"- Python: {sys.version.split()[0]}",
    ]
    try:
        import win32com.client  # noqa: F401

        lines.append("- win32com.client: available")
    except Exception as exc:  # pragma: no cover - host dependent
        lines.append(f"- win32com.client: unavailable ({type(exc).__name__}: {exc})")
    return lines


def run_solidworks_automation() -> tuple[bool, list[str]]:
    lines: list[str] = [
        "# Rough Assembly v1 Log",
        "",
        "## Environment",
        "",
        *environment_lines(),
        "",
        "## Input",
        "",
        f"- Placement table: `{md_path(PLACEMENT_CSV)}`",
        f"- CAD inventory: `{md_path(INVENTORY_CSV)}`; exists={INVENTORY_CSV.exists()}",
        f"- Template config: `{md_path(TEMPLATE_CONFIG)}`; exists={TEMPLATE_CONFIG.exists()}",
        f"- Target assembly: `{md_path(OUTPUT_ASM)}`",
        "",
    ]

    rows = read_rows()
    lines.extend(["## Row Precheck", ""])
    valid_rows: list[tuple[dict[str, str], Path]] = []
    skipped_rows: list[tuple[dict[str, str], str]] = []
    for row in rows:
        ok, reason, path = is_usable_cad_path(row.get("cad_file_path", ""))
        if ok and path is not None:
            valid_rows.append((row, path))
            lines.append(f"- OK `{row.get('component_name')}` -> `{md_path(path)}`")
        else:
            skipped_rows.append((row, reason))
            raw = row.get("cad_file_path", "")
            lines.append(f"- SKIP `{row.get('component_name')}`: {reason}; path=`{raw}`")

    lines.extend(["", "## SolidWorks Automation", ""])
    if platform.system().lower() != "windows":
        lines.append("- Result: skipped. SolidWorks COM automation requires Windows.")
        write_log(lines)
        return False, lines

    try:
        import win32com.client
    except Exception as exc:
        lines.append(f"- Result: skipped. `win32com.client` unavailable: {type(exc).__name__}: {exc}")
        write_log(lines)
        return False, lines

    try:
        sw_app = win32com.client.Dispatch("SldWorks.Application")
        sw_app.Visible = True
        lines.append("- COM dispatch: succeeded (`SldWorks.Application`).")
    except Exception as exc:
        lines.append(f"- COM dispatch: failed: {type(exc).__name__}: {exc}")
        write_log(lines)
        return False, lines

    try:
        template = resolve_assembly_template(sw_app, lines)
        if not template:
            lines.append("- Assembly template: unavailable; cannot create a new assembly automatically.")
            write_log(lines)
            return False, lines

        model = sw_app.NewDocument(template, 0, 0, 0)
        if model is None:
            lines.append("- NewDocument returned no model; assembly not created.")
            write_log(lines)
            return False, lines
        assembly = model
        try:
            math_util = sw_app.GetMathUtility()
            lines.append("- MathUtility: available.")
        except Exception as exc:
            math_util = None
            lines.append(f"- MathUtility: unavailable; components will use AddComponent5 coordinate placement only. {type(exc).__name__}: {exc}")
    except Exception as exc:
        lines.append(f"- Assembly creation failed: {type(exc).__name__}: {exc}")
        write_log(lines)
        return False, lines

    inserted = 0
    failed = 0
    lines.extend(["", "## Insert Results", ""])

    for row, cad_path in valid_rows:
        name = row.get("instance_name") or row.get("component_name") or cad_path.stem
        x_m = parse_float(row.get("approx_x_mm")) / 1000.0
        y_m = parse_float(row.get("approx_y_mm")) / 1000.0
        z_m = parse_float(row.get("approx_z_mm")) / 1000.0
        rx = parse_float(row.get("rotation_x_deg"))
        ry = parse_float(row.get("rotation_y_deg"))
        rz = parse_float(row.get("rotation_z_deg"))
        manual = str(row.get("manual_check_required", "")).strip().lower() in {"yes", "true", "1"}

        try:
            comp = assembly.AddComponent5(str(cad_path), 0, "", False, "", x_m, y_m, z_m)
            if comp is None:
                failed += 1
                lines.append(f"- FAIL `{name}`: AddComponent5 returned None.")
                continue

            try:
                comp.Name2 = name
            except Exception:
                pass

            if math_util is not None:
                try:
                    transform = math_util.CreateTransform(transform_array(x_m, y_m, z_m, rx, ry, rz))
                    comp.Transform2 = transform
                except Exception as exc:
                    lines.append(f"- WARN `{name}`: placement inserted but transform update failed: {type(exc).__name__}: {exc}")
            elif any(abs(v) > 1e-9 for v in [rx, ry, rz]):
                lines.append(f"- WARN `{name}`: nonzero rotation requested but MathUtility is unavailable; rotation requires manual correction.")

            try:
                model.ClearSelection2(True)
                comp.Select4(False, None, False)
                assembly.FixComponent()
            except Exception as exc:
                lines.append(f"- WARN `{name}`: fixed-component step failed: {type(exc).__name__}: {exc}")

            inserted += 1
            suffix = " manual orientation check required" if manual else ""
            lines.append(f"- INSERTED `{name}` from `{md_path(cad_path)}` at ({x_m:.4f}, {y_m:.4f}, {z_m:.4f}) m.{suffix}")
        except Exception as exc:
            failed += 1
            lines.append(f"- FAIL `{name}`: {type(exc).__name__}: {exc}")

    success = False
    try:
        model.ForceRebuild3(False)
        result = model.SaveAs3(str(OUTPUT_ASM), 0, 2)
        success = bool(result) and inserted > 0 and failed == 0
        lines.extend(["", "## Save Result", ""])
        lines.append(f"- SaveAs3 returned: `{result}`")
        lines.append(f"- Output exists: `{OUTPUT_ASM.exists()}`")
        if not success and OUTPUT_ASM.exists():
            try:
                OUTPUT_ASM.unlink()
                lines.append("- Removed incomplete or failed rough assembly output to avoid treating it as a valid SLDASM.")
            except Exception as exc:
                lines.append(f"- Could not remove incomplete rough assembly output: {type(exc).__name__}: {exc}")
    except Exception as exc:
        lines.extend(["", "## Save Result", ""])
        lines.append(f"- Save failed: {type(exc).__name__}: {exc}")

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Total CSV rows: {len(rows)}",
            f"- Valid CAD rows attempted: {len(valid_rows)}",
            f"- Skipped rows: {len(skipped_rows)}",
            f"- Inserted rows: {inserted}",
            f"- Failed insertions: {failed}",
            f"- Assembly generated: {success and OUTPUT_ASM.exists()}",
            f"- Output assembly path: `{md_path(OUTPUT_ASM)}`",
            "",
            "This log is diagnostic only. The rough assembly remains a coordinate scaffold and requires manual SolidWorks review.",
        ]
    )
    write_log(lines)
    return success and OUTPUT_ASM.exists(), lines


def main() -> int:
    try:
        success, _lines = run_solidworks_automation()
        print(f"Rough assembly automation completed. assembly_generated={success}")
        print(f"Log: {LOG_PATH}")
        return 0
    except Exception:
        lines = [
            "# Rough Assembly v1 Log",
            "",
            "Unexpected script-level failure:",
            "",
            "```text",
            traceback.format_exc(),
            "```",
        ]
        write_log(lines)
        print(f"Rough assembly automation failed at script level. Log: {LOG_PATH}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
