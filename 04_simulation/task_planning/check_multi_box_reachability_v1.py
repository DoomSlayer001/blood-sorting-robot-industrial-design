from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = ROOT / "04_simulation" / "task_planning"
FIGURE_DIR = TASK_DIR / "figures"
REPORT_DIR = ROOT / "reports"

COORDINATE_MODEL_MD = TASK_DIR / "multi_box_coordinate_model_v1.md"
SLOT_CSV = TASK_DIR / "multi_box_slot_coordinates_v1.csv"
HEIGHT_RULES_MD = TASK_DIR / "multi_box_pick_place_height_rules_v1.md"
REACHABILITY_CSV = TASK_DIR / "multi_box_reachability_check_v1.csv"
SUMMARY_CSV = TASK_DIR / "multi_box_slot_summary_v1.csv"
FIGURE_PATH = FIGURE_DIR / "multi_box_slot_map_top_view_v1.png"
REPORT_PATH = REPORT_DIR / "stage_7b_multi_box_coordinate_reachability_report.md"

BASE_PLATE_SIZE = (1200.0, 900.0, 15.0)
INPUT_BOX_ORIGINS = {
    "input_box_1": (-330.0, 285.0),
    "input_box_2": (-330.0, 155.0),
    "input_box_3": (-330.0, 25.0),
    "input_box_4": (-330.0, -105.0),
}
OUTPUT_BOX_ORIGINS = {
    "category_A_output_box": (160.0, 170.0),
    "category_B_output_box": (370.0, 170.0),
    "category_C_output_box": (160.0, -40.0),
    "category_D_output_box": (370.0, -40.0),
}
MANUAL_REVIEW_ORIGIN = (-180.0, -300.0)
SCAN_STATION_ORIGIN = (-140.0, 60.0)
PITCH_MM = 28.0
RACK_Z_INSERT_MM = 25.0
SCAN_Z_INSERT_MM = 24.0
NEAR_LIMIT_XY_MARGIN_MM = 30.0
NEAR_LIMIT_Z_MARGIN_MM = 15.0

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


def row_letter(index: int) -> str:
    return chr(ord("A") + index)


def slot_xy(origin: tuple[float, float], rows: int, cols: int, row_index: int, col_index: int) -> tuple[float, float]:
    x0 = -((cols - 1) * PITCH_MM) / 2.0
    y0 = ((rows - 1) * PITCH_MM) / 2.0
    return (origin[0] + x0 + col_index * PITCH_MM, origin[1] + y0 - row_index * PITCH_MM)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def slot_row(
    zone: str,
    box_id: str,
    rack_name: str,
    slot_id: str,
    row: str,
    col: int,
    x: float,
    y: float,
    z_insert: float,
    slot_role: str,
    notes: str,
) -> dict[str, object]:
    return {
        "zone": zone,
        "box_id": box_id,
        "rack_name": rack_name,
        "slot_id": slot_id,
        "row": row,
        "col": col,
        "x_mm": fmt(x),
        "y_mm": fmt(y),
        "z_insert_mm": fmt(z_insert),
        "z_pick_75mm": fmt(HEIGHT_RULES["grip_z_75mm"]),
        "z_pick_100mm": fmt(HEIGHT_RULES["grip_z_100mm"]),
        "z_place_75mm": fmt(HEIGHT_RULES["place_z_75mm"]),
        "z_place_100mm": fmt(HEIGHT_RULES["place_z_100mm"]),
        "slot_role": slot_role,
        "notes": notes,
    }


