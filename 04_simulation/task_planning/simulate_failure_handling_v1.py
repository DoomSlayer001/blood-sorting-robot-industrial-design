from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = ROOT / "04_simulation" / "task_planning"
REPORT_DIR = ROOT / "reports"
FIGURE_DIR = TASK_DIR / "figures"

SORTING_SEQUENCE_CSV = TASK_DIR / "sorting_sequence_v1.csv"
RACK_SLOT_CSV = TASK_DIR / "rack_slot_coordinates_v1.csv"
TRAJECTORY_CSV = TASK_DIR / "pick_scan_place_trajectory_v1.csv"
CYCLE_TIME_CSV = TASK_DIR / "cycle_time_estimate_v1.csv"
BATCH_SUMMARY_CSV = TASK_DIR / "batch_throughput_summary_v1.csv"
FAILURE_LOGIC_DOC = ROOT / "01_system_design" / "failure_handling_logic.md"
STATE_MACHINE_DOC = TASK_DIR / "sorting_state_machine_v1.md"
SCENARIO_CSV = TASK_DIR / "failure_scenarios_v1.csv"

SIMULATION_CSV = TASK_DIR / "failure_handling_simulation_v1.csv"
BIN_OCCUPANCY_CSV = TASK_DIR / "bin_occupancy_after_failure_sim_v1.csv"
ALARM_EVENTS_CSV = TASK_DIR / "alarm_events_v1.csv"
SUMMARY_CSV = TASK_DIR / "failure_handling_summary_v1.csv"
FAILURE_COUNTS_FIGURE = FIGURE_DIR / "failure_type_counts_v1.png"
BIN_OCCUPANCY_FIGURE = FIGURE_DIR / "bin_occupancy_summary_v1.png"
REPORT_PATH = REPORT_DIR / "stage_6d_failure_handling_simulation_report.md"

BIN_CAPACITY = {
    "category_a_bin": 6,
    "category_b_bin": 6,
    "category_c_bin": 6,
    "category_d_bin": 6,
    "manual_review_bin": 6,
}

CATEGORY_TO_BIN = {
    "Category A": "category_a_bin",
    "Category B": "category_b_bin",
    "Category C": "category_c_bin",
    "Category D": "category_d_bin",
}

