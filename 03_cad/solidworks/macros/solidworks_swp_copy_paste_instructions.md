# SolidWorks SWP Copy/Paste Instructions

## Key Point

SolidWorks cannot directly run the plain-text `.vba` files in this repository. A SolidWorks macro is normally stored as a `.swp` file created by SolidWorks itself.

The repository keeps `.vba` and `.bas` text files because they are reviewable in Git. To execute them, create a `.swp` macro in SolidWorks and paste the text module into it.

## Recommended File To Copy

Use:

```text
03_cad/solidworks/macros/create_minimal_verified_rough_assembly_2026_copy_to_swp.bas
```

The original source remains:

```text
03_cad/solidworks/macros/create_minimal_verified_rough_assembly_2026_internal_vba.vba
```

## Create A Runnable SWP Macro

1. Open SolidWorks 2026.
2. Choose `Tools / Macro / New`.
3. Save the new macro as:

```text
03_cad/solidworks/macros/create_minimal_verified_rough_assembly_2026_internal_vba.swp
```

4. SolidWorks opens the VBA editor.
5. Open `create_minimal_verified_rough_assembly_2026_copy_to_swp.bas` in a text editor.
6. Select all content and paste it into the SolidWorks VBA module.
7. Save the `.swp`.
8. Run the macro from SolidWorks with `Tools / Macro / Run`.

## Validation After Running

The macro is only considered successful when:

- FeatureManager shows the six expected components.
- The VBA Immediate Window shows attempted, inserted, failed, and final component counts.
- The saved `.SLDASM` can be closed and reopened with components still present.
- Referenced documents remain connected.

Do not accept a non-empty `.SLDASM` file by itself as proof of success.
