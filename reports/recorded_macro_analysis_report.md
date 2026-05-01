# Recorded Macro Analysis Report

## Source Status

The chat context provides the successful recorded macro's key insertion logic, but not a full exported raw macro listing. `03_cad/solidworks/macros/recorded_insert_baseplate_2026.vba` therefore preserves the provided recorded calls and wraps them in a reference macro for traceability.

## Key Successful API Calls

The recorded insertion sequence showed this working pattern inside SolidWorks:

```vb
OpenDoc6(native_file, 1, 32, "", errors, warnings)
ActivateDoc3(AssemblyTitle, True, 0, errors)
Part.AddComponent5(native_file, 0, "", False, "", x_m, y_m, z_m)
swInsertedComponent.SetTransformAndSolve2(swTransform)
SaveAs3(output_sldasm, 0, 0)
```

## Why Internal VBA Is More Reliable

External Python COM repeatedly produced files that existed on disk but reopened with zero components. SolidWorks internal VBA runs inside the SolidWorks process and follows the same command context as the recorded successful manual macro. It is therefore less exposed to cross-process activation, modal dialog, and active-document context issues.

## AddComponent5 Pattern

The useful pattern is:

1. Open the native `.SLDPRT` or `.SLDASM`.
2. Activate the assembly document again.
3. Call `AddComponent5` from the active assembly document.
4. Treat success as component count increase, not just a non-empty saved file.

## OpenDoc6 Pattern

The recorded macro opens native files with:

```vb
OpenDoc6(native_file, 1, 32, "", errors, warnings)
```

For `.SLDASM` inputs, the internal macros select document type `2`; for `.SLDPRT`, document type `1`.

## SetTransformAndSolve2 Pattern

After insertion, the component transform is set with a SolidWorks MathTransform. The rough assembly macros use identity rotation and translation from the placement table. This intentionally avoids final mate creation.

## Units

SolidWorks API coordinates are in meters. Project placement tables use millimeters. Internal VBA macros therefore convert:

```text
x_m = x_mm / 1000
y_m = y_mm / 1000
z_m = z_mm / 1000
```

## Template Update

The recorded macro context previously contained older template paths. The new macros use the SolidWorks 2026 assembly template:

```text
C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_assembly.asmdot
```

## Success Standard

A saved `.SLDASM` is only accepted when:

- FeatureManager contains real components.
- Component count is greater than zero.
- The assembly can be closed and reopened with components still present.
- Referenced documents exist.
- Debug output lists attempted, inserted, failed, and final component counts.
