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

## SMC LEHF20 Gripper Intake Update

### Check Metadata

- Check time: 2026-04-29 20:12:26 +08:00
- Check directory: `03_cad/standard_parts/downloaded/gripper/`
- Intake target: SMC LEHF20 electric parallel gripper CAD
- Configuration: 2-finger parallel electric gripper, 24 mm stroke, Size 20
- Usage: `electric_parallel_gripper` end effector for holding 13 mm blood tubes
- Commit/push status: local commit requested after this intake; no push performed

### Original Files Found

| file | size_bytes | note |
|---|---:|---|
| `03_cad/standard_parts/downloaded/gripper/PARTserver22026042914085532807997d0b6156e.zip` | 39405 | User-provided original supplier ZIP package; retained without deletion |
| `03_cad/standard_parts/downloaded/gripper/extracted/PARTserver22026042914085532807997d0b6156e/LEHF20K2-24(0_0).stp` | 228118 | Extracted supplier STP file retained in extracted package folder |
| `03_cad/standard_parts/downloaded/gripper/extracted/PARTserver22026042914085532807997d0b6156e/readme-and-terms-of-use-3d-cad-models.txt` | 2688 | Supplier text/terms file; retained but not treated as CAD |

### ZIP Check

- ZIP files found: one.
- Extraction performed: yes, into `03_cad/standard_parts/downloaded/gripper/extracted/PARTserver22026042914085532807997d0b6156e/`.
- Extracted CAD files: `LEHF20K2-24(0_0).stp`.
- Original ZIP retained: yes.

### Normalized File

- Normalized file name: `SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.step`
- Normalized file path: `03_cad/standard_parts/downloaded/gripper/SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.step`
- File size: 228118 bytes.
- Naming check:
  - Contains Chinese characters: no.
  - Contains spaces: no.
  - Extension allowed: yes, `.step`.
  - File size greater than zero: yes.

### Recorded Parameters

| parameter | value |
|---|---|
| supplier | SMC |
| series | LEHF20 |
| gripper_type | 2-finger parallel electric gripper |
| size | 20 |
| stroke | 24 mm |
| dimensions_when_open | 24 mm |
| dimensions_when_closed | 0 mm |
| maximum_gripping_force | 28 N |
| cable/controller | None |

Unconfirmed parameters remain `TBD`.

### CAD File Check Result

- Script: `python tools/check_standard_cad_files.py`
- Report: `reports/cad_file_check_report.md`
- Supported CAD file count: 7
- Valid CAD file count: 7
- Supplementary vendor document count: 3
- Invalid / unsupported CAD candidate count: 0
- Note: the supplier ZIP package and readme/terms files are reported as supplementary vendor documents and are not counted as invalid CAD.

### Local Status Updates

The following entries were updated locally because a real gripper CAD file exists and passed the CAD file check:

| file | entries updated |
|---|---|
| `03_cad/standard_parts/CAD_download_status_v2.md` | `SP-013 electric_parallel_gripper` set to `downloaded` |
| `02_bom/standard_parts_bom_v1.csv` | `SP-013` set to `downloaded`; supplier set to SMC; series/configuration set to LEHF20 |
| `02_bom/standard_parts_physical_parameters.csv` | `SP-013` stroke, rated gripping force, CAD path, and known LEHF20 notes recorded |

### Priority A Items Still Not Downloaded After Gripper Intake

- `SP-004` x_axis_motor.
- `SP-005` y_axis_motor.
- `SP-006` z_axis_motor.
- `SP-007` xyz_linear_guides_and_carriage_blocks, if separate guides are still needed.
- `SP-008` timing_belt.
- `SP-009` timing_belt_pulley.
- `SP-010` lead_screw, if not fully covered by integrated LS10 data for release documentation.
- `SP-011` coupling.
- `SP-012` bearing_block.
- `SP-016` limit_switches.
- `SP-019` emergency_stop.
- `SP-026` y_axis_sync_mechanism.
- `SP-027` gantry_beam_related_mounting_hardware.

## Oriental Motor AZM46AK Motor Intake Update

### Check Metadata

- Check time: 2026-04-29 20:31:37 +08:00
- Check directory: `03_cad/standard_parts/downloaded/motors/`
- Intake target: Oriental Motor AZ Series AZM46AK motor CAD
- Configuration: 42 mm / NEMA17 stepper motor with mechanical absolute encoder, DC input, no gearbox, no brake
- Usage: common motor CAD for X/Y/Z axis motor interface verification
- Commit/push status: local commit requested after this intake; no push performed

