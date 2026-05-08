# Simulation Platform Plan v1

## Python

Use Python first for task logic, tube occupancy table updates, output box state logic, and collision envelope pre-checks.

## MATLAB / Simulink

Use MATLAB/Simulink optionally for control models, trajectory demonstrations, and PID examples after the task/state logic is stable.

## Isaac Sim

Use Isaac Sim later for final visual digital twin and motion presentation. Do not start Isaac Sim integration in Stage 7B-0.

## SolidWorks

Use SolidWorks for final mechanical assembly verification, mates, and real interference checks, especially for the deferred Stage 7A-3f XY slider binding interface.

## Current Stage

Stage 7B-0 validates simulation tables, state-machine logic, and conservative collision envelopes with Python before moving into visual simulation.

