# CAD Download Status

Status enum: `not_started`, `manual_download_required`, `downloaded`, `fallback_needed`, `not_available`, `replaced_by_equivalent`.

No item is marked `downloaded`. This v1 status file is retained for continuity; `CAD_download_status_v2.md` is the active tracking table for the dual-side gantry architecture.

| part_id | part_name | supplier_candidate | cad_source | preferred_format | download_status | login_required | manual_action_required | fallback_status | note |
|---|---|---|---|---|---|---|---|---|---|
| SP-001 | X-axis belt module on gantry | MISUMI; THK; HIWIN-equivalent | MISUMI CAD/configurator | SLDASM/SLDPRT; STEP; X_T | manual_download_required | likely | yes | not_allowed_for_freeze | Needs configured 450-500 mm stroke and gantry carriage interface |
| SP-002 | Left Y-axis module or guide assembly | MISUMI; THK; HIWIN-equivalent | MISUMI CAD/configurator | SLDASM/SLDPRT; STEP; X_T | manual_download_required | likely | yes | not_allowed_for_freeze | Left Y datum and drive/sync side required |
| SP-003 | Z-axis lead screw lifting module | MISUMI; THK; HIWIN-equivalent | Supplier actuator CAD | SLDASM/SLDPRT; STEP; X_T | manual_download_required | likely | yes | not_allowed_for_freeze | Lead and holding strategy not frozen |
| SP-004 | X-axis motor | Oriental Motor; Leadshine; Delta; MISUMI | Supplier CAD or 3D ContentCentral | SLDPRT; STEP | manual_download_required | possible | yes | not_allowed_for_freeze | Requires torque-speed selection |
| SP-005 | Y-axis motor for synchronized gantry | Oriental Motor; Leadshine; Delta; MISUMI | Supplier CAD or 3D ContentCentral | SLDPRT; STEP | manual_download_required | possible | yes | not_allowed_for_freeze | Single motor plus mechanical synchronization preferred |
| SP-006 | Z-axis motor | Oriental Motor; Leadshine; Delta; MISUMI | Supplier CAD or 3D ContentCentral | SLDPRT; STEP | manual_download_required | possible | yes | not_allowed_for_freeze | Brake or self-lock review needed |
| SP-007 | X/Y/Z linear guides and sliders | THK; HIWIN; MISUMI | THK/MISUMI CAD | STEP; X_T | manual_download_required | likely | yes | not_allowed_for_freeze | Rail holes and block height are critical |
| SP-008 | Timing belt | MISUMI; Gates; McMaster-Carr | Supplier catalog/CAD | STEP if available | manual_download_required | possible | yes | not_allowed_for_freeze | Belt path depends on pulley and Y sync choice |
| SP-009 | Timing belt pulley | MISUMI; McMaster-Carr; Gates | McMaster-Carr or MISUMI CAD | SLDPRT; STEP | manual_download_required | possible | yes | not_allowed_for_freeze | Bore and tooth count required |
| SP-010 | Lead screw | MISUMI; THK; McMaster-Carr | Supplier CAD | STEP; X_T | manual_download_required | possible | yes | not_allowed_for_freeze | Lead and nut style not frozen |
| SP-011 | Coupling | MISUMI; McMaster-Carr; Ruland-equivalent | Supplier CAD | STEP | manual_download_required | possible | yes | not_allowed_for_freeze | Bore sizes not frozen |
| SP-012 | Bearing block | MISUMI; McMaster-Carr; TraceParts | Supplier CAD or TraceParts | STEP | manual_download_required | possible | yes | not_allowed_for_freeze | Depends on shaft layout and Y sync centerline |
| SP-013 | Electric two-finger parallel gripper | SMC; Festo | SMC/Festo CAD portal | SLDASM/SLDPRT; STEP | manual_download_required | likely | yes | not_allowed_for_freeze | Gripper flange and mass are critical |
| SP-014 | Gripper soft pad | Supplier accessory or custom | Supplier accessory CAD or future custom drawing | STEP later | not_started | possible | yes | fallback_allowed_temporarily | Final pad may be custom made |
| SP-015 | Cable drag chain | igus; MISUMI; McMaster-Carr | igus e-chain CAD | STEP; IGES | manual_download_required | possible | yes | fallback_allowed_temporarily | Needs gantry/X/Z cable list and bend radius |
| SP-016 | Limit switch | Omron; Panasonic; MISUMI; TraceParts | TraceParts or manufacturer CAD | SLDPRT; STEP | manual_download_required | possible | yes | not_allowed_for_freeze | Safety and homing part |
| SP-017 | Photoelectric sensor | SICK; Keyence; Omron; TraceParts | TraceParts or manufacturer CAD | SLDPRT; STEP | manual_download_required | possible | yes | not_allowed_for_freeze | Sensing distance not frozen |
| SP-018 | Barcode scanner module envelope | Keyence; SICK; Datalogic | Vendor CAD or TraceParts | SLDPRT; STEP | manual_download_required | likely | yes | fallback_allowed_temporarily | Envelope allowed until scanner selected |
| SP-019 | Emergency stop button | Schneider; Siemens; IDEC; TraceParts | TraceParts or manufacturer CAD | SLDPRT; STEP | manual_download_required | possible | yes | not_allowed_for_freeze | Safety-rated component |
| SP-020 | Control enclosure | Hammond; Rittal; McMaster-Carr; MISUMI | Supplier CAD | STEP | manual_download_required | possible | yes | fallback_allowed_temporarily | Final size depends on electronics |
| SP-021 | Aluminum extrusion or support frame components | MISUMI; McMaster-Carr; Bosch Rexroth-equivalent | MISUMI/McMaster CAD | STEP | manual_download_required | possible | yes | fallback_allowed_temporarily | Slot standard must be fixed |
| SP-022 | Angle bracket | MISUMI; McMaster-Carr; Bosch Rexroth-equivalent | Supplier CAD | STEP | manual_download_required | possible | yes | fallback_allowed_temporarily | Depends on extrusion family |
| SP-023 | Fasteners | MISUMI; McMaster-Carr | Supplier catalog/CAD | STEP optional | not_started | possible | yes | fallback_allowed_temporarily | Release BOM needs exact sizes |
| SP-024 | Transparent PC guard hardware | McMaster-Carr; MISUMI; local sheet supplier | Supplier CAD and panel drawings | STEP for hardware | manual_download_required | possible | yes | fallback_allowed_temporarily | Panels likely defined by drawings |
| SP-025 | Right Y-axis module or guide assembly | MISUMI; THK; HIWIN-equivalent | MISUMI CAD/configurator | SLDASM/SLDPRT; STEP; X_T | manual_download_required | likely | yes | not_allowed_for_freeze | Must match left Y height and datum |
| SP-026 | Y-axis mechanical synchronization mechanism | MISUMI; Gates; McMaster-Carr | Supplier CAD/catalog | SLDPRT; STEP | manual_download_required | possible | yes | not_allowed_for_freeze | Mechanical sync is preferred over dual Y motors |
| SP-027 | Gantry beam related mounting hardware | MISUMI; McMaster-Carr; profile suppliers | Supplier CAD/catalog and later drawings | STEP optional | manual_download_required | possible | yes | not_allowed_for_freeze | Controls beam squareness and X datum |