### Original Files Found

| file | size_bytes | note |
|---|---:|---|
| `03_cad/standard_parts/downloaded/motors/182509157-19-azm46ak.zip` | 126860 | User-provided original Oriental Motor ZIP package; retained without deletion |
| `03_cad/standard_parts/downloaded/motors/extracted/182509157-19-azm46ak/azm46ak.stp` | 900249 | Extracted supplier STP file retained in extracted package folder |
| `03_cad/standard_parts/downloaded/motors/extracted/182509157-19-azm46ak/azm46ak.txt` | 3303 | Supplier text file; retained but not treated as CAD |

### ZIP Check

- ZIP files found: one.
- Extraction performed: yes, into `03_cad/standard_parts/downloaded/motors/extracted/182509157-19-azm46ak/`.
- Extracted CAD files: `azm46ak.stp`.
- Original ZIP retained: yes.

### Normalized File

- Normalized file name: `OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.step`
- Normalized file path: `03_cad/standard_parts/downloaded/motors/OrientalMotor_AZM46AK_NEMA17_42mm_absolute_encoder_stepper_v1.step`
- File size: 900249 bytes.
- Naming check:
  - Contains Chinese characters: no.
  - Contains spaces: no.
  - Extension allowed: yes, `.step`.
  - File size greater than zero: yes.

### Recorded Parameters

| parameter | value |
|---|---|
| supplier | Oriental Motor |
| series | AZ Series |
| model | AZM46AK |
| frame_size | 42 mm / NEMA17 |
| encoder | mechanical absolute encoder |
| input | DC |
| gearbox | none |
| brake | none |
| motor_length | 70 mm |

Unconfirmed torque, current, inertia, shaft detail, connector, and driver parameters remain `TBD`.

### CAD File Check Result

- Script: `python tools/check_standard_cad_files.py`
- Report: `reports/cad_file_check_report.md`
- Supported CAD file count: 9
- Valid CAD file count: 9
- Supplementary vendor document count: 5
- Invalid / unsupported CAD candidate count: 0
- Note: the supplier ZIP package and text file are reported as supplementary vendor documents and are not counted as invalid CAD.

### Local Status Updates

The following entries were updated locally because a real motor CAD file exists and passed the CAD file check:

| file | entries updated |
|---|---|
| `03_cad/standard_parts/CAD_download_status_v2.md` | `SP-004 x_axis_motor`, `SP-005 y_axis_motor`, `SP-006 z_axis_motor` set to `downloaded` |
| `02_bom/standard_parts_bom_v1.csv` | `SP-004`, `SP-005`, `SP-006` set to `downloaded`; supplier set to Oriental Motor; series/model set to AZ Series / AZM46AK |
| `02_bom/standard_parts_physical_parameters.csv` | `SP-004`, `SP-005`, `SP-006` motor length, frame size, motor interface, CAD path, and known AZM46AK notes recorded |

The same normalized motor CAD file is intended to be instantiated three times in SolidWorks for X, Y, and Z motor interface verification.

### Priority A Items Still Not Downloaded After Motor Intake

- `SP-007` xyz_linear_guides_and_carriage_blocks, if separate guides are still needed.
- `SP-008` timing_belt.
- `SP-009` timing_belt_pulley.
- `SP-010` lead_screw, if not fully covered by integrated LS10 data for release documentation.
- `SP-011` coupling.
- `SP-012` bearing_block.
- `SP-016` limit_switches.
- `SP-019` emergency_stop.
- `SP-026` y_axis_sync_mechanism.
- `SP-027` gantry_beam_related_mounting_hardware.

## OMRON D4N Limit Switch Intake Update

### Check Metadata

- Check time: 2026-04-29 20:48:00 +08:00
- Check directory: `03_cad/standard_parts/downloaded/sensors/`
- Intake target: OMRON D4N limit switch CAD
- Configuration: D4N-1A20 roller lever limit switch
- Usage: X/Y/Z axis homing and travel limit detection
- Commit/push status: local commit requested after this intake; no push performed

### Original Files Found

| file | size_bytes | note |
|---|---:|---|
| `03_cad/standard_parts/downloaded/sensors/D4N-1A20_214.STEP` | 491902 | User-provided original OMRON STEP file; retained without deletion |

### ZIP Check

- ZIP files found: none.
- Extraction performed: no.
- Extracted CAD files: none.