BIN_LABELS = {
    "category_a_bin": "Category A",
    "category_b_bin": "Category B",
    "category_c_bin": "Category C",
    "category_d_bin": "Category D",
    "manual_review_bin": "Manual review",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def slot_ids() -> list[str]:
    return [f"{row}{col}" for row in ["A", "B"] for col in range(1, 4)]


def next_slot(occupancy: dict[str, list[str]], zone: str) -> str | None:
    slots = slot_ids()
    used = set(occupancy[zone])
    for slot in slots:
        if slot not in used:
            return slot
    return None


def occupy(occupancy: dict[str, list[str]], zone: str, slot: str) -> None:
    if slot and slot not in occupancy[zone]:
        occupancy[zone].append(slot)


def initial_occupancy(scenario_id: str) -> tuple[dict[str, list[str]], dict[str, int], list[str]]:
    occupancy = {zone: [] for zone in BIN_CAPACITY}
    capacities = dict(BIN_CAPACITY)
    notes: list[str] = []
    if scenario_id == "forced_output_full":
        occupancy["category_a_bin"] = slot_ids()[:5]
        notes.append("preloaded category_a_bin with five occupied slots")
    if scenario_id == "forced_manual_review_full":
        capacities["manual_review_bin"] = 1
        notes.append("manual_review_bin capacity limited to one slot")
    return occupancy, capacities, notes


def enabled_scenarios() -> list[dict[str, str]]:
    return [row for row in read_csv(SCENARIO_CSV) if row["enabled"].strip().lower() == "yes"]


def manifest_failure_type(row: dict[str, str]) -> str:
    if row["barcode_status"] == "fail":
        return "scan_failed"
    if row["category"].strip().lower() == "unknown":
        return "unknown_category"
    return "none"


def allocate_manual_review(
    run_id: str,
    sample_id: str,
    failure_type: str,
    occupancy: dict[str, list[str]],
    capacities: dict[str, int],
    alarm_rows: list[dict[str, object]],
    notes: str,
) -> tuple[str, str, str, str, str, bool]:
    if len(occupancy["manual_review_bin"]) >= capacities["manual_review_bin"]:
        alarm_rows.append(
            {
                "run_id": run_id,
                "event_id": f"{run_id}_ALARM_{len(alarm_rows) + 1:03d}",
                "sample_id": sample_id,
                "alarm_type": "manual_review_bin_full",
                "trigger_state": "PAUSE_ALARM",
                "reason": f"{failure_type} requires manual review but no slot is available",
                "recommended_operator_action": "Clear manual review bin and resume after operator confirmation.",
                "notes": notes,
            }
        )
        return ("manual_review_bin", "", "PAUSE_ALARM", "PAUSE_ALARM", "manual review full", True)
    slot = next_slot(occupancy, "manual_review_bin")
    if slot is None:
        return allocate_manual_review(run_id, sample_id, failure_type, occupancy, {"manual_review_bin": 0}, alarm_rows, notes)
    occupy(occupancy, "manual_review_bin", slot)
    return ("manual_review_bin", slot, "MOVE_TO_MANUAL_REVIEW", "ROUTE_TO_MANUAL_REVIEW", notes, False)


def injected_failure_for(scenario: dict[str, str], sample_id: str) -> str | None:
    failure_type = scenario["failure_type"]
    if scenario["sample_id"] == sample_id and failure_type in {"gripper_pick_failed", "gripper_place_failed"}:
        return failure_type
    return None


def simulate_run(
    scenario: dict[str, str],
    sequence_rows: list[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], Counter]:
    run_id = scenario["scenario_id"]
    occupancy, capacities, setup_notes = initial_occupancy(run_id)
    result_rows: list[dict[str, object]] = []
    alarm_rows: list[dict[str, object]] = []
    failure_counts: Counter = Counter()

    for sample in sequence_rows:
        sample_id = sample["sample_id"]
        initial_target = sample["target_zone"]
        failure_type = manifest_failure_type(sample)
        handling_action = "NORMAL_SORT"
        system_state = "COMPLETE_SAMPLE"
        alarm_triggered = False
        notes = "; ".join(setup_notes) if setup_notes else "baseline capacity"

        injected = injected_failure_for(scenario, sample_id)
        if injected:
            failure_type = injected
            alarm_rows.append(
                {
                    "run_id": run_id,
                    "event_id": f"{run_id}_ALARM_{len(alarm_rows) + 1:03d}",
                    "sample_id": sample_id,
                    "alarm_type": injected,
                    "trigger_state": "PAUSE_ALARM",
                    "reason": f"injected {injected} at {scenario['failure_step']}",
                    "recommended_operator_action": "Inspect gripper/tube, clear fault, and resume from safe state.",
                    "notes": scenario["notes"],
                }
            )
            final_zone = "manual_review_bin"
            final_slot = ""
            handling_action = "PAUSE_ALARM"
            system_state = "PAUSE_ALARM"
            alarm_triggered = True
            notes = "conservative v1 policy pauses on gripper pick/place failure"
            failure_counts[injected] += 1
        elif failure_type in {"scan_failed", "unknown_category"}:
            final_zone, final_slot, system_state, handling_action, extra_note, alarm_triggered = allocate_manual_review(
                run_id, sample_id, failure_type, occupancy, capacities, alarm_rows, "manifest exception routed to review"
            )
            notes = extra_note
            failure_counts[failure_type] += 1
            if sample["category"].strip().lower() == "unknown" and failure_type != "unknown_category":
                failure_counts["unknown_category"] += 1
        else:
            final_zone = CATEGORY_TO_BIN.get(sample["category"], "manual_review_bin")
            if len(occupancy[final_zone]) >= capacities[final_zone]:
                failure_type = "target_bin_full"
                failure_counts[failure_type] += 1
                final_zone, final_slot, system_state, handling_action, extra_note, alarm_triggered = allocate_manual_review(
                    run_id, sample_id, failure_type, occupancy, capacities, alarm_rows, f"{final_zone} full; rerouted to review"
                )
                notes = extra_note
            else:
                final_slot = next_slot(occupancy, final_zone)
                if final_slot is None:
                    failure_type = "target_bin_full"
                    failure_counts[failure_type] += 1
                    final_zone, final_slot, system_state, handling_action, notes, alarm_triggered = allocate_manual_review(
                        run_id, sample_id, failure_type, occupancy, capacities, alarm_rows, "no category slot available"
                    )
                else:
                    occupy(occupancy, final_zone, final_slot)

        if failure_type == "none":
            failure_counts["normal"] += 1
        if alarm_triggered and any(row["alarm_type"] == "manual_review_bin_full" for row in alarm_rows if row["sample_id"] == sample_id):
            failure_counts["manual_review_bin_full"] += 1

        result_rows.append(
            {
                "run_id": run_id,
                "sample_id": sample_id,
                "input_slot": sample["input_slot"],
                "barcode_status": sample["barcode_status"],
                "category": sample["category"],
                "initial_target_zone": initial_target,
                "failure_type": failure_type,
                "final_target_zone": final_zone,
                "final_target_slot": final_slot,
                "handling_action": handling_action,
                "system_state": system_state,
                "alarm_triggered": "yes" if alarm_triggered else "no",
                "notes": notes,
            }
        )

    occupancy_rows = []
    for zone, capacity in capacities.items():
        for index, slot in enumerate(slot_ids(), start=1):
            occupied = slot in occupancy[zone]
            preloaded = zone == "category_a_bin" and run_id == "forced_output_full" and index <= 5
            if index > capacity:
                status = "disabled_by_scenario"
            elif occupied:
                status = "preoccupied" if preloaded else "occupied"
            else:
                status = "empty"
            sample_id = ""
            if occupied and not preloaded:
                for result in result_rows:
                    if result["final_target_zone"] == zone and result["final_target_slot"] == slot:
                        sample_id = str(result["sample_id"])
                        break
            occupancy_rows.append(
                {
                    "run_id": run_id,
                    "zone": zone,
                    "slot_id": slot,
                    "occupied_by_sample_id": "PRELOADED" if preloaded else sample_id,
                    "status": status,
                    "notes": f"capacity={capacity}; {BIN_LABELS[zone]}",
                }
            )
    return result_rows, occupancy_rows, alarm_rows, failure_counts


def build_summary(all_results: list[dict[str, object]], all_alarms: list[dict[str, object]], scenario_counts: dict[str, Counter]) -> list[dict[str, object]]:
    baseline = [row for row in all_results if row["run_id"] == "baseline_manifest_failures"]
    all_counts = Counter()
    for counts in scenario_counts.values():
        all_counts.update(counts)
    baseline_alarm = any(row["run_id"] == "baseline_manifest_failures" for row in all_alarms)
    rows = [
        ("total_samples", len(baseline), "samples", "baseline manifest sample count"),
        ("normal_completed", sum(1 for row in baseline if row["failure_type"] == "none"), "samples", "baseline samples sorted to category bins"),
        ("scan_failed_count", all_counts["scan_failed"], "events", "all enabled runs"),
        ("unknown_category_count", all_counts["unknown_category"], "events", "all enabled runs"),
        ("target_bin_full_count", all_counts["target_bin_full"], "events", "all enabled runs"),
        ("manual_review_used_count", sum(1 for row in all_results if row["final_target_zone"] == "manual_review_bin" and row["system_state"] != "PAUSE_ALARM"), "samples", "all enabled runs"),
        ("manual_review_full_count", all_counts["manual_review_bin_full"], "events", "all enabled runs"),
        ("pick_failed_count", all_counts["gripper_pick_failed"], "events", "injected scenario count"),
        ("place_failed_count", all_counts["gripper_place_failed"], "events", "injected scenario count"),
        ("alarm_count", len(all_alarms), "events", "all enabled runs"),
        ("paused_runs", len({row["run_id"] for row in all_alarms}), "runs", "runs with PAUSE_ALARM"),
        ("baseline_run_status", "PASS_NO_ALARM" if not baseline_alarm else "PAUSE_ALARM", "status", "baseline manifest exceptions route to manual review"),
    ]
    return [{"metric": metric, "value": value, "unit": unit, "notes": notes} for metric, value, unit, notes in rows]


def make_figures(summary_rows: list[dict[str, object]], occupancy_rows: list[dict[str, object]]) -> tuple[bool, list[str], str]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        return False, [], f"matplotlib unavailable: {type(exc).__name__}: {exc}"

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    metrics = {row["metric"]: row["value"] for row in summary_rows}
    failure_metrics = [
        ("scan_failed", int(metrics["scan_failed_count"])),
        ("unknown_category", int(metrics["unknown_category_count"])),
        ("target_bin_full", int(metrics["target_bin_full_count"])),
        ("manual_review_full", int(metrics["manual_review_full_count"])),
        ("pick_failed", int(metrics["pick_failed_count"])),
        ("place_failed", int(metrics["place_failed_count"])),
    ]
    labels, values = zip(*failure_metrics)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(labels, values, color="#c0392b")
    ax.set_title("Stage 6D Failure Type Counts")
    ax.set_ylabel("Event count across enabled runs")
    ax.tick_params(axis="x", rotation=30)
    ax.grid(axis="y", linestyle=":", linewidth=0.7)
    fig.tight_layout()
    fig.savefig(FAILURE_COUNTS_FIGURE, dpi=180)
    plt.close(fig)

    baseline_occ = [row for row in occupancy_rows if row["run_id"] == "baseline_manifest_failures"]
    occupied_counts = Counter(row["zone"] for row in baseline_occ if row["status"] == "occupied")
    zones = list(BIN_CAPACITY)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([BIN_LABELS[zone] for zone in zones], [occupied_counts[zone] for zone in zones], color="#2c7fb8")
    ax.set_title("Stage 6D Baseline Bin Occupancy")
    ax.set_ylabel("Occupied slots")
    ax.set_ylim(0, 6)
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", linestyle=":", linewidth=0.7)
    fig.tight_layout()
    fig.savefig(BIN_OCCUPANCY_FIGURE, dpi=180)
    plt.close(fig)

    return True, [FAILURE_COUNTS_FIGURE.relative_to(ROOT).as_posix(), BIN_OCCUPANCY_FIGURE.relative_to(ROOT).as_posix()], "generated"


def write_report(summary_rows: list[dict[str, object]], figure_result: tuple[bool, list[str], str]) -> None:
    metrics = {row["metric"]: row["value"] for row in summary_rows}
    figure_ok, figure_paths, figure_note = figure_result
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# Stage 6D Failure Handling Simulation Report",
                "",
                "## Inputs",
                "",
                f"- `{SORTING_SEQUENCE_CSV.relative_to(ROOT).as_posix()}`",
                f"- `{RACK_SLOT_CSV.relative_to(ROOT).as_posix()}`",
                f"- `{TRAJECTORY_CSV.relative_to(ROOT).as_posix()}`",
                f"- `{CYCLE_TIME_CSV.relative_to(ROOT).as_posix()}`",
                f"- `{BATCH_SUMMARY_CSV.relative_to(ROOT).as_posix()}`",
                f"- `{FAILURE_LOGIC_DOC.relative_to(ROOT).as_posix()}`",
                f"- `{STATE_MACHINE_DOC.relative_to(ROOT).as_posix()}`",
                "",
                "## Results",
                "",
                "- Covered exception types: scan_failed, unknown_category, target_bin_full, manual_review_bin_full, gripper_pick_failed, gripper_place_failed.",
                f"- Baseline manifest status: {metrics['baseline_run_status']}",
                f"- Baseline normal completed: {metrics['normal_completed']} / {metrics['total_samples']}",
                f"- Manual review used count across enabled runs: {metrics['manual_review_used_count']}",
                f"- Alarm count: {metrics['alarm_count']}; paused runs: {metrics['paused_runs']}",
                f"- Target bin full events: {metrics['target_bin_full_count']} route to manual review when review space is available.",
                f"- Manual review full events: {metrics['manual_review_full_count']} trigger PAUSE_ALARM.",
                f"- Injected pick/place failures trigger PAUSE_ALARM under the conservative v1 policy.",
                f"- Figures: {', '.join(figure_paths) if figure_ok else figure_note}",
                "",
                "## Limits",
                "",
                "- This is a discrete logic simulation; it does not replay controller timing, retry loops, or sensor debounce.",
                "- Pick/place failure recovery is intentionally conservative and pauses for operator inspection.",
                "",
                "## Next",
                "",
                "- 6E: action animation / sorting flow visualization.",
                "- 6F: control-system interface and pseudocode.",
                "- 6G: final report / PPT summary.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    sequence_rows = read_csv(SORTING_SEQUENCE_CSV)
    all_results: list[dict[str, object]] = []
    all_occupancy: list[dict[str, object]] = []
    all_alarms: list[dict[str, object]] = []
    scenario_counts: dict[str, Counter] = {}

    for scenario in enabled_scenarios():
        result_rows, occupancy_rows, alarm_rows, failure_counts = simulate_run(scenario, sequence_rows)
        all_results.extend(result_rows)
        all_occupancy.extend(occupancy_rows)
        all_alarms.extend(alarm_rows)
        scenario_counts[scenario["scenario_id"]] = failure_counts

    summary_rows = build_summary(all_results, all_alarms, scenario_counts)
    figure_result = make_figures(summary_rows, all_occupancy)

    write_csv(
        SIMULATION_CSV,
        all_results,
        ["run_id", "sample_id", "input_slot", "barcode_status", "category", "initial_target_zone", "failure_type", "final_target_zone", "final_target_slot", "handling_action", "system_state", "alarm_triggered", "notes"],
    )
    write_csv(BIN_OCCUPANCY_CSV, all_occupancy, ["run_id", "zone", "slot_id", "occupied_by_sample_id", "status", "notes"])
    write_csv(ALARM_EVENTS_CSV, all_alarms, ["run_id", "event_id", "sample_id", "alarm_type", "trigger_state", "reason", "recommended_operator_action", "notes"])
    write_csv(SUMMARY_CSV, summary_rows, ["metric", "value", "unit", "notes"])
    write_report(summary_rows, figure_result)

    metrics = {row["metric"]: row["value"] for row in summary_rows}
    failure_counts = {row["metric"]: row["value"] for row in summary_rows if row["metric"].endswith("_count")}
    print(f"baseline_run_status={metrics['baseline_run_status']}")
    print(f"alarm_count={metrics['alarm_count']}")
    print(f"manual_review_used_count={metrics['manual_review_used_count']}")
    print(f"failure_type_counts={failure_counts}")
    print(f"figures={';'.join(figure_result[1]) if figure_result[0] else figure_result[2]}")
    print(f"report={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
