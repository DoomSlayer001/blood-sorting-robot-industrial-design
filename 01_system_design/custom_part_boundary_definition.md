# Custom Part Boundary Definition

## Custom Parts Required

| Custom part | Wait for standard CAD | Material | Manufacturing method | Drawing required | Strength check | Key dimensions come from |
|---|---|---|---|---|---|---|
| Base plate | Y-axis module/rails, rack mounts, guard hardware, control box mount | 6061-T6 aluminum | CNC machining | yes | yes | Axis mounting holes, rack datum holes, enclosure brackets |
| Input tube rack | Tube geometry, rack coordinate plan, gripper clearance | POM or PC | CNC machining | yes | no, stiffness review recommended | 4x6 hole array, 13 mm tube, locating pins |
| Output tube rack | Tube geometry, rack coordinate plan, gripper clearance | POM or PC | CNC machining | yes | no, stiffness review recommended | 4x6 hole array, 13 mm tube, locating pins |
| X-axis bridge connection plate | Y carriage CAD, X module CAD | 6061-T6 aluminum | CNC machining | yes | yes | Y carriage holes, X module base holes, bridge height |
| Y-axis support plate | Y module/rail CAD, base plate datum | 6061-T6 aluminum | CNC machining | yes | yes | Y rail/module mounting holes, base hole pattern |
| Z-axis connection plate | X carriage CAD, Z module CAD | 6061-T6 aluminum | CNC machining | yes | yes | X carriage holes, Z module rear face, cable clearance |
| Gripper adapter plate | Z carriage CAD, gripper CAD | 6061-T6 aluminum | CNC machining | yes | yes | Z carriage holes, gripper flange, gripping centerline |
| Sensor bracket | Photoelectric sensor/barcode scanner CAD, gripper/rack geometry | 6061-T6 aluminum or sheet metal | CNC machining or sheet-metal bending | yes | no, vibration review recommended | Sensor mounting holes, sensing axis, connector clearance |
| Protective cover bracket | Aluminum profile, hinges, latches, PC panel thickness | 6061-T6 aluminum or profile brackets | CNC machining or profile assembly | yes | yes for guard supports | Extrusion slot, panel hardware, access doors |
| Control box mounting plate | Control enclosure CAD, emergency stop, cable exits | 6061-T6 aluminum or sheet metal | CNC machining or sheet-metal bending | yes | no, stiffness review recommended | Enclosure mounting holes, E-stop panel cutout, cable glands |

## Boundary Rule

Custom parts define the robot-specific geometry. Standard parts define the fixed industrial interfaces. If a standard-part CAD file is not yet available, the related custom-part hole pattern must remain provisional.

## Design Freeze Rule

A custom part cannot reach design freeze until all Priority A standard parts that define its mounting holes, contact faces, travel envelope, or safety interfaces are available as real CAD or approved supplier drawings.
