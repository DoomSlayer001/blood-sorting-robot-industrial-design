from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = ROOT / "04_simulation" / "task_planning"
FIGURE_DIR = TASK_DIR / "figures"
REPORT_DIR = ROOT / "reports"

SLOT_CSV = TASK_DIR / "multi_box_slot_coordinates_v1.csv"
HEIGHT_RULES_MD = TASK_DIR / "multi_box_pick_place_height_rules_v1.md"
MANIFEST_CSV = TASK_DIR / "multi_box_sample_manifest_v1.csv"
POLICY_SIM_CSV = TASK_DIR / "multi_box_sorting_policy_simulation_v1.csv"
PENDING_QUEUE_CSV = TASK_DIR / "multi_box_pending_queue_v1.csv"
OPERATOR_EVENTS_CSV = TASK_DIR / "multi_box_operator_events_v1.csv"
POLICY_SUMMARY_CSV = TASK_DIR / "multi_box_sorting_policy_summary_v1.csv"

TRAJECTORY_CSV = TASK_DIR / "multi_box_pick_scan_place_trajectory_v1.csv"
MOTION_SUMMARY_CSV = TASK_DIR / "multi_box_motion_summary_v1.csv"
WORKSPACE_CHECK_CSV = TASK_DIR / "multi_box_trajectory_workspace_check_v1.csv"
EVENT_SUMMARY_CSV = TASK_DIR / "multi_box_trajectory_event_summary_v1.csv"
TOP_VIEW_FIGURE = FIGURE_DIR / "multi_box_trajectory_top_view_v1.png"
PENDING_RESUME_FIGURE = FIGURE_DIR / "multi_box_pending_resume_trajectory_v1.png"
MANUAL_REVIEW_FIGURE = FIGURE_DIR / "multi_box_manual_review_trajectory_v1.png"
REPORT_PATH = REPORT_DIR / "stage_7d_multi_box_trajectory_report.md"

HEIGHT_RULES = {
    "safe_z": 200.0,
    "approach_z": 130.0,
    "grip_z_75mm": 55.0,
    "grip_z_100mm": 80.0,
    "place_z_75mm": 45.0,
    "place_z_100mm": 70.0,
    "scan_z": 75.0,
}

