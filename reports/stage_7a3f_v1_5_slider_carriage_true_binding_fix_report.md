# Stage 7A-3f v1.5 Physical Slider Binding Correction Report

Status: NOT_ACCEPTED_FOR_FINAL_MECHANICAL_VALIDATION

Reason:
- v1.5 already attempted to distinguish the fixed Y rail body from the moving Y slider/carriage.
- Manual SolidWorks inspection shows the X/Y interface is still not fully and physically connected to the original Y slider/carriage mounting face.
- Local connector geometry still appears close to, or at risk of entering, the rail body / rail running zone.
- This version is not accepted as the final mechanical validation baseline.
- The v1.5 artifacts are preserved as the modification base for v1.6 / later refinement.
- Later system simulation can continue to use the abstract kinematic model and occupancy table, because it does not depend on this interface being mechanically finalized.

## Manual Inspection Override

The generated v1.5 CSV audits and report fields described the interface as mounted to the slider/carriage. That automated conclusion is superseded by manual SolidWorks visual inspection. The current accepted engineering status is:

- Final mechanical acceptance: no.
- X beam left end physically verified on original Y slider/carriage: no.
- X beam right end physically verified on original Y slider/carriage: no.
- Risk of rail-body / rail-running-zone interference: yes.
- Motor-like block regression: no known new motor-like block is the primary issue.
- New motor added: no.
- New rail added: no.
- Protected systems modified: no; boxes, gripper, drag chain/soft hose, electrical control box, enclosure, tubes, tube labels, and `legacy_v1` remain outside this v1.5 correction scope.
- Push status: not pushed.

## Preservation Decision

The v1.5 artifacts are intentionally kept in the repository as a documented failed-but-useful CAD attempt. They should not be used as the final CAD baseline, but they remain useful for later refinement because they contain the current v1.5 geometry, manifests, visibility/import checks, interference checks, and the generator script.

Future mechanical correction must verify the true Y slider/carriage mounting face using SolidWorks mate references, supplier carriage CAD, or measured mounting-hole geometry before declaring the X beam to Y slider binding mechanically accepted.