### Normalized File

- Normalized file name: `OMRON_D4N_roller_lever_limit_switch_v1.step`
- Normalized file path: `03_cad/standard_parts/downloaded/sensors/OMRON_D4N_roller_lever_limit_switch_v1.step`
- File size: 491902 bytes.
- Naming check:
  - Contains Chinese characters: no.
  - Contains spaces: no.
  - Extension allowed: yes, `.step`.
  - File size greater than zero: yes.

### Recorded Parameters

| parameter | value |
|---|---|
| supplier | OMRON |
| series | D4N |
| model | D4N-1A20 |
| type | roller lever limit switch |
| usage | X/Y/Z homing and travel limit detection |

Unconfirmed physical and electrical parameters remain `TBD`.

### CAD File Check Result

- Script: `python tools/check_standard_cad_files.py`
- Report: `reports/cad_file_check_report.md`
- Supported CAD file count: 11
- Valid CAD file count: 11
- Supplementary vendor document count: 5
- Invalid / unsupported CAD candidate count: 0

### Local Status Updates

The following entries were updated locally because a real limit switch CAD file exists and passed the CAD file check:

| file | entries updated |
|---|---|
| `03_cad/standard_parts/CAD_download_status_v2.md` | `SP-016 limit_switches` set to `downloaded` |
| `02_bom/standard_parts_bom_v1.csv` | `SP-016` set to `downloaded`; supplier set to OMRON; series/model set to D4N / D4N-1A20 |
| `02_bom/standard_parts_physical_parameters.csv` | `SP-016` CAD path and known D4N notes recorded |

The same normalized switch CAD file is intended to be instantiated multiple times in SolidWorks for X/Y/Z axis homing and travel limit detection.

### Priority A Items Still Not Downloaded After Limit Switch Intake

- `SP-007` xyz_linear_guides_and_carriage_blocks, if separate guides are still needed.
- `SP-008` timing_belt.
- `SP-009` timing_belt_pulley.
- `SP-010` lead_screw, if not fully covered by integrated LS10 data for release documentation.
- `SP-011` coupling.
- `SP-012` bearing_block.
- `SP-019` emergency_stop.
- `SP-026` y_axis_sync_mechanism.
- `SP-027` gantry_beam_related_mounting_hardware.

## Emergency Stop Visual Placeholder Intake Update

### Check Metadata

- Check time: 2026-04-29 21:08:29 +08:00
- Source directory: `03_cad/standard_parts/downloaded/safety/`
- Placeholder directory: `03_cad/standard_parts/placeholders/safety/`
- Intake target: emergency stop pushbutton visual placeholder
- Supplier status: community model or unknown official supplier
- Usage: visual placeholder for emergency stop button mounted on the control panel or base plate safety area
- Commit/push status: local commit requested after this intake; no push performed

### Original Files Found

| file | size_bytes | note |
|---|---:|---|
| `03_cad/standard_parts/downloaded/safety/User Library-K16-811-N.zip` | 2240997 | User-provided original ZIP package; retained without deletion |
| `03_cad/standard_parts/downloaded/safety/extracted/User Library-K16-811-N/User_Library-K16-811-N.sldprt` | 2281079 | Extracted SolidWorks part; extracted copy renamed to remove spaces so the CAD check does not fail on filename rules |

### ZIP Check

- ZIP files found: one.
- Extraction performed: yes, into `03_cad/standard_parts/downloaded/safety/extracted/User Library-K16-811-N/`.
- Extracted CAD files: `User_Library-K16-811-N.sldprt`.
- Original ZIP retained: yes.

### Placeholder Normalized File

- Placeholder file name: `emergency_stop_visual_placeholder_v1.sldprt`
- Placeholder file path: `03_cad/standard_parts/placeholders/safety/emergency_stop_visual_placeholder_v1.sldprt`
- File size: 2281079 bytes.
- Naming check:
  - Contains Chinese characters: no.
  - Contains spaces: no.
  - Extension allowed: yes, `.sldprt`.
  - File size greater than zero: yes.

### CAD File Check Result

- Script: `python tools/check_standard_cad_files.py`
- Report: `reports/cad_file_check_report.md`
- Supported CAD file count: 12
- Valid CAD file count: 12
- Supplementary vendor document count: 6
- Invalid / unsupported CAD candidate count: 0
- Note: the original ZIP package is reported as a supplementary vendor document/archive and is not counted as invalid CAD.

