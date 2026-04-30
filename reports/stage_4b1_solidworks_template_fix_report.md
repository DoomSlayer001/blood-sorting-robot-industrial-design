# Stage 4B-1 SolidWorks Template Fix Report

## 1. Stage Goal

Stage 4B-1 fixes the missing SolidWorks assembly template issue from Stage 4B and attempts to generate the first rough layout `.SLDASM`.

## 2. Problem Found In Stage 4B

SolidWorks COM could be started, but `create_rough_assembly_v1.py` could not create a new assembly because no default assembly template was configured in the SolidWorks user preferences.

## 3. Template Search Results

| template_path | exists | size_bytes | modified |
|---|---:|---:|---|
| `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2018\templates\gb_assembly.asmdot` | yes | 30220 | 2017-10-06 04:51:38 |
| `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2018\templates\MBD\assembly 0250mm and smaller.asmdot` | yes | 24901 | 2017-10-06 04:52:44 |
| `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2018\templates\MBD\assembly 0251mm to 1000mm.asmdot` | yes | 25293 | 2017-10-06 04:52:44 |
| `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2018\templates\MBD\assembly 1001mm and larger.asmdot` | yes | 25360 | 2017-10-06 04:52:44 |
| `C:\Users\Public\Documents\SOLIDWORKS\SOLIDWORKS 2018\samples\tutorial\advdrawings\assembly.asmdot` | yes | 59957 | 2017-10-06 04:50:54 |

Related templates found:

| template_path | exists | size_bytes | modified |
|---|---:|---:|---|
| `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2018\templates\gb_part.prtdot` | yes | 35881 | 2017-10-06 04:51:38 |
| `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2018\templates\gb_a4.drwdot` | yes | 70186 | 2017-10-06 04:51:38 |

## 4. Selected Template

The selected assembly template is:

```text
C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2018\templates\gb_assembly.asmdot
```

Reason: it is a normal SolidWorks 2018 assembly template in the standard template folder. MBD-specific and tutorial templates were retained as candidates but not selected.

Configuration file:

```text
03_cad/solidworks/macros/solidworks_template_config.json
```

## 5. Script Changes

`create_rough_assembly_v1.py` now:

- reads `solidworks_template_config.json` before using SolidWorks default templates.
- logs the selected template path.
- falls back to SolidWorks user preferences if the config path is empty or invalid.
- keeps MathUtility optional because the current SolidWorks 2018 COM wrapper reports it as unavailable.
- removes incomplete `.SLDASM` output when insert/save fails, so a blank assembly is not mistaken for success.

## 6. Generation Attempt Result

The script was rerun after template configuration:

```text
python 03_cad/solidworks/macros/create_rough_assembly_v1.py
```

Result:

- SolidWorks COM dispatch: succeeded.
- Assembly template from config: found and used.
- Valid CAD rows attempted: 26.
- Skipped rows: 2 wildcard scenario rows.
- Inserted rows: 0.
- Failed insertions: 26.
- `.SLDASM` generated: no.

The script briefly produced an incomplete assembly file, but removed it because `SaveAs3` returned `0` and no components were inserted.

Expected output path remains:

```text
03_cad/solidworks/assembly/blood_sorting_robot_rough_layout_v1.SLDASM
```

Current status: file does not exist.

## 7. Failure Reason And Next Input Needed

The template issue is fixed, but component insertion through Python COM still fails: `AddComponent5` returns `None` for all component files in this environment.

Likely next actions:

- Run the VBA fallback macro from inside SolidWorks.
- Manually confirm a STEP file can be inserted into an empty SolidWorks assembly.
- If Python automation must be used, replace `AddComponent5` with a SolidWorks-version-specific flow that first imports STEP files or uses a tested insertion API for SolidWorks 2018.
- If a custom assembly template is preferred, update `solidworks_template_config.json` with the user-provided `.asmdot` path.

## 8. Next Stage 4C

Stage 4C should open SolidWorks, run the macro inside the configured SolidWorks environment, save the first rough assembly, and capture screenshots for layout/orientation review.
