# CadQuery Rough Assembly v5 Report

- v5 is based on v4/v3 and keeps the main gantry layout.
- Colors were attempted through CadQuery XCAF/STEPCAF assembly export; color manifest fallback was generated.
- Automated interference/clearance audit was added.
- Layout fixes: input rack moved inward, output bins moved away from right Y axis, scan station moved away from gantry center, adapter plate resized/shifted.
- Successful imported/generated components: 37
- Failed components: 0
- Total solids: 263 added / 263 exported
- Total bbox: 1100.000 x 900.000 x 487.500 mm
- STEP color export: attempted, but SolidWorks color recognition is not locally proven.
- Interference audit summary: overlap=0, too_close=0, allowed_mount_contact=17.
- Output STEP path: `03_cad/freecad_assembly/blood_sorting_robot_cadquery_rough_layout_v5.step`
- Remaining issue: open v5 STEP in SolidWorks 2026 to verify color interpretation and visual clearance.