def generate_slot_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for box_id, origin in INPUT_BOX_ORIGINS.items():
        for row_index in range(4):
            for col_index in range(6):
                x, y = slot_xy(origin, 4, 6, row_index, col_index)
                row_name = row_letter(row_index)
                rows.append(
                    slot_row(
                        "input",
                        box_id,
                        f"{box_id}_4x6",
                        f"{row_name}{col_index + 1}",
                        row_name,
                        col_index + 1,
                        x,
                        y,
                        RACK_Z_INSERT_MM,
                        "input_pick",
                        "v7.1 4x6 input box origin; coordinates generated from 28 mm pitch",
                    )
                )

    for box_id, origin in OUTPUT_BOX_ORIGINS.items():
        category = box_id.split("_")[1]
        for row_index in range(4):
            for col_index in range(6):
                x, y = slot_xy(origin, 4, 6, row_index, col_index)
                row_name = row_letter(row_index)
                rows.append(
                    slot_row(
                        f"output_{category}",
                        box_id,
                        f"{box_id}_4x6",
                        f"{row_name}{col_index + 1}",
                        row_name,
                        col_index + 1,
                        x,
                        y,
                        RACK_Z_INSERT_MM,
                        "output_place",
                        "v7.1 4x6 category output box origin; normal output full triggers category_hold, not manual review",
                    )
                )

    for row_index in range(2):
        for col_index in range(3):
            x, y = slot_xy(MANUAL_REVIEW_ORIGIN, 2, 3, row_index, col_index)
            row_name = row_letter(row_index)
            rows.append(
                slot_row(
                    "manual_review",
                    "manual_review_bin",
                    "manual_review_bin_2x3",
                    f"{row_name}{col_index + 1}",
                    row_name,
                    col_index + 1,
                    x,
                    y,
                    RACK_Z_INSERT_MM,
                    "manual_review_place",
                    "v7.1 2x3 manual review bin; true abnormal samples only",
                )
            )

    rows.append(
        slot_row(
            "scan_station",
            "scan_station",
            "scan_tube_holder",
            "SCAN_01",
            "SCAN",
            1,
            SCAN_STATION_ORIGIN[0],
            SCAN_STATION_ORIGIN[1],
            SCAN_Z_INSERT_MM,
            "scan_position",
            "v7.1 scan tube holder origin; scan_z used for recognition posture",
        )
    )
    rows[-1]["z_pick_75mm"] = fmt(HEIGHT_RULES["scan_z"])
    rows[-1]["z_pick_100mm"] = fmt(HEIGHT_RULES["scan_z"])
    rows[-1]["z_place_75mm"] = fmt(HEIGHT_RULES["scan_z"])
    rows[-1]["z_place_100mm"] = fmt(HEIGHT_RULES["scan_z"])
    return rows


def in_range(value: float, min_value: float, max_value: float) -> bool:
    return min_value <= value <= max_value


def near_range_limit(value: float, min_value: float, max_value: float, margin: float) -> bool:
    return in_range(value, min_value, max_value) and (value - min_value <= margin or max_value - value <= margin)


def z_values_for_reachability(slot: dict[str, object]) -> list[float]:
    return [
        float(slot["z_insert_mm"]),
        float(slot["z_pick_75mm"]),
        float(slot["z_pick_100mm"]),
        float(slot["z_place_75mm"]),
        float(slot["z_place_100mm"]),
        HEIGHT_RULES["approach_z"],
        HEIGHT_RULES["safe_z"],
    ]


