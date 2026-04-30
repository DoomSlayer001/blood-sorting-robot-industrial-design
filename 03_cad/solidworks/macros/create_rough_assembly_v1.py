"""
Create the first rough SolidWorks assembly from component_placement_table_v1.csv.

The Stage 4B-2 workflow is intentionally conservative:

1. Resolve and diagnose every CAD path.
2. Convert STEP/STP files to native SolidWorks files first.
3. Insert only SLDPRT/SLDASM files into the rough assembly.

The script does not create final mates, does not infer mounting faces, and does
not select holes. It is a rough layout scaffold for manual inspection.
"""

from __future__ import annotations

import csv
import json
import math
import platform
import re
import shutil
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PLACEMENT_CSV = ROOT / "03_cad" / "solidworks" / "component_placement_table_v1.csv"
INVENTORY_CSV = ROOT / "03_cad" / "solidworks" / "current_cad_inventory_for_assembly.csv"
ASSEMBLY_DIR = ROOT / "03_cad" / "solidworks" / "assembly"
LOG_PATH = ASSEMBLY_DIR / "rough_assembly_v1_log.md"
OUTPUT_ASM = ASSEMBLY_DIR / "blood_sorting_robot_rough_layout_v1.SLDASM"
TEMPLATE_CONFIG = ROOT / "03_cad" / "solidworks" / "macros" / "solidworks_template_config.json"
CONVERTED_DIR = ROOT / "03_cad" / "solidworks" / "converted_native"
CONVERTED_PARTS_DIR = CONVERTED_DIR / "parts"
CONVERTED_ASM_DIR = CONVERTED_DIR / "assemblies"
CONVERSION_REPORT_DIR = ROOT / "03_cad" / "solidworks" / "conversion_reports"
CONVERSION_REPORT_CSV = CONVERSION_REPORT_DIR / "step_to_native_conversion_report.csv"
CONVERSION_REPORT_MD = CONVERSION_REPORT_DIR / "step_to_native_conversion_report.md"
BASE_PLATE_PATH = ROOT / "03_cad" / "custom_parts" / "base_plate" / "base_plate_1100x900x15.step"


SW_DOC_PART = 1
SW_DOC_ASSEMBLY = 2
SW_OPEN_SILENT = 1
SW_SAVE_SILENT = 1
SUPPORTED_NATIVE = {".sldprt", ".sldasm"}
SUPPORTED_CONVERT = {".step", ".stp"}


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


