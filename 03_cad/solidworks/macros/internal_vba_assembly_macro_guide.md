# Internal VBA Assembly Macro Guide

## Why Use Internal VBA

The previous external Python COM route could create `.SLDASM` files, but later audit showed that the assemblies opened with zero components and no referenced documents. SolidWorks internal VBA is now preferred for rough assembly generation because the user-recorded macro proved that SolidWorks can successfully insert a native part when the macro runs inside SolidWorks itself.

External Python COM is paused for assembly generation. It remains useful for reports and table preparation, but not as the primary mechanism for creating rough SolidWorks assemblies.

## Macros

- Minimum test macro: `03_cad/solidworks/macros/create_minimal_verified_rough_assembly_2026_internal_vba.vba`
- Full rough assembly skeleton: `03_cad/solidworks/macros/create_full_verified_rough_assembly_2026_internal_vba.vba`
- Recorded insertion reference: `03_cad/solidworks/macros/recorded_insert_baseplate_2026.vba`

## How To Run The Minimum Macro

1. Open SolidWorks 2026.
2. Use `Tools / Macro / Run`.
3. Select `create_minimal_verified_rough_assembly_2026_internal_vba.vba`.
4. Keep the VBA Immediate Window visible when possible so `Debug.Print` output can be checked.
5. The macro should create:
   `03_cad/solidworks/assembly/minimal_verified_internal_macro_rough_layout_2026_v1.SLDASM`

## Minimum Macro Success Checks

- FeatureManager contains six real components:
  - `base_plate`
  - `input_mixed_tube_rack_4x6`
  - `category_A_output_bin_2x3`
  - `electric_parallel_gripper`
  - `barcode_scanner`
  - `photoelectric_sensor`
- Macro Debug output reports `inserted count = 6`.
- Save, close, and reopen the assembly.
- Components remain present after reopen.
- Referenced documents are present.

## Screenshot Checks After Success

- Isometric view.
- Top view.
- Scan station local view.
- Category output bin local view.

## Full Macro Use

Run `create_full_verified_rough_assembly_2026_internal_vba.vba` only after the minimum macro succeeds. The full macro adds the gantry modules, Z module, tube bins, cable chain, emergency stop placeholder, and Y-axis synchronization placeholder. It still performs only rough coordinate placement and does not define final mates or manufacturing hole positions.

## Troubleshooting

- If a component fails, open the VBA Immediate Window and inspect `Debug.Print` output.
- Check whether the source file exists at the hard-coded path.
- Confirm coordinates are in millimeters in planning tables but converted to meters in VBA.
- Confirm the macro uses the SolidWorks 2026 assembly template:
  `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_assembly.asmdot`
- If FeatureManager remains empty, do not treat the saved `.SLDASM` as valid.
