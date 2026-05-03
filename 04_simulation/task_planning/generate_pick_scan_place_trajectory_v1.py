from __future__ import annotations

import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = ROOT / "04_simulation" / "task_planning"
REPORT_DIR = ROOT / "reports"
FIGURE_DIR = TASK_DIR / "figures"

SORTING_SEQUENCE_CSV = TASK_DIR / "sorting_sequence_v1.csv"
RACK_SLOT_CSV = TASK_DIR / "rack_slot_coordinates_v1.csv"
REACHABILITY_CSV = TASK_DIR / "reachability_check_v1.csv"

TRAJECTORY_CSV = TASK_DIR / "pick_scan_place_trajectory_v1.csv"
MOTION_SUMMARY_CSV = TASK_DIR / "sorting_motion_summary_v1.csv"
WORKSPACE_CHECK_CSV = TASK_DIR / "trajectory_workspace_check_v1.csv"
TOP_VIEW_FIGURE = FIGURE_DIR / "pick_scan_place_top_view_v1.png"
REPORT_PATH = REPORT_DIR / "stage_6b_pick_scan_place_trajectory_report.md"

HEIGHT_RULES = {
    "safe_z": 180.0,
    "approach_z": 120.0,
    "grip_z_75mm": 55.0,
    "grip_z_100mm": 80.0,
    "place_z_75mm": 45.0,
    "place_z_100mm": 70.0,
    "scan_z": 75.0,
}

WORK_ENVELOPE = {
    "x_min": -500.0,
    "x_max": 500.0,
    "y_min": -400.0,
    "y_max": 400.0,
    "z_min": 0.0,
    "z_max": 260.0,
}

