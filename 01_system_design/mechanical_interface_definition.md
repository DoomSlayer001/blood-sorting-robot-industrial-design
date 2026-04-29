# Mechanical Interface Definition

## Left Y-Axis Interfaces

- Selected standard module: MISUMI MSA-628, configuration `MSA-628-B-AB-B1-0750`.
- Mounting face: base plate or support rail datum for the left Y module.
- Mounting holes: supplier CAD hole pattern drives the base plate and left support plate.
- Carriage interface: left Y carriage top face connects to the gantry beam.
- Drive side: preferred location for the single Y motor or synchronization input.
- Limit switch targets: home and end-limit switch brackets must reference the left Y travel.

## Right Y-Axis Interfaces

- Selected standard module: MISUMI MSA-628, configuration `MSA-628-B-AB-B1-0750`.
- Mounting face: base plate or support rail datum for the right Y module.
- Mounting holes: supplier CAD hole pattern drives the base plate and right support plate.
- Carriage interface: right Y carriage top face connects to the gantry beam.
- Guide side: may be driven through the synchronization mechanism or act as the synchronized guide side.
- Parallelism: right Y datum must remain parallel to left Y datum.

## Gantry Beam To Y-Carriage Interfaces

- Left/right carriage connection holes must come from real Y-axis carriage CAD.
- The gantry beam connection must resist yaw, pitch, and roll caused by acceleration and gripper loads.
- Adjustment slots may be used for initial squaring, but final datums must be locked by pins or controlled hole fits.
- Beam end plates must align left and right Y carriage top planes.

## X-Axis Module On Gantry Interfaces

- Selected standard module: MISUMI MSA-628, configuration `MSA-628-B-AB-B1-0750`.
- X module base mounting face attaches to the gantry beam front or top mounting surface.
- X module mounting holes must come from real supplier CAD.
- X carriage top/front face defines the Z module connection.
- X motor side and cable exit must be coordinated with drag-chain routing.
- The X module uses the same MSA-628 series as the left/right Y modules, but it is a separate SolidWorks instance with a different assembly orientation and role.

## MSA-M6S Note

MISUMI MSA-M6S was considered as a higher-rigidity candidate. Because its larger package size is not the current mainline fit for this desktop blood sorting layout, it is not included in the active BOM. It may remain only as an engineering comparison note.

## Gantry Beam Deflection And Parallelism

- The gantry beam must be checked for deflection under the X module, Z module, gripper, tube, cable chain, and acceleration loads.
- Y-axis left/right parallelism must be defined from base datums and verified in SolidWorks.
- X-axis straightness depends on gantry beam stiffness and mounting flatness.

## Y-Axis Synchronization Mechanism Interfaces

- Preferred architecture: single motor plus synchronization shaft or synchronization belt linkage.
- Synchronization mechanism must define shaft/pulley/bearing support positions.
- Couplings, pulleys, and bearing blocks require real CAD before bracket holes are frozen.
- Belt tension or shaft alignment features must be accessible for assembly and maintenance.

## Z-Axis Module Interfaces

- X carriage connection face: Z module rear or base face mounts to X slider adapter plate.
- Z slider mounting face: front carriage face defines gripper adapter location.
- Screw/motor space: reserve vertical and rear clearance for motor, screw, coupling, and cable exit.
- Gripper adapter holes: supplier gripper flange and Z carriage hole pattern define adapter plate holes.
- Z axis does not use MSA-628. It remains a separate lead-screw lifting module to be selected later.

## Gripper Interfaces

- Z adapter mounting holes: use real gripper flange CAD or supplier drawing.
- Finger opening range: must clear 13 mm tube diameter plus tolerance and soft-pad thickness.
- Gripping centerline: centerline must align with tube rack hole center coordinates.
- Tube gripping height: soft pads should grip below cap and above rack top surface, with clearance for 75 mm tube height.
- Frozen gripping assumption: grip the 13 mm tube body about 15-25 mm below the cap.
- Pad material: TPU or silicone soft pads.
- Force strategy: use low-force gripping below the SMC LEHF20 maximum 28 N value; final force requires tube and pad validation.

## Tube Rack Interfaces

- Fixing holes: rack mounting holes attach to base plate with repeatable location.
- Locating pins: recommended for input/output rack repeatability.
- Hole array origin: define first hole center as local rack origin reference.
- Input/output coordinate systems: each rack has a local coordinate system mapped into the base/world coordinate system.
- Input rack: 4 x 6, 24 vertical positions for randomly mixed tube categories; loose or piled tube feeding is not included.
- Output bins: four separate 2 x 3 bins, one each for Category A, Category B, Category C, and Category D.
- Manual review bin: one 2 x 3 bin, used for barcode failure, unknown category, full output category, or abnormal samples.
- Physical tube box/rack count: six total, including one mixed input rack, four category output bins, and one manual review bin.
- Recommended placement: input rack in the rear area, scanning station in the middle area, output bins in a 2 x 2 group in the front or front-right area, and manual review bin at a front corner or near the output edge.
- Mixed tube accommodation: rack and gripper clearances should account for different cap colors, label positions, barcode labels, and possible tube height variants.

## Scanning Station Interfaces

- Photoelectric sensor: Panasonic CX-421-J detects whether a tube is present at the scanning position and provides the trigger condition.
- Barcode reader: Cognex DataMan 80 USB fixed-mount image-based reader scans 1D/2D barcode or QR code labels on the tube.
- Tube presentation: gripper centerline, tube label face, sensor optical axis, and barcode reader field of view must be defined as adjustable station interfaces.
- Bracket adjustment: sensor and scanner brackets should include adjustment slots or datum features for focus distance, reading angle, and tube-to-reader alignment.
- Exception routing: failed read, unknown category, full target category bin, or abnormal sample sends the tube to the `manual_review_bin`.
- Interference rule: scanner, sensor, racks, output bins, and gripper-held tubes must be checked for clearance before final bracket and bin positions are frozen.
- Scanning assumption: no tube rotation mechanism is included in the current layout; the label is assumed to face the scanner-visible side.

## Cable Chain And Wiring Interfaces

- Fixed drag-chain end should mount to the rear frame or base support.
- Moving drag-chain end should mount to the gantry beam or X carriage depending on cable route.
- X/Z/gripper cable exit must not collide with tube racks or protective cover.
- Cable service loops must not enter the gripper pick/place envelope.

## Rule

Custom parts must not be finalized from placeholder geometry. They must reference real standard-part CAD faces, axes, and hole patterns before design freeze.
