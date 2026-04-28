# Priority A Manual CAD Download Queue

Stage 3A prepares the manual download queue only. No CAD is downloaded in this stage, and no part is marked as `downloaded`.

| Queue item | part_id | Recommended spec range | Supplier type | CAD format | Target folder | Manual download required | Parameters to record after download | Affected custom parts | Risk if CAD is missing |
|---|---|---|---|---|---|---|---|---|---|
| X-axis belt driven linear module | SP-001 | Travel >=420 mm, carriage payload for Z module and gripper, repeatability target +/-0.5 mm | MISUMI, THK, HIWIN-equivalent linear actuator suppliers | SLDASM/SLDPRT, STEP/STP, X_T | `03_cad/standard_parts/downloaded/x_axis_module/` | yes | Supplier, model, stroke, carriage size, mounting holes, carriage height, motor side, moving mass, CAD format, source URL, download date | Base plate, X bridge adapter, Z connection plate, drag-chain bracket | X bridge and Z adapter hole positions cannot be frozen |
| Y-axis belt driven linear module or dual-rail belt assembly | SP-002 | Travel >=260 mm, gantry support, dual-guide or synchronized drive if required | MISUMI, HIWIN-equivalent, THK guide plus belt assembly suppliers | SLDASM/SLDPRT, STEP/STP, X_T | `03_cad/standard_parts/downloaded/y_axis_module/` | yes | Supplier, model, stroke, rail spacing, carriage top height, drive side, motor mount, moving mass, CAD source | Base plate, Y support plates, X bridge connection plates | Gantry parallelism and bridge mounting cannot be verified |
| Z-axis lead screw lifting module | SP-003 | Travel >=120 mm, compact carriage, low backlash, vertical holding margin | MISUMI, THK, HIWIN-equivalent actuator suppliers | SLDASM/SLDPRT, STEP/STP, X_T | `03_cad/standard_parts/downloaded/z_axis_module/` | yes | Supplier, model, stroke, lead, carriage face, motor orientation, screw efficiency if available, moving mass | Z connection plate, gripper adapter, sensor bracket | Z stroke, motor clearance, and gripper centerline may be wrong |
| Electric two-finger parallel gripper | SP-013 | Stroke suitable for 13 mm tube plus pads, compact flange, controllable force | SMC, Festo, equivalent electric gripper suppliers | SLDASM/SLDPRT, STEP/STP | `03_cad/standard_parts/downloaded/gripper/` | yes | Supplier, model, stroke, gripping force, mass, flange holes, finger interface, cable exit, CAD source | Gripper adapter, soft pads, sensor bracket, Z plate | Tube may not align with gripper center or may be damaged |
| X/Y/Z motors | SP-004; SP-005; SP-006 | Closed-loop stepper or compact servo, torque-speed curve matched to axis | Oriental Motor, Leadshine, Delta, MISUMI, 3D ContentCentral references | SLDPRT, STEP/STP | `03_cad/standard_parts/downloaded/motors/` | yes | Supplier, model, frame size, shaft diameter, shaft length, flange holes, body length, connector/cable exit, torque-speed curve reference | Motor plates, coupling region, cable routing, axis module motor interface | Motor may not fit, shaft/coupling may mismatch, torque may be insufficient |
| X/Y/Z linear guides and sliders | SP-007 | Compact linear guide size, length per axis or integrated into module | THK, HIWIN, MISUMI | SLDPRT, STEP/STP, X_T | `03_cad/standard_parts/downloaded/linear_guides/` | yes | Supplier, series, rail length, block type, rail hole pitch, block height, block mounting holes, preload if known | Base plate, axis plates, carriage plates | Hole pattern and carriage height cannot be trusted |
| Timing belt | SP-008 | GT/HTD belt class, width and length based on axis module and pulley | MISUMI, Gates, McMaster-Carr | STEP/STP if available, catalog data acceptable for belt length | `03_cad/standard_parts/downloaded/belts_pulleys/` | yes | Supplier, belt type, pitch, width, length, reinforcement, allowable tension, source | Belt covers, pulley supports, module envelope | Belt length and stiffness assumptions may be wrong |
| Timing belt pulley | SP-009 | Tooth count and bore matched to motor/shaft; pitch matched to belt | MISUMI, McMaster-Carr, Gates | SLDPRT, STEP/STP | `03_cad/standard_parts/downloaded/belts_pulleys/` | yes | Supplier, tooth count, pitch, bore, width, hub type, set screw/key details, pitch diameter | Motor mount, shaft support, belt cover | Torque estimate and shaft stack may be invalid |
| Lead screw | SP-010 | Lead and nut type for 120 mm Z travel; backlash and efficiency reviewed | MISUMI, THK, McMaster-Carr | SLDPRT, STEP/STP, X_T | `03_cad/standard_parts/downloaded/lead_screws/` | yes | Supplier, screw diameter, lead, nut style, nut holes, efficiency, backlash, CAD source | Z screw support, nut mount, motor/coupling stack | Z torque, speed and holding behavior cannot be estimated |
| Coupling | SP-011 | Flexible coupling with bores matching motor and screw/pulley shaft | MISUMI, McMaster-Carr, Ruland-equivalent | SLDPRT, STEP/STP | `03_cad/standard_parts/downloaded/couplings_bearings/` | yes | Supplier, bore sizes, length, outer diameter, rated torque, clamp/set-screw type | Motor plates, bearing supports, Z screw connection | Shaft spacing and coupling clearance may be wrong |
| Bearing block | SP-012 | Compact support bearing or pillow/flanged block matched to shaft | MISUMI, McMaster-Carr, TraceParts | SLDPRT, STEP/STP | `03_cad/standard_parts/downloaded/couplings_bearings/` | yes | Supplier, bore, center height, mounting holes, bearing type, support style | Bearing support plates, belt/screw brackets | Shaft centerline and support holes cannot be finalized |
| Limit switch | SP-016 | Mechanical or proximity home/limit switch, compact mount, repeatable actuation | Omron, Panasonic, MISUMI, TraceParts | SLDPRT, STEP/STP | `03_cad/standard_parts/downloaded/safety/` | yes | Supplier, model, body size, mounting holes, actuation direction, cable/connector, repeatability if available | Axis end brackets, home targets, wiring holes | Homing and travel limit brackets may be redesigned |
| Emergency stop button | SP-019 | Safety-rated 22 mm panel-mount mushroom E-stop with contact block | Schneider, Siemens, IDEC, TraceParts | SLDPRT, STEP/STP | `03_cad/standard_parts/downloaded/safety/` | yes | Supplier, model, panel cutout, contact block depth, wiring clearance, safety rating, CAD source | Control box panel, guard panel | Safety panel cutout and operator access envelope may be wrong |