def reachability_status(slot: dict[str, object]) -> dict[str, object]:
    try:
        x = float(slot["x_mm"])
        y = float(slot["y_mm"])
        z_values = z_values_for_reachability(slot)
    except (TypeError, ValueError) as exc:
        return {
            "within_x_range": "no",
            "within_y_range": "no",
            "within_z_range_75mm": "no",
            "within_z_range_100mm": "no",
            "reachability_status": "needs_review",
            "near_limit": "yes",
            "notes": f"coordinate parse error: {exc}",
        }

    x_ok = in_range(x, WORK_ENVELOPE["x_min"], WORK_ENVELOPE["x_max"])
    y_ok = in_range(y, WORK_ENVELOPE["y_min"], WORK_ENVELOPE["y_max"])
    z_75_ok = all(
        in_range(z, WORK_ENVELOPE["z_min"], WORK_ENVELOPE["z_max"])
        for z in [float(slot["z_insert_mm"]), float(slot["z_pick_75mm"]), float(slot["z_place_75mm"]), HEIGHT_RULES["approach_z"], HEIGHT_RULES["safe_z"]]
    )
    z_100_ok = all(
        in_range(z, WORK_ENVELOPE["z_min"], WORK_ENVELOPE["z_max"])
        for z in [float(slot["z_insert_mm"]), float(slot["z_pick_100mm"]), float(slot["z_place_100mm"]), HEIGHT_RULES["approach_z"], HEIGHT_RULES["safe_z"]]
    )
    near_limit = (
        near_range_limit(x, WORK_ENVELOPE["x_min"], WORK_ENVELOPE["x_max"], NEAR_LIMIT_XY_MARGIN_MM)
        or near_range_limit(y, WORK_ENVELOPE["y_min"], WORK_ENVELOPE["y_max"], NEAR_LIMIT_XY_MARGIN_MM)
        or any(near_range_limit(z, WORK_ENVELOPE["z_min"], WORK_ENVELOPE["z_max"], NEAR_LIMIT_Z_MARGIN_MM) for z in z_values)
    )

    notes = []
    if not x_ok:
        notes.append("x outside v7.1 planning envelope")
    if not y_ok:
        notes.append("y outside v7.1 planning envelope")
    if not z_75_ok:
        notes.append("75 mm tube Z heights outside v7.1 planning envelope")
    if not z_100_ok:
        notes.append("100 mm tube Z heights outside v7.1 planning envelope")
    if near_limit and x_ok and y_ok and z_75_ok and z_100_ok:
        notes.append("inside envelope but close to configured limit")

    if not (x_ok and y_ok and z_75_ok and z_100_ok):
        status = "unreachable"
    elif near_limit:
        status = "near_limit"
    else:
        status = "reachable"

    return {
        "within_x_range": "yes" if x_ok else "no",
        "within_y_range": "yes" if y_ok else "no",
        "within_z_range_75mm": "yes" if z_75_ok else "no",
        "within_z_range_100mm": "yes" if z_100_ok else "no",
        "reachability_status": status,
        "near_limit": "yes" if near_limit else "no",
        "notes": "; ".join(notes) if notes else "within v7.1 planning envelope",
    }


