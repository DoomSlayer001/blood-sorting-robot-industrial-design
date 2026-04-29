# Real CAD Intake Report

## Check Metadata

- Check time: 2026-04-29 19:35:37 +08:00
- Check directories:
  - `03_cad/standard_parts/downloaded/y_axis_module/`
  - `03_cad/standard_parts/downloaded/x_axis_module/`
- Intake target: MISUMI MSA-628-B-AB-B1-0750 Guided Belt Drive Actuator CAD
- Intended use: `left_y_axis_module`, `right_y_axis_module`, and `x_axis_module_on_gantry` in the dual-side gantry structure
- Commit/push status: no commit and no push performed in this stage

## Original Files Found

| file | size_bytes | note |
|---|---:|---|
| `03_cad/standard_parts/downloaded/y_axis_module/MSA-628-B-AB-B1-0750.STEP` | 5514777 | User-provided original MISUMI STEP file; retained without deletion |

## ZIP Check

- ZIP files found: none.
- Extraction performed: no.
- Extracted CAD files: none.

## CAD Files Found

| file | format | size_bytes | role |
|---|---|---:|---|
| `03_cad/standard_parts/downloaded/y_axis_module/MSA-628-B-AB-B1-0750.STEP` | STEP | 5514777 | Original user-downloaded file |
| `03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step` | STEP | 5514777 | Normalized copy for BOM/CAD status registration |
| `03_cad/standard_parts/downloaded/x_axis_module/MISUMI_MSA628_X_axis_L750_double_shaft_B1_v1.step` | STEP | 5514777 | Normalized X-axis copy for X-on-gantry BOM/CAD status registration |

## Normalized File

- Normalized Y file name: `MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step`
- Normalized Y file path: `03_cad/standard_parts/downloaded/y_axis_module/MISUMI_MSA628_Y_axis_L750_double_shaft_B1_v1.step`
- Normalized X file name: `MISUMI_MSA628_X_axis_L750_double_shaft_B1_v1.step`
- Normalized X file path: `03_cad/standard_parts/downloaded/x_axis_module/MISUMI_MSA628_X_axis_L750_double_shaft_B1_v1.step`
- Naming check:
  - Contains Chinese characters: no.
  - Contains spaces: no.
  - Extension allowed: yes, `.step`.
  - File size greater than zero: yes.

## CAD File Check Result

- Script: `python tools/check_standard_cad_files.py`
- Report: `reports/cad_file_check_report.md`
- Real CAD file count reported by script: 3
- Valid CAD file count reported by script: 3
- Unsupported formats found in MSA-628 intake: none.
- Chinese file names found in MSA-628 intake: none.
- Space-containing file names found in MSA-628 intake: none.
- Empty CAD files found in MSA-628 intake: none.

## Local Status Updates

The following entries were updated locally because a real CAD file exists and passed the file check:

| file | entries updated |
|---|---|
| `03_cad/standard_parts/CAD_download_status_v2.md` | `SP-001 x_axis_module_on_gantry`, `SP-002 left_y_axis_module`, `SP-025 right_y_axis_module` set to `downloaded` |
| `02_bom/standard_parts_bom_v1.csv` | `SP-001`, `SP-002`, `SP-025` set to `downloaded`; supplier set to MISUMI; model set to MSA-628-B-AB-B1-0750 |
| `02_bom/standard_parts_physical_parameters.csv` | `SP-001`, `SP-002`, `SP-025` CAD path and nominal length 750 mm recorded; other unconfirmed parameters remain `TBD` |

The same MSA-628 standard CAD/configuration is intended to be instantiated three times in the SolidWorks assembly: once for the left Y-axis module, once for the right Y-axis module, and once for the X-axis module on the gantry.

MSA-M6S was considered as a higher-rigidity candidate, but it is larger and is not part of the current mainline BOM.

## Priority A Items Still Not Downloaded

- `SP-003` z_axis_screw_module.
- `SP-004` x_axis_motor.
- `SP-005` y_axis_motor.
- `SP-006` z_axis_motor.
- `SP-007` xyz_linear_guides_and_carriage_blocks.
- `SP-008` timing_belt.
- `SP-009` timing_belt_pulley.
- `SP-010` lead_screw.
- `SP-011` coupling.
- `SP-012` bearing_block.
- `SP-013` electric_parallel_gripper.
- `SP-016` limit_switches.
- `SP-019` emergency_stop.
- `SP-026` y_axis_sync_mechanism.
- `SP-027` gantry_beam_related_mounting_hardware.

## Next Step Recommendation

