"""
Build a verified SolidWorks 2026 rough assembly from original STEP/STP CAD.

This script intentionally avoids the converted_native cache. It uses the
original CAD paths from component_placement_table_v1.csv, inserts components
one at a time, and only counts an insertion as successful when the SolidWorks
assembly component count actually increases. It also audits older rough
assembly files that were later found to open as empty assemblies.
"""

from __future__ import annotations

import csv
import json
import math
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PLACEMENT_CSV = ROOT / "03_cad" / "solidworks" / "component_placement_table_v1.csv"
ASSEMBLY_DIR = ROOT / "03_cad" / "solidworks" / "assembly"
ASSEMBLY_TEMPLATE_2026 = Path(r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_assembly.asmdot")

SMOKE_ASM = ASSEMBLY_DIR / "step_import_smoke_test_2026.SLDASM"
SMOKE_LOG = ASSEMBLY_DIR / "step_import_smoke_test_2026_log.md"
OUTPUT_ASM = ASSEMBLY_DIR / "blood_sorting_robot_verified_step_rough_layout_2026_v1.SLDASM"
OUTPUT_PNG = ASSEMBLY_DIR / "blood_sorting_robot_verified_step_rough_layout_2026_v1_isometric.png"
OUTPUT_LOG = ASSEMBLY_DIR / "verified_step_rough_assembly_2026_v1_log.md"

AUDIT_REPORT = ROOT / "reports" / "stage_4c_existing_assembly_audit_report.md"
REDO_REPORT = ROOT / "reports" / "stage_4c_redo_verified_step_rough_assembly_report.md"

OLD_ASSEMBLIES = [
    ASSEMBLY_DIR / "blood_sorting_robot_rough_layout_v1.SLDASM",
    ASSEMBLY_DIR / "blood_sorting_robot_rough_layout_2026_v1.SLDASM",
    ASSEMBLY_DIR / "solidworks_2026_native_smoke_test.SLDASM",
]

SUPPORTED_INSERT_EXTENSIONS = {".step", ".stp", ".sldprt", ".sldasm"}
CRITICAL_COMPONENTS = {
    "base_plate",
    "left_y_axis_module",
    "right_y_axis_module",
    "x_axis_module_on_gantry",
    "z_axis_module",
    "electric_parallel_gripper",
    "input_mixed_tube_rack_4x6",
    "category_A_output_bin_2x3",
    "category_B_output_bin_2x3",
    "category_C_output_bin_2x3",
    "category_D_output_bin_2x3",
    "manual_review_bin_2x3",
    "barcode_scanner",
    "photoelectric_sensor",
}

SMOKE_COMPONENTS = {
    "base_plate",
    "input_mixed_tube_rack_4x6",
    "electric_parallel_gripper",
}


def rel(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def resolve_path(raw: str | None) -> Path | None:
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


def transform_array(row: dict[str, str]) -> list[float]:
    x_m = parse_float(row.get("approx_x_mm")) / 1000.0
    y_m = parse_float(row.get("approx_y_mm")) / 1000.0
    z_m = parse_float(row.get("approx_z_mm")) / 1000.0
    rx = parse_float(row.get("rotation_x_deg"))
    ry = parse_float(row.get("rotation_y_deg"))
    rz = parse_float(row.get("rotation_z_deg"))
    return rotation_matrix_xyz(rx, ry, rz) + [x_m, y_m, z_m, 1.0, 0.0, 0.0, 0.0]


def cast_assembly(doc: Any) -> Any:
    import win32com.client

    try:
        return win32com.client.CastTo(doc, "AssemblyDoc")
    except Exception:
        return doc


def component_objects(doc: Any) -> list[Any]:
    asm = cast_assembly(doc)
    try:
        comps = asm.GetComponents(False)
        if comps is None:
            return []
        if isinstance(comps, tuple):
            return list(comps)
        if isinstance(comps, list):
            return comps
        return [comps]
    except Exception:
        return []


def component_count(doc: Any) -> int:
    asm = cast_assembly(doc)
    try:
        return int(asm.GetComponentCount(False))
    except Exception:
        return len(component_objects(doc))


def component_names(doc: Any) -> list[str]:
    names: list[str] = []
    for comp in component_objects(doc):
        try:
            names.append(str(comp.GetName2()))
        except Exception:
            names.append("<unnamed_component>")
    return names


def referenced_documents(doc: Any) -> list[str]:
    for method_name, args in [
        ("GetDependencies2", (True, True, False)),
        ("GetDependencies", (True, True, False)),
    ]:
        try:
            deps = getattr(doc, method_name)(*args)
            if deps is None:
                continue
            values = [str(item) for item in (deps if isinstance(deps, (tuple, list)) else [deps]) if str(item)]
            paths = [
                item
                for item in values
                if any(item.lower().endswith(ext) for ext in [".sldprt", ".sldasm", ".step", ".stp"])
            ]
            return sorted(set(paths or values))
        except Exception:
            continue
    return []


def start_solidworks() -> tuple[Any | None, dict[str, str]]:
    info = {"started": "false", "revision": "", "executable_path": "", "exception": ""}
    try:
        import win32com.client

        sw = win32com.client.DispatchEx("SldWorks.Application")
        sw.Visible = True
        info["started"] = "true"
        try:
            rev = getattr(sw, "RevisionNumber")
            info["revision"] = str(rev() if callable(rev) else rev)
        except Exception as exc:
            info["revision"] = f"lookup_failed: {type(exc).__name__}: {exc}"
        try:
            exe = getattr(sw, "GetExecutablePath")
            info["executable_path"] = str(exe() if callable(exe) else exe)
        except Exception as exc:
            info["executable_path"] = f"lookup_failed: {type(exc).__name__}: {exc}"
        return sw, info
    except Exception as exc:
        info["exception"] = f"{type(exc).__name__}: {exc}"
        return None, info


def open_doc(sw: Any, path: Path, doc_type: int) -> tuple[Any | None, dict[str, Any]]:
    import pythoncom
    from win32com.client import VARIANT

    info: dict[str, Any] = {
        "path": rel(path),
        "exists": path.exists(),
        "opened": False,
        "errors": None,
        "warnings": None,
        "exception": "",
        "title": "",
    }
    if not path.exists():
        return None, info
    try:
        errors = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        warnings = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        doc = sw.OpenDoc6(str(path), doc_type, 3, "", errors, warnings)
        info["errors"] = int(errors.value)
        info["warnings"] = int(warnings.value)
        info["opened"] = doc is not None
        if doc is not None:
            try:
                info["title"] = str(doc.GetTitle())
            except Exception:
                pass
        return doc, info
    except Exception as exc:
        info["exception"] = f"{type(exc).__name__}: {exc}"
        return None, info


def close_doc(sw: Any, doc: Any | None, title: str = "") -> None:
    if doc is None:
        return
    try:
        title = title or str(doc.GetTitle())
        if title:
            sw.CloseDoc(title)
    except Exception:
        pass


def audit_assembly(sw: Any, path: Path) -> dict[str, Any]:
    doc, first = open_doc(sw, path, 2)
    result = {
        "path": rel(path),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "opened_first": first,
        "component_count_first": 0,
        "component_names_first": [],
        "references_first": [],
        "opened_second": {},
        "component_count_second": 0,
        "component_names_second": [],
        "references_second": [],
        "status": "not_opened",
        "can_continue_using": False,
    }
    if doc is not None:
        result["component_count_first"] = component_count(doc)
        result["component_names_first"] = component_names(doc)
        result["references_first"] = referenced_documents(doc)
        close_doc(sw, doc, str(first.get("title", "")))
    doc2, second = open_doc(sw, path, 2)
    result["opened_second"] = second
    if doc2 is not None:
        result["component_count_second"] = component_count(doc2)
        result["component_names_second"] = component_names(doc2)
        result["references_second"] = referenced_documents(doc2)
        close_doc(sw, doc2, str(second.get("title", "")))
    ref_count = len(result["references_second"] or result["references_first"])
    comp_count = int(result["component_count_second"] or result["component_count_first"])
    if not first.get("opened"):
        result["status"] = "open_failed"
    elif comp_count <= 0 or ref_count <= 0:
        result["status"] = "invalid_empty_assembly"
    else:
        result["status"] = "valid_nonempty_assembly"
        result["can_continue_using"] = True
    return result


def new_component_by_names(doc: Any, before: set[str]) -> Any | None:
    for comp in component_objects(doc):
        try:
            name = str(comp.GetName2())
        except Exception:
            continue
        if name not in before:
            return comp
    return None


def apply_transform_and_fix(model: Any, comp: Any | None, row: dict[str, str], math_util: Any, log: list[str]) -> None:
    if comp is None:
        return
    name = row.get("instance_name") or row.get("component_name") or "component"
    try:
        comp.Name2 = name
    except Exception:
        pass
    if math_util is not None:
        try:
            comp.Transform2 = math_util.CreateTransform(transform_array(row))
        except Exception as exc:
            log.append(f"- WARN `{name}`: transform failed: {type(exc).__name__}: {exc}")
    try:
        model.ClearSelection2(True)
        comp.Select4(False, None, False)
        cast_assembly(model).FixComponent()
    except Exception as exc:
        log.append(f"- WARN `{name}`: fix failed: {type(exc).__name__}: {exc}")


def activate_doc(sw: Any, title: str) -> None:
    import pythoncom
    from win32com.client import VARIANT

    errors = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    try:
        sw.ActivateDoc3(title, False, 0, errors)
    except Exception:
        pass


def insert_component(sw: Any, model: Any, row: dict[str, str], path: Path, math_util: Any, log: list[str]) -> dict[str, Any]:
    name = row.get("component_name", "")
    asm = cast_assembly(model)
    before_names = set(component_names(model))
    before_count = component_count(model)
    result = {
        "component_name": name,
        "path": rel(path),
        "before_count": before_count,
        "after_count": before_count,
        "returned_object": False,
        "success": False,
        "method": "",
        "reason": "",
    }
    x_m = parse_float(row.get("approx_x_mm")) / 1000.0
    y_m = parse_float(row.get("approx_y_mm")) / 1000.0
    z_m = parse_float(row.get("approx_z_mm")) / 1000.0
    try:
        activate_doc(sw, str(model.GetTitle()))
    except Exception:
        pass

    attempts = [
        ("AddComponent5", lambda: asm.AddComponent5(str(path), 0, "", False, "", x_m, y_m, z_m)),
        ("AddComponent4", lambda: asm.AddComponent4(str(path), "", x_m, y_m, z_m)),
        ("AddComponent", lambda: asm.AddComponent(str(path), x_m, y_m, z_m)),
    ]
    for method, call in attempts:
        try:
            comp = call()
            result["returned_object"] = comp is not None
            after = component_count(model)
            candidate = comp if comp is not None and hasattr(comp, "GetName2") else new_component_by_names(model, before_names)
            if after > before_count:
                result.update({"success": True, "method": method, "after_count": after, "reason": ""})
                apply_transform_and_fix(model, candidate, row, math_util, log)
                log.append(f"- INSERTED `{name}` with {method}; count {before_count} -> {after}.")
                return result
            result["reason"] = f"{method} did not increase component count"
            result["after_count"] = after
            log.append(f"- WARN `{name}`: {method} returned_object={comp is not None}; count {before_count} -> {after}.")
        except Exception as exc:
            result["reason"] = f"{method} failed: {type(exc).__name__}: {exc}"
            log.append(f"- WARN `{name}`: {result['reason']}")
    log.append(f"- FAIL `{name}` from `{rel(path)}`: {result['reason']}")
    return result


def usable_row(row: dict[str, str]) -> tuple[Path | None, str]:
    path = resolve_path(row.get("cad_file_path"))
    if path is None:
        return None, "missing_or_wildcard_path"
    if not path.exists():
        return path, "file_not_found"
    if path.suffix.lower() not in SUPPORTED_INSERT_EXTENSIONS:
        return path, f"unsupported_extension_{path.suffix}"
    return path, "ok"


def save_and_reopen(sw: Any, model: Any, target: Path, screenshot: Path | None = None) -> dict[str, Any]:
    result = {
        "saved": False,
        "save_return": "",
        "size_bytes": None,
        "pre_save_count": component_count(model),
        "post_reopen_count": 0,
        "reference_count": 0,
        "component_names": [],
        "references": [],
        "screenshot_exported": False,
        "screenshot_exception": "",
    }
    try:
        model.ForceRebuild3(False)
    except Exception:
        pass
    try:
        save_return = model.SaveAs3(str(target), 0, 1)
        result["save_return"] = str(save_return)
        result["saved"] = target.exists() and target.stat().st_size > 0
        result["size_bytes"] = target.stat().st_size if target.exists() else None
    except Exception as exc:
        result["save_return"] = f"{type(exc).__name__}: {exc}"
    try:
        close_doc(sw, model, str(model.GetTitle()))
    except Exception:
        pass
    if not result["saved"]:
        return result
    reopened, open_info = open_doc(sw, target, 2)
    result["reopen_info"] = open_info
    if reopened is not None:
        result["post_reopen_count"] = component_count(reopened)
        result["component_names"] = component_names(reopened)
        result["references"] = referenced_documents(reopened)
        result["reference_count"] = len(result["references"])
        if screenshot is not None:
            try:
                reopened.ShowNamedView2("*Isometric", 7)
                reopened.ViewZoomtofit2()
                reopened.SaveAs3(str(screenshot), 0, 1)
                result["screenshot_exported"] = screenshot.exists() and screenshot.stat().st_size > 0
            except Exception as exc:
                result["screenshot_exception"] = f"{type(exc).__name__}: {exc}"
        close_doc(sw, reopened, str(open_info.get("title", "")))
    return result


def build_assembly(sw: Any, rows: list[dict[str, str]], target: Path, log_path: Path, screenshot: Path | None = None) -> dict[str, Any]:
    log = [
        f"# {target.name} Build Log",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"- Assembly template: `{ASSEMBLY_TEMPLATE_2026}`",
        "- Source CAD: original STEP/STP/native paths from `component_placement_table_v1.csv`",
        "",
    ]
    model = sw.NewDocument(str(ASSEMBLY_TEMPLATE_2026), 0, 0, 0)
    result = {
        "created": model is not None,
        "attempted_count": 0,
        "insert_success_count": 0,
        "insert_failed_count": 0,
        "skipped_count": 0,
        "success_components": [],
        "failed_components": [],
        "skipped_components": [],
        "critical_missing": [],
        "save_verification": {},
        "verified_success": False,
    }
    if model is None:
        log.append("- NewDocument returned None.")
        log_path.write_text("\n".join(log) + "\n", encoding="utf-8")
        return result
    try:
        math_util = sw.GetMathUtility()
    except Exception:
        math_util = None
    for row in rows:
        name = row.get("component_name", "")
        path, status = usable_row(row)
        if status != "ok" or path is None:
            result["skipped_count"] += 1
            result["skipped_components"].append({"component_name": name, "reason": status})
            log.append(f"- SKIPPED `{name}`: {status}.")
            continue
        result["attempted_count"] += 1
        insertion = insert_component(sw, model, row, path, math_util, log)
        if insertion["success"]:
            result["insert_success_count"] += 1
            result["success_components"].append(name)
        else:
            result["insert_failed_count"] += 1
            result["failed_components"].append({"component_name": name, "reason": insertion["reason"]})
    result["critical_missing"] = sorted(CRITICAL_COMPONENTS - set(result["success_components"]))
    log.extend(
        [
            "",
            "## Insert Summary",
            "",
            f"- Attempted components: {result['attempted_count']}",
            f"- Inserted components: {result['insert_success_count']}",
            f"- Failed components: {result['insert_failed_count']}",
            f"- Skipped components: {result['skipped_count']}",
            f"- Critical components all satisfied: {not result['critical_missing']}",
        ]
    )
    if result["critical_missing"]:
        log.append("- Critical components missing:")
        for item in result["critical_missing"]:
            log.append(f"  - {item}")
    if not result["critical_missing"] and result["insert_success_count"] > 0:
        result["save_verification"] = save_and_reopen(sw, model, target, screenshot)
        verify = result["save_verification"]
        result["verified_success"] = bool(
            verify.get("saved")
            and verify.get("post_reopen_count", 0) >= len(CRITICAL_COMPONENTS)
            and verify.get("reference_count", 0) > 0
        )
    else:
        try:
            close_doc(sw, model, str(model.GetTitle()))
        except Exception:
            pass
    verify = result.get("save_verification", {})
    log.extend(
        [
            "",
            "## Reopen Verification",
            "",
            f"- Saved: {verify.get('saved', False)}",
            f"- File size bytes: {verify.get('size_bytes')}",
            f"- Component count before save: {verify.get('pre_save_count', component_count(model) if model else 0)}",
            f"- Component count after reopen: {verify.get('post_reopen_count', 0)}",
            f"- Referenced document count: {verify.get('reference_count', 0)}",
            f"- Screenshot exported: {verify.get('screenshot_exported', False)}",
            f"- Verified success: {result['verified_success']}",
            "",
            "## Component Names After Reopen",
            "",
        ]
    )
    log.extend([f"- {item}" for item in verify.get("component_names", [])] or ["- None"])
    log.extend(["", "## Failed Components", ""])
    if result["failed_components"]:
        for item in result["failed_components"]:
            log.append(f"- {item['component_name']}: {item['reason']}")
    else:
        log.append("- None")
    log_path.write_text("\n".join(log) + "\n", encoding="utf-8")
    return result


def smoke_rows(all_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in all_rows if row.get("component_name") in SMOKE_COMPONENTS]


def write_audit_report(audits: list[dict[str, Any]]) -> None:
    lines = [
        "# Stage 4C Existing Assembly Audit Report",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "| File | Size bytes | Opened | Component count | Referenced document count | Status | Can continue using |",
        "|---|---:|---:|---:|---:|---|---:|",
    ]
    for audit in audits:
        opened = audit.get("opened_second", {}).get("opened") or audit.get("opened_first", {}).get("opened")
        comp_count = audit.get("component_count_second") or audit.get("component_count_first") or 0
        ref_count = len(audit.get("references_second") or audit.get("references_first") or [])
        lines.append(
            f"| `{audit['path']}` | {audit['size_bytes']} | {opened} | {comp_count} | {ref_count} | {audit['status']} | {audit['can_continue_using']} |"
        )
    lines.extend(["", "## Component Names", ""])
    for audit in audits:
        lines.append(f"### `{audit['path']}`")
        names = audit.get("component_names_second") or audit.get("component_names_first") or []
        lines.extend([f"- {name}" for name in names] or ["- None"])
        lines.append("")
    AUDIT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_redo_report(audits: list[dict[str, Any]], smoke: dict[str, Any], full: dict[str, Any], sw_info: dict[str, str]) -> None:
    verify = full.get("save_verification", {})
    lines = [
        "# Stage 4C-Redo Verified STEP Rough Assembly Report",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Why The Rough Assembly Was Rebuilt",
        "",
        "Earlier rough assemblies existed on disk but opened with zero components and no referenced documents. This report therefore treats those files as invalid and rebuilds from original STEP/STP CAD using SolidWorks 2026.",
        "",
        "## Existing Assembly Audit",
        "",
    ]
    for audit in audits:
        comp_count = audit.get("component_count_second") or audit.get("component_count_first") or 0
        ref_count = len(audit.get("references_second") or audit.get("references_first") or [])
        lines.append(f"- `{audit['path']}`: {audit['status']}; component_count={comp_count}; referenced_documents={ref_count}")
    lines.extend(
        [
            "",
            "## STEP/STP Workflow",
            "",
            "- Main flow: original STEP/STP CAD -> SolidWorks 2026 insert -> coordinate rough placement -> component/references/reopen verification.",
            "- The manual `converted_native` cache is not used as the source for this rebuild.",
            "- No complex mates, hole selection, or installation-face inference are performed.",
            "",
            "## Smoke Test Result",
            "",
            f"- Smoke test verified success: {smoke.get('verified_success')}",
            f"- Smoke inserted components: {smoke.get('insert_success_count')}",
            f"- Smoke failed components: {smoke.get('insert_failed_count')}",
            f"- Smoke skipped components: {smoke.get('skipped_count')}",
            "",
            "## Full Verified Rough Assembly Result",
            "",
            f"- SolidWorks revision: `{sw_info.get('revision', '')}`",
            f"- Assembly template: `{ASSEMBLY_TEMPLATE_2026}`",
            f"- Output assembly: `{rel(OUTPUT_ASM)}`",
            f"- Output size bytes: {verify.get('size_bytes')}",
            f"- Component count before save: {verify.get('pre_save_count')}",
            f"- Component count after reopen: {verify.get('post_reopen_count')}",
            f"- Referenced document count: {verify.get('reference_count')}",
            f"- Inserted components: {full.get('insert_success_count')}",
            f"- Failed insertions: {full.get('insert_failed_count')}",
            f"- Skipped components: {full.get('skipped_count')}",
            f"- Critical components all satisfied: {not full.get('critical_missing')}",
            f"- Screenshot exported: {verify.get('screenshot_exported', False)}",
            f"- Verified success: {full.get('verified_success')}",
            "",
            "## Inserted Components",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in full.get("success_components", [])] or ["- None"])
    lines.extend(["", "## Failed Or Skipped Components", ""])
    for item in full.get("failed_components", []):
        lines.append(f"- Failed `{item['component_name']}`: {item['reason']}")
    for item in full.get("skipped_components", []):
        lines.append(f"- Skipped `{item['component_name']}`: {item['reason']}")
    if not full.get("failed_components") and not full.get("skipped_components"):
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Next Manual Checks",
            "",
            "- Open the verified STEP rough assembly in SolidWorks 2026.",
            "- Check overall isometric, top, front, side, gripper/tube, scan-station, and output-bin views.",
            "- Correct coordinate or rotation rows in `component_placement_table_v1.csv` based on screenshots.",
        ]
    )
    REDO_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ASSEMBLY_DIR.mkdir(parents=True, exist_ok=True)
    sw, sw_info = start_solidworks()
    if sw is None:
        message = f"SolidWorks COM unavailable: {sw_info.get('exception', '')}"
        SMOKE_LOG.write_text(message + "\n", encoding="utf-8")
        OUTPUT_LOG.write_text(message + "\n", encoding="utf-8")
        write_audit_report([])
        write_redo_report([], {"verified_success": False}, {"verified_success": False}, sw_info)
        print(message)
        return 0
    try:
        audits = [audit_assembly(sw, path) for path in OLD_ASSEMBLIES]
        write_audit_report(audits)
        rows = read_csv(PLACEMENT_CSV)
        smoke = build_assembly(sw, smoke_rows(rows), SMOKE_ASM, SMOKE_LOG, None)
        if smoke.get("verified_success"):
            full = build_assembly(sw, rows, OUTPUT_ASM, OUTPUT_LOG, OUTPUT_PNG)
        else:
            full = {
                "verified_success": False,
                "attempted_count": 0,
                "insert_success_count": 0,
                "insert_failed_count": 0,
                "skipped_count": 0,
                "success_components": [],
                "failed_components": [{"component_name": "full_assembly", "reason": "smoke_test_failed"}],
                "skipped_components": [],
                "critical_missing": sorted(CRITICAL_COMPONENTS),
                "save_verification": {},
            }
            OUTPUT_LOG.write_text(
                "# Verified STEP Rough Assembly 2026 v1 Log\n\n- Full assembly skipped because STEP import smoke test failed.\n",
                encoding="utf-8",
            )
        write_redo_report(audits, smoke, full, sw_info)
        print(json.dumps({"audits": audits, "smoke": smoke, "full": full, "solidworks": sw_info}, ensure_ascii=False, indent=2))
    except Exception:
        trace = traceback.format_exc()
        OUTPUT_LOG.write_text(trace, encoding="utf-8")
        print(trace)
    finally:
        try:
            sw.ExitApp()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