## Manual Download Rule

Keep `manual_download_required` whenever a supplier portal requires login, registration, captcha, configurator selection, license acceptance, or manual CAD format selection.

## Manual Download Steps

Use these steps for each Priority A item:

1. Open the supplier or trusted CAD source page listed in `priority_a_auto_download_feasibility.csv`.
2. Select the exact series, model, travel, stroke, rail length, motor flange, bore, lead, tooth count, or safety component variant required by the design.
3. If the site requires login, registration, captcha, license acceptance, or CAD format selection, complete that manually; do not automate or bypass it.
4. Prefer `SLDPRT/SLDASM`, then `STEP/STP`, then `X_T`, then `IGES`.
5. Rename the downloaded file using `standard_parts_file_naming_rule.md`.
6. Place the file in the matching `03_cad/standard_parts/downloaded/<category>/` folder.
7. Run `python tools/check_standard_cad_files.py`.
8. Only after the file exists and passes intake checks, update `CAD_download_status_v2.md` and `standard_parts_bom_v1.csv`.
9. Record supplier, model, source URL, download date, format, and manual download requirement.

## Stage 3A-2 Accessibility Notes

- THK, MISUMI, igus, TraceParts, and McMaster entry pages were reachable.
- SMCWorld showed access-limited behavior in this environment.
- 3DContentCentral timed out in this environment.
- No direct public CAD file link was verified, so no automatic CAD download was performed.
