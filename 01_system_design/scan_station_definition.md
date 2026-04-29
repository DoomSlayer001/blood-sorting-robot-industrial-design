# Scan Station Definition

## 1. Function

The scanning station is the intermediate identification location. The gripper holds one tube at this station while the sensor and barcode reader perform tube presence confirmation and label reading.

The scanning station is not a tube storage box.

## 2. Components

- Panasonic CX-421-J photoelectric sensor.
- Cognex DataMan 80 USB fixed-mount barcode reader.
- barcode scanner bracket.
- photoelectric sensor bracket.
- tube scanning reference position.
- cable routing allowance for sensor and scanner cables.

## 3. Scanning Assumptions

- The tube label faces the barcode reader.
- The gripper holds the tube in a fixed scanning posture.
- No tube rotation mechanism is included in the current mainline design.
- The barcode/QR code in CAD models is a visual placeholder.
- Scan retry and rotation search are future industrial upgrade items.

## 4. Recommended Spatial Position

- Place the scanning station in the middle work area, preferably middle-right or middle-front.
- It must not block X/Y/Z motion.
- It must not interfere with output bins.
- The barcode reader should face the tube label laterally.
- The photoelectric sensor should detect the tube body at the scanning reference position.

## 5. Future Modeling Needs

- `scan_station_reference_block`.
- `barcode_scanner_bracket`.
- `photoelectric_sensor_bracket`.
- cable routing allowance.
- adjustable scanner/sensor slots for line-of-sight and trigger alignment.

## 6. Design Risk

The station cannot be frozen only from nominal coordinates. Final SolidWorks layout must check scanner line of sight, gripper clearance, tube label orientation, bracket stiffness, and cable exit direction using the real Cognex and Panasonic CAD files.