def generate_reachability_rows(slot_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for slot in slot_rows:
        status = reachability_status(slot)
        rows.append(
            {
                "zone": slot["zone"],
                "box_id": slot["box_id"],
                "rack_name": slot["rack_name"],
                "slot_id": slot["slot_id"],
                "x_mm": slot["x_mm"],
                "y_mm": slot["y_mm"],
                "z_insert_mm": slot["z_insert_mm"],
                "z_pick_75mm": slot["z_pick_75mm"],
                "z_pick_100mm": slot["z_pick_100mm"],
                **status,
            }
        )
    return rows


def zone_counts(slot_rows: list[dict[str, object]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in slot_rows:
        if row["zone"] == "input":
            counts["input"] += 1
        elif str(row["zone"]).startswith("output_"):
            counts["output"] += 1
        elif row["zone"] == "manual_review":
            counts["manual_review"] += 1
        elif row["zone"] == "scan_station":
            counts["scan_station"] += 1
    return counts


def summary_rows(slot_rows: list[dict[str, object]], reach_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = zone_counts(slot_rows)
    status_counts = Counter(row["reachability_status"] for row in reach_rows)
    return [
        {"metric": "input_box_count", "value": len(INPUT_BOX_ORIGINS), "unit": "box", "notes": "Stage 6R frozen requirement"},
        {"metric": "input_slots_per_box", "value": 24, "unit": "slot", "notes": "4 x 6"},
        {"metric": "total_input_slots", "value": counts["input"], "unit": "slot", "notes": "4 input boxes"},
        {"metric": "output_category_count", "value": len(OUTPUT_BOX_ORIGINS), "unit": "category", "notes": "A/B/C/D"},
        {"metric": "output_slots_per_category", "value": 24, "unit": "slot", "notes": "4 x 6 per category"},
        {"metric": "total_output_slots", "value": counts["output"], "unit": "slot", "notes": "4 category output boxes"},
        {"metric": "manual_review_slots", "value": counts["manual_review"], "unit": "slot", "notes": "2 x 3 true abnormal sample bin"},
        {"metric": "scan_station_slots", "value": counts["scan_station"], "unit": "slot", "notes": "single scan holder position"},
        {"metric": "total_task_points", "value": len(slot_rows), "unit": "point", "notes": "input + output + manual review + scan"},
        {"metric": "reachable_points", "value": status_counts["reachable"], "unit": "point", "notes": "inside envelope and not near limit"},
        {"metric": "unreachable_points", "value": status_counts["unreachable"], "unit": "point", "notes": "outside envelope"},
        {"metric": "near_limit_points", "value": status_counts["near_limit"], "unit": "point", "notes": "inside envelope but close to configured limits"},
        {"metric": "selected_base_plate_size", "value": "1200 x 900 x 15", "unit": "mm", "notes": "v7.1 recommended multi-box layout"},
        {"metric": "workspace_assumption_version", "value": "stage_7b_v1", "unit": "id", "notes": "x=[-570,570], y=[-420,420], z=[0,280]"},
    ]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_coordinate_model_doc() -> None:
    COORDINATE_MODEL_MD.write_text(
        "\n".join(
            [
                "# Multi-box Coordinate Model v1",
                "",
                "This coordinate model is based on the validated v7.1 multi-box CadQuery/OCP rough layout.",
                "",
                "## Global Frame",
                "",
                "- Origin: center of the 1200 x 900 x 15 mm base plate.",
                "- +X: left-to-right across the machine, from input side toward output side.",
                "- +Y: rearward along the base plate.",
                "- +Z: upward from the base plate top/robot workspace.",
                "- Units: millimeters.",
                "",
                "## Coordinate Sources",
                "",
                "- Input boxes: `input_box_1..4` from `generate_cadquery_multi_box_layout_v7_1.py`, using origins `(-330,285)`, `(-330,155)`, `(-330,25)`, `(-330,-105)`.",
                "- Output boxes: Category A/B/C/D from v7.1 origins `(160,170)`, `(370,170)`, `(160,-40)`, `(370,-40)`.",
                "- Manual review: v7.1 `manual_review_bin` origin `(-180,-300)`.",
                "- Scan station: v7.1 scan tube holder origin `(-140,60)`.",
                "- Slot pitch: 28 mm, matching the v7.1 4 x 6 rack helper.",
                "",
                "These coordinates are for task planning and reachability checks only. They are not final machining datums and should be updated after final SolidWorks assembly constraints, drawings, gripper pads, and engineered brackets are frozen.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_height_rules_doc() -> None:
    HEIGHT_RULES_MD.write_text(
        "\n".join(
            [
                "# Multi-box Pick/Place Height Rules v1",
                "",
                "| Rule | Value mm | Notes |",
                "|---|---:|---|",
                f"| `safe_z` | {HEIGHT_RULES['safe_z']:.0f} | Safe XY travel height above the tallest 100 mm tube, box rims, and common rough-layout obstacles. |",
                f"| `approach_z` | {HEIGHT_RULES['approach_z']:.0f} | Pre-pick/pre-place approach height before descending. |",
                f"| `grip_z_75mm` | {HEIGHT_RULES['grip_z_75mm']:.0f} | Initial grip height for 75 mm tubes. |",
                f"| `grip_z_100mm` | {HEIGHT_RULES['grip_z_100mm']:.0f} | Initial grip height for 100 mm tubes. |",
                f"| `place_z_75mm` | {HEIGHT_RULES['place_z_75mm']:.0f} | Initial placement height for 75 mm tubes. |",
                f"| `place_z_100mm` | {HEIGHT_RULES['place_z_100mm']:.0f} | Initial placement height for 100 mm tubes. |",
                f"| `scan_z` | {HEIGHT_RULES['scan_z']:.0f} | Recognition posture at the scan station. |",
                "",
                "75 mm and 100 mm tubes need different grip and place heights because the cap/body region presented to the gripper changes with tube length. These values are planning defaults for v7.1; later phases should revise them using the real gripper jaw pads, bracket geometry, and clearance tests.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def plot_slot_map(slot_rows: list[dict[str, object]], reach_rows: list[dict[str, object]]) -> str:
    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
    except Exception as exc:
        return f"matplotlib unavailable: {exc}"

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    status_by_key = {(row["box_id"], row["slot_id"]): row["reachability_status"] for row in reach_rows}
    colors = {
        "input": "#377eb8",
        "output_A": "#7b3294",
        "output_B": "#d8b365",
        "output_C": "#4393c3",
        "output_D": "#d6604d",
        "manual_review": "#666666",
        "scan_station": "#000000",
    }
    markers = {"reachable": "o", "near_limit": "^", "unreachable": "x", "needs_review": "s"}

    fig, ax = plt.subplots(figsize=(11, 8))
    ax.add_patch(Rectangle((-BASE_PLATE_SIZE[0] / 2, -BASE_PLATE_SIZE[1] / 2), BASE_PLATE_SIZE[0], BASE_PLATE_SIZE[1], fill=False, linewidth=1.5, edgecolor="gray", label="1200 x 900 base"))
    ax.add_patch(Rectangle((WORK_ENVELOPE["x_min"], WORK_ENVELOPE["y_min"]), WORK_ENVELOPE["x_max"] - WORK_ENVELOPE["x_min"], WORK_ENVELOPE["y_max"] - WORK_ENVELOPE["y_min"], fill=False, linestyle="--", linewidth=1.5, edgecolor="black", label="planning workspace"))

    for origin in INPUT_BOX_ORIGINS.values():
        ax.add_patch(Rectangle((origin[0] - 90, origin[1] - 60), 180, 120, fill=False, edgecolor=colors["input"], linewidth=1.0))
    for key, origin in OUTPUT_BOX_ORIGINS.items():
        category = key.split("_")[1]
        ax.add_patch(Rectangle((origin[0] - 90, origin[1] - 60), 180, 120, fill=False, edgecolor=colors[f"output_{category}"], linewidth=1.0))
    ax.add_patch(Rectangle((MANUAL_REVIEW_ORIGIN[0] - 45, MANUAL_REVIEW_ORIGIN[1] - 30), 90, 60, fill=False, edgecolor=colors["manual_review"], linewidth=1.0))

    grouped = defaultdict(list)
    for row in slot_rows:
        grouped[row["zone"]].append(row)
    for zone, rows in grouped.items():
        for row in rows:
            status = status_by_key[(row["box_id"], row["slot_id"])]
            ax.scatter(float(row["x_mm"]), float(row["y_mm"]), c=colors.get(zone, "#333333"), marker=markers[status], s=28)

    for label, origin in {**INPUT_BOX_ORIGINS, **OUTPUT_BOX_ORIGINS, "manual_review": MANUAL_REVIEW_ORIGIN, "scan_station": SCAN_STATION_ORIGIN}.items():
        ax.text(origin[0], origin[1] + 70, label, fontsize=8, ha="center")

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-640, 640)
    ax.set_ylim(-480, 480)
    ax.set_xlabel("X mm")
    ax.set_ylabel("Y mm")
    ax.set_title("Stage 7B Multi-box Slot Map Top View")
    ax.grid(True, linewidth=0.3, alpha=0.4)
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=180)
    plt.close(fig)
    return "generated"


def write_report(slot_rows: list[dict[str, object]], reach_rows: list[dict[str, object]], figure_status: str) -> None:
    counts = zone_counts(slot_rows)
    status_counts = Counter(row["reachability_status"] for row in reach_rows)
    by_zone_status = defaultdict(Counter)
    for row in reach_rows:
        by_zone_status[row["zone"]][row["reachability_status"]] += 1
    issues = [row for row in reach_rows if row["reachability_status"] in {"near_limit", "unreachable", "needs_review"}]
    safe_z_ok = HEIGHT_RULES["safe_z"] > 100.0 and HEIGHT_RULES["safe_z"] <= WORK_ENVELOPE["z_max"]

    issue_lines = ["- near_limit / unreachable points: none."] if not issues else ["- near_limit / unreachable points:"]
    for row in issues[:20]:
        issue_lines.append(f"  - {row['zone']} {row['box_id']} {row['slot_id']}: {row['reachability_status']} ({row['notes']})")
    if len(issues) > 20:
        issue_lines.append(f"  - plus {len(issues) - 20} additional point(s), see CSV.")

    zone_lines = []
    for zone in sorted(by_zone_status):
        counts_for_zone = by_zone_status[zone]
        zone_lines.append(f"- {zone}: reachable={counts_for_zone['reachable']}, near_limit={counts_for_zone['near_limit']}, unreachable={counts_for_zone['unreachable']}, needs_review={counts_for_zone['needs_review']}")

    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Stage 7B Multi-box Coordinate Reachability Report",
                "",
                "- Goal: generate the v7.1 multi-box task coordinate model and validate rough gantry reachability.",
                "- Reference files: v7.1 CadQuery generator, v7.1 validation CSV, multi-box architecture, policy, data model, and state machine documents.",
                "- Layout basis: v7.1 recommended multi-box batch layout prototype on a 1200 x 900 x 15 mm base plate.",
                f"- Total task points: {len(slot_rows)}",
                f"- Input slots: {counts['input']}",
                f"- Output slots: {counts['output']}",
                f"- Manual review slots: {counts['manual_review']}",
                f"- Scan station slots: {counts['scan_station']}",
                f"- Workspace assumption: x=[{WORK_ENVELOPE['x_min']:.0f},{WORK_ENVELOPE['x_max']:.0f}], y=[{WORK_ENVELOPE['y_min']:.0f},{WORK_ENVELOPE['y_max']:.0f}], z=[{WORK_ENVELOPE['z_min']:.0f},{WORK_ENVELOPE['z_max']:.0f}] mm; near-limit margin={NEAR_LIMIT_XY_MARGIN_MM:.0f} mm XY / {NEAR_LIMIT_Z_MARGIN_MM:.0f} mm Z.",
                f"- Reachability summary: reachable={status_counts['reachable']}, near_limit={status_counts['near_limit']}, unreachable={status_counts['unreachable']}, needs_review={status_counts['needs_review']}.",
                f"- safe_z reasonable: {'yes' if safe_z_ok else 'no'} (`safe_z={HEIGHT_RULES['safe_z']:.0f} mm`).",
                f"- Top-view figure: {'generated at `' + FIGURE_PATH.relative_to(ROOT).as_posix() + '`' if figure_status == 'generated' else 'not generated; ' + figure_status}",
                "",
                "## Zone Summary",
                "",
                *zone_lines,
                "",
                "## Issues",
                "",
                *issue_lines,
                "",
                "## Limits",
                "",
                "- Coordinates are planning coordinates derived from v7.1 script constants, not final machining datums.",
                "- Future updates should follow final SolidWorks assembly constraints, engineered brackets, gripper pads, and released drawings.",
                "",
                "## Next Steps",
                "",
                "- Stage 7C: multi-box sample manifest and category hold simulation.",
                "- Stage 7D: multi-box trajectory and cycle time update.",
                "- Stage 8: PID / dynamics simulation after multi-box task logic stabilizes.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    write_coordinate_model_doc()
    write_height_rules_doc()

    slot_rows = generate_slot_rows()
    reach_rows = generate_reachability_rows(slot_rows)
    summary = summary_rows(slot_rows, reach_rows)
    figure_status = plot_slot_map(slot_rows, reach_rows)
    write_report(slot_rows, reach_rows, figure_status)

    write_csv(
        SLOT_CSV,
        slot_rows,
        ["zone", "box_id", "rack_name", "slot_id", "row", "col", "x_mm", "y_mm", "z_insert_mm", "z_pick_75mm", "z_pick_100mm", "z_place_75mm", "z_place_100mm", "slot_role", "notes"],
    )
    write_csv(
        REACHABILITY_CSV,
        reach_rows,
        ["zone", "box_id", "rack_name", "slot_id", "x_mm", "y_mm", "z_insert_mm", "z_pick_75mm", "z_pick_100mm", "within_x_range", "within_y_range", "within_z_range_75mm", "within_z_range_100mm", "reachability_status", "near_limit", "notes"],
    )
    write_csv(SUMMARY_CSV, summary, ["metric", "value", "unit", "notes"])

    counts = zone_counts(slot_rows)
    status_counts = Counter(row["reachability_status"] for row in reach_rows)
    print(f"total_task_points={len(slot_rows)}")
    print(f"input_slots={counts['input']}")
    print(f"output_slots={counts['output']}")
    print(f"manual_review_slots={counts['manual_review']}")
    print(f"scan_station_slots={counts['scan_station']}")
    print(f"reachable_points={status_counts['reachable']}")
    print(f"near_limit_points={status_counts['near_limit']}")
    print(f"unreachable_points={status_counts['unreachable']}")
    print(f"figure_status={figure_status}")
    print(f"slot_csv={SLOT_CSV}")
    print(f"reachability_csv={REACHABILITY_CSV}")
    print(f"summary_csv={SUMMARY_CSV}")
    print(f"report={REPORT_PATH}")
    return 0 if status_counts["unreachable"] == 0 and status_counts["needs_review"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