def safe_stem(text: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", text.strip())
    safe = re.sub(r"_+", "_", safe).strip("._")
    return safe or "component"


def path_notes(path: Path) -> str:
    text = str(path)
    notes: list[str] = []
    if any("\u4e00" <= ch <= "\u9fff" for ch in text):
        notes.append("contains_chinese")
    if " " in text:
        notes.append("contains_space")
    if "(" in text or ")" in text:
        notes.append("contains_parentheses")
    return ";".join(notes) if notes else "clean"


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


def read_rows() -> list[dict[str, str]]:
    with PLACEMENT_CSV.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def ensure_dirs() -> None:
    for folder in [ASSEMBLY_DIR, CONVERTED_PARTS_DIR, CONVERTED_ASM_DIR, CONVERSION_REPORT_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def load_template_config() -> dict[str, str]:
    if not TEMPLATE_CONFIG.exists():
        return {}
    try:
        with TEMPLATE_CONFIG.open(encoding="utf-8") as fp:
            data = json.load(fp)
    except Exception:
        return {}
    return {str(k): str(v) for k, v in data.items()}


def resolve_assembly_template(sw_app: Any, lines: list[str]) -> str | None:
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
        default_template = sw_app.GetUserPreferenceStringValue(2)
    except Exception as exc:
        lines.append(f"- SolidWorks default assembly template lookup failed: {type(exc).__name__}: {exc}")
        return None
    if default_template and Path(default_template).exists():
        lines.append(f"- Assembly template from SolidWorks defaults: `{default_template}`")
        return str(default_template)
    lines.append("- SolidWorks default assembly template: not configured or missing.")
    return None


def resolve_cad_path(row: dict[str, str]) -> dict[str, Any]:
    raw = (row.get("cad_file_path") or "").strip()
    result: dict[str, Any] = {
        "row": row,
        "original_path": raw,
        "resolved_path": None,
        "exists": False,
        "extension": "",
        "path_notes": "",
        "precheck_status": "ok",
        "precheck_note": "",
    }
    if not raw or raw.upper() == "TBD":
        result["precheck_status"] = "skipped"
        result["precheck_note"] = "missing_or_tbd_path"
        return result
    if "*" in raw or "?" in raw:
        result["precheck_status"] = "skipped"
        result["precheck_note"] = "wildcard_path_not_expanded_in_4B2"
        return result
    path = (ROOT / raw).resolve()
    result["resolved_path"] = path
    result["exists"] = path.exists() and path.is_file()
    result["extension"] = path.suffix.lower()
    result["path_notes"] = path_notes(path)
    if not result["exists"]:
        result["precheck_status"] = "failed"
        result["precheck_note"] = "file_not_found"
    elif result["extension"] not in SUPPORTED_NATIVE | SUPPORTED_CONVERT:
        result["precheck_status"] = "skipped"
        result["precheck_note"] = f"unsupported_extension_{result['extension']}"
    return result


def conversion_report_row(
    diag: dict[str, Any],
    native_path: Path | None,
    status: str,
    open_status: str,
    save_status: str,
    error_message: str,
    notes: str,
) -> dict[str, str]:
    row = diag["row"]
    return {
        "component_name": row.get("component_name", ""),
        "instance_name": row.get("instance_name", ""),
        "original_cad_path": diag.get("original_path", ""),
        "resolved_path": str(diag.get("resolved_path") or ""),
        "original_extension": diag.get("extension", ""),
        "native_output_path": str(native_path or ""),
        "conversion_status": status,
        "open_status": open_status,
        "save_status": save_status,
        "error_message": error_message,
        "notes": notes,
    }


def open_step_document(sw_app: Any, path: Path) -> tuple[Any | None, str, str]:
    import pythoncom
    import win32com.client

    errors_seen: list[str] = []
    for doc_type in [SW_DOC_PART, SW_DOC_ASSEMBLY]:
        try:
            errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            model = sw_app.OpenDoc6(str(path), doc_type, SW_OPEN_SILENT, "", errors, warnings)
            if model is not None:
                return model, f"opened_doc_type_{doc_type}; errors={errors.value}; warnings={warnings.value}", ""
            errors_seen.append(f"OpenDoc6_doc_type_{doc_type}_returned_None; errors={errors.value}; warnings={warnings.value}")
        except Exception as exc:
            errors_seen.append(f"OpenDoc6_doc_type_{doc_type}_{type(exc).__name__}: {exc}")

    for arg_string in ["r", ""]:
        try:
            errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            model = sw_app.LoadFile4(str(path), arg_string, None, errors)
            if model is not None:
                return model, f"LoadFile4_arg_{arg_string or 'empty'}; errors={errors.value}", ""
            errors_seen.append(f"LoadFile4_arg_{arg_string or 'empty'}_returned_None; errors={errors.value}")
        except Exception as exc:
            errors_seen.append(f"LoadFile4_arg_{arg_string or 'empty'}_{type(exc).__name__}: {exc}")

    return None, "failed", " | ".join(errors_seen) if errors_seen else "STEP import returned None"


def model_doc_type(model: Any) -> int:
    try:
        return int(model.GetType())
    except Exception:
        return SW_DOC_PART


def save_model_native(model: Any, output_path: Path) -> tuple[bool, str]:
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result = model.SaveAs3(str(output_path), 0, SW_SAVE_SILENT)
        ok = bool(result) and output_path.exists() and output_path.stat().st_size > 0
        return ok, f"SaveAs3_return={result}; exists={output_path.exists()}"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def close_doc(sw_app: Any, model: Any) -> None:
    try:
        title = model.GetTitle()
        if title:
            sw_app.CloseDoc(title)
    except Exception:
        pass


def convert_cad_to_native_if_needed(sw_app: Any, diag: dict[str, Any]) -> tuple[Path | None, dict[str, str]]:
    path: Path | None = diag.get("resolved_path")
    row = diag["row"]
    if diag["precheck_status"] != "ok" or path is None:
        report = conversion_report_row(
            diag,
            None,
            diag["precheck_status"],
            "not_attempted",
            "not_attempted",
            diag.get("precheck_note", ""),
            diag.get("path_notes", ""),
        )
        return None, report

    ext = path.suffix.lower()
    if ext in SUPPORTED_NATIVE:
        report = conversion_report_row(
            diag,
            path,
            "native_reused",
            "not_needed",
            "not_needed",
            "",
            diag.get("path_notes", ""),
        )
        return path, report

    if ext not in SUPPORTED_CONVERT:
        report = conversion_report_row(
            diag,
            None,
            "skipped",
            "not_attempted",
            "not_attempted",
            f"unsupported_extension_{ext}",
            diag.get("path_notes", ""),
        )
        return None, report

    model, open_status, open_error = open_step_document(sw_app, path)
    if model is None:
        report = conversion_report_row(diag, None, "failed", open_status, "not_attempted", open_error, diag.get("path_notes", ""))
        return None, report

    doc_type = model_doc_type(model)
    stem = safe_stem(f"{row.get('component_name', path.stem)}_{path.stem}")
    if doc_type == SW_DOC_ASSEMBLY:
        native_path = CONVERTED_ASM_DIR / f"{stem}.SLDASM"
    else:
        native_path = CONVERTED_PARTS_DIR / f"{stem}.SLDPRT"

    ok, save_status = save_model_native(model, native_path)
    close_doc(sw_app, model)
    if ok:
        report = conversion_report_row(diag, native_path, "converted", open_status, save_status, "", diag.get("path_notes", ""))
        return native_path, report
    report = conversion_report_row(diag, native_path, "failed", open_status, save_status, save_status, diag.get("path_notes", ""))
    return None, report


def write_conversion_reports(report_rows: list[dict[str, str]], base_diag: dict[str, str], assembly_generated: bool) -> None:
    fieldnames = [
        "component_name",
        "instance_name",
        "original_cad_path",
        "resolved_path",
        "original_extension",
        "native_output_path",
        "conversion_status",
        "open_status",
        "save_status",
        "error_message",
        "notes",
    ]
    with CONVERSION_REPORT_CSV.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_rows)

    converted = [r for r in report_rows if r["conversion_status"] in {"converted", "native_reused"}]
    failed = [r for r in report_rows if r["conversion_status"] == "failed"]
    skipped = [r for r in report_rows if r["conversion_status"] == "skipped"]
    lines = [
        "# STEP To Native Conversion Report",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"- Base plate diagnostic status: {base_diag.get('status', 'unknown')}",
        f"- Base plate diagnostic detail: {base_diag.get('detail', '')}",
        f"- Successful native outputs or reused native files: {len(converted)}",
        f"- Failed conversions: {len(failed)}",
        f"- Skipped rows: {len(skipped)}",
        f"- Rough assembly generated: {assembly_generated}",
        "",
        "## Native Files Used Or Produced",
        "",
    ]
    if converted:
        for row in converted:
            lines.append(f"- `{row['component_name']}` -> `{row['native_output_path']}` ({row['conversion_status']})")
    else:
        lines.append("- None.")
    lines.extend(["", "## Failed Rows", ""])
    if failed:
        for row in failed:
            lines.append(f"- `{row['component_name']}`: {row['error_message']}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Skipped Rows", ""])
    if skipped:
        for row in skipped:
            lines.append(f"- `{row['component_name']}`: {row['error_message']}")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            "If Python COM conversion or insertion fails, run the VBA fallback from inside SolidWorks or manually verify opening `base_plate_1100x900x15.step`, saving it as `.SLDPRT`, and inserting it into a new assembly.",
        ]
    )
    CONVERSION_REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_log(lines: list[str]) -> None:
    ensure_dirs()
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
    except Exception as exc:
        lines.append(f"- win32com.client: unavailable ({type(exc).__name__}: {exc})")
    return lines