### Local Status Updates

The following entries were updated locally as a visual placeholder only:

| file | entries updated |
|---|---|
| `03_cad/standard_parts/CAD_download_status_v2.md` | `SP-019 emergency_stop` set to `visual_placeholder` |
| `02_bom/standard_parts_bom_v1.csv` | `SP-019` set to `visual_placeholder`; supplier set to `community_model`; fallback allowed |
| `02_bom/standard_parts_physical_parameters.csv` | `SP-019` placeholder path recorded; verified remains `no` because this is not official vendor CAD |

### Placeholder Limitations

- Current model is only for visual layout.
- It is not official vendor CAD.
- It must not be used for final production, safety certification, or a rigorous final report release.
- Final version should replace this placeholder with official CAD from Schneider Harmony XB5, OMRON A22E, Fuji AR22, or IDEC XW.
- `official_cad_required_later=true`.

### Priority A Items Still Requiring Official CAD After Placeholder Intake

- `SP-007` xyz_linear_guides_and_carriage_blocks, if separate guides are still needed.
- `SP-008` timing_belt.
- `SP-009` timing_belt_pulley.
- `SP-010` lead_screw, if not fully covered by integrated LS10 data for release documentation.
- `SP-011` coupling.
- `SP-012` bearing_block.
- `SP-019` emergency_stop official CAD replacement.
- `SP-026` y_axis_sync_mechanism.
- `SP-027` gantry_beam_related_mounting_hardware.

## Panasonic CX-421-J Photoelectric Sensor Intake Update

- Check time: 2026-04-29 21:46:57 +08:00
- Check directory: `03_cad/standard_parts/downloaded/sensors/`
- Related part_id: `SP-017 photoelectric_sensor`
- Supplier: Panasonic
- Series: CX-400
- Model: CX-421-J
- Type: diffuse reflective photoelectric sensor
- Usage: tube presence detection and barcode scan trigger at the pick/place or scanning station.

### Original Downloaded Files

| file | type | size_bytes | action |
|---|---:|---:|---|
| `03_cad/standard_parts/downloaded/sensors/cx-42_48_49-j_st.zip` | supplier ZIP package | 30373 | kept as original vendor package |

### Extracted Files

| file | type | size_bytes | action |
|---|---:|---:|---|
| `03_cad/standard_parts/downloaded/sensors/extracted/cx-42_48_49-j_st/cx-421-j.STEP` | extracted CAD | 205238 | kept as extracted original CAD |

### Normalized Working CAD File

| file | format | size_bytes | naming_check |
|---|---:|---:|---|
| `03_cad/standard_parts/downloaded/sensors/Panasonic_CX421J_diffuse_photoelectric_sensor_v1.step` | STEP | 205238 | passed: no Chinese characters, no spaces, supported extension |

### CAD File Check Result

- Script: `python tools/check_standard_cad_files.py`
- Report: `reports/cad_file_check_report.md`
- Supported CAD file count: 16
- Valid CAD file count: 16
- Supplementary vendor document count: 9
- Invalid / unsupported CAD candidate count: 0
- Note: the supplier ZIP package is reported as a supplementary vendor document and is not counted as invalid CAD.

### Local Status Updates

The following entries were updated locally because a real Panasonic photoelectric sensor CAD file exists and passed the CAD file check:

| file | entries updated |
|---|---|
| `03_cad/standard_parts/CAD_download_status_v2.md` | `SP-017 photoelectric_sensor` set to `downloaded` |
| `02_bom/standard_parts_bom_v1.csv` | `SP-017` set to `downloaded`; supplier set to Panasonic; series/model set to CX-400 / CX-421-J |
| `02_bom/standard_parts_physical_parameters.csv` | `SP-017` CAD path and verified source recorded; unknown physical and sensing parameters remain `TBD` |

The sensor is intended to detect whether a tube is present at the pick/place or barcode scanning station and to provide a trigger condition for barcode scanning.

### Priority Items Still Not Downloaded After Photoelectric Sensor Intake

- `SP-007` xyz_linear_guides_and_carriage_blocks, if separate guides are still needed.
- `SP-008` timing_belt.
- `SP-009` timing_belt_pulley.
- `SP-010` lead_screw, if not fully covered by integrated LS10 data for release documentation.
- `SP-011` coupling.
- `SP-012` bearing_block.
- `SP-019` emergency_stop official CAD replacement.
- `SP-026` y_axis_sync_mechanism.
- `SP-027` gantry_beam_related_mounting_hardware.

