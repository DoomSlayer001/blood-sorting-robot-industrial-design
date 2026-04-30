# Custom Part Dependency Plan v1

## Purpose

This plan lists custom parts needed after the SolidWorks first rough assembly. It defines function, standard-part dependencies, whether the part should wait for rough-assembly confirmation, material, STEP need, and drawing need.

## Priority A

| custom_part | function | depends_on | wait_for_rough_assembly | suggested_material | step_needed | drawing_needed |
|---|---|---|---|---|---|---|
| `base_plate_1100x900x15` | main mounting datum for all modules and bins | Y modules, bins, control box, emergency stop, guards | yes | 6061-T6 aluminum | yes | yes |
| `y_axis_mounting_plates_left_right` | mount left/right MSA-628 modules to base/frame | MISUMI MSA-628, base plate | yes | 6061-T6 aluminum | yes | yes |
| `gantry_side_supports` | connect Y carriages to gantry beam ends | left/right MSA-628 carriages, gantry beam | yes | 6061-T6 aluminum | yes | yes |
| `x_axis_gantry_mounting_plate` | mount X-axis MSA-628 onto gantry beam | X-axis MSA-628, gantry beam | yes | 6061-T6 aluminum | yes | yes |
| `z_axis_adapter_plate` | attach LS10 Z module to X-axis carriage | MISUMI LS10, X-axis carriage | yes | 6061-T6 aluminum | yes | yes |
| `gripper_adapter_plate` | attach SMC LEHF20 gripper to Z carriage | SMC LEHF20, LS10 carriage | yes | 6061-T6 aluminum | yes | yes |
| `gripper_soft_pads` | compliant gripping surface for 13 mm tubes | SMC LEHF20 fingers, tube geometry | yes | TPU or silicone | yes | yes |
| `scanner_bracket` | hold Cognex DataMan 80 USB at scan station | Cognex scanner, scan station datum | yes | 6061-T6 aluminum or sheet metal | yes | yes |
| `photoelectric_sensor_bracket` | hold Panasonic CX-421-J at scan station | Panasonic sensor, scan station datum | yes | 6061-T6 aluminum or sheet metal | yes | yes |
| `limit_switch_brackets` | mount OMRON D4N switches near axes | OMRON D4N, X/Y/Z modules | yes | 6061-T6 aluminum or sheet metal | yes | yes |

## Priority B

| custom_part | function | depends_on | wait_for_rough_assembly | suggested_material | step_needed | drawing_needed |
|---|---|---|---|---|---|---|
| `cable_chain_mounting_brackets` | attach fixed/moving ends of cable chain | MISUMI MHPKS204, gantry/X/Z route | yes | 6061-T6 aluminum or sheet metal | yes | yes |
| `control_box_mounting_plate` | locate control box envelope near base edge | control box envelope, base plate | yes | 6061-T6 aluminum or sheet metal | yes | yes |
| `emergency_stop_mounting_plate` | mount emergency stop at operator edge | emergency stop placeholder, base/control panel | yes | sheet metal or 6061-T6 aluminum | yes | yes |
| `scan_station_reference_block` | physical datum or temporary alignment block for tube scanning | scanner, sensor, gripper/tube path | yes | POM, PC, or aluminum | yes | yes |
| `tube_bin_locator_pins_or_stoppers` | repeatable placement of input/output/manual bins | tube bins, base plate | yes | stainless steel pins or POM stops | yes | yes |

## Priority C

| custom_part | function | depends_on | wait_for_rough_assembly | suggested_material | step_needed | drawing_needed |
|---|---|---|---|---|---|---|
| `decorative_covers` | visual covers and simple guarding surfaces | final assembly envelope | yes | transparent PC or sheet metal | optional | optional |
| `cable_clips` | organize non-moving cables | cable routing plan | yes | nylon or printed plastic | optional | optional |
| `simplified_screw_sets` | visual fastener representation | final mounting holes | yes | 304 stainless steel | optional | no |
| `label_plates` | bin/axis/area identification labels | final area naming | no | plastic or adhesive label | optional | no |

## Notes

- Priority A parts should not be finalized before the first rough assembly is reviewed.
- All mounting holes must be derived from real CAD faces, axes, and hole patterns.
- STEP files are required for all structural custom parts before final SolidWorks assembly.
- Engineering drawings are required for all machined plates, brackets, and locating features before manufacturing release.