def create_solidworks_app(lines: list[str]) -> Any | None:
    if platform.system().lower() != "windows":
        lines.append("- Result: skipped. SolidWorks COM automation requires Windows.")
        return None
    try:
        import win32com.client
    except Exception as exc:
        lines.append(f"- Result: skipped. `win32com.client` unavailable: {type(exc).__name__}: {exc}")
        return None
    try:
        sw_app = win32com.client.Dispatch("SldWorks.Application")
        sw_app.Visible = True
        lines.append("- COM dispatch: succeeded (`SldWorks.Application`).")
        return sw_app
    except Exception as exc:
        lines.append(f"- COM dispatch: failed: {type(exc).__name__}: {exc}")
        return None


def base_plate_diagnostic(sw_app: Any, template: str | None, base_diag: dict[str, Any], lines: list[str]) -> tuple[bool, Path | None, dict[str, str]]:
    lines.extend(["", "## Base Plate Single-File Diagnostic", ""])
    native_path, report = convert_cad_to_native_if_needed(sw_app, base_diag)
    if native_path is None:
        detail = report.get("error_message") or report.get("conversion_status", "")
        lines.append(f"- Base plate conversion failed: {detail}")
        return False, None, {"status": "failed", "detail": detail}
    lines.append(f"- Base plate conversion/native path: `{md_path(native_path)}`")

    if template is None:
        return False, native_path, {"status": "converted_but_no_template", "detail": "No assembly template available for insert test."}

    try:
        model = sw_app.NewDocument(template, 0, 0, 0)
        if model is None:
            return False, native_path, {"status": "insert_failed", "detail": "NewDocument returned None for base plate insert test."}
        comp = model.AddComponent5(str(native_path), 0, "", "", False, 0.0, 0.0, -0.0075)
        if comp is None:
            return False, native_path, {"status": "insert_failed", "detail": "AddComponent5 returned None for base plate native file."}
        lines.append("- Base plate native insertion into test assembly succeeded.")
        return True, native_path, {"status": "success", "detail": "Base plate converted and inserted into a test assembly."}
    except Exception as exc:
        return False, native_path, {"status": "insert_failed", "detail": f"{type(exc).__name__}: {exc}"}


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
            lines.append(f"- WARN `{name}`: fix step failed: {type(exc).__name__}: {exc}")
        suffix = " manual orientation check required" if manual else ""
        lines.append(f"- INSERTED `{name}` from `{md_path(native_path)}`.{suffix}")
        return True
    except Exception as exc:
        lines.append(f"- FAIL `{name}`: {type(exc).__name__}: {exc}")
        return False