## MISUMI MHPKS Cable Carrier Intake Update

### Check Metadata

- Check time: 2026-04-29 21:28:27 +08:00
- Check directory: `03_cad/standard_parts/downloaded/cable_chain/`
- Intake target: MISUMI MHPKS compact cable carrier CAD
- Configuration: `MHPKS204-38-18-A`
- Usage: cable management for moving X/Z axis motor cables, gripper cable, limit switch wires, and future sensor/barcode scanner cables
- Commit/push status: local commit requested after this intake; no push performed

### Original Files Found

| file | size_bytes | note |
|---|---:|---|
| `03_cad/standard_parts/downloaded/cable_chain/MHPKS204-38-18-A_STEP_AP214_20260429.zip` | 37736 | User-provided original MISUMI ZIP package; retained without deletion |
| `03_cad/standard_parts/downloaded/cable_chain/extracted/MHPKS204-38-18-A_STEP_AP214_20260429/MHPKS204-38-18-A.stp` | 217055 | Extracted supplier STP file retained in extracted package folder |
| `03_cad/standard_parts/downloaded/cable_chain/extracted/MHPKS204-38-18-A_STEP_AP214_20260429/readme-and-terms-of-use-3d-cad-models.txt` | 2688 | Supplier text/terms file; retained but not treated as CAD |

### ZIP Check

- ZIP files found: one.
- Extraction performed: yes, into `03_cad/standard_parts/downloaded/cable_chain/extracted/MHPKS204-38-18-A_STEP_AP214_20260429/`.
- Extracted CAD files: `MHPKS204-38-18-A.stp`.
- Original ZIP retained: yes.

### Normalized File

- Normalized file name: `MISUMI_MHPKS204_cable_carrier_R38_18links_v1.step`
- Normalized file path: `03_cad/standard_parts/downloaded/cable_chain/MISUMI_MHPKS204_cable_carrier_R38_18links_v1.step`
- File size: 217055 bytes.
- Naming check:
  - Contains Chinese characters: no.
  - Contains spaces: no.
  - Extension allowed: yes, `.step`.
  - File size greater than zero: yes.

### Recorded Parameters

| parameter | value |
|---|---|
| supplier | MISUMI |
| series | MHPKS |
| model | MHPKS204-38-18-A |
| type | compact cable carrier |
| inner_height_mm | 16 |
| inner_width_mm | 29 |
| bending_radius_mm | 38 |
| link_pitch_mm | 32 |
| number_of_links | 18 |
| mounting_direction | A |
| material | Nylon 6 + Glass 20% |

Unconfirmed bracket/interface and cable fill parameters remain `TBD`.

### CAD File Check Result

- Script: `python tools/check_standard_cad_files.py`
- Report: `reports/cad_file_check_report.md`
- Supported CAD file count: 14
- Valid CAD file count: 14
- Supplementary vendor document count: 8
- Invalid / unsupported CAD candidate count: 0
- Note: the supplier ZIP package and readme/terms file are reported as supplementary vendor documents and are not counted as invalid CAD.

### Local Status Updates

The following entries were updated locally because a real cable carrier CAD file exists and passed the CAD file check:

| file | entries updated |
|---|---|
| `03_cad/standard_parts/CAD_download_status_v2.md` | `SP-015 cable_chain` set to `downloaded` |
| `02_bom/standard_parts_bom_v1.csv` | `SP-015` set to `downloaded`; supplier set to MISUMI; series/model set to MHPKS / MHPKS204-38-18-A |
| `02_bom/standard_parts_physical_parameters.csv` | `SP-015` inner dimensions, bending radius, link pitch, number of links, material notes, and CAD path recorded |

The normalized cable carrier CAD will be used first for X/Z moving cable management. It may later be copied as additional SolidWorks instances for Y-axis or other moving cable routes.

### Priority Items Still Not Downloaded After Cable Carrier Intake

- `SP-007` xyz_linear_guides_and_carriage_blocks, if separate guides are still needed.
- `SP-008` timing_belt.
- `SP-009` timing_belt_pulley.
- `SP-010` lead_screw, if not fully covered by integrated LS10 data for release documentation.
- `SP-011` coupling.
- `SP-012` bearing_block.
- `SP-019` emergency_stop official CAD replacement.
- `SP-026` y_axis_sync_mechanism.
- `SP-027` gantry_beam_related_mounting_hardware.
