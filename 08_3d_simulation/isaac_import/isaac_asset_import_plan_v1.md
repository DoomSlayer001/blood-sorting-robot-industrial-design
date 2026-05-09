# Isaac Asset Import Plan v1

Stage 7D-1 prepares Isaac Sim / 3D CAD import assets only. It does not run Isaac Sim, does not create a 2D animation, does not create a PPT, and does not modify Stage 7A CAD.

## Baseline Asset

- Current mechanical baseline: `03_cad/freecad_assembly/blood_sorting_robot_v7_3f_gantry_joint_adapter_preview_v1_7.step`
- Baseline status: Stage 7A-3f v1.7 accepted as current mechanical baseline.
- Rejected asset: Stage 7A-3f v1.8 must not be used.

## Import Preparation Flow

1. Import or convert the accepted v1.7 STEP into an Isaac-compatible USD scene.
2. Split the imported CAD into fixed and moving prim groups following `kinematic_group_definition_v1.csv`.
3. Create prismatic joints for Y gantry, X slider, Z axis, and mirrored gripper fingers.
4. Load `isaac_joint_command_timeseries_v1.csv` to drive playback in meters.
5. Load `isaac_tube_attach_detach_events_v1.csv` for tube visual parenting.
6. Use simplified collision proxies for initial validation; do not treat them as final CAD mesh collision.
7. Add visual materials for category labels and state highlights if useful.

## Non-Camera Boundary

The system still does not use camera logic. Input occupancy is provided by the internal tube occupancy table, and scan behavior remains a state-machine/trajectory event in this preparation package.

## Output Of This Stage

This stage produces scene hierarchy, joint config, collision proxy config, material config, playback input manifest, tube attach/detach events, environment check, and skeleton playback scripts. Actual Isaac import/playback is deferred to Stage 7D-2.
