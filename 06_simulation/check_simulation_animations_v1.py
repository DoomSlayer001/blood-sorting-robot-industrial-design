from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = ROOT / "06_simulation"
FIG_DIR = SIM_DIR / "figures"
ANIM_DIR = SIM_DIR / "animations"
REPORT_DIR = ROOT / "reports"

MANIFEST_CSV = SIM_DIR / "animation_manifest_v1.csv"
FRAME_SUMMARY_CSV = SIM_DIR / "animation_frame_summary_v1.csv"
EVENT_OVERLAY_CSV = SIM_DIR / "animation_event_overlay_v1.csv"
VALIDATION_CSV = SIM_DIR / "animation_validation_summary_v1.csv"
REPORT_MD = REPORT_DIR / "stage_7b9_python_simulation_animation_package_report.md"

TOP_GIF = ANIM_DIR / "top_view_sorting_animation_v1.gif"
XYZ_GIF = ANIM_DIR / "xyz_motion_trajectory_animation_v1.gif"
TIMELINE_GIF = ANIM_DIR / "output_pending_timeline_animation_v1.gif"
DASHBOARD_PNG = FIG_DIR / "simulation_animation_dashboard_v1.png"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def as_int(value: str | int | float, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def is_true(value: str) -> bool:
    return str(value).strip().lower() == "true"


def add_check(rows: list[dict[str, object]], check_item: str, expected: str, observed: str, passed: bool, notes: str = "") -> None:
    rows.append(
        {
            "check_item": check_item,
            "expected": expected,
            "observed": observed,
            "status": "PASS" if passed else "FAIL",
            "notes": notes,
        }
    )


def manifest_frame_count(manifest: list[dict[str, str]], animation_id: str, fmt: str = "gif") -> int:
    for row in manifest:
        if row["animation_id"] == animation_id and row["format"] == fmt:
            return as_int(row["frame_count"])
    return 0


def main() -> int:
    rows: list[dict[str, object]] = []

    required_files = [
        MANIFEST_CSV,
        FRAME_SUMMARY_CSV,
        EVENT_OVERLAY_CSV,
        TOP_GIF,
        XYZ_GIF,
        TIMELINE_GIF,
        DASHBOARD_PNG,
        REPORT_MD,
    ]
    for path in required_files:
        add_check(
            rows,
            f"{path.relative_to(ROOT).as_posix()} exists",
            "file exists and is non-empty",
            f"exists={path.exists()}, size={path.stat().st_size if path.exists() else 0}",
            path.exists() and path.stat().st_size > 0,
        )

    manifest = read_csv(MANIFEST_CSV) if MANIFEST_CSV.exists() else []
    frame_summary = read_csv(FRAME_SUMMARY_CSV) if FRAME_SUMMARY_CSV.exists() else []
    overlays = read_csv(EVENT_OVERLAY_CSV) if EVENT_OVERLAY_CSV.exists() else []
    task_results = read_csv(SIM_DIR / "sorting_state_machine_task_result_v1.csv")
    task_manifest = read_csv(SIM_DIR / "sorting_task_manifest_v1.csv")
    input_rows = read_csv(SIM_DIR / "input_box_occupancy_map_v1.csv")
    metrics = read_csv(SIM_DIR / "simulation_chain_key_metrics_v1.csv")

    for animation_id in [
        "top_view_sorting_animation_v1",
        "xyz_motion_trajectory_animation_v1",
        "output_pending_timeline_animation_v1",
    ]:
        count = manifest_frame_count(manifest, animation_id)
        add_check(rows, f"{animation_id} frame count > 0", "> 0", str(count), count > 0)

    baseline_results = [row for row in task_results if row["scenario_id"] == "baseline"]
    manifest_task_count = len(task_manifest)
    occupied_count = sum(1 for row in input_rows if is_true(row["tube_present"]))
    metric_baseline_completed = next((as_int(row["value"]) for row in metrics if row["metric_name"] == "baseline completed count"), 0)
    task_count_ok = len(baseline_results) == manifest_task_count == occupied_count == metric_baseline_completed
    add_check(
        rows,
        "task count consistent with Stage 7B",
        "baseline_results == task_manifest == occupied_slots == baseline completed metric",
        f"{len(baseline_results)} == {manifest_task_count} == {occupied_count} == {metric_baseline_completed}",
        task_count_ok,
    )

    abnormal_results = [row for row in baseline_results if is_true(row["abnormal_flag"])]
    manual_abnormal = [row for row in abnormal_results if row["target_type"] == "manual_review" and is_true(row["went_to_manual_review"])]
    overlay_manual = any(row["overlay_type"] == "manual_review_route" for row in overlays)
    add_check(
        rows,
        "abnormal samples shown in manual review",
        "all abnormal baseline samples went_to_manual_review and overlay exists",
        f"abnormal={len(abnormal_results)}, manual_review={len(manual_abnormal)}, overlay={overlay_manual}",
        len(abnormal_results) > 0 and len(abnormal_results) == len(manual_abnormal) and overlay_manual,
    )

    hold_events = read_csv(SIM_DIR / "category_hold_resume_events_v1.csv")
    overlay_hold = any(row["overlay_type"] in {"category_hold_resume", "hold_resume_markers"} for row in overlays)
    add_check(
        rows,
        "hold/resume events shown if present",
        "hold/resume events present imply overlay exists",
        f"hold_resume_events={len(hold_events)}, overlay={overlay_hold}",
        len(hold_events) == 0 or overlay_hold,
    )

    overlay_no_camera = any(row["overlay_type"] == "no_camera_logic" and "NO_CAMERA_LOGIC_USED=True" in row["notes"] for row in overlays)
    report_text = REPORT_MD.read_text(encoding="utf-8") if REPORT_MD.exists() else ""
    input_notes = " ".join(row.get("notes", "") for row in input_rows[:8]).lower()
    no_camera_ok = overlay_no_camera and "no camera logic is used" in report_text.lower() and "no camera" in input_notes
    add_check(
        rows,
        "no camera logic used",
        "internal occupancy table source and no camera overlay/report statement",
        f"overlay={overlay_no_camera}, report_statement={'no camera logic is used' in report_text.lower()}",
        no_camera_ok,
    )

    manifest_gif_success = sum(1 for row in manifest if row["format"] == "gif" and row["generation_status"] == "success")
    add_check(
        rows,
        "required GIF generation status",
        "3 GIF rows success",
        f"gif_success={manifest_gif_success}",
        manifest_gif_success == 3,
    )

    mp4_rows = [row for row in manifest if row["format"] == "mp4"]
    mp4_ok = all(row["generation_status"] in {"success", "warning"} for row in mp4_rows) and len(mp4_rows) == 3
    add_check(
        rows,
        "MP4 optional status",
        "3 MP4 rows success or warning",
        "; ".join(f"{row['animation_name']}={row['generation_status']}" for row in mp4_rows),
        mp4_ok,
        "MP4 warning is acceptable for Stage 7B-9.",
    )

    summary_rows_ok = len(frame_summary) >= 3
    add_check(rows, "animation frame summary rows", ">= 3", str(len(frame_summary)), summary_rows_ok)

    validation_status = "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL"
    add_check(rows, "validation_status", "PASS", validation_status, validation_status == "PASS")
    write_csv(VALIDATION_CSV, ["check_item", "expected", "observed", "status", "notes"], rows)

    print(f"validation_status={validation_status}")
    print(f"checks={len(rows)}")
    print(f"failed_checks={sum(1 for row in rows if row['status'] == 'FAIL')}")
    print(f"gif_success={manifest_gif_success}")
    mp4_status_text = "; ".join(f"{row['animation_name']}={row['generation_status']}" for row in mp4_rows)
    print(f"mp4_status={mp4_status_text}")
    if validation_status != "PASS":
        for row in rows:
            if row["status"] == "FAIL":
                print(f"issue={row['check_item']}: observed={row['observed']}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
