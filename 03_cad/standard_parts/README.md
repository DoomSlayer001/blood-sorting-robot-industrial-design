# Standard Parts CAD Workspace

This directory manages real supplier CAD for industrial standard parts.

## Directory Policy

- `downloaded/` is reserved for real supplier CAD downloaded from manufacturer portals, TraceParts, McMaster-Carr, MISUMI, THK, SMC, Festo, igus, or equivalent sources.
- `placeholders/` is reserved for temporary placeholder models only. Placeholder models are not valid for design freeze.
- Stage 2 creates the directory structure and workflow only. No new CAD files are added in this stage.

## Required Recording Rule

Every real CAD file placed here must have:

- A matching `part_id` in `02_bom/standard_parts_bom_v1.csv`.
- A record in `03_cad/standard_parts/CAD_download_status_v2.md`.
- A supplier source URL or supplier portal reference.
- Download date.
- File format.
- Manual download flag when login, registration, captcha, configurator selection, or human format selection was required.

## Folder Map

- `downloaded/x_axis_module/`
- `downloaded/y_axis_module/`
- `downloaded/z_axis_module/`
- `downloaded/motors/`
- `downloaded/gripper/`
- `downloaded/linear_guides/`
- `downloaded/belts_pulleys/`
- `downloaded/lead_screws/`
- `downloaded/couplings_bearings/`
- `downloaded/sensors/`
- `downloaded/safety/`
- `downloaded/cable_chain/`
- `downloaded/fasteners/`
- `placeholders/`

## Current Stage

No CAD has been downloaded in Stage 2.
