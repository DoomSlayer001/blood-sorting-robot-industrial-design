# Multi-box Pick/Place Height Rules v1

| Rule | Value mm | Notes |
|---|---:|---|
| `safe_z` | 200 | Safe XY travel height above the tallest 100 mm tube, box rims, and common rough-layout obstacles. |
| `approach_z` | 130 | Pre-pick/pre-place approach height before descending. |
| `grip_z_75mm` | 55 | Initial grip height for 75 mm tubes. |
| `grip_z_100mm` | 80 | Initial grip height for 100 mm tubes. |
| `place_z_75mm` | 45 | Initial placement height for 75 mm tubes. |
| `place_z_100mm` | 70 | Initial placement height for 100 mm tubes. |
| `scan_z` | 75 | Recognition posture at the scan station. |

75 mm and 100 mm tubes need different grip and place heights because the cap/body region presented to the gripper changes with tube length. These values are planning defaults for v7.1; later phases should revise them using the real gripper jaw pads, bracket geometry, and clearance tests.
