# Stage 4C Internal VBA Macro Preparation Report

## Objective

Prepare SolidWorks 2026 internal VBA macros for rough assembly generation after external Python COM attempts produced empty assemblies.

## Why Earlier Rough Assemblies Are Invalid

The existing rough assemblies were audited with SolidWorks 2026 and opened with zero components and no referenced documents. File existence and file size are therefore not valid success criteria.

## External Python COM Failure Summary

External Python COM could start SolidWorks and create files, but insertion attempts did not reliably increase assembly component count. The workflow is paused as the main assembly generation method.

## Recorded Macro Evidence

The user-recorded internal macro proved that SolidWorks VBA can:

1. Create a new assembly.
2. Open a native `.SLDPRT`.
3. Activate the assembly.
4. Insert with `AddComponent5`.
5. Move the inserted component with `SetTransformAndSolve2`.
6. Save the assembly.

## Prepared Macro Files

- Recorded reference: `03_cad/solidworks/macros/recorded_insert_baseplate_2026.vba`
- Minimum macro: `03_cad/solidworks/macros/create_minimal_verified_rough_assembly_2026_internal_vba.vba`
- Full macro skeleton: `03_cad/solidworks/macros/create_full_verified_rough_assembly_2026_internal_vba.vba`
- Run guide: `03_cad/solidworks/macros/internal_vba_assembly_macro_guide.md`

## Minimum Macro Components

The minimum macro inserts six components:

1. `base_plate`
2. `input_mixed_tube_rack_4x6`
3. `category_A_output_bin_2x3`
4. `electric_parallel_gripper`
5. `barcode_scanner`
6. `photoelectric_sensor`

## Full Macro Target Components

The full macro skeleton includes:

- `base_plate`
- `left_y_axis_module`
- `right_y_axis_module`
- `x_axis_module_on_gantry`
- `z_axis_module`
- `electric_parallel_gripper`
- `input_mixed_tube_rack_4x6`
- `category_A_output_bin_2x3`
- `category_B_output_bin_2x3`
- `category_C_output_bin_2x3`
- `category_D_output_bin_2x3`
- `manual_review_bin_2x3`
- `barcode_scanner`
- `photoelectric_sensor`
- `cable_chain_xz`
- `emergency_stop_placeholder`
- `control_box_placeholder` as a documented skip until native path is confirmed
- `y_axis_sync_mechanism`

## Next User Action

Run the minimum macro inside SolidWorks 2026:

```text
Tools / Macro / Run / create_minimal_verified_rough_assembly_2026_internal_vba.vba
```

## Success Standard

The minimum macro is successful only if:

- FeatureManager shows real components.
- Component count is greater than zero.
- The assembly is saved, closed, and reopened with components still present.
- Referenced documents remain attached.
- The Immediate Window shows attempted, inserted, failed, and final component counts.

Do not accept `.SLDASM` file size alone as proof of success.
