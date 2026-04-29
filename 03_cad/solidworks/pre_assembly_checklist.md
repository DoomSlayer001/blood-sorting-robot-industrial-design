# SolidWorks Pre-Assembly Checklist

## 1. Existing CAD Check

- [ ] X-axis MSA-628 module CAD available and registered.
- [ ] Left Y-axis MSA-628 module CAD available and registered.
- [ ] Right Y-axis MSA-628 module CAD available and registered.
- [ ] Z-axis MISUMI LS10 module CAD available and registered.
- [ ] SMC LEHF20 gripper CAD available and registered.
- [ ] Oriental Motor AZM46AK motor CAD available and registered.
- [ ] OMRON D4N limit switch CAD available and registered.
- [ ] Panasonic CX-421-J photoelectric sensor CAD available and registered.
- [ ] Cognex DataMan 80 USB barcode reader CAD available and registered.
- [ ] MISUMI MHPKS cable carrier CAD available and registered.
- [ ] simplified blood collection tube STEP files available.
- [ ] input/output/manual-review tube bin STEP files available.

## 2. Requirement Check

- [ ] classification count `n = 4`.
- [ ] six tube boxes/bins total.
- [ ] one 4 x 6 mixed input rack.
- [ ] four 2 x 3 category output bins.
- [ ] one 2 x 3 manual review bin.
- [ ] one scanning station.
- [ ] exception handling logic documented.
- [ ] label-facing-scanner assumption documented.
- [ ] no tube rotation mechanism in current design.
- [ ] output bin capacity rule documented.
- [ ] tube height handling rule documented.

## 3. Assembly Check

- [ ] base plate size set to 1100 mm x 900 mm x 15 mm.
- [ ] left/right Y axes parallel and coplanar.
- [ ] gantry beam connects left and right Y carriages squarely.
- [ ] X-axis module mounted on gantry beam without collision.
- [ ] Z-axis module orientation supports vertical pick/place.
- [ ] gripper fingers align with tube centerline.
- [ ] gripper can grip the 13 mm tube body below the cap.
- [ ] scanner line-of-sight reaches the tube label.
- [ ] photoelectric sensor detects the scan reference position.
- [ ] cable chain path clears gantry and brackets.
- [ ] emergency stop is reachable by operator.
- [ ] control box has service and cable clearance.

## 4. Before Layout Freeze

- [ ] import initial workspace layout table.
- [ ] place bins using temporary datums.
- [ ] verify gripper reach to all hole centers.
- [ ] check safe-height clearance for 100 mm tube.
- [ ] check scanner/sensor bracket interference.
- [ ] update layout table with final SolidWorks coordinates.
