# Mechanical Interface Definition

## Left Y-Axis Interfaces

- Mounting face: base plate or support rail datum for the left Y module/guide.
- Mounting holes: supplier CAD hole pattern drives the base plate and left support plate.
- Carriage interface: left Y carriage top face connects to the gantry beam.
- Drive side: preferred location for the single Y motor or synchronization input.
- Limit switch targets: home and end-limit switch brackets must reference the left Y travel.

## Right Y-Axis Interfaces

- Mounting face: base plate or support rail datum for the right Y module/guide.
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

- X module base mounting face attaches to the gantry beam front or top mounting surface.
- X module mounting holes must come from real supplier CAD.
- X carriage top/front face defines the Z module connection.
- X motor side and cable exit must be coordinated with drag-chain routing.

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

## Gripper Interfaces

- Z adapter mounting holes: use real gripper flange CAD or supplier drawing.
- Finger opening range: must clear 13 mm tube diameter plus tolerance and soft-pad thickness.
- Gripping centerline: centerline must align with tube rack hole center coordinates.
- Tube gripping height: soft pads should grip below cap and above rack top surface, with clearance for 75 mm tube height.

## Tube Rack Interfaces

- Fixing holes: rack mounting holes attach to base plate with repeatable location.
- Locating pins: recommended for input/output rack repeatability.
- Hole array origin: define first hole center as local rack origin reference.
- Input/output coordinate systems: each rack has a local coordinate system mapped into the base/world coordinate system.

## Cable Chain And Wiring Interfaces

- Fixed drag-chain end should mount to the rear frame or base support.
- Moving drag-chain end should mount to the gantry beam or X carriage depending on cable route.
- X/Z/gripper cable exit must not collide with tube racks or protective cover.
- Cable service loops must not enter the gripper pick/place envelope.

## Rule

Custom parts must not be finalized from placeholder geometry. They must reference real standard-part CAD faces, axes, and hole patterns before design freeze.