WORK_ENVELOPE = {
    "x_min": -570.0,
    "x_max": 570.0,
    "y_min": -420.0,
    "y_max": 420.0,
    "z_min": 0.0,
    "z_max": 280.0,
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def point_key(box_id: str, slot_id: str) -> tuple[str, str]:
    return (box_id, slot_id)


def load_points() -> dict[tuple[str, str], dict[str, float]]:
    points: dict[tuple[str, str], dict[str, float]] = {}
    for row in read_csv(SLOT_CSV):
        points[point_key(row["box_id"], row["slot_id"])] = {
            "x": float(row["x_mm"]),
            "y": float(row["y_mm"]),
            "z_insert": float(row["z_insert_mm"]),
        }
    return points


def load_height_rules() -> dict[str, float]:
    if not HEIGHT_RULES_MD.is_file():
        return dict(HEIGHT_RULES)
    text = HEIGHT_RULES_MD.read_text(encoding="utf-8")
    rules = dict(HEIGHT_RULES)
    for key in list(rules):
        marker = f"`{key}`"
        for line in text.splitlines():
            if marker in line:
                parts = [part.strip() for part in line.strip("|").split("|")]
                if len(parts) >= 2:
                    try:
                        rules[key] = float(parts[1])
                    except ValueError:
                        pass
    return rules


def manifest_by_sample() -> dict[str, dict[str, str]]:
    return {row["sample_id"]: row for row in read_csv(MANIFEST_CSV)}


def input_point(points: dict[tuple[str, str], dict[str, float]], row: dict[str, str]) -> dict[str, float]:
    return points[point_key(row["input_box_id"], row["input_slot_id"])]


def scan_point(points: dict[tuple[str, str], dict[str, float]]) -> dict[str, float]:
    return points[point_key("scan_station", "SCAN_01")]


def target_point(points: dict[tuple[str, str], dict[str, float]], row: dict[str, str]) -> dict[str, float] | None:
    target_box = row["target_box_id"]
    target_slot = row["target_slot_id"]
    if not target_box or not target_slot:
        return None
    return points.get(point_key(target_box, target_slot))


def grip_z(height_mm: str, rules: dict[str, float]) -> float:
    return rules["grip_z_100mm"] if float(height_mm) >= 100.0 else rules["grip_z_75mm"]


def place_z(height_mm: str, rules: dict[str, float]) -> float:
    return rules["place_z_100mm"] if float(height_mm) >= 100.0 else rules["place_z_75mm"]


def waypoint(
    run_row: dict[str, str],
    trajectory_id: str,
    step_order: int,
    state: str,
    point: dict[str, float],
    z: float,
    gripper_action: str,
    scanner_action: str,
    expected_result: str,
    notes: str,
) -> dict[str, object]:
    return {
        "run_id": run_row["run_id"],
        "trajectory_id": trajectory_id,
        "sample_id": run_row["sample_id"],
        "step_order": step_order,
        "state": state,
        "input_box_id": run_row["input_box_id"],
        "input_slot_id": run_row["input_slot_id"],
        "target_zone": run_row["target_zone"],
        "target_box_id": run_row["target_box_id"],
        "target_slot_id": run_row["target_slot_id"],
        "x_mm": f"{point['x']:.3f}",
        "y_mm": f"{point['y']:.3f}",
        "z_mm": f"{z:.3f}",
        "gripper_action": gripper_action,
        "scanner_action": scanner_action,
        "category_status": run_row["current_category_status"],
        "pending_queue_action": run_row["pending_queue_action"],
        "operator_event": run_row["operator_event"],
        "expected_result": expected_result,
        "notes": notes,
    }


def full_trajectory(
    run_row: dict[str, str],
    sample: dict[str, str],
    points: dict[tuple[str, str], dict[str, float]],
    rules: dict[str, float],
    trajectory_index: int,
) -> list[dict[str, object]]:
    inp = input_point(points, run_row)
    scan = scan_point(points)
    target = target_point(points, run_row)
    if target is None:
        return alarm_trajectory(run_row, sample, points, rules, trajectory_index, "missing target point")

    trajectory_id = f"{run_row['run_id']}_{trajectory_index:04d}_{run_row['sample_id']}"
    gz = grip_z(sample["tube_height_mm"], rules)
    pz = place_z(sample["tube_height_mm"], rules)
    rows = [
        ("MOVE_SAFE_ABOVE_INPUT", inp, rules["safe_z"], "open", "off", "move to input safe height"),
        ("APPROACH_INPUT_SLOT", inp, rules["approach_z"], "open", "off", "approach input slot"),
        ("PICK_TUBE", inp, gz, "close", "off", "pick tube"),
        ("LIFT_TO_SAFE_Z", inp, rules["safe_z"], "hold", "off", "lift picked tube"),
        ("MOVE_SAFE_ABOVE_SCAN", scan, rules["safe_z"], "hold", "off", "move above scan station"),
        ("APPROACH_SCAN_STATION", scan, rules["scan_z"], "hold", "off", "approach scan station"),
        ("SCAN_BARCODE", scan, rules["scan_z"], "hold", "scan", "scan and classify"),
        ("LIFT_TO_SAFE_Z_AFTER_SCAN", scan, rules["safe_z"], "hold", "off", "lift after scan"),
        ("MOVE_SAFE_ABOVE_TARGET", target, rules["safe_z"], "hold", "off", "move above target"),
        ("APPROACH_TARGET_SLOT", target, rules["approach_z"], "hold", "off", "approach target slot"),
        ("PLACE_TUBE", target, pz, "open", "off", "place tube"),
        ("RETREAT_TO_SAFE_Z", target, rules["safe_z"], "open", "off", "retreat after place"),
    ]
    expected = "placed_manual_review" if run_row["target_box_id"] == "manual_review_bin" else "placed_output"
    return [
        waypoint(run_row, trajectory_id, index, state, point, z, gripper, scanner, expected, notes)
        for index, (state, point, z, gripper, scanner, notes) in enumerate(rows, start=1)
    ]


def alarm_trajectory(
    run_row: dict[str, str],
    sample: dict[str, str],
    points: dict[tuple[str, str], dict[str, float]],
    rules: dict[str, float],
    trajectory_index: int,
    reason: str,
) -> list[dict[str, object]]:
    inp = input_point(points, run_row)
    scan = scan_point(points)
    trajectory_id = f"{run_row['run_id']}_{trajectory_index:04d}_{run_row['sample_id']}"
    gz = grip_z(sample["tube_height_mm"], rules)
    rows = [
        ("MOVE_SAFE_ABOVE_INPUT", inp, rules["safe_z"], "open", "off", "move to input safe height"),
        ("APPROACH_INPUT_SLOT", inp, rules["approach_z"], "open", "off", "approach input slot"),
        ("PICK_TUBE", inp, gz, "close", "off", "pick tube before exception is known"),
        ("LIFT_TO_SAFE_Z", inp, rules["safe_z"], "hold", "off", "lift picked tube"),
        ("MOVE_SAFE_ABOVE_SCAN", scan, rules["safe_z"], "hold", "off", "move above scan station"),
        ("APPROACH_SCAN_STATION", scan, rules["scan_z"], "hold", "off", "approach scan station"),
        ("SCAN_BARCODE", scan, rules["scan_z"], "hold", "scan", "scan reveals sample needs manual review"),
        ("PAUSE_ALARM", scan, rules["safe_z"], "hold", "off", reason),
    ]
    return [
        waypoint(run_row, trajectory_id, index, state, point, z, gripper, scanner, "pause_alarm", notes)
        for index, (state, point, z, gripper, scanner, notes) in enumerate(rows, start=1)
    ]


def queue_trajectory(
    run_row: dict[str, str],
    points: dict[tuple[str, str], dict[str, float]],
    rules: dict[str, float],
    trajectory_index: int,
) -> list[dict[str, object]]:
    inp = input_point(points, run_row)
    trajectory_id = f"{run_row['run_id']}_{trajectory_index:04d}_{run_row['sample_id']}_queued"
    return [
        waypoint(run_row, trajectory_id, 1, run_row["selected_action"], inp, rules["safe_z"], "open", "off", "queued_pending", "held-category sample skipped before pick and queued"),
    ]


def generate_trajectory_rows() -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, float]]:
    points = load_points()
    rules = load_height_rules()
    samples = manifest_by_sample()
    sim_rows = read_csv(POLICY_SIM_CSV)
    trajectory_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    trajectory_counter = Counter()

    for sim in sim_rows:
        run_id = sim["run_id"]
        trajectory_counter[run_id] += 1
        sample = samples[sim["sample_id"]]
        if sim["selected_action"] in {"SKIP_HELD_CATEGORY", "HOLD_CATEGORY"}:
            rows = queue_trajectory(sim, points, rules, trajectory_counter[run_id])
        elif sim["system_state"] == "PAUSE_ALARM":
            rows = alarm_trajectory(sim, sample, points, rules, trajectory_counter[run_id], sim["notes"])
        else:
            rows = full_trajectory(sim, sample, points, rules, trajectory_counter[run_id])
        trajectory_rows.extend(rows)
        event_rows.extend(events_for_sim_row(sim, rows))
    event_rows.extend(operator_event_rows(points, rules))
    return trajectory_rows, event_rows, rules


