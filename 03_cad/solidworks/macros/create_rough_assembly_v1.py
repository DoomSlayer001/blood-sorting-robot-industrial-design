"""
Create the first rough SolidWorks assembly from native CAD cache files.

Stage 4B-3 intentionally does not open or convert STEP/STP files through Python
COM. SolidWorks 2018 shows import/template/diagnostics dialogs during STEP import,
and those dialogs made automated COM conversion unreliable in this environment.

The script therefore reads native_file_mapping.csv and inserts only SLDPRT/SLDASM
files that already exist in the native cache or are otherwise registered as
native SolidWorks files.
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
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PLACEMENT_CSV = ROOT / "03_cad" / "solidworks" / "component_placement_table_v1.csv"
NATIVE_MAPPING_CSV = ROOT / "03_cad" / "solidworks" / "converted_native" / "native_file_mapping.csv"
MANUAL_TODO_CSV = ROOT / "03_cad" / "solidworks" / "converted_native" / "manual_native_conversion_todo.csv"
ASSEMBLY_DIR = ROOT / "03_cad" / "solidworks" / "assembly"
LOG_PATH = ASSEMBLY_DIR / "rough_assembly_v1_log.md"
OUTPUT_ASM = ASSEMBLY_DIR / "blood_sorting_robot_rough_layout_v1.SLDASM"
TEMPLATE_CONFIG = ROOT / "03_cad" / "solidworks" / "macros" / "solidworks_template_config.json"
SUPPORTED_NATIVE = {".sldprt", ".sldasm"}

CRITICAL_COMPONENTS = {
    "base_plate",
    "left_y_axis_module",
    "right_y_axis_module",
    "x_axis_module_on_gantry",
    "z_axis_module",
    "electric_parallel_gripper",
    "input_mixed_tube_rack_4x6",
    "barcode_scanner",
    "photoelectric_sensor",
}
OUTPUT_BIN_COMPONENTS = {
    "category_A_output_bin_2x3",
    "category_B_output_bin_2x3",
    "category_C_output_bin_2x3",
    "category_D_output_bin_2x3",
}


def md_path(path: Path | None) -> str:
    if path is None:
        return ""
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
    return rotation_matrix_xyz(rx_deg, ry_deg, rz_deg) + [x_m, y_m, z_m, 1.0, 0.0, 0.0, 0.0]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def load_template_config() -> dict[str, Any]:
    if not TEMPLATE_CONFIG.exists():
        return {}
    try:
        with TEMPLATE_CONFIG.open(encoding="utf-8") as fp:
            data = json.load(fp)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def resolve_assembly_template(sw_app: Any, lines: list[str]) -> str | None:
    config = load_template_config()
    configured = str(config.get("assembly_template_path", "")).strip()
    if configured:
        configured_path = Path(configured)
        if configured_path.exists() and configured_path.is_file():
            lines.append(f"- Assembly template from config: `{configured}`")
            return str(configured_path)
        lines.append(f"- Config assembly template missing or not a file: `{configured}`")
    try:
        default_template = sw_app.GetUserPreferenceStringValue(2)
    except Exception as exc:
        lines.append(f"- SolidWorks default assembly template lookup failed: {type(exc).__name__}: {exc}")
        return None
    if default_template and Path(default_template).exists():
        lines.append(f"- Assembly template from SolidWorks defaults: `{default_template}`")
        return str(default_template)
    lines.append("- Assembly template unavailable.")
    return None


def create_solidworks_app(lines: list[str]) -> Any | None:
    if platform.system().lower() != "windows":
        lines.append("- SolidWorks COM skipped: Windows is required.")
        return None
    try:
        import win32com.client
    except Exception as exc:
        lines.append(f"- SolidWorks COM skipped: win32com unavailable: {type(exc).__name__}: {exc}")
        return None
    try:
        sw_app = win32com.client.Dispatch("SldWorks.Application")
        sw_app.Visible = True
        lines.append("- COM dispatch: succeeded (`SldWorks.Application`).")
        return sw_app
    except Exception as exc:
        lines.append(f"- COM dispatch failed: {type(exc).__name__}: {exc}")
        return None


def resolve_native_path(raw_path: str) -> Path | None:
    raw = (raw_path or "").strip()
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / raw
    return path.resolve()


def mapping_by_component() -> dict[str, dict[str, str]]:
    if not NATIVE_MAPPING_CSV.exists():
        return {}
    return {row.get("component_name", ""): row for row in read_csv(NATIVE_MAPPING_CSV)}


def missing_critical_components(mapping: dict[str, dict[str, str]]) -> list[str]:
    missing: list[str] = []
    for name in sorted(CRITICAL_COMPONENTS):
        row = mapping.get(name)
        if not row or str(row.get("native_file_exists", "")).lower() != "true":
            missing.append(name)
    if not any(
        mapping.get(name) and str(mapping[name].get("native_file_exists", "")).lower() == "true"
        for name in OUTPUT_BIN_COMPONENTS
    ):
        missing.append("at_least_one_category_output_bin")
    return missing


def insert_native_component(model: Any, row: dict[str, str], native_path: Path, math_util: Any, lines: list[str]) -> bool:
    name = row.get("instance_name") or row.get("component_name") or native_path.stem
    x_m = parse_float(row.get("approx_x_mm")) / 1000.0
    y_m = parse_float(row.get("approx_y_mm")) / 1000.0
    z_m = parse_float(row.get("approx_z_mm")) / 1000.0
    rx = parse_float(row.get("rotation_x_deg"))
    ry = parse_float(row.get("rotation_y_deg"))
    rz = parse_float(row.get("rotation_z_deg"))
    manual = str(row.get("manual_check_required", "")).strip().lower() in {"yes", "true", "1"}

    try:
        comp = model.AddComponent5(str(native_path), 0, "", "", False, x_m, y_m, z_m)
        if comp is None:
            lines.append(f"- FAIL `{name}`: AddComponent5 returned None for native file `{md_path(native_path)}`.")
            return False
        try:
            comp.Name2 = name
        except Exception:
            pass
        if math_util is not None:
            try:
                transform = math_util.CreateTransform(transform_array(x_m, y_m, z_m, rx, ry, rz))
                comp.Transform2 = transform
            except Exception as exc:
                lines.append(f"- WARN `{name}`: transform update failed: {type(exc).__name__}: {exc}")
        elif any(abs(v) > 1e-9 for v in [rx, ry, rz]):
            lines.append(f"- WARN `{name}`: nonzero rotation requested but MathUtility unavailable; manual correction required.")
        try:
            model.ClearSelection2(True)
            comp.Select4(False, None, False)
            model.FixComponent()
        except Exception as exc:
            lines.append(f"- WARN `{name}`: fixed component step failed: {type(exc).__name__}: {exc}")
        suffix = " manual orientation check required" if manual else ""
        lines.append(f"- INSERTED `{name}` from `{md_path(native_path)}`.{suffix}")
        return True
    except Exception as exc:
        lines.append(f"- FAIL `{name}`: {type(exc).__name__}: {exc}")
        return False


def write_log(lines: list[str]) -> None:
    ASSEMBLY_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_solidworks_automation() -> tuple[bool, list[str]]:
    ASSEMBLY_DIR.mkdir(parents=True, exist_ok=True)
    placement_rows = read_csv(PLACEMENT_CSV)
    native_mapping = mapping_by_component()

    lines: list[str] = [
        "# Rough Assembly v1 Log",
        "",
        "## Environment",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"- Platform: {platform.platform()}",
        f"- Python: {sys.version.split()[0]}",
        "",
        "## Native Cache Inputs",
        "",
        f"- Placement table: `{md_path(PLACEMENT_CSV)}`",
        f"- Native mapping: `{md_path(NATIVE_MAPPING_CSV)}`; exists={NATIVE_MAPPING_CSV.exists()}",
        f"- Manual conversion TODO: `{md_path(MANUAL_TODO_CSV)}`; exists={MANUAL_TODO_CSV.exists()}",
        f"- Target assembly: `{md_path(OUTPUT_ASM)}`",
        "",
    ]

    found = []
    missing = []
    for row in placement_rows:
        name = row.get("component_name", "")
        mapping = native_mapping.get(name)
        native_path = resolve_native_path(mapping.get("native_cad_path", "")) if mapping else None
        exists = bool(native_path and native_path.exists() and native_path.suffix.lower() in SUPPORTED_NATIVE)
        if exists:
            found.append(name)
            lines.append(f"- FOUND `{name}` -> `{md_path(native_path)}`")
        else:
            missing.append(name)
            lines.append(f"- MISSING `{name}`; native conversion required.")

    critical_missing = missing_critical_components(native_mapping)
    lines.extend(["", "## Critical Component Gate", ""])
    if critical_missing:
        lines.append("- Critical native CAD is incomplete. The script will not create a misleading rough assembly.")
        for name in critical_missing:
            lines.append(f"  - {name}")
        lines.extend(
            [
                "",
                "## Summary",
                "",
                f"- Native files found: {len(found)}",
                f"- Native files missing: {len(missing)}",
                "- Inserted rows: 0",
                "- Skipped rows: all rows skipped by critical gate",
                "- Assembly generated: False",
            ]
        )
        write_log(lines)
        if OUTPUT_ASM.exists():
            OUTPUT_ASM.unlink()
        return False, lines

    lines.extend(["- Critical native CAD gate passed.", "", "## SolidWorks Native Insert", ""])
    sw_app = create_solidworks_app(lines)
    if sw_app is None:
        write_log(lines)
        return False, lines
    template = resolve_assembly_template(sw_app, lines)
    if not template:
        write_log(lines)
        return False, lines
    try:
        model = sw_app.NewDocument(template, 0, 0, 0)
        if model is None:
            lines.append("- NewDocument returned None; assembly not created.")
            write_log(lines)
            return False, lines
    except Exception as exc:
        lines.append(f"- Assembly creation failed: {type(exc).__name__}: {exc}")
        write_log(lines)
        return False, lines
    try:
        math_util = sw_app.GetMathUtility()
    except Exception:
        math_util = None

    inserted = 0
    failed = 0
    skipped = 0
    for row in placement_rows:
        name = row.get("component_name", "")
        mapping = native_mapping.get(name)
        native_path = resolve_native_path(mapping.get("native_cad_path", "")) if mapping else None
        if not native_path or not native_path.exists() or native_path.suffix.lower() not in SUPPORTED_NATIVE:
            skipped += 1
            continue
        if insert_native_component(model, row, native_path, math_util, lines):
            inserted += 1
        else:
            failed += 1

    success = False
    try:
        model.ForceRebuild3(False)
        result = model.SaveAs3(str(OUTPUT_ASM), 0, 1)
        success = bool(result) and inserted > 0 and failed == 0 and OUTPUT_ASM.exists()
        lines.extend(["", "## Save Result", ""])
        lines.append(f"- SaveAs3 returned: `{result}`")
        lines.append(f"- Output exists: `{OUTPUT_ASM.exists()}`")
        if not success and OUTPUT_ASM.exists():
            OUTPUT_ASM.unlink()
            lines.append("- Removed incomplete or failed rough assembly output.")
    except Exception as exc:
        lines.append(f"- Save failed: {type(exc).__name__}: {exc}")

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Native files found: {len(found)}",
            f"- Native files missing: {len(missing)}",
            f"- Inserted rows: {inserted}",
            f"- Insertion failed rows: {failed}",
            f"- Skipped rows: {skipped}",
            f"- Assembly generated: {success}",
        ]
    )
    write_log(lines)
    return success, lines


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
