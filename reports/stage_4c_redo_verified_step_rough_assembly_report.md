# Stage 4C-Redo Verified STEP Rough Assembly Report

- Generated at: 2026-05-01T16:34:30

## Why The Rough Assembly Was Rebuilt

Earlier rough assemblies existed on disk but opened with zero components and no referenced documents. This report therefore treats those files as invalid and rebuilds from original STEP/STP CAD using SolidWorks 2026.

## Existing Assembly Audit

- `03_cad/solidworks/assembly/blood_sorting_robot_rough_layout_v1.SLDASM`: invalid_empty_assembly; component_count=0; referenced_documents=0
- `03_cad/solidworks/assembly/blood_sorting_robot_rough_layout_2026_v1.SLDASM`: invalid_empty_assembly; component_count=0; referenced_documents=0
- `03_cad/solidworks/assembly/solidworks_2026_native_smoke_test.SLDASM`: invalid_empty_assembly; component_count=0; referenced_documents=0

## STEP/STP Workflow

- Main flow: original STEP/STP CAD -> SolidWorks 2026 insert -> coordinate rough placement -> component/references/reopen verification.
- The manual `converted_native` cache is not used as the source for this rebuild.
- No complex mates, hole selection, or installation-face inference are performed.

## Smoke Test Result

- Smoke test verified success: False
- Smoke inserted components: 0
- Smoke failed components: 3
- Smoke skipped components: 0

## Full Verified Rough Assembly Result

- SolidWorks revision: `34.2.1`
- Assembly template: `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_assembly.asmdot`
- Output assembly: `03_cad/solidworks/assembly/blood_sorting_robot_verified_step_rough_layout_2026_v1.SLDASM`
- Output size bytes: None
- Component count before save: None
- Component count after reopen: None
- Referenced document count: None
- Inserted components: 0
- Failed insertions: 0
- Skipped components: 0
- Critical components all satisfied: False
- Screenshot exported: False
- Verified success: False

## Inserted Components

- None

## Failed Or Skipped Components

- Failed `full_assembly`: smoke_test_failed

## Next Manual Checks

- Open the verified STEP rough assembly in SolidWorks 2026.
- Check overall isometric, top, front, side, gripper/tube, scan-station, and output-bin views.
- Correct coordinate or rotation rows in `component_placement_table_v1.csv` based on screenshots.
