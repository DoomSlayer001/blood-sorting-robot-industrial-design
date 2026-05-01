# SolidWorks 2026 Native-Only Smoke Test Report

- Test time: 2026-05-01T16:17:29
- Scope: native `.SLDPRT/.SLDASM` open and insert only; no STEP/STP open; no batch CAD upgrade.

## 1. Existing SolidWorks Process Check

- Existing SLDWORKS process: id=22824; path=`D:\SW2026\SOLIDWORKS\SLDWORKS.exe`; responding=True
- Existing responding process was not forcibly closed.

## 2. SolidWorks 2026 COM Startup

- win32com available: True
- Dispatch method: DispatchEx
- Dispatch started: True
- SolidWorks revision: `34.2.1`
- Executable path: `D:\SW2026\SOLIDWORKS`
- Process id: `15848`

## 3. Template Check

| Template | Path | Exists | Size bytes |
|---|---|---:|---:|
| part | `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_part.prtdot` | True | 40446 |
| assembly | `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_assembly.asmdot` | True | 36546 |
| drawing | `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_a4.drwdot` | True | 72852 |

## 4. Native Part Open Test

- Path: `C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\solidworks\converted_native\parts\base_plate_1100x900x15.SLDPRT`
- Exists: True
- Opened: True
- Errors: 0
- Warnings: 0
- Closed without save: True

## 5. Native Assembly Open Test

- Path: `C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\solidworks\converted_native\assemblies\SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.SLDASM`
- Exists: True
- Opened: True
- Errors: 0
- Warnings: 0
- Closed without save: True

## 6. New Assembly Test

- Template: `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_assembly.asmdot`
- Template exists: True
- Created: True

## 7. Base Plate Insert Test

- Attempted: True
- Inserted: True
- Method: `AddComponent`

## 8. Smoke Test Assembly Output

- Attempted: True
- Saved: True
- Path: `C:\Users\29868\Desktop\作业\医用机器人\blood-sorting-robot-industrial-design\03_cad\solidworks\assembly\solidworks_2026_native_smoke_test.SLDASM`
- Size bytes: 35618

## 9. Recommendation

- Recommendation: native-only SolidWorks 2026 workflow passed. It is reasonable to consider a controlled 2026 main-flow switch in a separate commit after reviewing the smoke assembly manually.

## 10. Raw Result Snapshot

```json
{
  "timestamp": "2026-05-01T16:17:29",
  "platform": "Windows-11-10.0.26200-SP0",
  "pre_existing_sldworks": [
    {
      "Id": 22824,
      "Path": "D:\\SW2026\\SOLIDWORKS\\SLDWORKS.exe",
      "Responding": true
    }
  ],
  "com": {
    "win32com_available": true,
    "dispatch_method": "DispatchEx",
    "started": true,
    "revision": "34.2.1",
    "executable_path": "D:\\SW2026\\SOLIDWORKS",
    "process_id": "15848",
    "exception": "",
    "revision_exception": "TypeError: 'str' object is not callable",
    "executable_exception": "TypeError: 'str' object is not callable",
    "exit_app_called": true
  },
  "templates": {
    "part": {
      "path": "C:\\ProgramData\\SOLIDWORKS\\SOLIDWORKS 2026\\templates\\gb_part.prtdot",
      "exists": true,
      "is_file": true,
      "size": 40446
    },
    "assembly": {
      "path": "C:\\ProgramData\\SOLIDWORKS\\SOLIDWORKS 2026\\templates\\gb_assembly.asmdot",
      "exists": true,
      "is_file": true,
      "size": 36546
    },
    "drawing": {
      "path": "C:\\ProgramData\\SOLIDWORKS\\SOLIDWORKS 2026\\templates\\gb_a4.drwdot",
      "exists": true,
      "is_file": true,
      "size": 72852
    }
  },
  "open_sldprt": {
    "path": "C:\\Users\\29868\\Desktop\\作业\\医用机器人\\blood-sorting-robot-industrial-design\\03_cad\\solidworks\\converted_native\\parts\\base_plate_1100x900x15.SLDPRT",
    "exists": true,
    "opened": true,
    "errors": 0,
    "warnings": 0,
    "title": "",
    "exception": "",
    "closed_without_save": true
  },
  "open_sldasm": {
    "path": "C:\\Users\\29868\\Desktop\\作业\\医用机器人\\blood-sorting-robot-industrial-design\\03_cad\\solidworks\\converted_native\\assemblies\\SMC_LEHF20_2finger_parallel_gripper_24stroke_v1.SLDASM",
    "exists": true,
    "opened": true,
    "errors": 0,
    "warnings": 0,
    "title": "",
    "exception": "",
    "closed_without_save": true
  },
  "new_assembly": {
    "template": "C:\\ProgramData\\SOLIDWORKS\\SOLIDWORKS 2026\\templates\\gb_assembly.asmdot",
    "template_exists": true,
    "created": true,
    "exception": ""
  },
  "insert_base_plate": {
    "attempted": true,
    "inserted": true,
    "method": "AddComponent",
    "exception": ""
  },
  "save_smoke_assembly": {
    "attempted": true,
    "saved": true,
    "path": "C:\\Users\\29868\\Desktop\\作业\\医用机器人\\blood-sorting-robot-industrial-design\\03_cad\\solidworks\\assembly\\solidworks_2026_native_smoke_test.SLDASM",
    "size": 35618,
    "exception": "",
    "save_return": "0"
  },
  "recommend_switch_to_2026": true
}
```
