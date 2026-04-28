# Standard Parts Download Plan v1

## Purpose

This plan defines how real industrial standard-part CAD will be downloaded and recorded in later stages. Stage 2 does not download CAD and does not mark any part as downloaded.

## Supplier Source Types

- Linear modules and actuators: MISUMI, THK, HIWIN-equivalent suppliers.
- Linear guides and sliders: THK, HIWIN, MISUMI.
- Motors: Oriental Motor, Leadshine, Delta, MISUMI, 3D ContentCentral references.
- Belt drive parts: MISUMI, Gates, McMaster-Carr.
- Lead screw and screw supports: MISUMI, THK, McMaster-Carr.
- Couplings and bearing blocks: MISUMI, McMaster-Carr, TraceParts.
- Electric gripper: SMC, Festo.
- Cable drag chain: igus, MISUMI, McMaster-Carr.
- Sensors and safety parts: Omron, SICK, Keyence, Schneider, Siemens, IDEC, TraceParts.
- Enclosures and guard hardware: McMaster-Carr, Hammond, Rittal, MISUMI, local sheet suppliers.

## Format Priority

```text
SLDPRT / SLDASM > STEP / STP > X_T > IGES > STL
```

Native SolidWorks files are preferred when supplier-provided and trustworthy. STEP/STP is the default neutral exchange format. X_T is acceptable for Parasolid workflows. IGES is a backup format. STL is not suitable for mechanical interface design.

## Manual Download Rule

Mark a part as `manual_download_required` when any of the following is true:

- Supplier login is required.
- Registration is required.
- Captcha is shown.
- A product configurator must be completed.
- CAD format must be selected manually.
- CAD terms or license conditions must be accepted manually.
- The supplier page does not expose a direct stable download URL.

## Temporary Equivalent Model Rule

Equivalent placeholder models may be used only for layout envelopes of low-risk parts. They must not be used for design freeze of moving modules, safety devices, gripper interfaces, rail mounting holes, motor flanges, belt pulley bores, lead screw interfaces, or bearing supports.

## Updating CAD Download Status

After a real CAD file is downloaded:

1. Place it in `03_cad/standard_parts/downloaded/<category>/`.
2. Rename it according to `02_bom/standard_parts_file_naming_rule.md`.
3. Update `03_cad/standard_parts/CAD_download_status_v2.md`.
4. If the BOM remains valid, update `02_bom/standard_parts_bom_v1.csv` `cad_download_status` from `manual_download_required` or `not_started` to `downloaded`.
5. Record the original supplier source and manual action status.
6. If the downloaded CAD is replaced by an equivalent supplier model, use `replaced_by_equivalent` and explain why.

## Current Stage Status

No real CAD has been downloaded in Stage 2.
