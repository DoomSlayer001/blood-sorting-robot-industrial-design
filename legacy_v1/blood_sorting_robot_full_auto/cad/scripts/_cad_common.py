from __future__ import annotations

import sys
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import cad_config as C


def export_colored(obj, path: Path, color=(0.75, 0.75, 0.75, 1.0), name: str | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    asm = cq.Assembly(name=f"{name or path.stem}_asm")
    asm.add(obj, name=name or path.stem, color=cq.Color(*color))
    asm.save(str(path), exportType="STEP")


def safe_fillet(obj, radius=1.0):
    try:
        return obj.edges().fillet(radius)
    except Exception:
        return obj


def safe_chamfer(obj, radius=0.8):
    try:
        return obj.edges().chamfer(radius)
    except Exception:
        return obj


def box_with_holes(length, width, height, holes, hole_diameter, fillet=1.0):
    part = cq.Workplane("XY").box(length, width, height)
    if holes:
        part = part.faces(">Z").workplane().pushPoints(holes).hole(hole_diameter, depth=height + 2)
    return safe_fillet(part, fillet)


def cylinder_x(length, radius):
    return cq.Workplane("XY").circle(radius).extrude(length).rotate((0, 0, 0), (0, 1, 0), 90)


def rack_dimensions():
    length = (C.rack_cols - 1) * C.tube_pitch + 2 * C.rack_margin
    width = (C.rack_rows - 1) * C.tube_pitch + 2 * C.rack_margin
    return length, width