def events_for_sim_row(sim: dict[str, str], waypoints: list[dict[str, object]]) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    for row in waypoints:
        state = str(row["state"])
        event_type = ""
        if state == "SCAN_BARCODE":
            event_type = "scan_event"
        elif state == "PLACE_TUBE" and row["target_box_id"] == "manual_review_bin":
            event_type = "place_to_manual_review"
        elif state == "PLACE_TUBE":
            event_type = "place_to_category_output"
        elif state in {"SKIP_HELD_CATEGORY", "HOLD_CATEGORY"}:
            event_type = "queued_pending_sample" if state == "SKIP_HELD_CATEGORY" else "category_hold"
        elif state == "PAUSE_ALARM":
            event_type = "PAUSE_ALARM"
        if event_type:
            events.append(event_row_from_waypoint(row, event_type, "trajectory event"))
    if sim["pending_queue_action"] == "released":
        release_wp = waypoints[-1]
        events.append(event_row_from_waypoint(release_wp, "released_pending_sample", "pending sample resumed and placed"))
    return events


def event_row_from_waypoint(row: dict[str, object], event_type: str, notes: str) -> dict[str, object]:
    related_category = ""
    if str(row["category_status"]) == "held" or str(row["target_zone"]).startswith("output_"):
        related_category = str(row["target_zone"]).replace("output_", "Category ") if row["target_zone"] else ""
    return {
        "run_id": row["run_id"],
        "event_id": f"{row['trajectory_id']}_{event_type}_{row['step_order']}",
        "sample_id": row["sample_id"],
        "event_type": event_type,
        "state": row["state"],
        "related_category": related_category,
        "related_box_id": row["target_box_id"],
        "x_mm": row["x_mm"],
        "y_mm": row["y_mm"],
        "z_mm": row["z_mm"],
        "notes": notes,
    }


