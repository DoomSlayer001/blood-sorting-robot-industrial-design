# Stage 7A-3f v1.5 Not Accepted But Preserved Status

Status: NOT_ACCEPTED_FOR_FINAL_MECHANICAL_VALIDATION

## Preserved v1.5 Files

- `03_cad/freecad_assembly/blood_sorting_robot_gantry_joint_adapter_module_v1_5.step`
- `03_cad/freecad_assembly/blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_5.step`
- `03_cad/freecad_assembly/generate_stage_7a3f_v1_5_slider_binding_correction.py`
- `03_cad/freecad_assembly/stage_7a3f_v1_5_color_manifest.csv`
- `03_cad/freecad_assembly/stage_7a3f_v1_5_import_display_audit.csv`
- `03_cad/freecad_assembly/stage_7a3f_v1_5_interference_audit.csv`
- `03_cad/freecad_assembly/stage_7a3f_v1_5_load_path_audit.csv`
- `03_cad/freecad_assembly/stage_7a3f_v1_5_slider_binding_interface_manifest.csv`
- `03_cad/freecad_assembly/stage_7a3f_v1_5_slider_vs_rail_mount_audit.csv`
- `03_cad/freecad_assembly/stage_7a3f_v1_5_validation.csv`
- `03_cad/freecad_assembly/stage_7a3f_v1_5_visibility_audit.csv`
- `03_cad/freecad_assembly/stage_7a3f_v1_5_xy_joint_motion_envelope_check.csv`
- `03_cad/freecad_assembly/stage_7a3f_v1_5_xy_joint_tube_clearance_check.csv`
- `reports/stage_7a3f_v1_5_slider_carriage_true_binding_fix_report.md`

## Manual Check Result

Stage 7A-3f v1.5 did not pass manual SolidWorks visual inspection. The X/Y joint still does not clearly and physically mount the X beam end adapter to the original moving Y slider/carriage. Some local connector geometry still appears too close to, or at risk of entering, the fixed Y rail body / rail running zone.

## Why The Files Are Preserved

The v1.5 artifacts are preserved because they are the latest concrete CAD attempt at separating the rail body from the slider/carriage. Although this attempt is not accepted for final mechanical validation, it is useful as the starting point for v1.6 or later refinement.

## Forward Use

Later work should use v1.5 as the modification base, then correct the interface using the true Y slider/carriage mounting face, mounting-hole positions, SolidWorks mates, supplier carriage CAD, or measured carriage geometry.

## Simulation Impact

This issue does not block Stage 7B-0 simulation architecture. The simulation work can continue with abstract axis kinematics, the occupancy input table, task state logic, and collision-envelope placeholders.

## CAD Baseline Status

v1.5 is not a final CAD baseline and must not be treated as mechanically accepted before final SolidWorks / real carriage mounting-face verification.
