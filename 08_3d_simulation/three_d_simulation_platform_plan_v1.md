# 3D Simulation Platform Plan v1

Stage 7D-0 prepares a true 3D moving-part simulation hierarchy. It is not a 2D animation stage, not a PPT stage, and not a rendering stage.

## Primary Route: Isaac Sim Digital Twin Playback

Isaac Sim is the recommended primary path for high-quality 3D scene playback. The intended flow is:

- Import the accepted Stage 7A-3f v1.7 baseline STEP or converted USD.
- Split imported geometry into fixed and moving groups.
- Drive X/Y/Z prismatic joints from `time_stepped_motion_trace_v1.csv`.
- Drive gripper open/close joints from `trajectory_waypoints_v1.csv`.
- Implement tube attach/detach events for pick, transport, scan wait, output place, and manual review place.
- Add collision proxies for practical digital twin playback checks.
- Produce final 3D presentation video after import validation and playback scripting.

## Alternative / Quick Validation: SolidWorks Motion

SolidWorks Motion can help validate assembly relationships and mate-based travel. It is useful for checking whether the mechanical hierarchy moves plausibly, but it is not ideal for the full sorting state machine, pending queue logic, tube attach/detach behavior, or event overlays.

## Python 3D Preview

A Python 3D preview can be useful as a lightweight debugging view of X/Y/Z motion and tube attach/detach timing. It is not equivalent to a CAD digital twin because the imported STEP hierarchy, CAD part grouping, joint constraints, and collision proxy behavior are not validated there.

## Recommended Project Sequence

1. Finish the 3D kinematic hierarchy and trajectory mapping.
2. Prepare Isaac Sim import and CAD-to-USD grouping.
3. Build Isaac Sim playback for X/Y/Z joints, gripper joints, tube attach/detach, and event overlays.

Current Stage 7D-0 completes step 1 and creates the preparation manifests for steps 2 and 3.