def operator_event_rows(points: dict[tuple[str, str], dict[str, float]], rules: dict[str, float]) -> list[dict[str, object]]:
    rows = []
    output_a = points[point_key("category_A_output_box", "A1")]
    scan = scan_point(points)
    for event in read_csv(OPERATOR_EVENTS_CSV):
        if event["event_type"] in {"clear_or_replace_category_A_output_box", "resume_category_A"}:
            point = output_a
        else:
            point = scan
        rows.append(
            {
                "run_id": event["run_id"],
                "event_id": event["event_id"],
                "sample_id": "",
                "event_type": event["event_type"],
                "state": event["system_response"],
                "related_category": event["related_category"],
                "related_box_id": event["related_box_id"],
                "x_mm": f"{point['x']:.3f}",
                "y_mm": f"{point['y']:.3f}",
                "z_mm": f"{rules['safe_z']:.3f}",
                "notes": event["notes"],
            }
        )
    return rows


def distance_summary(rows: list[dict[str, object]]) -> tuple[float, float]:
    xy_distance = 0.0
    z_distance = 0.0
    for prev, curr in zip(rows, rows[1:]):
        dx = float(curr["x_mm"]) - float(prev["x_mm"])
        dy = float(curr["y_mm"]) - float(prev["y_mm"])
        dz = float(curr["z_mm"]) - float(prev["z_mm"])
        xy_distance += math.hypot(dx, dy)
        z_distance += abs(dz)
    return xy_distance, z_distance


