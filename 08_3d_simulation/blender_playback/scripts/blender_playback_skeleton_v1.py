"""
This script is intended to be executed inside Blender Python environment.

It is a Stage 7D-1A skeleton for keyframe playback preparation. It expects CAD
objects to already be imported or linked into a Blender scene and renamed or
parented according to blender_group_mapping_v1.csv.
"""

from __future__ import annotations

import csv
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[3]
PLAYBACK_DIR = ROOT / "08_3d_simulation" / "blender_playback"
KEYFRAME_CSV = PLAYBACK_DIR / "blender_keyframe_commands_v1.csv"
TUBE_EVENTS_CSV = PLAYBACK_DIR / "blender_tube_attach_detach_events_v1.csv"
MATERIAL_CSV = PLAYBACK_DIR / "blender_material_color_map_v1.csv"

OBJECTS = {
    "fixed_base_group": "FixedBase",
    "y_gantry_moving_group": "YGantryMoving",
    "x_slider_moving_group": "XSliderMoving",
    "z_axis_moving_group": "ZAxisMoving",
    "gripper_left_finger_group": "GripperLeftFinger",
    "gripper_right_finger_group": "GripperRightFinger",
    "tube_dynamic_group": "DynamicTubes",
    "event_overlay_group": "EventOverlay",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def get_object(name: str) -> bpy.types.Object | None:
    return bpy.data.objects.get(name)


def ensure_empty(name: str) -> bpy.types.Object:
    existing = get_object(name)
    if existing:
        return existing
    empty = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(empty)
    return empty


def load_or_reference_imported_cad_objects() -> None:
    for object_name in OBJECTS.values():
        ensure_empty(object_name)


def create_materials() -> None:
    for row in read_csv(MATERIAL_CSV):
        rgba = tuple(float(part.strip()) for part in row["rgba"].split(","))
        material = bpy.data.materials.get(row["material_id"]) or bpy.data.materials.new(row["material_id"])
        material.diffuse_color = rgba


def insert_motion_keyframes() -> None:
    y_obj = ensure_empty(OBJECTS["y_gantry_moving_group"])
    x_obj = ensure_empty(OBJECTS["x_slider_moving_group"])
    z_obj = ensure_empty(OBJECTS["z_axis_moving_group"])
    left_finger = ensure_empty(OBJECTS["gripper_left_finger_group"])
    right_finger = ensure_empty(OBJECTS["gripper_right_finger_group"])

    for row in read_csv(KEYFRAME_CSV):
        frame = int(row["frame"])
        x_m = float(row["location_x_m"])
        y_m = float(row["location_y_m"])
        z_m = float(row["location_z_m"])
        opening_m = float(row["gripper_opening_m"])

        y_obj.location.y = y_m
        y_obj.keyframe_insert(data_path="location", frame=frame)

        x_obj.location.x = x_m
        x_obj.keyframe_insert(data_path="location", frame=frame)

        z_obj.location.z = z_m
        z_obj.keyframe_insert(data_path="location", frame=frame)

        left_finger.location.x = opening_m
        right_finger.location.x = -opening_m
        left_finger.keyframe_insert(data_path="location", frame=frame)
        right_finger.keyframe_insert(data_path="location", frame=frame)


def process_tube_attach_detach_events() -> None:
    dynamic_tubes = ensure_empty(OBJECTS["tube_dynamic_group"])
    for row in read_csv(TUBE_EVENTS_CSV):
        tube = ensure_empty(row["tube_id"])
        frame = int(row["frame"])
        event_type = row["event_type"]
        if event_type == "attach_to_gripper":
            tube.parent = ensure_empty("GripperTCP")
        elif event_type in {"detach_to_output_box", "detach_to_manual_review", "pick_failed_no_attach", "before_pick"}:
            tube.parent = dynamic_tubes
        tube.keyframe_insert(data_path="location", frame=frame)
        tube.keyframe_insert(data_path="scale", frame=frame)


def apply_material_color_changes() -> None:
    material_by_id = {mat.name: mat for mat in bpy.data.materials}
    for row in read_csv(TUBE_EVENTS_CSV):
        tube = get_object(row["tube_id"])
        material = material_by_id.get(row["tube_visual_color"])
        if tube and material:
            tube.data.materials.clear()
            tube.data.materials.append(material)


def add_event_text_overlay() -> None:
    overlay = ensure_empty(OBJECTS["event_overlay_group"])
    for row in read_csv(KEYFRAME_CSV):
        if not row["event_label"]:
            continue
        frame = int(row["frame"])
        text_curve = bpy.data.curves.new(f"event_{frame}_{row['event_label']}", "FONT")
        text_curve.body = row["event_label"]
        text_obj = bpy.data.objects.new(text_curve.name, text_curve)
        bpy.context.scene.collection.objects.link(text_obj)
        text_obj.parent = overlay
        text_obj.location = (-0.6, -0.6, 0.8)
        text_obj.hide_viewport = False
        text_obj.hide_render = False
        text_obj.keyframe_insert(data_path="hide_viewport", frame=frame)
        text_obj.keyframe_insert(data_path="hide_render", frame=frame)


def configure_camera_and_lights() -> None:
    if not bpy.context.scene.camera:
        camera_data = bpy.data.cameras.new("PlaybackCamera")
        camera = bpy.data.objects.new("PlaybackCamera", camera_data)
        bpy.context.scene.collection.objects.link(camera)
        camera.location = (0.8, -1.2, 0.9)
        camera.rotation_euler = (1.1, 0.0, 0.55)
        bpy.context.scene.camera = camera
    if not bpy.data.objects.get("PlaybackAreaLight"):
        light_data = bpy.data.lights.new("PlaybackAreaLight", "AREA")
        light = bpy.data.objects.new("PlaybackAreaLight", light_data)
        bpy.context.scene.collection.objects.link(light)
        light.location = (0.0, -0.6, 1.5)
        light.data.energy = 500


def optionally_render_animation(render: bool = False) -> None:
    if not render:
        return
    bpy.context.scene.render.filepath = str(PLAYBACK_DIR / "assets" / "blender_playback_v1.mp4")
    bpy.ops.render.render(animation=True)


def main(render: bool = False) -> None:
    load_or_reference_imported_cad_objects()
    create_materials()
    insert_motion_keyframes()
    process_tube_attach_detach_events()
    apply_material_color_changes()
    add_event_text_overlay()
    configure_camera_and_lights()
    optionally_render_animation(render=render)


if __name__ == "__main__":
    main(render=False)
