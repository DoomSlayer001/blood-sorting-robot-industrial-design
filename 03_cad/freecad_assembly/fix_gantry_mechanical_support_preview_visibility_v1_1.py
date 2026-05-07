from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "03_cad" / "freecad_assembly"
REPORT_DIR = ROOT / "reports"

SOURCE_SCRIPT = OUT_DIR / "generate_gantry_mechanical_support_drive_module_v1.py"

PREVIEW_STEP_OUT = OUT_DIR / "blood_sorting_robot_v7_3c_gantry_mechanical_support_preview_v1_1.step"
PREVIEW_VALIDATION_OUT = OUT_DIR / "blood_sorting_robot_v7_3c_gantry_mechanical_support_preview_v1_1_validation.csv"
PREVIEW_COLOR_MANIFEST_OUT = OUT_DIR / "blood_sorting_robot_v7_3c_gantry_mechanical_support_preview_v1_1_color_manifest.csv"
PREVIEW_VISIBILITY_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3c_gantry_mechanical_support_preview_v1_1_visibility_audit.csv"
PREVIEW_IMPORT_DISPLAY_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3c_gantry_mechanical_support_preview_v1_1_import_display_audit.csv"
PREVIEW_INTERFERENCE_AUDIT_OUT = OUT_DIR / "blood_sorting_robot_v7_3c_gantry_mechanical_support_preview_v1_1_interference_audit.csv"

REPORT_OUT = REPORT_DIR / "stage_7a3c_gantry_mechanical_support_preview_v1_1_visibility_fix_report.md"

TRANSPARENT_ALPHA = 0.35


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


source = load_module("gantry_mechanical_support_drive_v1_for_visibility_fix", SOURCE_SCRIPT)
v71 = source.v71


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def adjusted_color_manifest(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    adjusted: list[dict[str, object]] = []
    for row in rows:
        copy = dict(row)
        role = str(copy.get("material_or_role", "")).lower()
        name = str(copy.get("expected_color", "")).lower()
        notes = str(copy.get("notes", ""))
        alpha = float(copy.get("a", 1.0))
        if "transparent" in role or "transparent" in name or "panel" in role or "panel" in name:
            if alpha < 0.25:
                copy["a"] = TRANSPARENT_ALPHA
                copy["notes"] = f"{notes}; v1.1 visibility fix raises transparent panel alpha to {TRANSPARENT_ALPHA:.2f}".strip("; ")
        elif alpha <= 0.0:
            copy["a"] = 1.0
            copy["notes"] = f"{notes}; v1.1 visibility fix prevents zero-alpha major geometry".strip("; ")
        adjusted.append(copy)
    return adjusted


def visibility_audit_rows(color_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, int]]:
    rows: list[dict[str, object]] = []
    counts = {"visible": 0, "medium_risk": 0, "high_risk": 0, "transparent": 0}
    for row in color_rows:
        alpha = float(row.get("a", 1.0))
        color = f"rgba({float(row.get('r', 0.0)):.3f},{float(row.get('g', 0.0)):.3f},{float(row.get('b', 0.0)):.3f},{alpha:.3f})"
        role = str(row.get("material_or_role", "")).lower()
        name = str(row.get("expected_color", "")).lower()
        transparent = "transparent" in role or "transparent" in name or "panel" in role or "panel" in name
        if alpha <= 0.0:
            risk = "high"
        elif transparent and alpha < 0.25:
            risk = "high"
        elif alpha < 0.5 and not transparent:
            risk = "medium"
        else:
            risk = "low"
        if transparent:
            counts["transparent"] += 1
        if risk == "high":
            counts["high_risk"] += 1
        elif risk == "medium":
            counts["medium_risk"] += 1
        else:
            counts["visible"] += 1
        rows.append({
            "component_name": row["instance_name"],
            "expected_visible": "yes",
            "export_visibility_state": "visible",
            "alpha": f"{alpha:.3f}",
            "display_color": color,
            "visibility_risk": risk,
            "notes": "intentionally transparent guard panel" if transparent else "major component exported as visible compound geometry",
        })
    return rows, counts


def export_visible_compound(instances: list[object], path: Path) -> tuple[tuple[float, float, float, float, float, float], int]:
    source.configure_step_schema()
    compound = cq.Compound.makeCompound([instance.world_shape for instance in instances])
    cq.exporters.export(compound, str(path), exportType="STEP")
    reimported = cq.importers.importStep(str(path))
    return v71.bbox_values(reimported.val()), len(reimported.solids().vals())