def motion_summary_rows(trajectory_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    samples = manifest_by_sample()
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in trajectory_rows:
        grouped[(str(row["run_id"]), str(row["sample_id"]), str(row["trajectory_id"]))].append(row)
    rows = []
    for (run_id, sample_id, trajectory_id), points in grouped.items():
        sample = samples[sample_id]
        final = points[-1]
        xy_distance, z_distance = distance_summary(points)
        rows.append(
            {
                "run_id": run_id,
                "sample_id": sample_id,
                "input_box_id": sample["input_box_id"],
                "input_slot_id": sample["input_slot_id"],
                "tube_height_mm": sample["tube_height_mm"],
                "category": sample["category"],
                "barcode_status": sample["barcode_status"],
                "is_abnormal": sample["is_abnormal"],
                "target_zone": final["target_zone"],
                "target_box_id": final["target_box_id"],
                "target_slot_id": final["target_slot_id"],
                "num_waypoints": len(points),
                "estimated_xy_distance_mm": f"{xy_distance:.3f}",
                "estimated_z_distance_mm": f"{z_distance:.3f}",
                "uses_manual_review": "yes" if final["target_box_id"] == "manual_review_bin" else "no",
                "was_queued": "yes" if any(row["pending_queue_action"] in {"queued", "released"} or row["expected_result"] == "queued_pending" for row in points) else "no",
                "queue_wait_event": final["operator_event"],
                "final_status": final["expected_result"],
                "notes": f"trajectory_id={trajectory_id}",
            }
        )
    return rows


def workspace_check_rows(trajectory_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for row in trajectory_rows:
        x = float(row["x_mm"])
        y = float(row["y_mm"])
        z = float(row["z_mm"])
        x_ok = WORK_ENVELOPE["x_min"] <= x <= WORK_ENVELOPE["x_max"]
        y_ok = WORK_ENVELOPE["y_min"] <= y <= WORK_ENVELOPE["y_max"]
        z_ok = WORK_ENVELOPE["z_min"] <= z <= WORK_ENVELOPE["z_max"]
        rows.append(
            {
                "run_id": row["run_id"],
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
                "notes": "within Stage 7B envelope" if x_ok and y_ok and z_ok else "outside Stage 7B envelope",
            }
        )
    return rows


def plot_figures(trajectory_rows: list[dict[str, object]], event_rows: list[dict[str, object]]) -> list[str]:
    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
    except Exception as exc:
        return [f"matplotlib unavailable: {exc}"]
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    plot_run_top_view(plt, trajectory_rows, "baseline_multi_box_run", TOP_VIEW_FIGURE, "Baseline Multi-box Pick-Scan-Place Trajectories")
    outputs.append(str(TOP_VIEW_FIGURE))
    plot_run_top_view(plt, trajectory_rows, "forced_category_A_full", PENDING_RESUME_FIGURE, "Forced Category A Hold / Pending / Resume Trajectories")
    outputs.append(str(PENDING_RESUME_FIGURE))
    plot_manual_review(plt, trajectory_rows, event_rows)
    outputs.append(str(MANUAL_REVIEW_FIGURE))
    return outputs


def draw_layout(ax) -> None:
    from matplotlib.patches import Rectangle

    for x, y, w, h, label in [
        (-420, 225, 180, 120, "input boxes"),
        (70, 110, 180, 120, "A"),
        (280, 110, 180, 120, "B"),
        (70, -100, 180, 120, "C"),
        (280, -100, 180, 120, "D"),
        (-225, -330, 90, 60, "manual"),
    ]:
        ax.add_patch(Rectangle((x, y), w, h, fill=False, linewidth=0.8, edgecolor="#555555"))
        ax.text(x + w / 2, y + h / 2, label, fontsize=7, ha="center", va="center")
    ax.scatter([-140], [60], marker="*", s=80, c="black", label="scan station")


def plot_run_top_view(plt, trajectory_rows: list[dict[str, object]], run_id: str, path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 7))
    draw_layout(ax)
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in trajectory_rows:
        if row["run_id"] == run_id and row["expected_result"] != "queued_pending":
            grouped[str(row["trajectory_id"])].append(row)
    for points in grouped.values():
        xs = [float(row["x_mm"]) for row in points if row["state"].startswith("MOVE") or row["state"].startswith("RETREAT")]
        ys = [float(row["y_mm"]) for row in points if row["state"].startswith("MOVE") or row["state"].startswith("RETREAT")]
        if len(xs) >= 2:
            alpha = 0.18 if run_id == "baseline_multi_box_run" else 0.35
            ax.plot(xs, ys, color="#377eb8", alpha=alpha, linewidth=0.7)
    pending = [row for row in trajectory_rows if row["run_id"] == run_id and row["expected_result"] == "queued_pending"]
    if pending:
        ax.scatter([float(row["x_mm"]) for row in pending], [float(row["y_mm"]) for row in pending], marker="^", c="#d95f02", s=35, label="queued")
    ax.set_title(title)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-600, 600)
    ax.set_ylim(-450, 420)
    ax.grid(True, linewidth=0.3, alpha=0.4)
    ax.set_xlabel("X mm")
    ax.set_ylabel("Y mm")
    ax.legend(loc="upper right", fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_manual_review(plt, trajectory_rows: list[dict[str, object]], event_rows: list[dict[str, object]]) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    draw_layout(ax)
    rows = [row for row in trajectory_rows if row["target_box_id"] == "manual_review_bin" or row["expected_result"] == "pause_alarm"]
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["trajectory_id"])].append(row)
    for points in grouped.values():
        xs = [float(row["x_mm"]) for row in points]
        ys = [float(row["y_mm"]) for row in points]
        ax.plot(xs, ys, color="#666666", alpha=0.45, linewidth=0.8)
    alarms = [row for row in event_rows if row["event_type"] == "PAUSE_ALARM"]
    if alarms:
        ax.scatter([float(row["x_mm"]) for row in alarms], [float(row["y_mm"]) for row in alarms], marker="x", c="red", s=70, label="PAUSE_ALARM")
    ax.set_title("Manual Review and PAUSE_ALARM Trajectories")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-600, 600)
    ax.set_ylim(-450, 420)
    ax.grid(True, linewidth=0.3, alpha=0.4)
    ax.legend(loc="upper right", fontsize=7)
    fig.tight_layout()
    fig.savefig(MANUAL_REVIEW_FIGURE, dpi=180)
    plt.close(fig)


