# Pick And Place Height Rules v1

These initial heights are task-planning values for Stage 6A. They are based on the v6 rough layout and should be refined after checking the real gripper jaw, soft pads, tube cap geometry, and collision margins.

| rule | z_mm | purpose |
|---|---:|---|
| `safe_z` | 180 | XY travel height above the tallest 100 mm tube. |
| `approach_z` | 120 | Pre-pick/pre-place approach height before descending to grip or place. |
| `grip_z_75mm` | 55 | Grip height for 75 mm tubes, near the upper body/cap region. |
| `grip_z_100mm` | 80 | Grip height for 100 mm tubes, higher to keep a similar grip position along the tube. |
| `place_z_75mm` | 45 | Placement descent height for 75 mm tubes. |
| `place_z_100mm` | 70 | Placement descent height for 100 mm tubes. |
| `scan_z` | 75 | Scan station tube handling height. |

75 mm and 100 mm tubes need different grip heights because the gripper should approach a comparable physical region near the upper tube body/cap without hitting the rack, cap, or holder. The current numbers are conservative planning defaults, not final robot calibration values.
