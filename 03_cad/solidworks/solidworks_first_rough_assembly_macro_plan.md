# SolidWorks First Rough Assembly Macro Plan

## 1. Macro Goal

The first rough assembly macro is intended to create a Level 2 engineering layout assembly for manual inspection.

The macro should:

- create a new SolidWorks assembly.
- insert base, standard parts, custom parts, and scenario parts.
- read `03_cad/solidworks/component_placement_table_v1.csv`.
- place components by approximate X/Y/Z coordinates and Euler rotations.
- temporarily fix inserted components.
- avoid complex automatic mates in the first version.
- save a rough layout assembly for manual review.

## 2. Macro Principles

- Version 1 only performs coordinate placement.
- Do not automatically identify mounting faces.
- Do not automatically select screw holes or hole patterns.
- Do not create complex mates.
- Do not infer final installation surfaces from imported STEP geometry.
- Avoid face-selection errors that could make the assembly misleading or unstable.

The rough assembly is a review scaffold, not a final mechanical assembly.

## 3. Macro Inputs

- `03_cad/solidworks/component_placement_table_v1.csv`
- `03_cad/solidworks/current_cad_inventory_for_assembly.csv`

The component placement table is the primary input. The inventory file is used to confirm source CAD, placeholder status, and missing CAD notes.

## 4. Suggested Macro Output

Suggested assembly output:

```text
03_cad/solidworks/assembly/blood_sorting_robot_rough_layout_v1.SLDASM
```

If the current environment cannot operate SolidWorks directly, the project should generate the macro script and keep the CSV placement plan as the execution reference.

## 5. Suggested Macro File

One of the following should be generated in a later stage:

```text
03_cad/solidworks/macros/create_rough_assembly_v1.py
03_cad/solidworks/macros/create_rough_assembly_v1.vba
```

Python can be used when SolidWorks COM automation is available. VBA can be used when running from inside SolidWorks.

## 6. Recommended Macro Behavior

For each row in `component_placement_table_v1.csv`:

1. skip rows with `cad_file_path = TBD` and create a note in the macro log.
2. open the referenced STEP/STP/SLDPRT file.
3. insert it into the assembly.
4. apply rough translation and rotation from the CSV.
5. fix the component in place.
6. name the instance using `instance_name`.
7. write any skipped or failed insertions to a log.

## 7. Manual Inspection After Macro

After the rough assembly is opened:

- check whether left and right Y axes are parallel.
- check whether X axis spans the two Y axes.
- check whether Z axis points downward.
- check whether the gripper faces the tubes.
- check whether the scanner faces the label side.
- check whether input/output/manual review bins are inside the reachable area.
- check whether cable chain, scanner, sensors, and brackets will need revised placement.

## 8. Out Of Scope For Macro v1

- final mates.
- interference resolution.
- automatic bracket design.
- hole-pattern matching.
- screw insertion.
- motion study.
- motor/belt/sync mechanism finalization.