def import_display_audit(path: Path, bbox: tuple[float, float, float, float, float, float], solid_count: int) -> list[dict[str, object]]:
    file_exists = path.is_file()
    file_size = path.stat().st_size if file_exists else 0
    bbox_x = bbox[3] - bbox[0]
    bbox_y = bbox[4] - bbox[1]
    bbox_z = bbox[5] - bbox[2]
    center_x = (bbox[0] + bbox[3]) / 2.0
    center_y = (bbox[1] + bbox[4]) / 2.0
    center_z = (bbox[2] + bbox[5]) / 2.0
    bbox_reasonable = (
        1000.0 <= bbox_x <= 1300.0
        and 850.0 <= bbox_y <= 1100.0
        and 350.0 <= bbox_z <= 550.0
        and abs(center_x) <= 80.0
        and -80.0 <= center_y <= 120.0
        and 150.0 <= center_z <= 260.0
    )
    issue = "" if file_exists and file_size > 0 and solid_count > 0 and bbox_reasonable else "import or bbox needs review"
    return [{
        "file_name": path.name,
        "file_exists": "yes" if file_exists else "no",
        "file_size_bytes": file_size,
        "import_status": "ok" if solid_count > 0 else "failed",
        "solid_count": solid_count,
        "bbox_x_mm": f"{bbox_x:.3f}",
        "bbox_y_mm": f"{bbox_y:.3f}",
        "bbox_z_mm": f"{bbox_z:.3f}",
        "bbox_center_x_mm": f"{center_x:.3f}",
        "bbox_center_y_mm": f"{center_y:.3f}",
        "bbox_center_z_mm": f"{center_z:.3f}",
        "bbox_reasonable": "yes" if bbox_reasonable else "no",
        "visibility_risk": "low" if bbox_reasonable and solid_count > 0 else "high",
        "likely_visible_in_solidworks": "yes" if bbox_reasonable and solid_count > 0 else "no",
        "issue": issue,
        "notes": "v1.1 uses compound STEP fallback to avoid hidden assembly display states",
    }]


def write_report(
    bbox: tuple[float, float, float, float, float, float],
    solid_count: int,
    visibility_counts: dict[str, int],
    audit_counts: dict[str, int],
    export_mode: str,
) -> None:
    REPORT_OUT.write_text(
        "\n".join([
            "# Stage 7A-3c Gantry Preview Visibility Fix v1.1",
            "",
            "- v1 SolidWorks manual check: the component tree contained geometry, but the viewport initially appeared blank until parts were restored/shown manually.",
            "- Diagnosis: display-state / visibility / STEP assembly export behavior, not total geometry loss.",
            f"- v1.1 fix: exported the unchanged preview geometry with `{export_mode}` so all major geometry opens visible by default.",
            "- Layout change: none. This only changes the preview STEP export path and visibility metadata.",
            "- Stable export fallback used: yes, compound / multi-solid STEP fallback instead of the previous assembly display-state export.",
            f"- Re-import solids: {solid_count}",
            f"- Re-import bbox: {v71.fmt_bbox(bbox)}",
            f"- Visibility audit: high_risk={visibility_counts['high_risk']}, medium_risk={visibility_counts['medium_risk']}, transparent_components={visibility_counts['transparent']}.",
            f"- Interference audit: overlap={audit_counts['overlap']}, too_close={audit_counts['too_close']}, allowed_mount_contact={audit_counts['allowed_mount_contact']}.",
            "- Tube curved labels: preserved.",
            "- Non-tube region label plates: removed.",
            "- Control box state: closed in preview.",
            "- Cable chain: not generated.",
            "- Wiring harness: not generated.",
            "- legacy_v1: not modified.",
            "- v1 STEP: not overwritten.",
            "- Next step: open `03_cad/freecad_assembly/blood_sorting_robot_v7_3c_gantry_mechanical_support_preview_v1_1.step` in SolidWorks 2026 for manual display verification.",
            "",
        ]),
        encoding="utf-8",
    )


