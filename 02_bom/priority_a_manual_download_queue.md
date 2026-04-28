# Priority A Manual CAD Download Queue

Stage 3A/architecture switch update: the main mechanical architecture is now a dual-side gantry Cartesian robot. No CAD is downloaded in this stage, no fallback model is treated as a real standard part, and no part is marked as `downloaded`.

The Y axis is mechanically dual-side: `Y_left = Y_right = y`. The preferred implementation is one drive source with mechanical synchronization through a timing shaft, belt loop, or equivalent coupling. If a later design uses two Y motors, a separate synchronization-control and anti-racking risk document is required.

| Priority | Queue item | part_id | Recommended spec range | Supplier type | CAD format | Target folder | Manual download required | Parameters to record after download | Affected custom parts | Risk if CAD is missing |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | left_y_axis_module | SP-002 | Belt-driven or guide-supported Y module, travel 260-300 mm, matched height with right side | MISUMI, THK, HIWIN-equivalent, industrial linear module suppliers | SLDASM/SLDPRT, STEP/STP, X_T | `03_cad/standard_parts/downloaded/y_axis_module/` | yes | Supplier, series, stroke, rail/carriage height, mounting hole pitch, drive-side geometry, carriage top face, parallelism reference, CAD source, download date | Base plate, left Y support plate, gantry beam end plate, drag-chain bracket | Left/right Y spacing and gantry beam mounting holes cannot be frozen |
| A2 | right_y_axis_module | SP-025 | Right-side support/guide module matched to left side, travel 260-300 mm | MISUMI, THK, HIWIN-equivalent, industrial linear module suppliers | SLDASM/SLDPRT, STEP/STP, X_T | `03_cad/standard_parts/downloaded/y_axis_module/` | yes | Supplier, series, stroke, rail/carriage height, mounting hole pitch, carriage top face, guide preload if available, CAD source, download date | Base plate, right Y support plate, gantry beam end plate | Gantry may rack or bind if right-side height and hole pattern are assumed |
| A3 | y_axis_sync_mechanism | SP-026 | Single-motor mechanical synchronization by timing shaft, cross belt, pulley pair, or equivalent Y coupling | MISUMI, Gates, McMaster-Carr, industrial belt/shaft suppliers | SLDPRT, STEP/STP, X_T | `03_cad/standard_parts/downloaded/belts_pulleys/` | yes | Belt pitch/width, pulley tooth count, shaft diameter, bearing spacing, tension adjustment method, coupling details, allowable torque, CAD/source data | Base plate, Y support plates, bearing brackets, belt covers, motor mount | Y-left/Y-right synchronization and anti-racking envelope cannot be verified |
| A4 | x_axis_module_on_gantry | SP-001 | Belt-driven X module mounted on gantry beam, travel 450-500 mm, payload for Z module and gripper | MISUMI, THK, HIWIN-equivalent linear actuator suppliers | SLDASM/SLDPRT, STEP/STP, X_T | `03_cad/standard_parts/downloaded/x_axis_module/` | yes | Supplier, series, stroke, carriage size, module length, carriage top height, mounting holes, motor side, moving mass, CAD source, download date | Gantry beam, X mounting plate, Z connection plate, drag-chain bracket | X module envelope and Z mounting interface cannot be frozen |
| A5 | z_axis_screw_module | SP-003 | Lead-screw lifting module, travel 120 mm, compact carriage, vertical holding margin | MISUMI, THK, HIWIN-equivalent actuator suppliers | SLDASM/SLDPRT, STEP/STP, X_T | `03_cad/standard_parts/downloaded/z_axis_module/` | yes | Supplier, series, stroke, lead, carriage face, motor orientation, screw efficiency if available, moving mass, CAD source | Z connection plate, gripper adapter, sensor bracket | Z stroke, motor clearance, and gripper centerline may be wrong |
| A6 | electric_parallel_gripper | SP-013 | Electric two-finger parallel gripper, stroke for 13 mm tube plus pads, controllable force | SMC, Festo, equivalent electric gripper suppliers | SLDASM/SLDPRT, STEP/STP | `03_cad/standard_parts/downloaded/gripper/` | yes | Supplier, model, stroke, gripping force, mass, flange holes, finger interface, cable exit, CAD source | Gripper adapter, soft pads, sensor bracket, Z plate | Tube centerline and finger-pad geometry cannot be verified |
| A7 | motors | SP-004; SP-005; SP-006 | Closed-loop stepper or compact servo matched to X, synchronized Y, and Z screw loads | Oriental Motor, Leadshine, Delta, MISUMI, 3D ContentCentral references | SLDPRT, STEP/STP | `03_cad/standard_parts/downloaded/motors/` | yes | Supplier, model, frame size, shaft diameter, shaft length, flange holes, body length, connector/cable exit, torque-speed curve reference | Motor plates, coupling/pulley stack, cable routing, axis module motor interfaces | Motor may not fit, shaft/coupling may mismatch, torque estimate may be invalid |
| A8 | limit_switches | SP-016 | Compact mechanical/proximity home and limit switches for X/Y/Z, repeatable actuation | Omron, Panasonic, MISUMI, TraceParts | SLDPRT, STEP/STP | `03_cad/standard_parts/downloaded/safety/` | yes | Supplier, model, body size, mounting holes, actuation direction, cable/connector, repeatability if available | Axis end brackets, home targets, wiring holes | Homing brackets and travel-limit clearances may be redesigned |
| A9 | emergency_stop | SP-019 | Safety-rated 22 mm panel-mount mushroom E-stop with contact block | Schneider, Siemens, IDEC, TraceParts | SLDPRT, STEP/STP | `03_cad/standard_parts/downloaded/safety/` | yes | Supplier, model, panel cutout, contact block depth, wiring clearance, safety rating, CAD source | Control box panel, guard panel | Safety panel cutout and operator access envelope may be wrong |

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