def run_solidworks_automation() -> tuple[bool, list[str]]:
    ensure_dirs()
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
    diagnostics = [resolve_cad_path(row) for row in rows]
    report_rows: list[dict[str, str]] = []
    native_map: dict[str, Path] = {}

    lines.extend(["## Path Precheck", ""])
    for diag in diagnostics:
        row = diag["row"]
        resolved = diag.get("resolved_path")
        lines.append(
            f"- `{row.get('component_name')}` original=`{diag.get('original_path')}` "
            f"resolved=`{resolved}` exists={diag.get('exists')} ext=`{diag.get('extension')}` notes=`{diag.get('path_notes')}` "
            f"status={diag.get('precheck_status')} {diag.get('precheck_note')}"
        )

    lines.extend(["", "## SolidWorks Automation", ""])
    sw_app = create_solidworks_app(lines)
    if sw_app is None:
        for diag in diagnostics:
            report_rows.append(conversion_report_row(diag, None, "failed", "not_attempted", "not_attempted", "SolidWorks COM unavailable", diag.get("path_notes", "")))
        write_conversion_reports(report_rows, {"status": "failed", "detail": "SolidWorks COM unavailable"}, False)
        write_log(lines)
        return False, lines

    template = resolve_assembly_template(sw_app, lines)
    try:
        math_util = sw_app.GetMathUtility()
        lines.append("- MathUtility: available.")
    except Exception as exc:
        math_util = None
        lines.append(f"- MathUtility: unavailable; insertion will use AddComponent5 coordinates only. {type(exc).__name__}: {exc}")

    base_diag = next((d for d in diagnostics if d.get("resolved_path") == BASE_PLATE_PATH.resolve()), None)
    if base_diag is None:
        base_diag = resolve_cad_path({"component_name": "base_plate", "instance_name": "base_plate_diag", "cad_file_path": md_path(BASE_PLATE_PATH)})
    base_ok, _base_native, base_status = base_plate_diagnostic(sw_app, template, base_diag, lines)
    report_rows.append(conversion_report_row(base_diag, _base_native, "diagnostic_success" if base_ok else "failed", "see_log", "see_log", base_status.get("detail", ""), "base_plate_single_file_diagnostic"))

    if not base_ok:
        lines.append("- Base plate diagnostic failed; batch conversion stopped by design.")
        write_conversion_reports(report_rows + [conversion_report_row(d, None, "skipped", "not_attempted", "not_attempted", "stopped_after_base_plate_failure", d.get("path_notes", "")) for d in diagnostics if d is not base_diag], base_status, False)
        write_log(lines)
        return False, lines

    lines.extend(["", "## Batch Native Conversion", ""])
    for diag in diagnostics:
        native_path, report = convert_cad_to_native_if_needed(sw_app, diag)
        report_rows.append(report)
        if native_path is not None:
            native_map[diag["row"].get("component_name", "")] = native_path
            lines.append(f"- NATIVE `{diag['row'].get('component_name')}` -> `{md_path(native_path)}` status={report['conversion_status']}")
        else:
            lines.append(f"- NO NATIVE `{diag['row'].get('component_name')}` status={report['conversion_status']} reason={report['error_message']}")

    lines.extend(["", "## Native Assembly Insert", ""])
    inserted = 0
    insertion_failed = 0
    skipped_insert = 0
    if template is None:
        lines.append("- Assembly insertion skipped: no assembly template available.")
    else:
        try:
            model = sw_app.NewDocument(template, 0, 0, 0)
            if model is None:
                lines.append("- Assembly insertion skipped: NewDocument returned None.")
            else:
                for diag in diagnostics:
                    row = diag["row"]
                    native_path = native_map.get(row.get("component_name", ""))
                    if native_path is None:
                        skipped_insert += 1
                        continue
                    if native_path.suffix.lower() not in SUPPORTED_NATIVE:
                        skipped_insert += 1
                        lines.append(f"- SKIP `{row.get('component_name')}`: native path is not SLDPRT/SLDASM.")
                        continue
                    if insert_native_component(model, row, native_path, math_util, lines):
                        inserted += 1
                    else:
                        insertion_failed += 1

                try:
                    model.ForceRebuild3(False)
                    result = model.SaveAs3(str(OUTPUT_ASM), 0, SW_SAVE_SILENT)
                    success = bool(result) and inserted > 0 and insertion_failed == 0
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
                    success = False
                    lines.extend(["", "## Save Result", ""])
                    lines.append(f"- Save failed: {type(exc).__name__}: {exc}")
        except Exception as exc:
            success = False
            lines.append(f"- Assembly insertion failed at setup: {type(exc).__name__}: {exc}")

    if "success" not in locals():
        success = False

    converted_count = sum(1 for r in report_rows if r["conversion_status"] in {"converted", "native_reused", "diagnostic_success"})
    conversion_failed_count = sum(1 for r in report_rows if r["conversion_status"] == "failed")
    manual_checks = [d["row"].get("component_name", "") for d in diagnostics if str(d["row"].get("manual_check_required", "")).lower() in {"yes", "true", "1"}]
    lines.extend(
        [
            "",
            "## Manual Orientation Check List",
            "",
            *(f"- {name}" for name in manual_checks),
            "",
            "## Summary",
            "",
            f"- Total CSV rows: {len(rows)}",
            f"- Native conversion/reuse count: {converted_count}",
            f"- Conversion failed count: {conversion_failed_count}",
            f"- Skipped rows: {sum(1 for d in diagnostics if d.get('precheck_status') == 'skipped')}",
            f"- Inserted rows: {inserted}",
            f"- Insertion failed rows: {insertion_failed}",
            f"- Insertion skipped rows: {skipped_insert}",
            f"- Assembly generated: {success and OUTPUT_ASM.exists()}",
            f"- Output assembly path: `{md_path(OUTPUT_ASM)}`",
        ]
    )
    write_conversion_reports(report_rows, base_status, success and OUTPUT_ASM.exists())
    write_log(lines)
    return success and OUTPUT_ASM.exists(), lines


def main() -> int:
    try:
        success, _lines = run_solidworks_automation()
        print(f"Rough assembly automation completed. assembly_generated={success}")
        print(f"Log: {LOG_PATH}")
        print(f"Conversion report: {CONVERSION_REPORT_MD}")
        return 0
    except Exception:
        ensure_dirs()
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
