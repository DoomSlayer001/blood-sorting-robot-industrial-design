# CAD Download Priority List

This priority list follows the dual-side gantry architecture. No CAD is marked as downloaded until a real supplier file exists under `03_cad/standard_parts/downloaded/` and passes the intake check.

## Priority A: Must Use Real CAD First

| Item | Why real CAD is required | Affects custom parts | Risk if CAD is missing |
|---|---|---|---|
| Left Y-axis module | Defines left datum height, carriage face, mounting holes, drive/sync side, and base interface | Base plate, left Y support plate, gantry beam left end plate, sync input bracket | Left/right Y mismatch can cause gantry skew or binding |
| Right Y-axis module | Defines matched support height, guide face, carriage top plane, and right base interface | Base plate, right Y support plate, gantry beam right end plate | Gantry beam may not stay parallel to the base or left Y side |
| Y-axis mechanical synchronization mechanism | Defines shaft/belt path, pulley pitch, bearing center height, coupling stack, and tensioning envelope | Y drive bracket, bearing supports, belt covers, base holes, gantry hardware | Synchronization may be impossible to package or may introduce racking |
| X-axis belt module on gantry | Defines carriage height, module length, mounting holes, motor side, belt cover, and travel envelope | Gantry beam, X module mounting plate, Z connection plate, drag-chain bracket | X/Z/gripper interface cannot be frozen |
| Z-axis lead screw lifting module | Defines vertical carriage, screw/motor package, stroke, and gripper mounting area | Z connection plate, gripper adapter, sensor bracket | Z travel or gripper package may collide with rack/tubes |
| Electric two-finger parallel gripper | Defines flange, mass, finger stroke, cable exit, and finger centerline | Gripper adapter, soft pads, sensor bracket | Tube cannot be reliably gripped or centered |
| X/Y/Z motors | Defines flange, shaft, body length, cable exit, inertia, and torque constraints | Motor plates, coupling region, cable routing | Motor may not fit or may be undersized |
| X/Y/Z linear guides and sliders | Defines rail hole pitch, block top plane, block height, and preload envelope if not integrated into modules | Base plate, axis plates, carriage plates | Hole locations and axis heights become wrong |
| Timing belts, pulleys, lead screw, couplings, bearing blocks | Defines pulley bore, shaft stack, screw lead, bearing block holes, and synchronization geometry | Motor mounts, bearing supports, drive guards, Y sync supports | Torque path and mechanical stack cannot be frozen |
| Limit switches | Defines switch body, actuator direction, mounting holes, and trigger target | Axis end brackets, home targets, cable routing | Homing repeatability and safety limits unreliable |
| Emergency stop button | Defines panel cutout, contact block depth, and operator access envelope | Control box panel, safety cover panel | Safety panel layout may be wrong |

## Priority B: Real CAD Recommended

| Item | Why real CAD is useful | Affects custom parts | Risk if CAD is missing |
|---|---|---|---|
| Drag chain | Defines bend radius, moving/fixed end, chain width and height for gantry/X/Z cable routing | Cable brackets, rear support, moving carriage bracket | Cable chain may collide or exceed bend radius |
| Photoelectric sensor | Defines sensing axis, body size, connector clearance | Sensor bracket, rack detection features | Sensor cannot be aimed or mounted properly |
| Barcode scanner envelope | Defines scan axis, body size, connector and field of view | Scanner bracket, gripper-side or fixed-station mount | Barcode may not be visible or within focus distance |
| Aluminum extrusion | Defines slot geometry, profile size, compatible nuts | Guard frame, support frame, accessory brackets | Incompatible angle brackets or panel clips |
| Angle brackets | Defines hole positions and slot engagement | Guard frame, profile supports | Frame cannot be assembled as intended |
| Fasteners | Defines head diameter, clearance, washer stack | All custom parts with holes/counterbores | Hole sizes or counterbores may be wrong |

## Priority C: Temporary Fallback Allowed

| Item | Why fallback can be temporary | Affects custom parts | Risk if CAD is missing |
|---|---|---|---|
| Control enclosure shell | Early layout can use bounding box | Control box mounting plate, cable exit area | Final panel cutouts and mounting holes may change |
| Cables | Cable routes can use diameter bundles first | Drag-chain fill, cable clips | Bend radius and connector clearances may be underestimated |
| Cable clips | Can be selected after cable route is fixed | Cable bracket holes | Minor hole pattern changes |
| Protective cover hardware | Panels and hardware can be finalized after guard concept | Guard frame, access doors, PC panels | Hinge/latch holes may move |
| Appearance trim parts | Not part of mechanical datum chain | Cover panels only | Low mechanical risk |
