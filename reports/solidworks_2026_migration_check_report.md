# SolidWorks 2026 Migration Check Report

- Check date: 2026-05-01
- Scope: environment check and minimum automation smoke test only
- Constraints: no `legacy_v1` changes, no control simulation, no push, no batch upgrade of existing SolidWorks files

## 1. Summary

SolidWorks COM now resolves to the SolidWorks 2026 installation, but the minimum automation smoke test is not yet stable enough to switch the project automation flow to 2026.

Observed result:

- SolidWorks COM dispatch: available
- SolidWorks revision: `34.2.1`
- SolidWorks executable path reported by COM: `D:\SW2026\SOLIDWORKS`
- STEP open test: failed with COM/RPC failure
- SLDPRT open test: not completed because the COM server became unavailable after the STEP open failure
- SLDASM open test: not completed because the COM server became unavailable after the STEP open failure
- New assembly test: failed after COM/RPC disconnect; `NewDocument` was unavailable in the disconnected COM object
- Base plate insertion test: not attempted because the new assembly was not created
- Existing macro compile check: passed for both rough assembly scripts

Recommendation:

- Do not switch the main SolidWorks automation flow to 2026 yet.
- First validate manual open/save behavior in SolidWorks 2026 and rerun a clean COM smoke test from a fresh SolidWorks process.
- Keep the current manual native cache workflow as the stable project route until STEP/native open, new assembly, and one-part insertion all pass in 2026.

## 2. COM And Version Check

| Item | Result |
|---|---|
| Windows platform | `Windows-11-10.0.26200-SP0` |
| `win32com.client` import | passed |
| `SldWorks.Application` dispatch | passed |
| SolidWorks revision | `34.2.1` |
| Reported executable path | `D:\SW2026\SOLIDWORKS` |

Interpretation:

- Revision `34.x` indicates the COM server is SolidWorks 2026 generation.
- The detected `SLDWORKS.exe` search result from `C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe` still has an old timestamp, but COM reports the active 2026 installation path under `D:\SW2026\SOLIDWORKS`.

## 3. Template Check

Current project config still points to 2018 templates:

| Template | Config path | Exists |
|---|---|---|
| Part | `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2018\templates\gb_part.prtdot` | yes |
| Assembly | `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2018\templates\gb_assembly.asmdot` | yes |
| Drawing | `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2018\templates\gb_a4.drwdot` | yes |

SolidWorks 2026 templates were found:

| Template | 2026 path | Exists |
|---|---|---|
| Part | `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_part.prtdot` | yes |
| Assembly | `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_assembly.asmdot` | yes |
| Drawing | `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_a4.drwdot` | yes |

Additional 2026 template candidates:

- `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_a0.drwdot`
- `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_a1.drwdot`
- `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_a2.drwdot`
- `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_a3.drwdot`
- `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_a4p.drwdot`
- `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\MBD\assembly 0250mm and smaller.asmdot`
- `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\MBD\assembly 0251mm to 1000mm.asmdot`
- `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\MBD\assembly 1001mm and larger.asmdot`

Project config update is recommended only after the minimum 2026 COM open/new/insert smoke test passes.

## 4. Minimum File Open Tests

| Test | File | Result |
|---|---|---|
| STEP open | `03_cad/custom_parts/base_plate/base_plate_1100x900x15.step` | failed |
| Existing SLDPRT open | `03_cad/solidworks/converted_native/parts/base_plate_1100x900x15.SLDPRT` | failed after COM server became unavailable |
| Existing SLDASM open | `03_cad/solidworks/assembly/blood_sorting_robot_rough_layout_v1.SLDASM` | failed after COM server became unavailable |

Detailed observed errors:

- STEP open exception: `com_error: (-2147023170, '远程过程调用失败。', None, None)`
- SLDPRT open exception: `com_error: (-2147023174, 'RPC 服务器不可用。', None, None)`
- SLDASM open exception: `com_error: (-2147023174, 'RPC 服务器不可用。', None, None)`

Interpretation:

- The STEP open test appears to destabilize or disconnect the SolidWorks COM server in this session.
- The SLDPRT/SLDASM failures are therefore not conclusive file-format failures; they happened after the COM server became unavailable.

## 5. Assembly And Insert Tests

| Test | Result |
|---|---|
| New assembly | failed after COM/RPC disconnect |
| Insert `base_plate_1100x900x15.SLDPRT` | not attempted because new assembly was not created |

Observed new assembly error:

- `AttributeError: SldWorks.Application.NewDocument`

Interpretation:

- This is consistent with a disconnected or invalid COM object after the earlier RPC failure, not necessarily a missing SolidWorks API.

## 6. Rough Assembly Script Check

The existing automation scripts compile successfully:

| Script | Compile result |
|---|---|
| `03_cad/solidworks/macros/create_rough_assembly_v1.py` | ok |
| `03_cad/solidworks/macros/create_rough_assembly_auto_retry_v1.py` | ok |

The scripts were not executed as a full rough assembly run during this migration check because the minimum COM smoke test failed and running the full script could rewrite the existing rough assembly output.

## 7. Migration Recommendation

Do not switch to a SolidWorks 2026 automation main flow yet.

Required before switching:

1. Start SolidWorks 2026 fresh and close any hung/disconnected COM instance.
2. Manually confirm that the same STEP, SLDPRT, and SLDASM files open in the 2026 UI.
3. Rerun the minimum COM smoke test in this report from a fresh process.
4. If STEP open remains unstable, keep using manual native conversion and only test native SLDPRT/SLDASM insertion.
5. After the smoke test passes, update `solidworks_template_config.json` to the 2026 templates.
6. Only then rerun `create_rough_assembly_v1.py` and compare the generated SLDASM against the existing rough assembly.

## 8. Git Status At Check Time

Before this report was generated:

```text
## main...origin/main
```

No `legacy_v1` changes were detected.
