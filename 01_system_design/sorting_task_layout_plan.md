# Sorting Task Layout Plan

## 1. Task Definition

The project is a mixed blood collection tube automatic identification and classification sorting system. Multiple blood collection tube types are batch-loaded into the input rack with random positions and mixed categories. Each tube is inserted vertically. The robot picks tubes one by one, moves each tube to the scanning station, triggers barcode reading through tube-presence detection, queries the sample category, and places the tube into the matching output bin.

Barcode failures, unknown categories, full target bins, or abnormal samples are routed to the manual review bin.

## 2. Classification Quantity

The classification quantity is frozen as:

```text
n = 4
```

The default course demonstration categories are:

- Category A
- Category B
- Category C
- Category D

## 3. Tube Box / Rack Count

The physical tube box/rack count is frozen as six:

| item | quantity | layout | capacity | purpose |
|---|---:|---|---:|---|
| mixed input rack | 1 | 4 x 6 | 24 | random mixed input |
| Category A output bin | 1 | 2 x 3 | 6 | classified output |
| Category B output bin | 1 | 2 x 3 | 6 | classified output |
| Category C output bin | 1 | 2 x 3 | 6 | classified output |
| Category D output bin | 1 | 2 x 3 | 6 | classified output |
| manual review bin | 1 | 2 x 3 | 6 | exception handling |

The scanning station is not counted as a tube box because the tube is held by the gripper during scanning.

## 4. Input Rack

- Layout: 4 x 6.
- Capacity: 24 tubes.
- Function: mixed random input.
- Tube posture: vertical insertion only.
- Supported variation: cap color, label, barcode/QR code, and possible tube height variation.
- Excluded feeding mode: loose, piled, or bulk random tube feeding.

## 5. Output Bins

The output area uses four separate 2 x 3 bins:

- `category_a_bin`
- `category_b_bin`
- `category_c_bin`
- `category_d_bin`

Each output bin has six positions. A tube is placed into the bin matching the category returned from barcode lookup. If the matching bin is full, the tube is routed to the manual review bin.

## 6. Manual Review Bin

- Layout: 2 x 3.
- Capacity: 6 tubes.
- Identifier: `manual_review_bin`.
- Use cases:
  - barcode read failure.
  - unknown category.
  - target output bin full.
  - abnormal sample or uncertain handling result.

## 7. Scanning Station

The scanning station is a fixed coordinate location where the gripper holds one tube for identification. It is not a storage rack.

Required station elements:

- tube presentation position.
- Panasonic CX-421-J photoelectric sensor.
- Cognex DataMan 80 USB fixed barcode reader.
- adjustable sensor/scanner brackets.
- clearance for gripper fingers and tube label orientation.

## 8. Sensor And Scanner Roles

- Panasonic CX-421-J: detects tube presence at the scanning station and provides the trigger signal.
- Cognex DataMan 80 USB: reads 1D/2D barcode or QR code on the tube label.
- Classification logic: barcode result maps to Category A/B/C/D or unknown.
- Exception logic: failed scan or unknown category sends the tube to `manual_review_bin`.

## 9. Recommended Base Layout

- Base plate: 1100 mm x 900 mm x 15 mm.
- X direction: left-right direction.
- Y direction: front-back direction.
- Z direction: vertical direction.
- Rear area: mixed 4 x 6 input rack.
- Middle area: scanning station.
- Front or front-right area: four output bins in a 2 x 2 arrangement.
- Front corner or output edge: manual review bin.
- Equipment edge: emergency stop and control box for operator access.

The robot motion path should avoid interference among output bins, the scanning station, racks, the barcode reader, the photoelectric sensor, cable chain, and gripper-held tubes.

## 10. Sorting Workflow

```text
Input rack pick
-> move to scanning station
-> photoelectric sensor confirms tube presence
-> Cognex barcode reader reads barcode/QR code
-> software queries category
-> place into Category A/B/C/D output bin
-> route failed/unknown/full/abnormal samples to manual_review_bin
```

## 11. Future Modeling Checklist

- mixed tube set with cap color variants.
- tube label and barcode/QR label appearance.
- possible tube height variants.
- 4 x 6 mixed input rack.
- four 2 x 3 output bins.
- 2 x 3 manual review bin.
- scanning station with sensor and barcode reader brackets.
- collision envelope between gripper-held tube and scanner/sensor/racks.
- layout coordinates for export to MATLAB/Simulink and Isaac Sim.
