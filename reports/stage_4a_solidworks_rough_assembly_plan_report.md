# Stage 4A SolidWorks Rough Assembly Plan Report

## 1. Stage Goal

Stage 4A prepares the first SolidWorks rough assembly plan. It does not create the final assembly and does not generate new CAD. The purpose is to make the next SolidWorks step controlled, repeatable, and reviewable.

## 2. Why Not Direct Final Assembly

The available CAD includes real supplier STEP files, simplified custom STEP files, a visual emergency-stop placeholder, and several missing custom interface parts. Automatic final mates would risk incorrect face selection, wrong mounting-hole assumptions, and misleading alignment. A coordinate-based Level 2 rough assembly is safer for the first pass.

## 3. Current CAD Inventory Summary

The inventory is recorded in:

```text
03_cad/solidworks/current_cad_inventory_for_assembly.csv
```

Summary:

- normalized standard-part CAD is available for MSA-628 X/Y modules, LS10 Z module, AZM46AK motor, LEHF20 gripper, D4N limit switch, CX-421-J sensor, DataMan 80 scanner, and MHPKS204 cable carrier.
- emergency stop is a visual placeholder only.
- custom/scenario STEP files are available for sample tubes and tube bins.
- base plate, scan-station reference block, control box placeholder, and Y-axis sync mechanism are not generated as CAD in Stage 4A.

## 4. First Rough Assembly Strategy

- Use `component_placement_table_v1.csv` for coordinate placement.
- Insert components and temporarily fix them.
- Do not create complex mates in the first pass.
- Do not auto-select faces or holes.
- Use manual review to correct orientation and spacing before bracket design.

## 5. Coordinate System

- Base plate: 1100 mm x 900 mm x 15 mm.
- Origin: base top surface center.
- X range: -550 mm to +550 mm.
- Y range: -450 mm to +450 mm.
- Z positive upward.
- Base plate rough center: `(0, 0, -7.5)`.

## 6. Initial Placement Summary

| component | approximate position |
|---|---|
| left Y module | `(-360, 0, 35)` |
| right Y module | `(360, 0, 35)` |
| X module on gantry | `(0, 0, 260)` |
| Z module | `(0, 0, 220)` |
| gripper | `(0, 0, 120)` |
| input rack | `(-250, 250, 17.5)` |
| scan station | `(80, 80, 40)` |
| output bin group | around `(180,-170)`, `(320,-170)`, `(180,-290)`, `(320,-290)` |
| manual review bin | `(-250, -300, 17.5)` |
| scanner | `(80, 160, 80)` |
| photoelectric sensor | `(20, 80, 60)` |

These are planning coordinates, not final mounting holes.

## 7. SolidWorks Macro Plan

The macro plan is documented in:

```text
03_cad/solidworks/solidworks_first_rough_assembly_macro_plan.md
```

The future macro should read the placement table, insert CAD files, apply rough transforms, and fix components for manual review.

## 8. Manual Check Focus

Manual review must check:

- left/right Y-axis parallelism and spacing.
- X-axis span across Y axes.
- Z-axis and gripper downward orientation.
- rack/bin reachability.
- scanner line-of-sight to tube labels.
- photoelectric sensor trigger alignment.
- cable chain sweep envelope.
- emergency stop accessibility.

## 9. Custom Part Dependency Plan

The dependency plan is recorded in:

```text
03_cad/custom_parts/custom_part_dependency_plan_v1.md
```

Priority A focuses on base plate, Y-axis mounting, gantry supports, X/Z/gripper adapter plates, soft pads, scanner/sensor brackets, and limit switch brackets.

## 10. Next Stages

- 4B: generate rough assembly macro.
- 4C: run SolidWorks rough assembly.
- 4D: revise layout from screenshots and manual checks.
- 4E: generate key custom-part STEP files.
