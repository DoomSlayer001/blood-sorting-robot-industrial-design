# Simulation Architecture v1

Stage 7B-0 starts simulation preparation only. It does not continue XY slider binding geometry work and does not create new appearance CAD.

## System Layers

1. Layer 1: CAD geometry / visual digital twin
   - Uses accepted CAD and STEP artifacts as visual references.
   - Known mechanical issue: Stage 7A-3f XY beam-to-Y-slider physical mounting interface is deferred.
2. Layer 2: kinematic motion model
   - Abstract Cartesian X/Y/Z axis model.
   - Independent of the unresolved physical XY slider binding details.
3. Layer 3: task planner
   - Converts tube occupancy input rows into pick/place tasks.
4. Layer 4: tube sorting logic
   - Maintains tube state, category, source slot, and target output box.
5. Layer 5: collision / reachability check
   - Uses conservative envelope tables before motion commands are accepted.
6. Layer 6: future Isaac Sim visualization
   - Reserved for visual digital twin presentation after table/state logic is stable.

## Current Stage Scope

- Cartesian axis motion.
- Pick/place sequencing.
- Collision envelope pre-check.
- Tube occupancy state update.
- Output box capacity logic.

## Current System Rule

No camera is used in the current system version. Tube presence, tube ID, category, and source rack slot are provided by an internal input table. A vision module is reserved as a future optional extension only.