TARGET_RACK_NAMES = {
    "category_a_bin": "category_A_output_bin_2x3",
    "category_b_bin": "category_B_output_bin_2x3",
    "category_c_bin": "category_C_output_bin_2x3",
    "category_d_bin": "category_D_output_bin_2x3",
    "manual_review_bin": "manual_review_bin_2x3",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def slot_lookup(slot_rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {(row["rack_name"], row["slot_id"]): row for row in slot_rows}


def point_from_slot(slot: dict[str, str], z_mm: float) -> tuple[float, float, float]:
    return (float(slot["x_mm"]), float(slot["y_mm"]), z_mm)


def grip_z_for_height(height_mm: int) -> float:
    return HEIGHT_RULES["grip_z_100mm"] if height_mm >= 100 else HEIGHT_RULES["grip_z_75mm"]


def place_z_for_height(height_mm: int) -> float:
    return HEIGHT_RULES["place_z_100mm"] if height_mm >= 100 else HEIGHT_RULES["place_z_75mm"]


def waypoint(
    trajectory_id: str,
    sample_id: str,
    order: int,
    state: str,
    zone: str,
    slot_id: str,
    point: tuple[float, float, float],
    gripper_action: str,
    scanner_action: str,
    expected_result: str,
    notes: str,
) -> dict[str, object]:
    return {
        "trajectory_id": trajectory_id,
        "sample_id": sample_id,
        "step_order": order,
        "state": state,
        "zone": zone,
        "slot_id": slot_id,
        "x_mm": f"{point[0]:.3f}",
        "y_mm": f"{point[1]:.3f}",
        "z_mm": f"{point[2]:.3f}",
        "gripper_action": gripper_action,
        "scanner_action": scanner_action,
        "expected_result": expected_result,
        "notes": notes,
    }


def build_waypoints_for_sample(
    sequence_row: dict[str, str],
    slots: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, object]]:
    sample_id = sequence_row["sample_id"]
    trajectory_id = f"traj_{int(sequence_row['step_id']):03d}"
    height_mm = int(float(sequence_row["tube_height_mm"]))
    input_slot_id = sequence_row["input_slot"]
    input_slot = slots[("input_mixed_tube_rack_4x6", input_slot_id)]
    scan_slot = slots[("scan_station_holder", "SCAN1")]
    target_zone = sequence_row["target_zone"]
    expected_scan = f"{sequence_row['barcode_status']} / {sequence_row['category']}"

    safe_z = HEIGHT_RULES["safe_z"]
    approach_z = HEIGHT_RULES["approach_z"]
    grip_z = grip_z_for_height(height_mm)
    place_z = place_z_for_height(height_mm)
    scan_z = HEIGHT_RULES["scan_z"]

    if target_zone == "PAUSE_ALARM":
        input_safe = point_from_slot(input_slot, safe_z)
        return [
            waypoint(trajectory_id, sample_id, 1, "MOVE_SAFE_ABOVE_INPUT", "input", input_slot_id, input_safe, "open", "idle", "pause before pick", "manual review full; operator intervention required"),
            waypoint(trajectory_id, sample_id, 2, "PAUSE_ALARM", "manual_review", "", input_safe, "open", "idle", "manual_review_full", "no target slot available"),
        ]

    target_rack = TARGET_RACK_NAMES[target_zone]
    target_slot_id = sequence_row["target_slot"]
    target_slot = slots[(target_rack, target_slot_id)]

    points = [
        ("MOVE_SAFE_ABOVE_INPUT", "input", input_slot_id, point_from_slot(input_slot, safe_z), "open", "idle", "above input slot"),
        ("APPROACH_INPUT_SLOT", "input", input_slot_id, point_from_slot(input_slot, approach_z), "open", "idle", "approach input slot"),
        ("PICK_TUBE", "input", input_slot_id, point_from_slot(input_slot, grip_z), "close", "idle", f"grip {height_mm} mm tube"),
        ("LIFT_TO_SAFE_Z", "input", input_slot_id, point_from_slot(input_slot, safe_z), "hold", "idle", "lift picked tube"),
        ("MOVE_SAFE_ABOVE_SCAN", "scan_station", "SCAN1", point_from_slot(scan_slot, safe_z), "hold", "idle", "move above scan station"),
        ("APPROACH_SCAN_STATION", "scan_station", "SCAN1", point_from_slot(scan_slot, scan_z), "hold", "idle", "present tube to scanner"),
        ("SCAN_BARCODE", "scan_station", "SCAN1", point_from_slot(scan_slot, scan_z), "hold", "trigger_scan", "scan and classify sample"),
        ("LIFT_TO_SAFE_Z_AFTER_SCAN", "scan_station", "SCAN1", point_from_slot(scan_slot, safe_z), "hold", "idle", "lift after scan"),
        ("MOVE_SAFE_ABOVE_TARGET", target_zone, target_slot_id, point_from_slot(target_slot, safe_z), "hold", "idle", "move above selected target"),
        ("APPROACH_TARGET_SLOT", target_zone, target_slot_id, point_from_slot(target_slot, approach_z), "hold", "idle", "approach target slot"),
        ("PLACE_TUBE", target_zone, target_slot_id, point_from_slot(target_slot, place_z), "open", "idle", f"place {height_mm} mm tube"),
        ("RETREAT_TO_SAFE_Z", target_zone, target_slot_id, point_from_slot(target_slot, safe_z), "open", "idle", "retreat after place"),
    ]

    rows = []
    for order, (state, zone, slot_id, point, grip, scanner, note) in enumerate(points, start=1):
        rows.append(
            waypoint(
                trajectory_id,
                sample_id,
                order,
                state,
                zone,
                slot_id,
                point,
                grip,
                scanner,
                expected_scan if state == "SCAN_BARCODE" else "",
                note,
            )
        )
    return rows


def xy_distance(waypoints: list[dict[str, object]]) -> float:
    total = 0.0
    previous: tuple[float, float] | None = None
    for row in waypoints:
        current = (float(row["x_mm"]), float(row["y_mm"]))
        if previous is not None:
            total += math.dist(previous, current)
        previous = current
    return total


def check_waypoints(trajectory_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    checks = []
    for row in trajectory_rows:
        x = float(row["x_mm"])
        y = float(row["y_mm"])
        z = float(row["z_mm"])
        x_ok = WORK_ENVELOPE["x_min"] <= x <= WORK_ENVELOPE["x_max"]
        y_ok = WORK_ENVELOPE["y_min"] <= y <= WORK_ENVELOPE["y_max"]
        z_ok = WORK_ENVELOPE["z_min"] <= z <= WORK_ENVELOPE["z_max"]
        notes = []
        if not x_ok:
            notes.append("x outside workspace")
        if not y_ok:
            notes.append("y outside workspace")
        if not z_ok:
            notes.append("z outside workspace")
        checks.append(
            {
                "trajectory_id": row["trajectory_id"],
                "sample_id": row["sample_id"],
                "step_order": row["step_order"],
                "state": row["state"],
                "x_mm": row["x_mm"],
                "y_mm": row["y_mm"],
                "z_mm": row["z_mm"],
                "within_x_range": "yes" if x_ok else "no",
                "within_y_range": "yes" if y_ok else "no",
                "within_z_range": "yes" if z_ok else "no",
                "check_status": "ok" if x_ok and y_ok and z_ok else "out_of_range",
                "notes": "within Stage 6A workspace" if x_ok and y_ok and z_ok else "; ".join(notes),
            }
        )
    return checks


def build_motion_summary(sequence_rows: list[dict[str, str]], trajectory_by_sample: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows = []
    for sequence in sequence_rows:
        sample_id = sequence["sample_id"]
        waypoints = trajectory_by_sample[sample_id]
        target_zone = sequence["target_zone"]
        uses_manual_review = target_zone == "manual_review_bin"
        status = "pause_alarm" if target_zone == "PAUSE_ALARM" else ("manual_review" if uses_manual_review else "ok")
        rows.append(
            {
                "sample_id": sample_id,
                "input_slot": sequence["input_slot"],
                "tube_height_mm": sequence["tube_height_mm"],
                "category": sequence["category"],
                "barcode_status": sequence["barcode_status"],
                "target_zone": target_zone,
                "target_slot": sequence["target_slot"],
                "num_waypoints": len(waypoints),
                "estimated_xy_distance_mm": f"{xy_distance(waypoints):.3f}",
                "uses_manual_review": "yes" if uses_manual_review else "no",
                "status": status,
            }
        )
    return rows


def make_top_view_figure(slot_rows: list[dict[str, str]], sequence_rows: list[dict[str, str]], trajectory_by_sample: dict[str, list[dict[str, object]]]) -> tuple[bool, str]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        return False, f"matplotlib unavailable: {type(exc).__name__}: {exc}"

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_title("Stage 6B Pick-Scan-Place Top View")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(WORK_ENVELOPE["x_min"] - 40, WORK_ENVELOPE["x_max"] + 40)
    ax.set_ylim(WORK_ENVELOPE["y_min"] - 40, WORK_ENVELOPE["y_max"] + 40)
    ax.grid(True, linestyle=":", linewidth=0.7)

    zone_styles = {
        "input": ("#2f80ed", "Input rack"),
        "scan_station": ("#111111", "Scan station"),
        "output_A": ("#7b3fbb", "Category A"),
        "output_B": ("#e0a800", "Category B"),
        "output_C": ("#1f77b4", "Category C"),
        "output_D": ("#d62728", "Category D"),
        "manual_review": ("#666666", "Manual review"),
    }
    for zone, (color, label) in zone_styles.items():
        points = [(float(row["x_mm"]), float(row["y_mm"])) for row in slot_rows if row["zone"] == zone]
        if points:
            xs, ys = zip(*points)
            ax.scatter(xs, ys, s=32, color=color, label=label, zorder=3)

    sequence_by_sample = {row["sample_id"]: row for row in sequence_rows}
    for sample_id, waypoints in trajectory_by_sample.items():
        key_states = {"MOVE_SAFE_ABOVE_INPUT", "MOVE_SAFE_ABOVE_SCAN", "MOVE_SAFE_ABOVE_TARGET", "PAUSE_ALARM"}
        path = [(float(row["x_mm"]), float(row["y_mm"])) for row in waypoints if row["state"] in key_states]
        if len(path) < 2:
            continue
        xs, ys = zip(*path)
        sequence = sequence_by_sample[sample_id]
        is_exception = sequence["target_zone"] == "manual_review_bin" or sequence["target_zone"] == "PAUSE_ALARM"
        ax.plot(xs, ys, color="#c0392b" if is_exception else "#2c7fb8", alpha=0.45, linewidth=1.2, linestyle="--" if is_exception else "-")

    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(TOP_VIEW_FIGURE, dpi=180)
    plt.close(fig)
    return True, TOP_VIEW_FIGURE.relative_to(ROOT).as_posix()


def write_report(
    trajectory_rows: list[dict[str, object]],
    summary_rows: list[dict[str, object]],
    workspace_rows: list[dict[str, object]],
    figure_status: tuple[bool, str],
) -> None:
    sample_count = len(summary_rows)
    waypoint_count = len(trajectory_rows)
    normal_count = sum(1 for row in summary_rows if row["status"] == "ok")
    manual_review_count = sum(1 for row in summary_rows if row["uses_manual_review"] == "yes")
    pause_alarm_count = sum(1 for row in summary_rows if row["status"] == "pause_alarm")
    out_of_range = [row for row in workspace_rows if row["check_status"] != "ok"]
    distances = [float(row["estimated_xy_distance_mm"]) for row in summary_rows]
    figure_ok, figure_note = figure_status
    safe_z_ok = HEIGHT_RULES["safe_z"] > 100.0 and HEIGHT_RULES["safe_z"] <= WORK_ENVELOPE["z_max"]

    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Stage 6B Pick-Scan-Place Trajectory Report",
                "",
                "## Inputs",
                "",
                f"- `{SORTING_SEQUENCE_CSV.relative_to(ROOT).as_posix()}`",
                f"- `{RACK_SLOT_CSV.relative_to(ROOT).as_posix()}`",
                f"- `{REACHABILITY_CSV.relative_to(ROOT).as_posix()}`",
                "",
                "## Results",
                "",
                f"- Sample count: {sample_count}",
                f"- Generated waypoint count: {waypoint_count}",
                f"- Normal classification samples: {normal_count}",
                f"- Manual review samples: {manual_review_count}",
                f"- Workspace check: {len(workspace_rows) - len(out_of_range)} ok / {len(out_of_range)} out of range",
                f"- safe_z check: {'ok' if safe_z_ok else 'not ok'}",
                f"- Max estimated XY distance: {max(distances):.3f} mm",
                f"- Average estimated XY distance: {sum(distances) / len(distances):.3f} mm",
                f"- Out-of-range waypoints: {len(out_of_range)}",
                f"- PAUSE_ALARM samples: {pause_alarm_count}",
                f"- Top-view figure: {'generated' if figure_ok else 'not generated'} ({figure_note})",
                "",
                "## Next",
                "",
                "- 6C: motion time and cycle-time estimation.",
                "- 6D: exception handling logic simulation.",
                "- 6E: animation or demonstration video generation.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    slot_rows = read_csv(RACK_SLOT_CSV)
    sequence_rows = read_csv(SORTING_SEQUENCE_CSV)
    slots = slot_lookup(slot_rows)

    trajectory_rows: list[dict[str, object]] = []
    trajectory_by_sample: dict[str, list[dict[str, object]]] = {}
    for sequence in sequence_rows:
        sample_waypoints = build_waypoints_for_sample(sequence, slots)
        trajectory_by_sample[sequence["sample_id"]] = sample_waypoints
        trajectory_rows.extend(sample_waypoints)

    summary_rows = build_motion_summary(sequence_rows, trajectory_by_sample)
    workspace_rows = check_waypoints(trajectory_rows)
    figure_status = make_top_view_figure(slot_rows, sequence_rows, trajectory_by_sample)

    write_csv(
        TRAJECTORY_CSV,
        trajectory_rows,
        ["trajectory_id", "sample_id", "step_order", "state", "zone", "slot_id", "x_mm", "y_mm", "z_mm", "gripper_action", "scanner_action", "expected_result", "notes"],
    )
    write_csv(
        MOTION_SUMMARY_CSV,
        summary_rows,
        ["sample_id", "input_slot", "tube_height_mm", "category", "barcode_status", "target_zone", "target_slot", "num_waypoints", "estimated_xy_distance_mm", "uses_manual_review", "status"],
    )
    write_csv(
        WORKSPACE_CHECK_CSV,
        workspace_rows,
        ["trajectory_id", "sample_id", "step_order", "state", "x_mm", "y_mm", "z_mm", "within_x_range", "within_y_range", "within_z_range", "check_status", "notes"],
    )
    write_report(trajectory_rows, summary_rows, workspace_rows, figure_status)

    out_of_range = sum(1 for row in workspace_rows if row["check_status"] != "ok")
    pause_alarm = sum(1 for row in summary_rows if row["status"] == "pause_alarm")
    manual_review = sum(1 for row in summary_rows if row["uses_manual_review"] == "yes")
    distances = [float(row["estimated_xy_distance_mm"]) for row in summary_rows]
    print(f"sample_count={len(summary_rows)}")
    print(f"waypoint_count={len(trajectory_rows)}")
    print(f"workspace_ok={len(workspace_rows) - out_of_range}")
    print(f"workspace_out_of_range={out_of_range}")
    print(f"manual_review_samples={manual_review}")
    print(f"pause_alarm_samples={pause_alarm}")
    print(f"max_xy_distance_mm={max(distances):.3f}")
    print(f"avg_xy_distance_mm={sum(distances) / len(distances):.3f}")
    print(f"figure={figure_status[1]}")
    print(f"report={REPORT_PATH}")
    return 0 if out_of_range == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
