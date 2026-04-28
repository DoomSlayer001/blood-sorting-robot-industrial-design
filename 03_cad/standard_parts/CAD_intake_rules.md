# CAD Intake Rules

## Storage Rule

Real supplier CAD must be placed under:

```text
03_cad/standard_parts/downloaded/<category>/
```

Temporary placeholder files, if used later, must be placed under:

```text
03_cad/standard_parts/placeholders/
```

Stage 3A does not download or add any CAD files.

## File Naming Rule

Use the naming format defined in `02_bom/standard_parts_file_naming_rule.md`:

```text
supplier_parttype_model_spec_version.ext
```

File names must not contain Chinese characters or spaces.

## Allowed CAD Extensions

The intake checker accepts:

- `.step`
- `.stp`
- `.sldprt`
- `.sldasm`
- `.x_t`
- `.igs`
- `.iges`

Preferred format order:

```text
SLDPRT / SLDASM > STEP / STP > X_T > IGES > STL
```

STL is not accepted for mechanical interface design and is not part of the Stage 3A intake checker allowed list.

## Multiple Formats For One Part

If a supplier provides multiple formats:

1. Keep the highest-priority usable format.
2. Record backup formats in `CAD_download_status_v2.md`.
3. Do not keep duplicate formats unless there is a clear review reason.
4. If both SLDASM and STEP are required, record the assembly reason in the note field.

## Status Table Update

After a real supplier CAD file is received and verified:

1. Update `03_cad/standard_parts/CAD_download_status_v2.md`.
2. Update `02_bom/standard_parts_bom_v1.csv` `cad_download_status`.
3. Record supplier, model/series, download date, source URL or portal, file format, manual download flag, and target file path.
4. Keep `manual_download_required` if the CAD required login, registration, captcha, configurator, or manual format selection.

Do not mark a part as `downloaded` unless the real CAD file exists in `03_cad/standard_parts/downloaded/`.

## Real CAD Versus Fallback

A file is considered real standard-part CAD only if it comes from one of the following:

- Manufacturer official CAD portal.
- Supplier or distributor CAD portal with a traceable product page.
- TraceParts, 3D ContentCentral, McMaster-Carr, MISUMI, THK, SMC, Festo, igus, or equivalent traceable source.

A fallback file is any manually modeled, simplified, estimated, or visual-only model. Fallback files must never be used as proof of real standard-part geometry.

## Required Intake Metadata

For every accepted real CAD file, record:

- `part_id`
- supplier
- model or series
- source URL or source portal
- download date
- downloaded by
- file format
- file path
- manual download required flag
- notes on configuration choices