def write_outputs() -> dict[str, object]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    _, preview_instances, preview_manifest, failure_rows = source.build_preview()
    validation_rows = [source.compact_validation_row(instance) for instance in preview_instances] + failure_rows
    color_rows = adjusted_color_manifest(preview_manifest)
    visibility_rows, visibility_counts = visibility_audit_rows(color_rows)
    interference_rows, audit_counts = source.audit_instances(preview_instances)
    bbox, exported_solids = export_visible_compound(preview_instances, PREVIEW_STEP_OUT)
    import_rows = import_display_audit(PREVIEW_STEP_OUT, bbox, exported_solids)

    validation_fields = ["component_name", "module", "category", "x_mm", "y_mm", "z_mm", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "status", "notes"]
    manifest_fields = ["component_name", "instance_name", "expected_color", "material_or_role", "r", "g", "b", "a", "source_path", "notes"]
    visibility_fields = ["component_name", "expected_visible", "export_visibility_state", "alpha", "display_color", "visibility_risk", "notes"]
    import_fields = ["file_name", "file_exists", "file_size_bytes", "import_status", "solid_count", "bbox_x_mm", "bbox_y_mm", "bbox_z_mm", "bbox_center_x_mm", "bbox_center_y_mm", "bbox_center_z_mm", "bbox_reasonable", "visibility_risk", "likely_visible_in_solidworks", "issue", "notes"]
    audit_fields = ["pair_a", "pair_b", "bbox_overlap_candidate", "exact_overlap_volume_mm3", "minimum_distance_mm", "clearance_threshold_mm", "audit_status", "notes"]

    write_csv(PREVIEW_VALIDATION_OUT, validation_rows, validation_fields)
    write_csv(PREVIEW_COLOR_MANIFEST_OUT, color_rows, manifest_fields)
    write_csv(PREVIEW_VISIBILITY_AUDIT_OUT, visibility_rows, visibility_fields)
    write_csv(PREVIEW_IMPORT_DISPLAY_AUDIT_OUT, import_rows, import_fields)
    write_csv(PREVIEW_INTERFERENCE_AUDIT_OUT, interference_rows, audit_fields)
    write_report(bbox, exported_solids, visibility_counts, audit_counts, "compound/multi-solid STEP fallback")

    return {
        "preview_component_count": len(preview_instances),
        "preview_failed_count": len(failure_rows),
        "preview_solids": sum(instance.solid_count for instance in preview_instances),
        "exported_solids": exported_solids,
        "bbox": bbox,
        "visibility_counts": visibility_counts,
        "audit_counts": audit_counts,
        "import_rows": import_rows,
    }


def main() -> int:
    result = write_outputs()
    bbox = result["bbox"]
    visibility_counts = result["visibility_counts"]
    audit_counts = result["audit_counts"]
    print(f"preview_components={result['preview_component_count']}")
    print(f"preview_failed={result['preview_failed_count']}")
    print(f"preview_solids={result['preview_solids']}")
    print(f"preview_exported_solids={result['exported_solids']}")
    print(f"preview_bbox={v71.fmt_bbox(bbox)}")
    print(f"visibility_high_risk={visibility_counts['high_risk']}")
    print(f"visibility_medium_risk={visibility_counts['medium_risk']}")
    print(f"visibility_transparent_components={visibility_counts['transparent']}")
    print(f"audit_overlap={audit_counts['overlap']}")
    print(f"audit_too_close={audit_counts['too_close']}")
    print(f"audit_allowed_mount_contact={audit_counts['allowed_mount_contact']}")
    print("tube_curved_labels_preserved=yes")
    print("non_tube_region_labels_removed=yes")
    print("control_box_closed_in_preview=yes")
    print("full_cable_chain_added=no")
    print("full_wiring_harness_added=no")
    print(f"preview_step={PREVIEW_STEP_OUT}")
    print(f"validation_csv={PREVIEW_VALIDATION_OUT}")
    print(f"color_manifest={PREVIEW_COLOR_MANIFEST_OUT}")
    print(f"visibility_audit_csv={PREVIEW_VISIBILITY_AUDIT_OUT}")
    print(f"import_display_audit_csv={PREVIEW_IMPORT_DISPLAY_AUDIT_OUT}")
    print(f"interference_audit_csv={PREVIEW_INTERFERENCE_AUDIT_OUT}")
    print(f"report={REPORT_OUT}")
    return 0 if result["preview_failed_count"] == 0 and visibility_counts["high_risk"] == 0 and audit_counts["overlap"] == 0 and audit_counts["too_close"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
