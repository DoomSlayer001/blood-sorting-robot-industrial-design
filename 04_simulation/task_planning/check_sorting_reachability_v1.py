from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = ROOT / "04_simulation" / "task_planning"
REPORT_DIR = ROOT / "reports"
MANIFEST_PATH = ROOT / "04_simulation" / "sample_data" / "sample_manifest.csv"

RACK_SLOT_CSV = TASK_DIR / "rack_slot_coordinates_v1.csv"
SORTING_SEQUENCE_CSV = TASK_DIR / "sorting_sequence_v1.csv"
REACHABILITY_CSV = TASK_DIR / "reachability_check_v1.csv"
REPORT_PATH = REPORT_DIR / "stage_6a_sorting_task_reachability_report.md"

INPUT_ORIGIN = (-160.0, 300.0)
OUTPUT_ORIGINS = {
    "category_a_bin": (90.0, -160.0),
    "category_b_bin": (250.0, -160.0),
    "category_c_bin": (90.0, -330.0),
    "category_d_bin": (250.0, -330.0),
    "manual_review_bin": (-205.0, -330.0),
}
SCAN_STATION = (-92.0, 170.0)
PITCH_MM = 28.0
Z_INSERT_MM = 25.0

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


def slot_xy(origin: tuple[float, float], rows: int, cols: int, row_index: int, col_index: int) -> tuple[float, float]:
    x0 = -((cols - 1) * PITCH_MM) / 2.0
    y0 = ((rows - 1) * PITCH_MM) / 2.0
    return (origin[0] + x0 + col_index * PITCH_MM, origin[1] + y0 - row_index * PITCH_MM)


def row_letter(index: int) -> str:
    return chr(ord("A") + index)


def generate_slot_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for row in range(4):
        for col in range(6):
            x, y = slot_xy(INPUT_ORIGIN, 4, 6, row, col)
            rows.append(
                {
                    "zone": "input",
                    "rack_name": "input_mixed_tube_rack_4x6",
                    "slot_id": f"{row_letter(row)}{col + 1}",
                    "row": row_letter(row),
                    "col": col + 1,
                    "x_mm": f"{x:.3f}",
                    "y_mm": f"{y:.3f}",
                    "z_insert_mm": f"{Z_INSERT_MM:.3f}",
                    "z_pick_75mm": f"{HEIGHT_RULES['grip_z_75mm']:.3f}",
                    "z_pick_100mm": f"{HEIGHT_RULES['grip_z_100mm']:.3f}",
                    "notes": "v6 input rack origin; 28 mm pitch from custom rack geometry",
                }
            )

    rack_names = {
        "category_a_bin": ("output_A", "category_A_output_bin_2x3"),
        "category_b_bin": ("output_B", "category_B_output_bin_2x3"),
        "category_c_bin": ("output_C", "category_C_output_bin_2x3"),
        "category_d_bin": ("output_D", "category_D_output_bin_2x3"),
        "manual_review_bin": ("manual_review", "manual_review_bin_2x3"),
    }
    for rack_key, origin in OUTPUT_ORIGINS.items():
        zone, rack_name = rack_names[rack_key]
        for row in range(2):
            for col in range(3):
                x, y = slot_xy(origin, 2, 3, row, col)
                rows.append(
                    {
                        "zone": zone,
                        "rack_name": rack_name,
                        "slot_id": f"{row_letter(row)}{col + 1}",
                        "row": row_letter(row),
                        "col": col + 1,
                        "x_mm": f"{x:.3f}",
                        "y_mm": f"{y:.3f}",
                        "z_insert_mm": f"{Z_INSERT_MM:.3f}",
                        "z_pick_75mm": f"{HEIGHT_RULES['place_z_75mm']:.3f}",
                        "z_pick_100mm": f"{HEIGHT_RULES['place_z_100mm']:.3f}",
                        "notes": "v6 output/review bin origin; 28 mm pitch from custom bin geometry",
                    }
                )

    rows.append(
        {
            "zone": "scan_station",
            "rack_name": "scan_station_holder",
            "slot_id": "SCAN1",
            "row": "A",
            "col": 1,
            "x_mm": f"{SCAN_STATION[0]:.3f}",
            "y_mm": f"{SCAN_STATION[1]:.3f}",
            "z_insert_mm": f"{Z_INSERT_MM:.3f}",
            "z_pick_75mm": f"{HEIGHT_RULES['scan_z']:.3f}",
            "z_pick_100mm": f"{HEIGHT_RULES['scan_z']:.3f}",
            "notes": "v6 scan station tube center; scan_z used for handling",
        }
    )
    return rows


