# Custom Parts Interface Requirements

## Purpose

This document defines what each custom part must extract from real standard-part CAD before detailed modeling. Stage 2 does not create CAD models.

| Custom part | Dependent standard parts | Dimensions to extract | Holes/slots to reserve | Cable/drag-chain points | Material and surface | Drawing requirements | Initial modeling risk |
|---|---|---|---|---|---|---|---|
| Base plate | Y module/rails, rack hardware, guard hardware, control enclosure | Rail/module hole patterns, rack origins, enclosure footprint | Axis mounting holes, rack fixing holes, locating pin holes, guard bracket holes | Rear cable exit and fixed drag-chain bracket | 6061-T6 aluminum, anodized | Overall dimensions, hole table, datums, tolerances | Hole layout changes if Y module is replaced |
| Input tube rack | Tube geometry, gripper clearance, locating pins | Hole diameter, pitch, cap clearance, locating pin spacing | Rack fixing holes, locating pin holes | none | POM or PC, deburred | Hole array drawing, material callout | Gripper clearance may change after gripper selection |
| Output tube rack | Tube geometry, gripper clearance, locating pins | Hole diameter, pitch, cap clearance, locating pin spacing | Rack fixing holes, locating pin holes | none | POM or PC, deburred | Hole array drawing, material callout | Coordinate mismatch affects placement accuracy |
| X-axis bridge connection plate | Y carriage CAD, X module CAD | Y carriage top hole pattern, X module base hole pattern, bridge height | Mounting holes and adjustment slots | Moving cable clamp if required | 6061-T6 aluminum, anodized | Hole pattern, flatness, datum faces | Gantry parallelism may require slot adjustment |
| Y-axis support plate | Y module/guide CAD, base plate datum | Rail/module base holes, rail centerline height | Base holes and Y-axis adjustment slots | Fixed cable route holes | 6061-T6 aluminum, anodized | Datum and parallelism requirements | Rail misalignment can bind the gantry |
| Z-axis connection plate | X carriage CAD, Z module CAD | X carriage top holes, Z module rear face holes, Z travel envelope | Mounting holes and vertical adjustment slots | Z motor cable strain relief | 6061-T6 aluminum, anodized | Hole pattern and perpendicularity | Z module may collide with bridge or rack |
| Gripper adapter plate | Z carriage CAD, gripper CAD | Z carriage holes, gripper flange holes, gripper centerline offset | Adapter holes and dowel pin holes if available | Gripper cable clamp | 6061-T6 aluminum, anodized | Centerline dimension, hole table | Tube center may shift if gripper CAD changes |
| Sensor bracket | Photoelectric sensor, barcode scanner, gripper geometry | Sensor mounting holes, sensing axis, connector clearance | Sensor holes and adjustment slots | Sensor cable tie points | Aluminum or sheet metal, anodized or powder coated | Bend/slot dimensions and sensing axis reference | Sensor view may be blocked by gripper/tube |
| Protective cover bracket | Aluminum profiles, hinges, latches, PC panels | Profile slot geometry, hinge holes, latch geometry, panel thickness | Profile holes, panel clip holes, hinge/latch slots | Optional cable pass-through | Aluminum profile or 6061-T6, clear anodized | Guard frame dimensions and hardware holes | Access doors may interfere with moving axes |
| Control box mounting plate | Control enclosure, emergency stop, cable glands | Enclosure mounting holes, E-stop panel cutout, connector clearance | Enclosure holes, cable gland holes, E-stop holes | Cable gland and strain relief points | Aluminum or sheet metal, powder coated/anodized | Panel cutout drawing, hole table | Electronics volume may change enclosure size |

## Rule

When standard-part CAD is unavailable, use only provisional envelope dimensions and mark the related custom-part interface as not frozen.