def write_report(
    trajectory_rows: list[dict[str, object]],
    motion_rows: list[dict[str, object]],
    workspace_rows: list[dict[str, object]],
    figures: list[str],
) -> None:
    waypoints_by_run = Counter(row["run_id"] for row in trajectory_rows)
    check_counts = Counter(row["check_status"] for row in workspace_rows)
    queued = sum(1 for row in motion_rows if row["was_queued"] == "yes" and row["final_status"] == "queued_pending")
    resumed = sum(1 for row in motion_rows if row["was_queued"] == "yes" and row["final_status"] == "placed_output")
    manual_review = sum(1 for row in motion_rows if row["uses_manual_review"] == "yes")
    out_of_range = [row for row in workspace_rows if row["check_status"] != "ok"]
    figure_text = ", ".join(Path(path).relative_to(ROOT).as_posix() if Path(path).is_file() else path for path in figures)
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Stage 7D Multi-box Trajectory Report",
                "",
                "- Goal: generate multi-box pick-scan-place trajectories from Stage 7B coordinates and Stage 7C policy simulation.",
                f"- Input files: `{MANIFEST_CSV.relative_to(ROOT).as_posix()}`, `{SLOT_CSV.relative_to(ROOT).as_posix()}`, `{POLICY_SIM_CSV.relative_to(ROOT).as_posix()}`, `{PENDING_QUEUE_CSV.relative_to(ROOT).as_posix()}`, `{OPERATOR_EVENTS_CSV.relative_to(ROOT).as_posix()}`.",
                f"- Baseline trajectory: {waypoints_by_run['baseline_multi_box_run']} waypoints for 96 samples.",
                f"- Forced Category A full trajectory: {waypoints_by_run['forced_category_A_full']} waypoints; queued samples are skipped, then resumed after operator clear/replacement.",
                f"- Forced manual review full trajectory: {waypoints_by_run['forced_manual_review_full']} waypoints and stops at PAUSE_ALARM.",
                f"- Pending queue: queued={queued}, resumed={resumed}.",
                f"- Manual review trajectories: {manual_review}.",
                f"- Workspace check: ok={check_counts['ok']}, out_of_range={check_counts['out_of_range']}.",
                f"- Out-of-range points: {'none' if not out_of_range else len(out_of_range)}.",
                "- Normal samples are not routed to manual review because of category output full; they are held, queued, and resumed.",
                f"- Figures: {figure_text}",
                "",
                "## Limits",
                "",
                "- This trajectory model is waypoint-level task planning only; it is not dynamic motion, collision simulation, or PID control.",
                "- Operator events are represented as discrete timeline markers rather than timed human actions.",
                "",
                "## Next Steps",
                "",
                "- Stage 7E: multi-box cycle time and throughput update.",
                "- Stage 7F: multi-box animation update.",
                "- Stage 8: PID / dynamics simulation after multi-box task logic stabilizes.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    trajectory_rows, event_rows, _ = generate_trajectory_rows()
    motion_rows = motion_summary_rows(trajectory_rows)
    workspace_rows = workspace_check_rows(trajectory_rows)
    figures = plot_figures(trajectory_rows, event_rows)
    write_report(trajectory_rows, motion_rows, workspace_rows, figures)

    write_csv(
        TRAJECTORY_CSV,
        trajectory_rows,
        ["run_id", "trajectory_id", "sample_id", "step_order", "state", "input_box_id", "input_slot_id", "target_zone", "target_box_id", "target_slot_id", "x_mm", "y_mm", "z_mm", "gripper_action", "scanner_action", "category_status", "pending_queue_action", "operator_event", "expected_result", "notes"],
    )
    write_csv(
        MOTION_SUMMARY_CSV,
        motion_rows,
        ["run_id", "sample_id", "input_box_id", "input_slot_id", "tube_height_mm", "category", "barcode_status", "is_abnormal", "target_zone", "target_box_id", "target_slot_id", "num_waypoints", "estimated_xy_distance_mm", "estimated_z_distance_mm", "uses_manual_review", "was_queued", "queue_wait_event", "final_status", "notes"],
    )
    write_csv(
        WORKSPACE_CHECK_CSV,
        workspace_rows,
        ["run_id", "trajectory_id", "sample_id", "step_order", "state", "x_mm", "y_mm", "z_mm", "within_x_range", "within_y_range", "within_z_range", "check_status", "notes"],
    )
    write_csv(
        EVENT_SUMMARY_CSV,
        event_rows,
        ["run_id", "event_id", "sample_id", "event_type", "state", "related_category", "related_box_id", "x_mm", "y_mm", "z_mm", "notes"],
    )

    waypoints = Counter(row["run_id"] for row in trajectory_rows)
    checks = Counter(row["check_status"] for row in workspace_rows)
    queued = sum(1 for row in motion_rows if row["was_queued"] == "yes" and row["final_status"] == "queued_pending")
    resumed = sum(1 for row in motion_rows if row["was_queued"] == "yes" and row["final_status"] == "placed_output")
    manual_review = sum(1 for row in motion_rows if row["uses_manual_review"] == "yes")
    print(f"baseline_waypoints={waypoints['baseline_multi_box_run']}")
    print(f"forced_category_A_full_waypoints={waypoints['forced_category_A_full']}")
    print(f"forced_manual_review_full_waypoints={waypoints['forced_manual_review_full']}")
    print(f"workspace_ok={checks['ok']}")
    print(f"workspace_out_of_range={checks['out_of_range']}")
    print(f"queued_samples={queued}")
    print(f"resumed_samples={resumed}")
    print(f"manual_review_trajectories={manual_review}")
    print(f"trajectory_csv={TRAJECTORY_CSV}")
    print(f"workspace_check_csv={WORKSPACE_CHECK_CSV}")
    print(f"report={REPORT_PATH}")
    return 0 if checks["out_of_range"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
