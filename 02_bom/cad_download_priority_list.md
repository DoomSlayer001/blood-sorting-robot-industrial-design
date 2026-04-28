# CAD Download Priority List

## Priority A: Must Use Real CAD First

| Item | Why real CAD is required | Affects custom parts | Risk if CAD is missing |
|---|---|---|---|
| X-axis belt driven linear module | Defines carriage height, mounting holes, motor side, belt cover, travel envelope | Base plate, X beam adapter, Z connection plate, drag-chain bracket | Wrong interface can invalidate the whole gantry layout |
| Y-axis belt driven linear module or dual-rail belt assembly | Defines gantry support height, rail spacing, drive side, synchronization layout | Base plate, Y support plates, X bridge connection plates | Gantry racking, misaligned bridge, unusable stroke |
| Z-axis lead screw lifting module | Defines vertical carriage, screw/motor package, stroke, gripper mounting area | Z connection plate, gripper adapter, sensor bracket | Z travel or gripper package may collide with rack/tubes |
| Electric two-finger parallel gripper | Defines flange, mass, finger stroke, cable exit, finger centerline | Gripper adapter, soft pads, sensor bracket | Tube cannot be reliably gripped or centered |
| X/Y/Z motors | Defines flange, shaft, body length, cable exit, inertia and torque constraints | Motor plates, coupling region, cable routing | Motor may not fit or may be undersized |
| X/Y/Z linear guides and sliders | Defines rail hole pitch, block top plane, block height, preload envelope | Base plate, axis plates, carriage plates | Hole locations and axis heights become wrong |
| Timing belt, pulleys, lead screw, couplings, bearing blocks | Defines pulley bore, shaft stack, screw lead, bearing block holes | Motor mounts, bearing supports, drive guards | Torque path and mechanical stack cannot be frozen |
| Limit switches | Defines switch body, actuator direction, mounting holes, trigger target | Axis end brackets, home targets, cable routing | Homing repeatability and safety limits unreliable |
| Emergency stop button | Defines panel cutout, contact block depth, operator access envelope | Control box panel, safety cover panel | Safety panel layout may be wrong |

## Priority B: Real CAD Recommended

| Item | Why real CAD is useful | Affects custom parts | Risk if CAD is missing |
|---|---|---|---|
| Drag chain | Defines bend radius, moving/fixed end, chain width and height | Cable brackets, rear support, moving carriage bracket | Cable chain may collide or exceed bend radius |
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
