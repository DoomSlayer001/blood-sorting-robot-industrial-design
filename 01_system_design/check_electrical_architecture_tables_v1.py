from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent

TABLES = {
    "components": {
        "path": ROOT / "electrical_component_list_v1.csv",
        "id": "component_id",
        "fields": [
            "component_id",
            "component_name",
            "category",
            "function",
            "location_zone",
            "mounted_in_control_box",
            "requires_moving_cable",
            "voltage_level",
            "signal_type",
            "notes",
        ],
    },
    "io": {
        "path": ROOT / "electrical_io_map_v1.csv",
        "id": "io_id",
        "fields": [
            "io_id",
            "device",
            "signal_name",
            "direction",
            "signal_type",
            "voltage_level",
            "normal_state",
            "safety_related",
            "moving_or_fixed",
            "notes",
        ],
    },
    "wiring": {
        "path": ROOT / "electrical_wiring_interface_table_v1.csv",
        "id": "cable_id",
        "fields": [
            "cable_id",
            "source_module",
            "target_module",
            "signal_type",
            "voltage_level",
            "moving_or_fixed",
            "suggested_route",
            "connector_side",
            "requires_cable_chain",
            "estimated_cable_group",
            "notes",
        ],
    },
}


def read_table(spec: dict[str, object]) -> list[dict[str, str]]:
    path = spec["path"]
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [field for field in spec["fields"] if field not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path.name}: missing fields {missing}")
        rows = list(reader)
    ids = [row[spec["id"]] for row in rows]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        raise ValueError(f"{path.name}: duplicate ids {duplicates}")
    return rows


def require_values(rows: list[dict[str, str]], field: str, allowed: set[str], table_name: str) -> None:
    bad = sorted({row[field] for row in rows if row[field] not in allowed})
    if bad:
        raise ValueError(f"{table_name}: invalid {field} values {bad}")


def main() -> int:
    components = read_table(TABLES["components"])
    io_rows = read_table(TABLES["io"])
    wiring = read_table(TABLES["wiring"])

    require_values(io_rows, "moving_or_fixed", {"fixed", "moving"}, "electrical_io_map_v1.csv")
    require_values(io_rows, "safety_related", {"yes", "no"}, "electrical_io_map_v1.csv")
    require_values(wiring, "moving_or_fixed", {"fixed", "moving"}, "electrical_wiring_interface_table_v1.csv")
    require_values(wiring, "requires_cable_chain", {"yes", "no"}, "electrical_wiring_interface_table_v1.csv")

    print(f"electrical_components={len(components)}")
    print(f"io_points={len(io_rows)}")
    print(f"wiring_interfaces={len(wiring)}")
    print(f"fixed_cables={sum(row['moving_or_fixed'] == 'fixed' for row in wiring)}")
    print(f"cable_chain_cables={sum(row['requires_cable_chain'] == 'yes' for row in wiring)}")
    print(f"safety_related_signals={sum(row['safety_related'] == 'yes' for row in io_rows)}")
    print("validation_status=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
