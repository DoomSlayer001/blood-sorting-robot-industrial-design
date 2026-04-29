# Reachability And Workspace Plan

## 1. Base Coordinate System

- Base plate size: 1100 mm x 900 mm x 15 mm.
- Origin: center of the base top surface.
- X range: -550 mm to +550 mm.
- Y range: -450 mm to +450 mm.
- Z direction: positive upward.

The coordinates in this document are initial layout planning coordinates, not final engineering hole positions.

## 2. Main Areas

- `input_mixed_tube_rack_4x6`
- `scan_station`
- `category_A_output_bin_2x3`
- `category_B_output_bin_2x3`
- `category_C_output_bin_2x3`
- `category_D_output_bin_2x3`
- `manual_review_bin_2x3`
- `control_box_area`
- `emergency_stop_area`

## 3. Initial Reachability Requirements

- Gripper centerline must reach every input rack hole.
- Gripper centerline must reach the scanning station.
- Gripper centerline must reach every category output bin hole.
- Gripper centerline must reach every manual review bin hole.
- Z axis must support pickup and placement of both 75 mm and 100 mm tubes.
- Safe height must be higher than the tallest tube, tube cap, rack wall, scanner bracket, sensor bracket, and expected gripper-held tube envelope.

## 4. Interference Risks

- X-axis gantry beam and Z-axis module interference.
- Gripper and rack/bin wall interference.
- Barcode scanner bracket and gripper motion path interference.
- Photoelectric sensor bracket and tube presentation interference.
- Cable chain and gantry/bracket interference.
- Input/output bins placed too close, reducing gripper clearance.

## 5. SolidWorks Checks Required Later

- reach envelope.
- collision check.
- tube clearance.
- gripper clearance.
- scanner line-of-sight.
- photoelectric sensor trigger alignment.
- cable chain sweep envelope.
- emergency stop access.
- control box and cable service clearance.

## 6. Relationship To Layout Table

Initial area coordinates are recorded in `03_cad/solidworks/initial_workspace_layout_table.csv`. The CSV is a pre-assembly planning table and must be updated after SolidWorks placement with real CAD dimensions.
