# Run 4E Transform Audit Guide

## Purpose

Stage 4E audits the real SolidWorks transforms and bounding boxes in:

```text
03_cad/solidworks/assembly/rough_layout_4d_corrected_2026_v1.SLDASM
```

The goal is to stop guessing rotation values and instead measure the actual component positions, bounding boxes, and dominant axes.

## Macro Files

- Source VBA:
  `03_cad/solidworks/macros/audit_4d_assembly_transforms_2026_internal_vba.vba`
- Copy-to-SWP module:
  `03_cad/solidworks/macros/audit_4d_assembly_transforms_2026_copy_to_swp.bas`

## How To Run

1. Open SolidWorks 2026.
2. Open:

```text
03_cad/solidworks/assembly/rough_layout_4d_corrected_2026_v1.SLDASM
```

3. Choose `Tools / Macro / New`.
4. Save the macro as:

```text
03_cad/solidworks/macros/audit_4d_assembly_transforms_2026_internal_vba.swp
```

5. SolidWorks opens the VBA editor.
6. Copy the full content of:

```text
03_cad/solidworks/macros/audit_4d_assembly_transforms_2026_copy_to_swp.bas
```

7. Paste it into the generated macro module.
8. Save and run the macro.

## Expected Output

The macro should create:

```text
03_cad/solidworks/assembly/rough_layout_4d_component_transform_audit.csv
```

## What To Send Back

After running the macro, send back the CSV or a summary of:

- component names
- actual position in mm
- bounding box min/max
- bounding box size
- longest bounding box axis
- any error notes

That data will be used to generate the next corrected placement table and macro.

## Important

The macro is read-only with respect to the assembly:

- it does not move components;
- it does not save assembly changes;
- it does not modify mates;
- it only exports transform and bounding box data.
