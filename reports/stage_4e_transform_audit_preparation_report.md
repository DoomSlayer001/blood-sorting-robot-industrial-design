# Stage 4E Transform Audit Preparation Report

## Objective

Prepare a SolidWorks 2026 internal VBA transform and bounding box audit for the Stage 4D corrected rough assembly.

## Current 4D Assembly Status

Assembly:

```text
03_cad/solidworks/assembly/rough_layout_4d_corrected_2026_v1.SLDASM
```

Current classification:

```text
valid component insertion, layout incorrect, needs transform audit
```

The assembly is not empty, and FeatureManager contains real components. However, the layout is still not geometrically correct.

## Observed Problems From Current Screenshots

- Left and right Y axes do not yet form a correct dual-side gantry.
- X/Y/Z axis spatial relationships are wrong.
- Some long modules appear to pass through the base plate or appear vertically through the layout.
- Input rack, output bins, barcode scanner, photoelectric sensor, and gripper remain clustered near the center.
- Output bin instances still appear suspicious because reused geometry can show as `category_A_output_bin_2x3`.
- Cable chain and synchronization shaft can interfere with visual inspection.

## Why Not Continue Guessing Rotation Angles

The current symptoms can be caused by several different mechanisms:

- `AddComponent5` initial coordinates and `SetTransformAndSolve2` may interact in unexpected ways.
- The `TransformData` rotation matrix may not match the row/column ordering expected by SolidWorks.
- The default long-axis orientation of each imported component is not confirmed.
- MSA-628 and LS10 native files may not share the same local coordinate convention.
- Reused output-bin geometry needs semantic instance naming separate from referenced file names.

Changing rotation values by guesswork would likely create another ambiguous result. The next step is to measure actual transforms and bounding boxes.

## Prepared Audit Tools

- VBA audit macro:
  `03_cad/solidworks/macros/audit_4d_assembly_transforms_2026_internal_vba.vba`
- Copy-to-SWP version:
  `03_cad/solidworks/macros/audit_4d_assembly_transforms_2026_copy_to_swp.bas`
- Run guide:
  `03_cad/solidworks/macros/run_4e_transform_audit_guide.md`
- Target-vs-actual template:
  `03_cad/solidworks/component_placement_4e_target_vs_actual_template.csv`

## Audit Output

When run inside SolidWorks 2026, the macro should create:

```text
03_cad/solidworks/assembly/rough_layout_4d_component_transform_audit.csv
```

The CSV contains:

- component name
- referenced file
- suppressed/fixed state
- actual translation in meters and millimeters
- bounding box min/max in millimeters
- bounding box size
- longest bounding box axis
- notes for read errors

## Next Step

The user should run the audit macro inside SolidWorks 2026 and send back the generated CSV. The next correction pass will use that measured data to create a 4E corrected placement table v2 and updated internal VBA macro.
