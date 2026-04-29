# Sample Tube Parameters

## Purpose

These blood collection tube STEP files are simplified scene objects for course design, SolidWorks assembly validation, Isaac Sim visualization, and sorting workflow demonstration. They are not production drawings for real medical consumables.

## Common Geometry

| parameter | value |
|---|---:|
| tube body diameter | 13 mm |
| cap diameter | 16 mm |
| cap height | 12 mm |
| label placeholder height | 40 mm |
| label placeholder width | about 10 mm |
| barcode placeholder | black visual stripes on the white label |

The tube body is represented as a simplified transparent or light-gray solid cylinder. The model does not include a detailed hollow wall, stopper details, internal vacuum structure, or real readable barcode.

## Generated Tube Types

| file | category | cap color | body height |
|---|---|---|---:|
| `purple_cap_tube_13x75.step` | Category A | purple | 75 mm |
| `yellow_cap_tube_13x100.step` | Category B | yellow | 100 mm |
| `blue_cap_tube_13x75.step` | Category C | blue | 75 mm |
| `red_cap_tube_13x75.step` | Category D | red | 75 mm |

## SolidWorks Use

Each tube type can be inserted multiple times as a consumable/scene object. For layout verification, tube origin is located at the center of the tube bottom plane, with Z upward along the tube axis. Color metadata may not be preserved by every STEP importer, so category and cap color must also be documented in the assembly notes.