def read_manifest() -> list[dict[str, str]]:
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def bin_capacity_map() -> dict[str, int]:
    return {key: 6 for key in OUTPUT_ORIGINS}


def target_zone_for(row: dict[str, str], used_counts: dict[str, int]) -> tuple[str, str, str]:
    requested_bin = row["target_bin"]
    if row["scan_status"] != "success":
        requested_bin = "manual_review_bin"
        reason = "scan fail routes to manual review"
    elif row["category"].strip().lower() == "unknown":
        requested_bin = "manual_review_bin"
        reason = "unknown category routes to manual review"
    else:
        reason = "normal category route"

    capacities = bin_capacity_map()
    if used_counts[requested_bin] >= capacities[requested_bin]:
        requested_bin = "manual_review_bin"
        reason = "target output full routes to manual review"

    if used_counts[requested_bin] >= capacities[requested_bin]:
        return ("PAUSE_ALARM", "", "manual review full; pause for operator action")

    used_counts[requested_bin] += 1
    slot_index = used_counts[requested_bin] - 1
    target_slot = f"{row_letter(slot_index // 3)}{slot_index % 3 + 1}"
    return (requested_bin, target_slot, reason)


def generate_sorting_sequence(manifest_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    used_counts: dict[str, int] = defaultdict(int)
    rows: list[dict[str, object]] = []
    for step, sample in enumerate(manifest_rows, start=1):
        target_zone, target_slot, reason = target_zone_for(sample, used_counts)
        input_slot = f"{sample['input_row']}{sample['input_col']}"
        if target_zone == "PAUSE_ALARM":
            action_sequence = "LOAD_SAMPLE_MANIFEST > MOVE_TO_INPUT_SLOT > PAUSE_ALARM"
            failure = "manual_review_full"
        elif target_zone == "manual_review_bin":
            action_sequence = "MOVE_TO_INPUT_SLOT > PICK_TUBE > LIFT_TO_SAFE_Z > MOVE_TO_SCAN_STATION > SCAN_BARCODE > MOVE_TO_MANUAL_REVIEW > PLACE_TUBE"
            failure = reason
        else:
            action_sequence = "MOVE_TO_INPUT_SLOT > PICK_TUBE > LIFT_TO_SAFE_Z > MOVE_TO_SCAN_STATION > SCAN_BARCODE > CLASSIFY_SAMPLE > MOVE_TO_OUTPUT_SLOT > PLACE_TUBE"
            failure = ""
        rows.append(
            {
                "step_id": step,
                "sample_id": sample["tube_id"],
                "input_slot": input_slot,
                "tube_height_mm": sample["height_mm"],
                "barcode_status": sample["scan_status"],
                "category": sample["category"],
                "target_zone": target_zone,
                "target_slot": target_slot,
                "action_sequence": action_sequence,
                "failure_handling": failure,
                "notes": f"{reason}; manifest target={sample['target_bin']} {sample['target_row']}{sample['target_col']}",
            }
        )
    return rows


def reachable_xy(x: float, y: float) -> bool:
    return WORK_ENVELOPE["x_min"] <= x <= WORK_ENVELOPE["x_max"] and WORK_ENVELOPE["y_min"] <= y <= WORK_ENVELOPE["y_max"]


def reachable_z(*z_values: float) -> bool:
    return all(WORK_ENVELOPE["z_min"] <= z <= WORK_ENVELOPE["z_max"] for z in z_values)


def generate_reachability_rows(slot_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for slot in slot_rows:
        x = float(slot["x_mm"])
        y = float(slot["y_mm"])
        z_values = [float(slot["z_insert_mm"]), float(slot["z_pick_75mm"]), float(slot["z_pick_100mm"]), HEIGHT_RULES["safe_z"], HEIGHT_RULES["approach_z"]]
        xy_ok = reachable_xy(x, y)
        z_ok = reachable_z(*z_values)
        notes = []
        if not xy_ok:
            notes.append("XY outside initial work envelope")
        if not z_ok:
            notes.append("one or more Z heights outside initial work envelope")
        rows.append(
            {
                "zone": slot["zone"],
                "rack_name": slot["rack_name"],
                "slot_id": slot["slot_id"],
                "x_mm": slot["x_mm"],
                "y_mm": slot["y_mm"],
                "z_insert_mm": slot["z_insert_mm"],
                "safe_z_mm": f"{HEIGHT_RULES['safe_z']:.3f}",
                "approach_z_mm": f"{HEIGHT_RULES['approach_z']:.3f}",
                "reachable_xy": "yes" if xy_ok else "no",
                "reachable_z": "yes" if z_ok else "no",
                "overall_status": "reachable" if xy_ok and z_ok else "out_of_range",
                "notes": "; ".join(notes) if notes else "within initial Stage 6A envelope",
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_report(slot_rows: list[dict[str, object]], reach_rows: list[dict[str, object]], sequence_rows: list[dict[str, object]]) -> None:
    total = len(slot_rows)
    reachable = sum(1 for row in reach_rows if row["overall_status"] == "reachable")
    unreachable = total - reachable
    scan_rows = [row for row in reach_rows if row["zone"] == "scan_station"]
    safe_z_ok = HEIGHT_RULES["safe_z"] > 100.0 and HEIGHT_RULES["safe_z"] <= WORK_ENVELOPE["z_max"]
    issues = [row for row in reach_rows if row["overall_status"] != "reachable"]

    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Stage 6A Sorting Task Reachability Report",
                "",
                f"- Total slot/check points: {total}",
                f"- Reachable points: {reachable}",
                f"- Unreachable points: {unreachable}",
                f"- Sorting sequence samples: {len(sequence_rows)}",
                f"- Scan station reachable: {'yes' if scan_rows and scan_rows[0]['overall_status'] == 'reachable' else 'no'}",
                f"- safe_z reasonable: {'yes' if safe_z_ok else 'no'} (`safe_z={HEIGHT_RULES['safe_z']:.0f} mm`, max tube height=100 mm, z_max={WORK_ENVELOPE['z_max']:.0f} mm)",
                f"- Current issues: {'none found in initial envelope' if not issues else str(len(issues)) + ' out-of-range point(s)'}",
                "- Next step: use these coordinates to build a motion sequence simulator and refine heights with real gripper clearances.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    slot_rows = generate_slot_rows()
    manifest_rows = read_manifest()
    sequence_rows = generate_sorting_sequence(manifest_rows)
    reach_rows = generate_reachability_rows(slot_rows)

    write_csv(
        RACK_SLOT_CSV,
        slot_rows,
        ["zone", "rack_name", "slot_id", "row", "col", "x_mm", "y_mm", "z_insert_mm", "z_pick_75mm", "z_pick_100mm", "notes"],
    )
    write_csv(
        SORTING_SEQUENCE_CSV,
        sequence_rows,
        ["step_id", "sample_id", "input_slot", "tube_height_mm", "barcode_status", "category", "target_zone", "target_slot", "action_sequence", "failure_handling", "notes"],
    )
    write_csv(
        REACHABILITY_CSV,
        reach_rows,
        ["zone", "rack_name", "slot_id", "x_mm", "y_mm", "z_insert_mm", "safe_z_mm", "approach_z_mm", "reachable_xy", "reachable_z", "overall_status", "notes"],
    )
    write_report(slot_rows, reach_rows, sequence_rows)

    unreachable = sum(1 for row in reach_rows if row["overall_status"] != "reachable")
    print(f"rack_slot_count={len(slot_rows)}")
    print(f"sorting_sequence_count={len(sequence_rows)}")
    print(f"reachable_count={len(reach_rows) - unreachable}")
    print(f"unreachable_count={unreachable}")
    print(f"scan_station_reachable={next(row['overall_status'] for row in reach_rows if row['zone'] == 'scan_station')}")
    print(f"safe_z_ok={HEIGHT_RULES['safe_z'] > 100.0 and HEIGHT_RULES['safe_z'] <= WORK_ENVELOPE['z_max']}")
    print(f"reachability_csv={REACHABILITY_CSV}")
    print(f"report={REPORT_PATH}")
    return 0 if unreachable == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