1. Open the normalized STEP file in SolidWorks and verify the imported geometry, units, orientation, and origin.
2. Confirm whether `0750` represents nominal body length, configured rail length, or usable stroke from the MISUMI specification page.
3. Record verified dimensions such as mounting hole pitch, carriage top height, carriage hole pattern, moving mass, rated load, belt pitch, pulley interface, and motor interface when supplier data is available.
4. Continue separate selection for the Z-axis lead-screw lifting module; Z does not use MSA-628.
5. After user confirmation, commit the normalized CAD files, intake report, check report, and local status updates in one controlled commit.

## Z Axis LS10 Intake Update

### Check Metadata

- Check time: 2026-04-29 19:53:21 +08:00
- Check directory: `03_cad/standard_parts/downloaded/z_axis_module/`
- Intake target: MISUMI LS10 Z-axis ball screw module CAD
- Configuration: `LS1004-140-T42`
- Usage: `z_axis_module` for vertical pick-and-place motion
- Commit/push status: no commit and no push performed in this stage

### Original Files Found

| file | size_bytes | note |
|---|---:|---|
| `03_cad/standard_parts/downloaded/z_axis_module/LS1004-140-T42_STEP_AP214_20260429/LS1004-140-T42.stp` | 903383 | User-provided MISUMI STEP/STP file retained in original supplier folder |
| `03_cad/standard_parts/downloaded/z_axis_module/LS1004-140-T42_STEP_AP214_20260429/readme-and-terms-of-use-3d-cad-models.txt` | 2684 | Supplier text/terms file; retained but not treated as CAD |

### ZIP Check

- ZIP files found: none.
- Extraction performed: no.
- Extracted CAD files: none.
- The folder `LS1004-140-T42_STEP_AP214_20260429/` appears to be an already-extracted supplier package.

### Normalized File

- Normalized file name: `MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.step`
- Normalized file path: `03_cad/standard_parts/downloaded/z_axis_module/MISUMI_LS10_Z_axis_140stroke_T42_ball_screw_v1.step`
- File size: 903383 bytes.
- Naming check:
  - Contains Chinese characters: no.
  - Contains spaces: no.
  - Extension allowed: yes, `.step`.
  - File size greater than zero: yes.

### Recorded Parameters

| parameter | value |
|---|---|
| supplier | MISUMI |
| series | LS10 |
| configuration | LS1004-140-T42 |
| drive_method | Rolled Ball Screws |
| stroke | 140 mm |
| lead | 4 mm |
| motor_adapter | T42 |
| positioning_repeatability | +/-20 um |
| max_velocity | 467 mm/s |
| ball_screw_diameter | 10 mm |
| table_width | 62 mm |
| table_length | 50 mm |

Unconfirmed parameters remain `TBD`.

### CAD File Check Result

- Script: `python tools/check_standard_cad_files.py`
- Report: `reports/cad_file_check_report.md`
- Real file count reported by script: 6
- Valid CAD file count reported by script: 5
- Note: the supplier text file `readme-and-terms-of-use-3d-cad-models.txt` is reported by the script as unsupported extension `.txt`. This is expected because it is not a CAD file and is retained for supplier terms/reference.

### Local Status Updates

The following entries were updated locally because a real Z-axis CAD file exists and passed the CAD file check:

| file | entries updated |
|---|---|
| `03_cad/standard_parts/CAD_download_status_v2.md` | `SP-003 z_axis_module` set to `downloaded` |
| `02_bom/standard_parts_bom_v1.csv` | `SP-003` set to `downloaded`; supplier set to MISUMI; series/configuration set to LS10 / LS1004-140-T42 |
| `02_bom/standard_parts_physical_parameters.csv` | `SP-003` stroke, lead, max velocity, motor adapter, CAD path, and known LS10 notes recorded |

### Priority A Items Still Not Downloaded After Z Intake

- `SP-004` x_axis_motor.
- `SP-005` y_axis_motor.
- `SP-006` z_axis_motor.
- `SP-007` xyz_linear_guides_and_carriage_blocks, if separate guides are still needed.
- `SP-008` timing_belt.
- `SP-009` timing_belt_pulley.
- `SP-010` lead_screw, if not fully covered by integrated LS10 data for release documentation.
- `SP-011` coupling.
- `SP-012` bearing_block.
- `SP-013` electric_parallel_gripper.
- `SP-016` limit_switches.
- `SP-019` emergency_stop.
- `SP-026` y_axis_sync_mechanism.
- `SP-027` gantry_beam_related_mounting_hardware.
