"""
Stage 4B-4 SolidWorks automation retry after default template repair.

This script tries the automatic STEP -> native SolidWorks -> rough assembly flow
again, but keeps the manual native cache as the fallback source of truth.

Safety rules:
- never delete original STEP/STP/SLDPRT/SLDASM files.
- never overwrite existing native cache files.
- run base plate + gripper smoke test first.
- do not save a misleading rough assembly if critical native files are missing.
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
TEMPLATE_CONFIG = ROOT / "03_cad" / "solidworks" / "macros" / "solidworks_template_config.json"
ASSEMBLY_DIR = ROOT / "03_cad" / "solidworks" / "assembly"
AUTO_LOG = ASSEMBLY_DIR / "auto_retry_smoke_test_log.md"
ROUGH_LOG = ASSEMBLY_DIR / "rough_assembly_v1_log.md"
SMOKE_ASM = ASSEMBLY_DIR / "auto_retry_smoke_test.SLDASM"
ROUGH_ASM = ASSEMBLY_DIR / "blood_sorting_robot_rough_layout_v1.SLDASM"
NATIVE_DIR = ROOT / "03_cad" / "solidworks" / "converted_native"
NATIVE_PARTS = NATIVE_DIR / "parts"
NATIVE_ASSEMBLIES = NATIVE_DIR / "assemblies"
NATIVE_MAPPING = NATIVE_DIR / "native_file_mapping.csv"
NATIVE_TODO = NATIVE_DIR / "manual_native_conversion_todo.csv"
NATIVE_TODO_FALLBACK = NATIVE_DIR / "manual_native_conversion_todo_autoretry.csv"
REPORT_PATH = ROOT / "reports" / "stage_4b4_auto_retry_after_template_fix_report.md"
WRITE_WARNINGS: list[str] = []

BASE_PLATE_STEP = ROOT / "03_cad" / "custom_parts" / "base_plate" / "base_plate_1100x900x15.step"
GRIPPER_STEP = ROOT / "03_cad" / "standard_parts" / "downloaded" / "gripper" / "SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.step"

SW_DOC_PART = 1
SW_DOC_ASSEMBLY = 2
SW_OPEN_SILENT = 1
SW_SAVE_SILENT = 1
NATIVE_EXTENSIONS = {".sldprt", ".sldasm"}
STEP_EXTENSIONS = {".step", ".stp"}

CRITICAL = {
    "base_plate",
    "left_y_axis_module",
    "right_y_axis_module",
    "x_axis_module_on_gantry",
    "z_axis_module",
    "electric_parallel_gripper",
    "input_mixed_tube_rack_4x6",
    "manual_review_bin_2x3",
    "barcode_scanner",
    "photoelectric_sensor",
}
OUTPUT_BINS = {
    "category_A_output_bin_2x3",
    "category_B_output_bin_2x3",
    "category_C_output_bin_2x3",
    "category_D_output_bin_2x3",
}


def ensure_dirs() -> None:
    for folder in [ASSEMBLY_DIR, NATIVE_PARTS, NATIVE_ASSEMBLIES, REPORT_PATH.parent]:
        folder.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def rel(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def safe_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", value)
    name = re.sub(r"_+", "_", name).strip("._")
    return name or "component"


def load_template_config() -> dict[str, Any]:
    if not TEMPLATE_CONFIG.exists():
        return {}
    try:
        return json.loads(TEMPLATE_CONFIG.read_text(encoding="utf-8"))
    except Exception:
        return {}


def template_status() -> dict[str, tuple[str, bool, bool]]:
    cfg = load_template_config()
    out = {}
    for key in ["part_template_path", "assembly_template_path", "drawing_template_path"]:
        raw = str(cfg.get(key, ""))
        path = Path(raw) if raw else None
        out[key] = (raw, bool(path and path.exists()), bool(path and path.is_file()))
    return out


def resolve_path(raw: str) -> Path | None:
    raw = (raw or "").strip()
    if not raw or raw.upper() == "TBD" or "*" in raw or "?" in raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / raw
    return path.resolve()


def parse_float(value: str | None) -> float:
    try:
        return float(str(value).strip()) if value not in (None, "") else 0.0
    except ValueError:
        return 0.0


def rotation_matrix_xyz(rx_deg: float, ry_deg: float, rz_deg: float) -> list[float]:
    rx, ry, rz = math.radians(rx_deg), math.radians(ry_deg), math.radians(rz_deg)
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


def create_sw_app(lines: list[str]) -> Any | None:
    lines.append(f"- Platform: {platform.platform()}")
    try:
        import win32com.client
        lines.append("- win32com.client: available")
        sw = win32com.client.Dispatch("SldWorks.Application")
        sw.Visible = True
        lines.append("- SldWorks.Application: dispatch_ok")
        return sw
    except Exception as exc:
        lines.append(f"- SolidWorks COM failed: {type(exc).__name__}: {exc}")
        return None


def get_template(kind: str) -> str:
    cfg = load_template_config()
    return str(cfg.get(f"{kind}_template_path", ""))


def open_step(sw: Any, path: Path) -> tuple[Any | None, str]:
    import pythoncom
    import win32com.client

    errors_seen: list[str] = []
    for doc_type in [SW_DOC_PART, SW_DOC_ASSEMBLY]:
        try:
            errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            model = sw.OpenDoc6(str(path), doc_type, SW_OPEN_SILENT, "", errors, warnings)
            if model is not None:
                return model, f"OpenDoc6_doc_type_{doc_type}; errors={errors.value}; warnings={warnings.value}"
            errors_seen.append(f"OpenDoc6_doc_type_{doc_type}_None; errors={errors.value}; warnings={warnings.value}")
        except Exception as exc:
            errors_seen.append(f"OpenDoc6_doc_type_{doc_type}_{type(exc).__name__}: {exc}")
    return None, " | ".join(errors_seen)


def doc_type(model: Any) -> int:
    try:
        return int(model.GetType())
    except Exception:
        return SW_DOC_PART


def close_model(sw: Any, model: Any) -> None:
    try:
        title = model.GetTitle()
        if title:
            sw.CloseDoc(title)
    except Exception:
        pass


def save_native(model: Any, output_path: Path) -> tuple[bool, str]:
    if output_path.exists():
        return True, "already_exists_no_overwrite"
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result = model.SaveAs3(str(output_path), 0, SW_SAVE_SILENT)
        ok = bool(result) and output_path.exists() and output_path.stat().st_size > 0
        return ok, f"SaveAs3_return={result}; exists={output_path.exists()}"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def native_output_for(component_name: str, original_path: Path, preferred_stem: str | None = None, doc_kind: int = SW_DOC_PART) -> Path:
    stem = safe_name(preferred_stem or component_name or original_path.stem)
    if doc_kind == SW_DOC_ASSEMBLY:
        return NATIVE_ASSEMBLIES / f"{stem}.SLDASM"
    return NATIVE_PARTS / f"{stem}.SLDPRT"


def convert_step(sw: Any, source: Path, output_stem: str) -> tuple[Path | None, str]:
    model, open_status = open_step(sw, source)
    if model is None:
        return None, open_status
    kind = doc_type(model)
    output = native_output_for(output_stem, source, output_stem, kind)
    ok, save_status = save_native(model, output)
    close_model(sw, model)
    if ok:
        return output, f"{open_status}; {save_status}"
    return None, f"{open_status}; {save_status}"


def add_component(model: Any, row: dict[str, str], native_path: Path, math_util: Any, lines: list[str]) -> bool:
    name = row.get("instance_name") or row.get("component_name") or native_path.stem
    x_m = parse_float(row.get("approx_x_mm")) / 1000.0
    y_m = parse_float(row.get("approx_y_mm")) / 1000.0
    z_m = parse_float(row.get("approx_z_mm")) / 1000.0
    rx, ry, rz = parse_float(row.get("rotation_x_deg")), parse_float(row.get("rotation_y_deg")), parse_float(row.get("rotation_z_deg"))
    try:
        comp = model.AddComponent5(str(native_path), 0, "", "", False, x_m, y_m, z_m)
        if comp is None:
            lines.append(f"- FAIL `{name}`: AddComponent5 returned None.")
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
                lines.append(f"- WARN `{name}` transform failed: {type(exc).__name__}: {exc}")
        try:
            model.ClearSelection2(True)
            comp.Select4(False, None, False)
            model.FixComponent()
        except Exception as exc:
            lines.append(f"- WARN `{name}` fix failed: {type(exc).__name__}: {exc}")
        lines.append(f"- INSERTED `{name}` from `{rel(native_path)}`")
        return True
    except Exception as exc:
        lines.append(f"- FAIL `{name}`: {type(exc).__name__}: {exc}")
        return False


def build_mapping_from_cache(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    existing = {
        "base_plate": "03_cad/solidworks/converted_native/parts/base_plate_1100x900x15.SLDPRT",
        "electric_parallel_gripper": "03_cad/solidworks/converted_native/assemblies/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.SLDASM",
        "emergency_stop_placeholder": "03_cad/standard_parts/placeholders/safety/emergency_stop_visual_placeholder_v1.sldprt",
        "left_y_axis_module": "03_cad/solidworks/converted_native/parts/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM",
        "right_y_axis_module": "03_cad/solidworks/converted_native/parts/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.SLDASM",
        "input_mixed_tube_rack_4x6": "03_cad/solidworks/converted_native/parts/input_mixed_tube_rack_4x6.SLDASM",
    }
    output = []
    for row in rows:
        comp = row["component_name"]
        native = existing.get(comp, "")
        path = ROOT / native if native else None
        exists = bool(path and path.exists())
        method = "manual_converted" if comp in {"base_plate", "electric_parallel_gripper", "left_y_axis_module", "right_y_axis_module", "input_mixed_tube_rack_4x6"} else "existing_native" if comp == "emergency_stop_placeholder" else "manual_required"
        status = "native_available" if exists else "manual_conversion_required"
        if comp in {"base_plate", "electric_parallel_gripper"} and exists:
            status = "manual_converted"
        output.append({
            "component_name": comp,
            "part_id": row["part_id"],
            "original_cad_path": row["cad_file_path"],
            "native_cad_path": native,
            "native_file_exists": "true" if exists else "false",
            "conversion_method": method,
            "conversion_status": status,
            "notes": "Native cache file found and registered." if exists else "Native SolidWorks file not found in cache; manual conversion required.",
        })
    return output


def todo_rows(rows: list[dict[str, str]], mapping: list[dict[str, str]]) -> list[dict[str, str]]:
    available = {row["component_name"] for row in mapping if row["native_file_exists"] == "true"}
    priority_a = [
        "base_plate", "left_y_axis_module", "right_y_axis_module", "x_axis_module_on_gantry", "z_axis_module",
        "electric_parallel_gripper", "input_mixed_tube_rack_4x6", "category_A_output_bin_2x3",
        "category_B_output_bin_2x3", "category_C_output_bin_2x3", "category_D_output_bin_2x3",
        "manual_review_bin_2x3", "barcode_scanner", "photoelectric_sensor",
    ]
    rank = {name: ("Priority A", idx) for idx, name in enumerate(priority_a)}
    result = []
    for idx, row in enumerate(rows):
        comp = row["component_name"]
        if comp in available:
            continue
        priority, order = rank.get(comp, ("Priority B", 100 + idx))
        original = row["cad_file_path"]
        recommended = f"03_cad/solidworks/converted_native/parts/{safe_name(comp)}.SLDPRT"
        if original.lower().endswith(".sldasm"):
            recommended = f"03_cad/solidworks/converted_native/assemblies/{safe_name(comp)}.SLDASM"
        result.append({
            "_order": str(order),
            "priority": priority,
            "component_name": comp,
            "part_id": row["part_id"],
            "original_cad_path": original,
            "recommended_native_output_path": recommended,
            "recommended_save_as_type": "SLDPRT_or_SLDASM_after_manual_import",
            "conversion_needed_for_rough_assembly": "yes" if priority == "Priority A" else "optional_for_first_rough_layout",
            "notes": "Open original CAD in SolidWorks, accept dialogs, repair if requested, then Save As native CAD. Do not delete original files.",
        })
    result.sort(key=lambda r: (r["priority"], int(r["_order"])))
    for row in result:
        del row["_order"]
    return result


def write_mapping_and_todo(mapping: list[dict[str, str]], todo: list[dict[str, str]]) -> None:
    mapping_fields = ["component_name", "part_id", "original_cad_path", "native_cad_path", "native_file_exists", "conversion_method", "conversion_status", "notes"]
    todo_fields = ["priority", "component_name", "part_id", "original_cad_path", "recommended_native_output_path", "recommended_save_as_type", "conversion_needed_for_rough_assembly", "notes"]
    with NATIVE_MAPPING.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=mapping_fields)
        writer.writeheader()
        writer.writerows(mapping)
    try:
        with NATIVE_TODO.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=todo_fields)
            writer.writeheader()
            writer.writerows(todo)
    except PermissionError as exc:
        with NATIVE_TODO_FALLBACK.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=todo_fields)
            writer.writeheader()
            writer.writerows(todo)
        WRITE_WARNINGS.append(
            f"`{rel(NATIVE_TODO)}` could not be overwritten ({exc}); "
            f"wrote `{rel(NATIVE_TODO_FALLBACK)}` instead."
        )


def critical_missing(mapping: list[dict[str, str]]) -> list[str]:
    by_name = {row["component_name"]: row for row in mapping}
    required = {
        "base_plate", "left_y_axis_module", "right_y_axis_module", "x_axis_module_on_gantry", "z_axis_module",
        "electric_parallel_gripper", "input_mixed_tube_rack_4x6", "manual_review_bin_2x3", "barcode_scanner", "photoelectric_sensor",
    }
    missing = [name for name in sorted(required) if by_name.get(name, {}).get("native_file_exists") != "true"]
    if not any(by_name.get(name, {}).get("native_file_exists") == "true" for name in {"category_A_output_bin_2x3", "category_B_output_bin_2x3", "category_C_output_bin_2x3", "category_D_output_bin_2x3"}):
        missing.append("at_least_one_category_output_bin")
    return missing


def smoke_test(sw: Any, lines: list[str]) -> tuple[bool, Path | None, Path | None, str]:
    lines.append("# Auto Retry Smoke Test Log")
    lines.append("")
    lines.append(f"- Generated at: {datetime.now().isoformat(timespec='seconds')}")
    bp_native, bp_status = convert_step(sw, BASE_PLATE_STEP, "auto_retry_smoke_base_plate_1100x900x15")
    gr_native, gr_status = convert_step(sw, GRIPPER_STEP, "auto_retry_smoke_SMC_LEHF20_gripper")
    lines.append(f"- Base plate conversion: {bool(bp_native)}; {bp_status}; native={rel(bp_native)}")
    lines.append(f"- Gripper conversion: {bool(gr_native)}; {gr_status}; native={rel(gr_native)}")
    if not bp_native or not gr_native:
        return False, bp_native, gr_native, "conversion_failed"
    template = get_template("assembly")
    try:
        model = sw.NewDocument(template, 0, 0, 0)
        if model is None:
            lines.append("- Smoke assembly NewDocument returned None.")
            return False, bp_native, gr_native, "new_document_failed"
        bp_row = {"instance_name": "smoke_base_plate", "component_name": "base_plate", "approx_x_mm": "0", "approx_y_mm": "0", "approx_z_mm": "-7.5", "rotation_x_deg": "0", "rotation_y_deg": "0", "rotation_z_deg": "0"}
        gr_row = {"instance_name": "smoke_gripper", "component_name": "electric_parallel_gripper", "approx_x_mm": "0", "approx_y_mm": "0", "approx_z_mm": "120", "rotation_x_deg": "0", "rotation_y_deg": "0", "rotation_z_deg": "0"}
        ok_bp = add_component(model, bp_row, bp_native, None, lines)
        ok_gr = add_component(model, gr_row, gr_native, None, lines)
        result = model.SaveAs3(str(SMOKE_ASM), 0, 1)
        ok = bool(result) and ok_bp and ok_gr and SMOKE_ASM.exists()
        lines.append(f"- Smoke SaveAs3 returned: {result}; assembly_exists={SMOKE_ASM.exists()}")
        if not ok and SMOKE_ASM.exists():
            SMOKE_ASM.unlink()
            lines.append("- Removed incomplete smoke test assembly.")
        return ok, bp_native, gr_native, "ok" if ok else "insert_or_save_failed"
    except Exception as exc:
        lines.append(f"- Smoke assembly failed: {type(exc).__name__}: {exc}")
        if SMOKE_ASM.exists():
            SMOKE_ASM.unlink()
        return False, bp_native, gr_native, f"{type(exc).__name__}: {exc}"


def run() -> tuple[bool, dict[str, Any]]:
    ensure_dirs()
    rows = read_csv(PLACEMENT_CSV)
    smoke_lines: list[str] = []
    env_lines: list[str] = []
    sw = create_sw_app(env_lines)
    smoke_ok = False
    smoke_reason = "solidworks_com_failed"
    bp_native = None
    gr_native = None
    if sw is not None:
        smoke_ok, bp_native, gr_native, smoke_reason = smoke_test(sw, smoke_lines)
    AUTO_LOG.write_text("\n".join(env_lines + [""] + smoke_lines) + "\n", encoding="utf-8")

    mapping = build_mapping_from_cache(rows)
    auto_success = 0
    auto_failed = 0
    if smoke_ok and sw is not None:
        for row in mapping:
            if row["native_file_exists"] == "true":
                continue
            original = resolve_path(row["original_cad_path"])
            if original is None or not original.exists() or original.suffix.lower() not in STEP_EXTENSIONS:
                auto_failed += 1
                continue
            native, status = convert_step(sw, original, row["component_name"])
            if native is not None:
                row["native_cad_path"] = rel(native)
                row["native_file_exists"] = "true"
                row["conversion_method"] = "auto_retry_converted"
                row["conversion_status"] = "auto_converted"
                row["notes"] = status
                auto_success += 1
            else:
                row["notes"] = status
                auto_failed += 1

    todo = todo_rows(rows, mapping)
    write_mapping_and_todo(mapping, todo)

    missing = critical_missing(mapping)
    rough_lines = [
        "# Rough Assembly v1 Log",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"- Smoke test success: {smoke_ok}",
        f"- Smoke test reason: {smoke_reason}",
        f"- Auto conversion success count: {auto_success}",
        f"- Auto conversion failed/skipped count: {auto_failed}",
        "",
    ]
    inserted = 0
    insert_failed = 0
    rough_ok = False
    if missing:
        rough_lines.append("## Critical Component Gate")
        rough_lines.append("")
        rough_lines.append("- Critical native files are still missing; rough assembly was not generated.")
        for name in missing:
            rough_lines.append(f"  - {name}")
        if ROUGH_ASM.exists():
            ROUGH_ASM.unlink()
    elif sw is None:
        rough_lines.append("- SolidWorks COM unavailable; rough assembly was not generated.")
    else:
        template = get_template("assembly")
        try:
            model = sw.NewDocument(template, 0, 0, 0)
            by_name = {row["component_name"]: row for row in mapping}
            for placement in rows:
                m = by_name.get(placement["component_name"])
                native = resolve_path(m.get("native_cad_path", "")) if m else None
                if not native or not native.exists() or native.suffix.lower() not in NATIVE_EXTENSIONS:
                    continue
                if add_component(model, placement, native, None, rough_lines):
                    inserted += 1
                else:
                    insert_failed += 1
            result = model.SaveAs3(str(ROUGH_ASM), 0, 1)
            rough_ok = bool(result) and inserted > 0 and insert_failed == 0 and ROUGH_ASM.exists()
            rough_lines.append(f"- Rough assembly SaveAs3 returned: {result}; exists={ROUGH_ASM.exists()}")
            if not rough_ok and ROUGH_ASM.exists():
                ROUGH_ASM.unlink()
                rough_lines.append("- Removed incomplete rough assembly.")
        except Exception as exc:
            rough_lines.append(f"- Rough assembly failed: {type(exc).__name__}: {exc}")
            if ROUGH_ASM.exists():
                ROUGH_ASM.unlink()
    rough_lines.extend([
        "",
        "## Summary",
        "",
        f"- Native registered count: {sum(1 for r in mapping if r['native_file_exists'] == 'true')}",
        f"- Manual conversion todo count: {len(todo)}",
        f"- Inserted component count: {inserted}",
        f"- Insertion failed count: {insert_failed}",
        f"- Rough assembly generated: {rough_ok}",
    ])
    ROUGH_LOG.write_text("\n".join(rough_lines) + "\n", encoding="utf-8")

    summary = {
        "smoke_ok": smoke_ok,
        "smoke_reason": smoke_reason,
        "base_plate_native": rel(bp_native),
        "gripper_native": rel(gr_native),
        "auto_success": auto_success,
        "auto_failed": auto_failed,
        "inserted": inserted,
        "insert_failed": insert_failed,
        "rough_ok": rough_ok,
        "native_registered": sum(1 for r in mapping if r["native_file_exists"] == "true"),
        "todo_count": len(todo),
        "priority_a_todo": sum(1 for r in todo if r["priority"] == "Priority A"),
        "write_warnings": list(WRITE_WARNINGS),
    }
    write_report(summary)
    return rough_ok, summary


def write_report(summary: dict[str, Any]) -> None:
    lines = [
        "# Stage 4B-4 Auto Retry After Template Fix Report",
        "",
        "## 1. Stage Goal",
        "",
        "Retry SolidWorks automation after the default template settings were repaired manually.",
        "",
        "## 2. Environment And Template Check",
        "",
    ]
    for key, (path, exists, is_file) in template_status().items():
        lines.append(f"- {key}: `{path}`; exists={exists}; readable_file={is_file}")
    lines.extend([
        "",
        "## 3. Smoke Test",
        "",
        f"- Smoke test success: {summary['smoke_ok']}",
        f"- Smoke test reason: {summary['smoke_reason']}",
        f"- base_plate native output: `{summary['base_plate_native']}`",
        f"- gripper native output: `{summary['gripper_native']}`",
        "",
        "## 4. Batch Conversion And Assembly",
        "",
        f"- Auto conversion success count: {summary['auto_success']}",
        f"- Auto conversion failed/skipped count: {summary['auto_failed']}",
        f"- Native registered count: {summary['native_registered']}",
        f"- Manual conversion todo count: {summary['todo_count']}",
        f"- Priority A todo count: {summary['priority_a_todo']}",
        f"- Inserted component count: {summary['inserted']}",
        f"- Insertion failed count: {summary['insert_failed']}",
        f"- Rough assembly generated: {summary['rough_ok']}",
        "",
        "## 4.1 File Write Notes",
        "",
    ])
    if summary.get("write_warnings"):
        lines.extend([f"- {warning}" for warning in summary["write_warnings"]])
    else:
        lines.append("- No write warnings.")
    lines.extend([
        "",
        "## 5. Output Assembly",
        "",
        f"- Path: `{rel(ROUGH_ASM)}`",
        f"- Exists: {ROUGH_ASM.exists()}",
        f"- Size bytes: {ROUGH_ASM.stat().st_size if ROUGH_ASM.exists() else 'N/A'}",
        "",
        "## 6. Next Step",
        "",
        "If the smoke test still fails, continue using the manual native cache workflow. If it succeeds but critical components are missing, convert the remaining Priority A files listed in `manual_native_conversion_todo.csv`, update `native_file_mapping.csv`, and rerun the macro.",
    ])
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    try:
        ok, summary = run()
        print(f"auto_retry_rough_assembly_generated={ok}")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    except Exception:
        ensure_dirs()
        message = traceback.format_exc()
        AUTO_LOG.write_text("# Auto Retry Smoke Test Log\n\n```text\n" + message + "\n```\n", encoding="utf-8")
        print("auto_retry_failed")
        print(message)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
