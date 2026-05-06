# Stage 7A-3b-0 Electrical Architecture Report

- Purpose: define concept-level electrical architecture before modeling cable chain and wiring geometry.
- Reason for sequence: cable-chain CAD needs known source/target modules, moving-vs-fixed wiring groups, service-side exits, and safety placeholders before route geometry is meaningful.
- This stage does not generate CAD or STEP files.

## Output Files

- `01_system_design/electrical_system_architecture_v1.md`
- `01_system_design/electrical_component_list_v1.csv`
- `01_system_design/electrical_io_map_v1.csv`
- `01_system_design/electrical_wiring_interface_table_v1.csv`
- `01_system_design/safety_circuit_concept_v1.md`
- `01_system_design/control_box_internal_layout_plan_v1.md`
- `01_system_design/cable_routing_plan_v1.md`
- `01_system_design/check_electrical_architecture_tables_v1.py`

## Table Summary

- Electrical component count: 28
- I/O point count: 25
- Wiring interface count: 26
- Fixed cable count: 20
- Cable-chain cable count: 6
- Safety-related signal count: 5
- CSV validation: PASS

## Design Boundary

- Current level: course / concept electrical architecture.
- Not included: production wiring diagrams, conductor sizing, certified safety circuit design, PCB design, medical electrical certification, EMC validation, connector pinouts, or terminal numbering release.
- The emergency stop and door interlock are safety placeholders; later design must select certified hardware and validate the safety chain.

## Stage 7A-3c Use

Stage 7A-3c cable chain / wiring module should use the wiring interface table to separate fixed rear service routes, base sensor routes, moving gantry cable-chain routes, scanner/photoelectric routes, and grounding routes. The `requires_cable_chain=yes` rows should drive the first cable-chain bundle model.

## CAD Check

- CAD check summary: supported=20, valid=20, invalid=0.
- Current status: no CAD / STEP generated in this stage.
