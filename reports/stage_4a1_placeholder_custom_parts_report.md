# Stage 4A-1 Placeholder Custom Parts Report

## 1. Stage Goal

Stage 4A-1 fills the four missing rough-assembly components identified in the Stage 4A CAD inventory: base plate, scan-station reference block, control box placeholder, and Y-axis synchronization placeholder.

## 2. Why These Models Were Added

The Stage 4B SolidWorks rough assembly macro will read component paths from CSV tables. Leaving these components as `TBD` would make the first rough assembly incomplete and harder to review. These simple STEP files provide physical envelopes and reference geometry without pretending to be final manufactured parts.

## 3. Generated STEP Files

| component | STEP file |
|---|---|
| base plate | `03_cad/custom_parts/base_plate/base_plate_1100x900x15.step` |
| scan station reference | `03_cad/custom_parts/scan_station/scan_station_reference_block.step` |
| control box placeholder | `03_cad/custom_parts/control_box/control_box_placeholder_160x120x80.step` |
| Y-axis sync placeholder | `03_cad/custom_parts/y_axis_sync_mechanism/y_axis_sync_shaft_placeholder.step` |

## 4. Dimensions And Use

| component | dimensions | purpose |
|---|---:|---|
| base plate | 1100 x 900 x 15 mm | rough assembly datum and equipment footprint |
| scan station reference block | 120 x 80 x 20 mm | temporary scan station reference position |
| control box placeholder | 160 x 120 x 80 mm | control box envelope reservation |
| Y-axis sync shaft placeholder | 720 mm long, 14 mm diameter | visual relation between left and right Y-axis synchronization |

## 5. Placeholder Status

- The base plate is an initial custom part design with no mounting holes and is not a final production drawing.
- The scan-station reference block is only a datum/envelope placeholder.
- The control box is only an external envelope placeholder.
- The Y-axis synchronization shaft is only a mechanical relationship placeholder and does not define the final transmission design.

## 6. Effect On SolidWorks Rough Assembly

`current_cad_inventory_for_assembly.csv` and `component_placement_table_v1.csv` now reference these STEP files directly. Stage 4B can insert the parts instead of skipping missing components or using empty coordinates.

## 7. Current Limitations

- Base plate has no installation holes.
- Control box has no internal controller, power supply, wiring, or connector detail.
- Scan station block does not replace scanner or photoelectric sensor brackets.
- Y-axis sync placeholder is not a final shaft, belt, pulley, coupling, or dual-motor design.

## 8. Next Stage

Stage 4B should generate the rough assembly macro using the updated CAD inventory and placement table.
