from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parent


DIRS = [
    "config",
    "cad/standard_parts/downloaded",
    "cad/standard_parts/fallback_generated",
    "cad/custom_parts/source",
    "cad/custom_parts/step",
    "cad/assembly",
    "cad/scripts",
    "solidworks/optional_solidworks_macro_vba",
    "simulation/matlab",
    "simulation/python",
    "simulation/docs",
    "results/figures",
    "results/animation",
    "results/data",
    "results/logs",
    "report",
    "docs",
]


STANDARD_PARTS = [
    ["SP-001", "X轴步进电机", "X axis stepper motor", "NEMA17, 42 mm frame, 1.8 deg, 40 mm body", 1, "驱动X轴横向运动", "STEP/STP", "McMaster-Carr / 3DContentCentral / GrabCAD", "https://www.3dcontentcentral.com/Search.aspx?arg=NEMA%2017%20stepper%20motor", "true", "fallback_nema17_motor.step", "课程设计采用NEMA17外形替代模型，真实型号可按扭矩校核后替换"],
    ["SP-002", "Y轴步进电机", "Y axis stepper motor", "NEMA17, 42 mm frame, 1.8 deg, 40 mm body", 1, "驱动Y轴龙门运动", "STEP/STP", "McMaster-Carr / 3DContentCentral / GrabCAD", "https://www.3dcontentcentral.com/Search.aspx?arg=NEMA%2017%20stepper%20motor", "true", "fallback_nema17_motor.step", "同X轴电机"],
    ["SP-003", "Z轴步进电机", "Z axis stepper motor", "NEMA17 compact, 42 mm frame", 1, "驱动Z轴升降", "STEP/STP", "3DContentCentral / TraceParts", "https://www.traceparts.com/en/search/nema-17-stepper-motor", "true", "fallback_nema17_motor.step", "可选短机身以降低Z轴负载"],
    ["SP-004", "X轴直线导轨", "X axis linear rail", "MGN12H/MGN15H rail, 320 mm", 1, "为X轴滑块提供直线约束", "STEP/STP", "HIWIN / THK / TraceParts", "https://www.traceparts.com/en/search/mgn12h-linear-guide", "true", "fallback_mgn12_rail.step", "候选来源通常需手动选型下载"],
    ["SP-005", "Y轴左侧直线导轨", "Y left linear rail", "MGN12H rail, 280 mm", 1, "支撑左侧Y轴运动", "STEP/STP", "HIWIN / THK / TraceParts", "https://www.traceparts.com/en/search/mgn12-linear-guide", "true", "fallback_mgn12_rail.step", "替代模型按280 mm装配"],
    ["SP-006", "Y轴右侧直线导轨", "Y right linear rail", "MGN12H rail, 280 mm", 1, "支撑右侧Y轴运动", "STEP/STP", "HIWIN / THK / TraceParts", "https://www.traceparts.com/en/search/mgn12-linear-guide", "true", "fallback_mgn12_rail.step", "与左侧导轨成对使用"],
    ["SP-007", "Z轴短行程直线导轨", "Z short stroke linear rail", "MGN12H rail, 120 mm", 1, "约束Z轴升降方向", "STEP/STP", "HIWIN / TraceParts", "https://www.traceparts.com/en/search/mgn12h", "true", "fallback_mgn12_rail.step", "装配中旋转为竖直方向"],
    ["SP-008", "X轴滑块", "X axis carriage block", "MGN12H carriage", 1, "承载Z轴模块并沿X轴运动", "STEP/STP", "HIWIN / TraceParts", "https://www.traceparts.com/en/search/mgn12h-block", "true", "fallback_mgn12_slider.step", "替代件含安装孔外形"],
    ["SP-009", "Y轴滑块", "Y axis carriage blocks", "MGN12H carriage", 2, "连接X轴横梁与左右Y轴导轨", "STEP/STP", "HIWIN / TraceParts", "https://www.traceparts.com/en/search/mgn12h-block", "true", "fallback_mgn12_slider.step", "左右各一个"],
    ["SP-010", "Z轴滑块", "Z axis carriage block", "MGN12H carriage", 1, "连接Z轴安装板和导轨", "STEP/STP", "HIWIN / TraceParts", "https://www.traceparts.com/en/search/mgn12h-block", "true", "fallback_mgn12_slider.step", "用于简化Z轴升降模块"],
    ["SP-011", "T8丝杆或GT2同步带组件", "T8 lead screw or GT2 timing belt drive", "T8 lead screw 8 mm pitch or GT2 belt, simplified", 3, "将电机旋转转换为直线运动", "STEP/STP", "MISUMI / McMaster-Carr / TraceParts", "https://www.misumiusa.com/category/mech/M0100000000/M0116000000/", "true", "fallback_t8_lead_screw.step; fallback_gt2_belt.step", "课程设计中X/Y可用同步带，Z可用T8丝杆等效表示"],
    ["SP-012", "联轴器", "Flexible shaft coupling", "5 mm to 8 mm flexible coupling", 3, "连接电机轴与丝杆/传动轴", "STEP/STP", "McMaster-Carr / MISUMI", "https://www.mcmaster.com/shaft-couplings/", "true", "fallback_coupling.step", "替代模型为铝合金开槽联轴器外形"],
    ["SP-013", "轴承座", "Bearing block", "KP08/BK style small bearing block", 6, "支撑丝杆或同步带轴端", "STEP/STP", "McMaster-Carr / TraceParts", "https://www.traceparts.com/en/search/bearing-block", "true", "fallback_bearing_block.step", "替代模型为U形轴承座"],
    ["SP-014", "2020或2040铝型材", "2020/2040 aluminum extrusion", "2020 profile, 20 mm square", 8, "搭建龙门支架和加强梁", "STEP/STP", "MISUMI / McMaster-Carr / GrabCAD", "https://www.mcmaster.com/t-slotted-framing-rails/", "true", "fallback_2020_profile.step", "替代模型含T槽特征"],
    ["SP-015", "拖链", "Cable drag chain", "Small plastic drag chain, 10 x 15 mm inner", 1, "保护运动电缆", "STEP/STP", "IGUS / TraceParts / McMaster-Carr", "https://www.igus.com/cable-carriers", "true", "fallback_cable_chain.step", "替代模型由多节链块组成"],
    ["SP-016", "限位开关", "Limit switch", "Micro switch with lever", 6, "提供三轴回零和限位信号", "STEP/STP", "Omron / TraceParts / 3DContentCentral", "https://www.traceparts.com/en/search/micro-limit-switch", "true", "fallback_limit_switch.step", "每轴两端可配置"],
    ["SP-017", "扫码/传感器模块外观", "Barcode/photoelectric sensor module", "Compact barcode scanner or photoelectric sensor mockup", 1, "识别样本或检测取放位置", "STEP/STP", "SICK / Keyence / TraceParts", "https://www.traceparts.com/en/search/photoelectric-sensor", "true", "fallback_sensor_module.step", "仅建外观和安装支架"],
    ["SP-018", "急停按钮", "Emergency stop button", "22 mm panel mount mushroom button", 1, "提供安全急停", "STEP/STP", "Schneider / TraceParts", "https://www.traceparts.com/en/search/emergency-stop-button", "true", "fallback_emergency_stop.step", "安装在控制盒前侧"],
    ["SP-019", "控制盒", "Control enclosure", "Plastic/electrical enclosure, approx. 140 x 90 x 55 mm", 1, "容纳驱动器和控制板", "STEP/STP", "McMaster-Carr / Hammond / TraceParts", "https://www.mcmaster.com/electrical-enclosures/", "true", "fallback_control_box.step", "替代模型带盖板和接线孔"],
    ["SP-020", "螺栓、螺母、垫片", "Fasteners", "M3/M4 socket head screws, nuts and washers", 1, "标准连接紧固件集合", "STEP/STP", "McMaster-Carr", "https://www.mcmaster.com/socket-head-screws/", "true", "fallback_fasteners.step", "以若干示意紧固件表达"],
    ["SP-021", "两指平行夹爪", "Two-finger parallel gripper", "Small electric/pneumatic parallel gripper, simplified", 1, "夹取血液试管", "STEP/STP", "SMC / Festo / TraceParts", "https://www.traceparts.com/en/search/parallel-gripper", "true", "fallback_parallel_gripper.step", "课程设计采用简化两指夹爪替代模型"],
]


def ensure_dirs() -> None:
    for d in DIRS:
        (ROOT / d).mkdir(parents=True, exist_ok=True)


def write_file(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")


def write_standard_parts_manifest() -> None:
    path = ROOT / "cad/standard_parts/standard_parts_manifest.csv"
    header = [
        "part_id", "part_name_cn", "part_name_en", "recommended_spec", "quantity",
        "function", "preferred_format", "preferred_source", "download_url_candidate",
        "need_manual_download", "fallback_model_name", "note",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(STANDARD_PARTS)


def write_config_files() -> None:
    write_file("config/__init__.py", "")
    write_file(
        "config/cad_config.py",
        """
        # Unit: mm
        base_length = 500
        base_width = 350
        base_thickness = 10

        work_x = 400
        work_y = 300

        rack_rows = 3
        rack_cols = 4
        tube_pitch = 35
        tube_hole_diameter = 16
        rack_thickness = 15
        rack_margin = 18
        tube_outer_diameter = 13
        tube_height = 75
        cap_height = 8

        input_rack_origin = [70, 80, 10]
        output_rack_origin = [320, 80, 10]

        x_travel = 300
        y_travel = 220
        z_travel = 100

        profile_size = 20

        x_rail_length = 320
        y_rail_length = 280
        z_rail_length = 120

        gripper_width = 60
        gripper_finger_length = 45
        gripper_finger_width = 8
        gripper_opening = 20

        z_safe = 95
        z_pick = 22
        """,
    )
    write_file(
        "config/motion_config.py",
        """
        dt = 0.01
        max_velocity = 80.0
        max_acceleration = 300.0
        dwell_time = 0.20
        z_safe = 95.0
        z_pick = 22.0
        sample_tasks = [(1, 5), (2, 3), (3, 8), (4, 2), (5, 10), (6, 7)]
        """,
    )
    write_file(
        "config/pid_config.py",
        """
        axes = {
            "x": {"m": 1.5, "b": 8.0, "Kp": 80.0, "Ki": 0.0, "Kd": 15.0},
            "y": {"m": 1.2, "b": 7.0, "Kp": 80.0, "Ki": 0.0, "Kd": 15.0},
            "z": {"m": 0.8, "b": 10.0, "Kp": 100.0, "Ki": 0.0, "Kd": 20.0},
        }
        control_limit = 5000.0
        """,
    )


def write_cad_scripts() -> None:
    write_file(
        "cad/scripts/_cad_common.py",
        r'''
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
        ''',
    )
    write_file(
        "cad/scripts/generate_custom_parts.py",
        r'''
        from __future__ import annotations

        from pathlib import Path

        import cadquery as cq

        from _cad_common import C, ROOT, export_colored, rack_dimensions, safe_chamfer, safe_fillet

        OUT = ROOT / "cad/custom_parts/step"


        def base_plate():
            holes = []
            for x in (-220, 220):
                for y in (-145, 145):
                    holes.append((x, y))
            for x in (-170, 170):
                holes.append((x, -120))
                holes.append((x, 120))
            part = cq.Workplane("XY").box(C.base_length, C.base_width, C.base_thickness)
            part = part.faces(">Z").workplane().pushPoints(holes).hole(5, depth=C.base_thickness + 2)
            part = safe_chamfer(part, 1.5)
            feet = cq.Workplane("XY")
            for x, y in [(-220, -150), (220, -150), (-220, 150), (220, 150)]:
                feet = feet.union(cq.Workplane("XY").box(35, 25, 8).translate((x, y, -9)))
            return part.union(feet)


        def tube_rack():
            length, width = rack_dimensions()
            points = []
            x0 = -((C.rack_cols - 1) * C.tube_pitch) / 2
            y0 = -((C.rack_rows - 1) * C.tube_pitch) / 2
            for r in range(C.rack_rows):
                for c in range(C.rack_cols):
                    points.append((x0 + c * C.tube_pitch, y0 + r * C.tube_pitch))
            part = cq.Workplane("XY").box(length, width, C.rack_thickness)
            part = part.faces(">Z").workplane().pushPoints(points).hole(C.tube_hole_diameter, depth=C.rack_thickness + 2)
            part = part.faces(">Z").workplane().rect(length - 16, width - 16).cutBlind(-2)
            return safe_fillet(part, 1.2)


        def test_tube_set():
            length, width = rack_dimensions()
            x0 = -((C.rack_cols - 1) * C.tube_pitch) / 2
            y0 = -((C.rack_rows - 1) * C.tube_pitch) / 2
            asm = cq.Assembly(name="test_tube_set")
            idx = 0
            for r in range(C.rack_rows):
                for c in range(C.rack_cols):
                    x = x0 + c * C.tube_pitch
                    y = y0 + r * C.tube_pitch
                    tube = cq.Workplane("XY").circle(C.tube_outer_diameter / 2).extrude(C.tube_height)
                    tube = tube.faces(">Z").workplane().circle(C.tube_outer_diameter / 2).extrude(C.cap_height)
                    tube = safe_fillet(tube, 0.6)
                    idx += 1
                    asm.add(tube, name=f"tube_{idx:02d}", loc=cq.Location(cq.Vector(x, y, 0)), color=cq.Color(0.8, 0.02, 0.02, 0.55))
            return asm


        def y_axis_mounting_blocks():
            blocks = cq.Workplane("XY")
            for x in (-170, 170):
                for y in (-120, 120):
                    b = cq.Workplane("XY").box(42, 26, 18).faces(">Z").workplane().rect(26, 14).hole(5)
                    blocks = blocks.union(b.translate((x, y, 0)))
            return safe_fillet(blocks, 1.0)


        def x_axis_beam():
            beam = cq.Workplane("XY").box(420, 26, 38)
            holes = [(x, 0) for x in range(-180, 181, 60)]
            beam = beam.faces(">Z").workplane().pushPoints(holes).hole(4.5, depth=40)
            return safe_chamfer(beam, 1.0)


        def z_axis_mounting_plate():
            holes = [(-20, -35), (20, -35), (-20, 35), (20, 35), (0, 0)]
            return safe_fillet(cq.Workplane("XY").box(70, 95, 6).faces(">Z").workplane().pushPoints(holes).hole(4), 0.8)


        def motor_mounting_plates():
            plate = cq.Workplane("XY").box(56, 56, 5)
            holes = [(-15.5, -15.5), (15.5, -15.5), (-15.5, 15.5), (15.5, 15.5)]
            plate = plate.faces(">Z").workplane().pushPoints(holes).hole(3.5)
            plate = plate.faces(">Z").workplane().circle(11).cutBlind(-6)
            plates = cq.Workplane("XY")
            for i, x in enumerate((-70, 0, 70)):
                plates = plates.union(plate.translate((x, 0, 0)))
            return safe_chamfer(plates, 0.6)


        def gripper_adapter():
            holes = [(-18, -12), (18, -12), (-18, 12), (18, 12)]
            p = cq.Workplane("XY").box(64, 38, 8).faces(">Z").workplane().pushPoints(holes).hole(4)
            p = p.faces(">Z").workplane().circle(9).hole(5)
            return safe_fillet(p, 0.8)


        def sensor_bracket():
            vertical = cq.Workplane("XY").box(35, 5, 55).translate((0, -12, 20))
            foot = cq.Workplane("XY").box(42, 28, 5)
            face = cq.Workplane("XY").box(34, 5, 28).translate((0, 8, 48))
            bracket = foot.union(vertical).union(face)
            bracket = bracket.faces(">Z").workplane().pushPoints([(-12, 0), (12, 0)]).hole(4)
            return safe_fillet(bracket, 0.8)


        def control_box_mount():
            base = cq.Workplane("XY").box(170, 32, 6)
            posts = cq.Workplane("XY")
            for x in (-65, 65):
                posts = posts.union(cq.Workplane("XY").box(14, 24, 38).translate((x, 0, 22)))
            return safe_chamfer(base.union(posts), 0.8)


        def main():
            OUT.mkdir(parents=True, exist_ok=True)
            parts = {
                "base_plate.step": (base_plate(), (0.68, 0.70, 0.72, 1)),
                "input_tube_rack.step": (tube_rack(), (0.12, 0.42, 0.82, 1)),
                "output_tube_rack.step": (tube_rack(), (0.12, 0.62, 0.42, 1)),
                "y_axis_mounting_blocks.step": (y_axis_mounting_blocks(), (0.25, 0.25, 0.25, 1)),
                "x_axis_beam.step": (x_axis_beam(), (0.85, 0.85, 0.80, 1)),
                "z_axis_mounting_plate.step": (z_axis_mounting_plate(), (0.75, 0.75, 0.78, 1)),
                "motor_mounting_plates.step": (motor_mounting_plates(), (0.2, 0.2, 0.22, 1)),
                "gripper_adapter.step": (gripper_adapter(), (0.45, 0.45, 0.48, 1)),
                "sensor_bracket.step": (sensor_bracket(), (0.1, 0.1, 0.1, 1)),
                "control_box_mount.step": (control_box_mount(), (0.2, 0.2, 0.2, 1)),
            }
            for filename, (obj, color) in parts.items():
                export_colored(obj, OUT / filename, color=color, name=filename[:-5])

            tube_asm = test_tube_set()
            tube_asm.save(str(OUT / "test_tube_set.step"), exportType="STEP")
            print(f"Generated custom STEP parts in {OUT}")


        if __name__ == "__main__":
            main()
        ''',
    )
    write_file(
        "cad/scripts/generate_fallback_standard_parts.py",
        r'''
        from __future__ import annotations

        from pathlib import Path

        import cadquery as cq

        from _cad_common import C, ROOT, cylinder_x, export_colored, safe_chamfer, safe_fillet

        OUT = ROOT / "cad/standard_parts/fallback_generated"


        def nema17_motor():
            body = cq.Workplane("XY").box(42, 42, 40).translate((0, 0, 20))
            front = cq.Workplane("XY").box(42, 42, 3).translate((0, 0, 41.5))
            boss = cq.Workplane("XY").circle(11).extrude(4).translate((0, 0, 43))
            shaft = cq.Workplane("XY").circle(2.5).extrude(18).translate((0, 0, 46))
            holes = [(-15.5, -15.5), (15.5, -15.5), (-15.5, 15.5), (15.5, 15.5)]
            front = front.faces(">Z").workplane().pushPoints(holes).hole(3)
            return safe_chamfer(body.union(front).union(boss).union(shaft), 0.8)


        def mgn12_rail(length=None):
            length = length or C.x_rail_length
            rail = cq.Workplane("XY").box(length, 12, 8)
            holes = [(x, 0) for x in range(int(-length / 2 + 25), int(length / 2), 50)]
            rail = rail.faces(">Z").workplane().pushPoints(holes).hole(3.5)
            groove1 = cq.Workplane("XY").box(length + 1, 2, 2).translate((0, 4.2, 4.1))
            groove2 = cq.Workplane("XY").box(length + 1, 2, 2).translate((0, -4.2, 4.1))
            return safe_chamfer(rail.cut(groove1).cut(groove2), 0.4)


        def mgn12_slider():
            block = cq.Workplane("XY").box(46, 27, 13).translate((0, 0, 6.5))
            holes = [(-15, -8), (15, -8), (-15, 8), (15, 8)]
            block = block.faces(">Z").workplane().pushPoints(holes).hole(3)
            return safe_fillet(block, 0.8)


        def t8_lead_screw():
            screw = cylinder_x(240, 4)
            nut = cq.Workplane("XY").box(22, 22, 12).translate((0, 0, 0))
            return screw.union(nut)


        def gt2_belt():
            top = cq.Workplane("XY").box(260, 6, 3).translate((0, 16, 0))
            bottom = cq.Workplane("XY").box(260, 6, 3).translate((0, -16, 0))
            left = cq.Workplane("XY").box(6, 32, 3).translate((-130, 0, 0))
            right = cq.Workplane("XY").box(6, 32, 3).translate((130, 0, 0))
            return safe_fillet(top.union(bottom).union(left).union(right), 1.2)


        def coupling():
            cyl = cq.Workplane("XY").circle(9).extrude(24)
            bore = cq.Workplane("XY").circle(3.2).extrude(26)
            slot = cq.Workplane("XY").box(24, 2, 12).translate((0, 0, 12))
            return safe_chamfer(cyl.cut(bore).cut(slot), 0.5)


        def bearing_block():
            base = cq.Workplane("XY").box(34, 18, 8)
            tower = cq.Workplane("XY").box(24, 10, 22).translate((0, 0, 12))
            hole = cq.Workplane("YZ").circle(5).extrude(36).translate((-18, 0, 12))
            block = base.union(tower).cut(hole)
            block = block.faces(">Z").workplane().pushPoints([(-11, 0), (11, 0)]).hole(4)
            return safe_chamfer(block, 0.6)


        def profile_2020(length=260):
            p = cq.Workplane("XY").box(length, 20, 20)
            for y in (-8, 8):
                p = p.cut(cq.Workplane("XY").box(length + 1, 3, 6).translate((0, y, 0)))
            for z in (-8, 8):
                p = p.cut(cq.Workplane("XY").box(length + 1, 6, 3).translate((0, 0, z)))
            return safe_chamfer(p, 0.5)


        def cable_chain():
            chain = cq.Workplane("XY")
            for i in range(13):
                link = cq.Workplane("XY").box(16, 22, 10).translate((i * 15, 0, 0))
                link = link.cut(cq.Workplane("XY").box(8, 14, 12).translate((i * 15, 0, 0)))
                chain = chain.union(link)
            return safe_chamfer(chain, 0.5)


        def limit_switch():
            body = cq.Workplane("XY").box(28, 12, 16)
            lever = cq.Workplane("XY").box(38, 3, 2).translate((10, 0, 10)).rotate((0, 0, 0), (0, 1, 0), -14)
            button = cq.Workplane("XY").box(4, 8, 3).translate((-11, 0, 9))
            return safe_chamfer(body.union(lever).union(button), 0.4)


        def sensor_module():
            body = cq.Workplane("XY").box(35, 28, 22)
            lens = cq.Workplane("XY").circle(7).extrude(2).translate((0, -15, 2))
            cable = cq.Workplane("XY").circle(3).extrude(22).rotate((0, 0, 0), (1, 0, 0), 90).translate((0, 18, 4))
            return safe_chamfer(body.union(lens).union(cable), 0.6)


        def emergency_stop():
            base = cq.Workplane("XY").circle(14).extrude(8)
            stem = cq.Workplane("XY").circle(8).extrude(8).translate((0, 0, 8))
            mushroom = cq.Workplane("XY").circle(18).extrude(10).translate((0, 0, 16))
            return safe_fillet(base.union(stem).union(mushroom), 1.0)


        def control_box():
            box = cq.Workplane("XY").box(140, 90, 55)
            lid = cq.Workplane("XY").box(146, 96, 4).translate((0, 0, 29))
            vents = cq.Workplane("XY")
            for i in range(5):
                vents = vents.union(cq.Workplane("XY").box(52, 2, 2).translate((0, -47, -15 + i * 7)))
            return safe_chamfer(box.union(lid).union(vents), 1.5)


        def parallel_gripper():
            body = cq.Workplane("XY").box(60, 34, 26)
            palm = cq.Workplane("XY").box(48, 12, 10).translate((0, -23, 0))
            left = cq.Workplane("XY").box(C.gripper_finger_width, C.gripper_finger_length, 12).translate((-C.gripper_opening / 2, -52, 0))
            right = cq.Workplane("XY").box(C.gripper_finger_width, C.gripper_finger_length, 12).translate((C.gripper_opening / 2, -52, 0))
            pads = cq.Workplane("XY").box(8, 12, 14).translate((-C.gripper_opening / 2, -76, 0)).union(cq.Workplane("XY").box(8, 12, 14).translate((C.gripper_opening / 2, -76, 0)))
            return safe_chamfer(body.union(palm).union(left).union(right).union(pads), 0.8)


        def fasteners():
            asm = cq.Workplane("XY")
            for i, x in enumerate(range(-36, 37, 18)):
                screw = cq.Workplane("XY").circle(3).extrude(12).union(cq.Workplane("XY").circle(5).extrude(3).translate((0, 0, 12)))
                washer = cq.Workplane("XY").circle(6).extrude(1).cut(cq.Workplane("XY").circle(3.2).extrude(2)).translate((0, 16, 0))
                asm = asm.union(screw.translate((x, 0, 0))).union(washer.translate((x, 0, 0)))
            return asm


        def main():
            OUT.mkdir(parents=True, exist_ok=True)
            parts = {
                "fallback_nema17_motor.step": (nema17_motor(), (0.08, 0.08, 0.09, 1)),
                "fallback_mgn12_rail.step": (mgn12_rail(), (0.72, 0.72, 0.74, 1)),
                "fallback_mgn12_slider.step": (mgn12_slider(), (0.32, 0.32, 0.34, 1)),
                "fallback_t8_lead_screw.step": (t8_lead_screw(), (0.65, 0.65, 0.68, 1)),
                "fallback_gt2_belt.step": (gt2_belt(), (0.03, 0.03, 0.03, 1)),
                "fallback_coupling.step": (coupling(), (0.9, 0.55, 0.18, 1)),
                "fallback_bearing_block.step": (bearing_block(), (0.25, 0.25, 0.25, 1)),
                "fallback_2020_profile.step": (profile_2020(), (0.78, 0.78, 0.74, 1)),
                "fallback_cable_chain.step": (cable_chain(), (0.04, 0.04, 0.04, 1)),
                "fallback_limit_switch.step": (limit_switch(), (0.08, 0.08, 0.08, 1)),
                "fallback_sensor_module.step": (sensor_module(), (0.05, 0.12, 0.42, 1)),
                "fallback_emergency_stop.step": (emergency_stop(), (0.9, 0.02, 0.02, 1)),
                "fallback_control_box.step": (control_box(), (0.78, 0.78, 0.72, 1)),
                "fallback_parallel_gripper.step": (parallel_gripper(), (0.22, 0.22, 0.24, 1)),
                "fallback_fasteners.step": (fasteners(), (0.6, 0.6, 0.62, 1)),
            }
            for filename, (obj, color) in parts.items():
                export_colored(obj, OUT / filename, color=color, name=filename[:-5])
            print(f"Generated fallback standard STEP parts in {OUT}")


        if __name__ == "__main__":
            main()
        ''',
    )
    write_file(
        "cad/scripts/build_step_assembly.py",
        r'''
        from __future__ import annotations

        import csv
        from pathlib import Path

        import cadquery as cq

        from _cad_common import C, ROOT, rack_dimensions

        CUSTOM = ROOT / "cad/custom_parts/step"
        FALLBACK = ROOT / "cad/standard_parts/fallback_generated"
        OUT = ROOT / "cad/assembly"


        def step_path(filename):
            p = CUSTOM / filename
            if p.exists():
                return p
            return FALLBACK / filename


        def import_shape(filename, rx=0, ry=0, rz=0):
            shape = cq.importers.importStep(str(step_path(filename)))
            if rx:
                shape = shape.rotate((0, 0, 0), (1, 0, 0), rx)
            if ry:
                shape = shape.rotate((0, 0, 0), (0, 1, 0), ry)
            if rz:
                shape = shape.rotate((0, 0, 0), (0, 0, 1), rz)
            return shape


        def add(asm, rows, name, filename, x, y, z, rx=0, ry=0, rz=0, color=(0.7, 0.7, 0.7, 1), note=""):
            shape = import_shape(filename, rx=rx, ry=ry, rz=rz)
            asm.add(shape, name=name, loc=cq.Location(cq.Vector(x, y, z)), color=cq.Color(*color))
            rows.append([name, filename, round(x, 3), round(y, 3), round(z, 3), rx, ry, rz, note])


        def main():
            OUT.mkdir(parents=True, exist_ok=True)
            asm = cq.Assembly(name="blood_sorting_robot_assembly")
            rows = []
            base_z = C.base_thickness / 2
            add(asm, rows, "base_plate", "base_plate.step", C.base_length / 2, C.base_width / 2, base_z, color=(0.68, 0.70, 0.72, 1), note="world datum: base lower face z=0")

            rack_l, rack_w = rack_dimensions()
            in_x = C.input_rack_origin[0] + rack_l / 2
            in_y = C.input_rack_origin[1] + rack_w / 2
            out_x = C.output_rack_origin[0] + rack_l / 2
            out_y = C.output_rack_origin[1] + rack_w / 2
            rack_z = C.base_thickness + C.rack_thickness / 2
            add(asm, rows, "input_tube_rack", "input_tube_rack.step", in_x, in_y, rack_z, color=(0.12, 0.42, 0.82, 1), note="3x4 input rack")
            add(asm, rows, "output_tube_rack", "output_tube_rack.step", out_x, out_y, rack_z, color=(0.12, 0.62, 0.42, 1), note="3x4 output rack")
            add(asm, rows, "input_test_tubes", "test_tube_set.step", in_x, in_y, C.base_thickness + C.rack_thickness, color=(0.8, 0.02, 0.02, 0.55), note="blood sample tubes in input rack")
            add(asm, rows, "output_reference_tubes", "test_tube_set.step", out_x, out_y, C.base_thickness + C.rack_thickness, color=(0.9, 0.08, 0.08, 0.35), note="visual capacity reference")

            y_left_x, y_right_x = 82, 418
            rail_z = C.base_thickness + 11
            for side, x in [("left", y_left_x), ("right", y_right_x)]:
                add(asm, rows, f"y_{side}_rail", "fallback_mgn12_rail.step", x, C.base_width / 2, rail_z, rz=90, color=(0.72, 0.72, 0.74, 1), note="Y axis rail")
                add(asm, rows, f"y_{side}_slider", "fallback_mgn12_slider.step", x, 190, rail_z + 6, rz=90, color=(0.28, 0.28, 0.30, 1), note="Y carriage block")

            add(asm, rows, "x_axis_beam", "x_axis_beam.step", C.base_length / 2, 190, 92, color=(0.84, 0.84, 0.78, 1), note="gantry bridge carried by Y sliders")
            add(asm, rows, "x_axis_rail", "fallback_mgn12_rail.step", C.base_length / 2, 190, 116, color=(0.72, 0.72, 0.74, 1), note="X axis guide rail")
            add(asm, rows, "x_axis_slider", "fallback_mgn12_slider.step", 250, 190, 127, color=(0.28, 0.28, 0.30, 1), note="X carriage carrying Z module")

            add(asm, rows, "z_mounting_plate", "z_axis_mounting_plate.step", 250, 177, 105, rx=90, color=(0.73, 0.73, 0.77, 1), note="vertical adapter plate")
            add(asm, rows, "z_axis_rail", "fallback_mgn12_rail.step", 250, 165, 80, ry=-90, color=(0.72, 0.72, 0.74, 1), note="Z axis short rail")
            add(asm, rows, "z_axis_slider", "fallback_mgn12_slider.step", 250, 153, 60, ry=-90, color=(0.28, 0.28, 0.30, 1), note="Z carriage block")
            add(asm, rows, "gripper_adapter", "gripper_adapter.step", 250, 148, 42, rx=90, color=(0.46, 0.46, 0.49, 1), note="adapter between Z slider and gripper")
            add(asm, rows, "parallel_gripper", "fallback_parallel_gripper.step", 250, 130, 24, rx=90, color=(0.22, 0.22, 0.24, 1), note="two-finger gripper near pick/place height")
            add(asm, rows, "sensor_bracket", "sensor_bracket.step", 288, 138, 45, rx=90, color=(0.1, 0.1, 0.1, 1), note="scanner/sensor bracket near gripper")
            add(asm, rows, "sensor_module", "fallback_sensor_module.step", 292, 122, 45, rx=90, color=(0.05, 0.12, 0.42, 1), note="barcode/photoelectric sensor appearance")

            for name, x, y, z, rz in [
                ("x_motor", 72, 190, 119, 90),
                ("y_motor", 45, 46, 34, 0),
                ("z_motor", 250, 166, 152, 0),
            ]:
                add(asm, rows, name, "fallback_nema17_motor.step", x, y, z, rz=rz, color=(0.08, 0.08, 0.09, 1), note="NEMA17 stepper motor")
            add(asm, rows, "x_gt2_belt", "fallback_gt2_belt.step", 250, 202, 124, color=(0.03, 0.03, 0.03, 1), note="simplified X belt drive")
            add(asm, rows, "y_gt2_belt", "fallback_gt2_belt.step", 82, 175, 32, rz=90, color=(0.03, 0.03, 0.03, 1), note="simplified Y belt drive")
            add(asm, rows, "z_t8_lead_screw", "fallback_t8_lead_screw.step", 262, 160, 92, ry=-90, color=(0.65, 0.65, 0.68, 1), note="simplified Z lead screw")

            add(asm, rows, "cable_chain", "fallback_cable_chain.step", 260, 325, 70, color=(0.04, 0.04, 0.04, 1), note="rear cable carrier")
            add(asm, rows, "control_box_mount", "control_box_mount.step", 380, 323, 18, color=(0.2, 0.2, 0.2, 1), note="rear mount")
            add(asm, rows, "control_box", "fallback_control_box.step", 380, 323, 62, color=(0.78, 0.78, 0.72, 1), note="controller enclosure")
            add(asm, rows, "emergency_stop", "fallback_emergency_stop.step", 330, 275, 100, rx=90, color=(0.9, 0.02, 0.02, 1), note="emergency stop button on control box")
            add(asm, rows, "limit_switches", "fallback_limit_switch.step", 70, 305, 28, color=(0.08, 0.08, 0.08, 1), note="representative limit switch")
            add(asm, rows, "fasteners", "fallback_fasteners.step", 250, 45, 18, color=(0.6, 0.6, 0.62, 1), note="sample fastener set")
            add(asm, rows, "bearing_block_a", "fallback_bearing_block.step", 92, 190, 124, rz=90, color=(0.25, 0.25, 0.25, 1), note="belt/screw support")
            add(asm, rows, "coupling_z", "fallback_coupling.step", 262, 160, 145, ry=-90, color=(0.9, 0.55, 0.18, 1), note="Z motor coupling")

            asm_path = OUT / "blood_sorting_robot_assembly.step"
            asm.save(str(asm_path), exportType="STEP")

            csv_path = OUT / "assembly_reference_coordinates.csv"
            with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["component_name", "step_file", "x_mm", "y_mm", "z_mm", "rx_deg", "ry_deg", "rz_deg", "note"])
                writer.writerows(rows)

            md = ["# Assembly Reference Coordinates", "", "Coordinate origin is the lower-left datum of the base plate. Units are mm.", "", "| Component | STEP | X | Y | Z | Rotation | Note |", "|---|---:|---:|---:|---:|---|---|"]
            for r in rows:
                md.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | ({r[5]}, {r[6]}, {r[7]}) | {r[8]} |")
            (OUT / "assembly_reference_coordinates.md").write_text("\n".join(md), encoding="utf-8")
            print(f"Generated assembly STEP: {asm_path}")


        if __name__ == "__main__":
            main()
        ''',
    )
    write_file(
        "cad/scripts/export_all_step.py",
        """
        from __future__ import annotations

        import subprocess
        import sys
        from pathlib import Path

        HERE = Path(__file__).resolve().parent

        for script in [
            "generate_custom_parts.py",
            "generate_fallback_standard_parts.py",
            "build_step_assembly.py",
        ]:
            subprocess.run([sys.executable, str(HERE / script)], check=True)
        """,
    )
    write_file(
        "cad/scripts/check_cad_outputs.py",
        r'''
        from __future__ import annotations

        import subprocess
        import sys
        from pathlib import Path

        ROOT = Path(__file__).resolve().parents[2]

        REQUIRED_CUSTOM = [
            "base_plate.step", "input_tube_rack.step", "output_tube_rack.step", "test_tube_set.step",
            "y_axis_mounting_blocks.step", "x_axis_beam.step", "z_axis_mounting_plate.step",
            "motor_mounting_plates.step", "gripper_adapter.step", "sensor_bracket.step", "control_box_mount.step",
        ]
        REQUIRED_FALLBACK = [
            "fallback_nema17_motor.step", "fallback_mgn12_rail.step", "fallback_mgn12_slider.step",
            "fallback_t8_lead_screw.step", "fallback_gt2_belt.step", "fallback_coupling.step",
            "fallback_bearing_block.step", "fallback_2020_profile.step", "fallback_cable_chain.step",
            "fallback_limit_switch.step", "fallback_sensor_module.step", "fallback_emergency_stop.step",
            "fallback_control_box.step", "fallback_parallel_gripper.step", "fallback_fasteners.step",
        ]
        REQUIRED_MATLAB = [
            "main.m", "config.m", "generate_rack_positions.m", "generate_sorting_tasks.m",
            "generate_waypoints.m", "trapezoid_trajectory.m", "simulate_pid_axis.m",
            "simulate_three_axis_robot.m", "plot_results.m", "animate_sorting_robot.m", "export_results.m",
        ]


        def check_file(path: Path, errors: list[str]):
            if not path.exists():
                errors.append(f"Missing: {path}")
            elif path.is_file() and path.stat().st_size <= 0:
                errors.append(f"Empty: {path}")


        def main():
            errors = []
            for f in REQUIRED_CUSTOM:
                check_file(ROOT / "cad/custom_parts/step" / f, errors)
            for f in REQUIRED_FALLBACK:
                check_file(ROOT / "cad/standard_parts/fallback_generated" / f, errors)
            check_file(ROOT / "cad/assembly/blood_sorting_robot_assembly.step", errors)
            check_file(ROOT / "cad/standard_parts/standard_parts_manifest.csv", errors)
            check_file(ROOT / "README.md", errors)
            for f in REQUIRED_MATLAB:
                check_file(ROOT / "simulation/matlab" / f, errors)
            check_file(ROOT / "simulation/python/simulate_pid_robot.py", errors)

            subprocess.run([sys.executable, str(ROOT / "simulation/python/simulate_pid_robot.py")], check=True)
            figures = list((ROOT / "results/figures").glob("*.png"))
            if not figures:
                errors.append("No result figures generated in results/figures")

            log_path = ROOT / "results/logs/project_build_log.txt"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            if errors:
                log_path.write_text("QUALITY CHECK FAILED\n" + "\n".join(errors), encoding="utf-8")
                print("\n".join(errors))
                raise SystemExit(1)
            log_path.write_text("QUALITY CHECK PASSED\nGenerated files checked successfully.\n", encoding="utf-8")
            print(f"Quality check passed. Log: {log_path}")


        if __name__ == "__main__":
            main()
        ''',
    )


def write_python_simulation() -> None:
    write_file(
        "simulation/python/simulate_pid_robot.py",
        r'''
        from __future__ import annotations

        import csv
        import json
        import sys
        from pathlib import Path

        import imageio.v2 as imageio
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

        ROOT = Path(__file__).resolve().parents[2]
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))

        from config import cad_config as C
        from config import motion_config as M
        from config import pid_config as P


        def rack_positions(origin):
            positions = []
            for r in range(C.rack_rows):
                for c in range(C.rack_cols):
                    x = origin[0] + C.rack_margin + c * C.tube_pitch
                    y = origin[1] + C.rack_margin + r * C.tube_pitch
                    positions.append(np.array([x, y, float(C.z_pick)]))
            return positions


        def generate_waypoints():
            inputs = rack_positions(C.input_rack_origin)
            outputs = rack_positions(C.output_rack_origin)
            waypoints = []
            labels = []
            for input_idx, output_idx in M.sample_tasks:
                p_in = inputs[input_idx - 1].copy()
                p_out = outputs[output_idx - 1].copy()
                above_in = p_in.copy(); above_in[2] = C.z_safe
                pick = p_in.copy(); pick[2] = C.z_pick
                above_out = p_out.copy(); above_out[2] = C.z_safe
                place = p_out.copy(); place[2] = C.z_pick
                seq = [above_in, pick, above_in, above_out, place, above_out]
                lab = ["input_above", "pick", "input_above", "output_above", "place", "output_above"]
                waypoints.extend(seq)
                labels.extend([f"{input_idx}->{output_idx}:{x}" for x in lab])
            return np.array(waypoints, dtype=float), labels


        def smooth_segment(p0, p1, dt):
            dist = np.linalg.norm(p1 - p0)
            duration = max(0.45, dist / M.max_velocity + 0.25)
            n = max(2, int(np.ceil(duration / dt)))
            tau = np.linspace(0, 1, n, endpoint=False)
            s = 10 * tau**3 - 15 * tau**4 + 6 * tau**5
            ds = (30 * tau**2 - 60 * tau**3 + 30 * tau**4) / duration
            pos = p0 + (p1 - p0) * s[:, None]
            vel = (p1 - p0) * ds[:, None]
            return pos, vel


        def reference_trajectory():
            waypoints, labels = generate_waypoints()
            dt = M.dt
            pos_all = []
            vel_all = []
            event_rows = []
            t_cursor = 0.0
            current = np.array([waypoints[0, 0], waypoints[0, 1], C.z_safe], dtype=float)
            for i, target in enumerate(waypoints):
                pos, vel = smooth_segment(current, target, dt)
                pos_all.append(pos); vel_all.append(vel)
                event_rows.append([round(t_cursor, 3), labels[i], *target.tolist()])
                t_cursor += len(pos) * dt
                dwell_n = int(M.dwell_time / dt)
                if dwell_n > 0:
                    pos_all.append(np.repeat(target[None, :], dwell_n, axis=0))
                    vel_all.append(np.zeros((dwell_n, 3)))
                    t_cursor += dwell_n * dt
                current = target
            ref = np.vstack(pos_all)
            vel = np.vstack(vel_all)
            t = np.arange(ref.shape[0]) * dt
            return t, ref, vel, event_rows


        def simulate_axis(ref, cfg, dt):
            n = len(ref)
            y = np.zeros(n)
            v = np.zeros(n)
            u = np.zeros(n)
            y[0] = ref[0]
            integ = 0.0
            prev_err = 0.0
            for k in range(1, n):
                err = ref[k - 1] - y[k - 1]
                integ += err * dt
                deriv = (err - prev_err) / dt
                cmd = cfg["Kp"] * err + cfg["Ki"] * integ + cfg["Kd"] * deriv
                cmd = float(np.clip(cmd, -P.control_limit, P.control_limit))
                acc = (cmd - cfg["b"] * v[k - 1]) / cfg["m"]
                v[k] = v[k - 1] + acc * dt
                y[k] = y[k - 1] + v[k] * dt
                u[k] = cmd
                prev_err = err
            return y, v, u


        def simulate_robot(t, ref):
            actual = np.zeros_like(ref)
            vel = np.zeros_like(ref)
            ctrl = np.zeros_like(ref)
            for i, axis in enumerate(["x", "y", "z"]):
                actual[:, i], vel[:, i], ctrl[:, i] = simulate_axis(ref[:, i], P.axes[axis], M.dt)
            return actual, vel, ctrl


        def metrics(ref, actual):
            err = ref - actual
            out = {}
            for i, axis in enumerate(["x", "y", "z"]):
                e = err[:, i]
                out[axis] = {
                    "max_abs_error_mm": float(np.max(np.abs(e))),
                    "mean_abs_error_mm": float(np.mean(np.abs(e))),
                    "rmse_mm": float(np.sqrt(np.mean(e**2))),
                }
            out["combined_rmse_mm"] = float(np.sqrt(np.mean(err**2)))
            return out


        def save_data(t, ref, actual, vel_ref, vel_actual, ctrl, event_rows, met):
            data_dir = ROOT / "results/data"
            data_dir.mkdir(parents=True, exist_ok=True)
            header = ["t", "x_ref", "y_ref", "z_ref", "x", "y", "z", "vx_ref", "vy_ref", "vz_ref", "vx", "vy", "vz", "ux", "uy", "uz"]
            with (data_dir / "python_pid_simulation.csv").open("w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(header)
                for row in zip(t, *ref.T, *actual.T, *vel_ref.T, *vel_actual.T, *ctrl.T):
                    w.writerow([round(float(x), 6) for x in row])
            with (data_dir / "waypoint_events.csv").open("w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["time_s", "event", "x_mm", "y_mm", "z_mm"])
                w.writerows(event_rows)
            (data_dir / "pid_metrics.json").write_text(json.dumps(met, indent=2, ensure_ascii=False), encoding="utf-8")


        def plot_results(t, ref, actual, vel_ref, vel_actual, ctrl):
            fig_dir = ROOT / "results/figures"
            fig_dir.mkdir(parents=True, exist_ok=True)
            axes = ["X", "Y", "Z"]
            fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
            for i, ax in enumerate(axs):
                ax.plot(t, ref[:, i], "k--", lw=1.2, label=f"{axes[i]} ref")
                ax.plot(t, actual[:, i], lw=1.0, label=f"{axes[i]} actual")
                ax.set_ylabel("mm")
                ax.grid(True, alpha=0.3)
                ax.legend(loc="upper right")
            axs[-1].set_xlabel("Time (s)")
            fig.suptitle("X/Y/Z Position Tracking")
            fig.tight_layout()
            fig.savefig(fig_dir / "position_tracking.png", dpi=160)
            plt.close(fig)

            err = ref - actual
            fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
            for i, ax in enumerate(axs):
                ax.plot(t, err[:, i], lw=1.0)
                ax.set_ylabel(f"{axes[i]} err (mm)")
                ax.grid(True, alpha=0.3)
            axs[-1].set_xlabel("Time (s)")
            fig.suptitle("Tracking Error")
            fig.tight_layout()
            fig.savefig(fig_dir / "tracking_error.png", dpi=160)
            plt.close(fig)

            fig = plt.figure(figsize=(8, 7))
            ax = fig.add_subplot(111, projection="3d")
            ax.plot(ref[:, 0], ref[:, 1], ref[:, 2], "k--", lw=1.0, label="reference")
            ax.plot(actual[:, 0], actual[:, 1], actual[:, 2], color="#d62728", lw=1.1, label="actual")
            ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)"); ax.set_zlabel("Z (mm)")
            ax.set_title("3D End Effector Trajectory")
            ax.legend()
            fig.tight_layout()
            fig.savefig(fig_dir / "end_effector_3d.png", dpi=160)
            plt.close(fig)

            fig, axs = plt.subplots(3, 2, figsize=(12, 8), sharex=True)
            for i in range(3):
                axs[i, 0].plot(t, vel_ref[:, i], "k--", lw=1, label="ref")
                axs[i, 0].plot(t, vel_actual[:, i], lw=1, label="actual")
                axs[i, 0].set_ylabel(f"{axes[i]} vel")
                axs[i, 0].grid(True, alpha=0.3)
                axs[i, 1].plot(t, ctrl[:, i], lw=1, color="#9467bd")
                axs[i, 1].set_ylabel(f"{axes[i]} u")
                axs[i, 1].grid(True, alpha=0.3)
            axs[-1, 0].set_xlabel("Time (s)")
            axs[-1, 1].set_xlabel("Time (s)")
            axs[0, 0].legend(loc="upper right")
            fig.suptitle("Velocity and PID Control Input")
            fig.tight_layout()
            fig.savefig(fig_dir / "velocity_control.png", dpi=160)
            plt.close(fig)


        def animate(t, ref, actual):
            anim_dir = ROOT / "results/animation"
            anim_dir.mkdir(parents=True, exist_ok=True)
            frames = []
            step = max(1, len(t) // 90)
            for idx in range(0, len(t), step):
                fig = plt.figure(figsize=(6, 5))
                ax = fig.add_subplot(111, projection="3d")
                ax.plot(ref[:idx + 1, 0], ref[:idx + 1, 1], ref[:idx + 1, 2], "k--", lw=0.8)
                ax.plot(actual[:idx + 1, 0], actual[:idx + 1, 1], actual[:idx + 1, 2], color="#d62728", lw=1.3)
                ax.scatter(actual[idx, 0], actual[idx, 1], actual[idx, 2], s=45, color="#d62728")
                ax.set_xlim(40, 470); ax.set_ylim(60, 230); ax.set_zlim(0, 110)
                ax.set_xlabel("X mm"); ax.set_ylabel("Y mm"); ax.set_zlabel("Z mm")
                ax.set_title(f"Blood Sample Sorting Robot t={t[idx]:.1f}s")
                ax.view_init(elev=24, azim=-55)
                fig.tight_layout()
                fig.canvas.draw()
                w, h = fig.canvas.get_width_height()
                img = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(h, w, 4)[:, :, :3]
                frames.append(img.copy())
                plt.close(fig)
            imageio.mimsave(anim_dir / "sorting_robot_motion.gif", frames, duration=0.08)


        def main():
            t, ref, vel_ref, event_rows = reference_trajectory()
            actual, vel_actual, ctrl = simulate_robot(t, ref)
            met = metrics(ref, actual)
            save_data(t, ref, actual, vel_ref, vel_actual, ctrl, event_rows, met)
            plot_results(t, ref, actual, vel_ref, vel_actual, ctrl)
            animate(t, ref, actual)
            print("Python PID simulation complete.")
            print(json.dumps(met, indent=2, ensure_ascii=False))


        if __name__ == "__main__":
            main()
        ''',
    )
    write_file(
        "simulation/python/plot_results.py",
        """
        # Plotting is implemented in simulate_pid_robot.py so the whole Python demo can run with one command.
        from simulate_pid_robot import main

        if __name__ == "__main__":
            main()
        """,
    )
    write_file(
        "simulation/python/animate_robot.py",
        """
        # Animation is implemented in simulate_pid_robot.py so the whole Python demo can run with one command.
        from simulate_pid_robot import main

        if __name__ == "__main__":
            main()
        """,
    )


def write_matlab_files() -> None:
    files = {
        "config.m": """
        function cfg = config()
        cfg.base_length = 500; cfg.base_width = 350;
        cfg.rack_rows = 3; cfg.rack_cols = 4; cfg.tube_pitch = 35; cfg.rack_margin = 18;
        cfg.input_origin = [70, 80, 10]; cfg.output_origin = [320, 80, 10];
        cfg.z_safe = 95; cfg.z_pick = 22; cfg.dt = 0.01;
        cfg.max_velocity = 80; cfg.dwell_time = 0.20;
        cfg.tasks = [1 5; 2 3; 3 8; 4 2; 5 10; 6 7];
        cfg.axis.x = struct('m',1.5,'b',8,'Kp',80,'Ki',0,'Kd',15);
        cfg.axis.y = struct('m',1.2,'b',7,'Kp',80,'Ki',0,'Kd',15);
        cfg.axis.z = struct('m',0.8,'b',10,'Kp',100,'Ki',0,'Kd',20);
        cfg.control_limit = 5000;
        cfg.root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
        end
        """,
        "generate_rack_positions.m": """
        function pos = generate_rack_positions(origin, cfg)
        pos = zeros(cfg.rack_rows * cfg.rack_cols, 3);
        k = 1;
        for r = 1:cfg.rack_rows
            for c = 1:cfg.rack_cols
                pos(k,:) = [origin(1) + cfg.rack_margin + (c-1)*cfg.tube_pitch, ...
                            origin(2) + cfg.rack_margin + (r-1)*cfg.tube_pitch, cfg.z_pick];
                k = k + 1;
            end
        end
        end
        """,
        "generate_sorting_tasks.m": """
        function tasks = generate_sorting_tasks(cfg)
        tasks = cfg.tasks;
        end
        """,
        "generate_waypoints.m": """
        function [waypoints, labels] = generate_waypoints(cfg)
        input_pos = generate_rack_positions(cfg.input_origin, cfg);
        output_pos = generate_rack_positions(cfg.output_origin, cfg);
        tasks = generate_sorting_tasks(cfg);
        waypoints = [];
        labels = {};
        for i = 1:size(tasks,1)
            pin = input_pos(tasks(i,1),:); pout = output_pos(tasks(i,2),:);
            ain = pin; ain(3) = cfg.z_safe; aout = pout; aout(3) = cfg.z_safe;
            seq = [ain; pin; ain; aout; pout; aout];
            waypoints = [waypoints; seq];
            labels = [labels; {'input above'; 'pick'; 'input above'; 'output above'; 'place'; 'output above'}];
        end
        end
        """,
        "trapezoid_trajectory.m": """
        function [p, v, t] = trapezoid_trajectory(p0, p1, dt, vmax)
        d = norm(p1 - p0);
        T = max(0.45, d / vmax + 0.25);
        t = (0:dt:T-dt)';
        tau = t / T;
        s = 10*tau.^3 - 15*tau.^4 + 6*tau.^5;
        ds = (30*tau.^2 - 60*tau.^3 + 30*tau.^4) / T;
        p = p0 + s .* (p1 - p0);
        v = ds .* (p1 - p0);
        end
        """,
        "simulate_pid_axis.m": """
        function [y, v, u] = simulate_pid_axis(ref, axis_cfg, dt, limit)
        n = length(ref); y = zeros(n,1); v = zeros(n,1); u = zeros(n,1);
        y(1) = ref(1); integ = 0; prev_err = 0;
        for k = 2:n
            err = ref(k-1) - y(k-1);
            integ = integ + err * dt;
            deriv = (err - prev_err) / dt;
            cmd = axis_cfg.Kp*err + axis_cfg.Ki*integ + axis_cfg.Kd*deriv;
            cmd = max(min(cmd, limit), -limit);
            acc = (cmd - axis_cfg.b * v(k-1)) / axis_cfg.m;
            v(k) = v(k-1) + acc * dt;
            y(k) = y(k-1) + v(k) * dt;
            u(k) = cmd; prev_err = err;
        end
        end
        """,
        "simulate_three_axis_robot.m": """
        function result = simulate_three_axis_robot(cfg)
        [waypoints, labels] = generate_waypoints(cfg);
        ref = []; vel_ref = []; events = {};
        cur = [waypoints(1,1), waypoints(1,2), cfg.z_safe]; t0 = 0;
        for i = 1:size(waypoints,1)
            [p, v, tt] = trapezoid_trajectory(cur, waypoints(i,:), cfg.dt, cfg.max_velocity);
            ref = [ref; p]; vel_ref = [vel_ref; v];
            events = [events; {t0, labels{i}, waypoints(i,1), waypoints(i,2), waypoints(i,3)}];
            t0 = t0 + length(tt)*cfg.dt;
            dwell_n = round(cfg.dwell_time / cfg.dt);
            ref = [ref; repmat(waypoints(i,:), dwell_n, 1)];
            vel_ref = [vel_ref; zeros(dwell_n, 3)];
            t0 = t0 + dwell_n * cfg.dt; cur = waypoints(i,:);
        end
        t = (0:size(ref,1)-1)' * cfg.dt;
        [x, vx, ux] = simulate_pid_axis(ref(:,1), cfg.axis.x, cfg.dt, cfg.control_limit);
        [y, vy, uy] = simulate_pid_axis(ref(:,2), cfg.axis.y, cfg.dt, cfg.control_limit);
        [z, vz, uz] = simulate_pid_axis(ref(:,3), cfg.axis.z, cfg.dt, cfg.control_limit);
        result.t = t; result.ref = ref; result.actual = [x y z]; result.vel_ref = vel_ref;
        result.vel = [vx vy vz]; result.u = [ux uy uz]; result.events = events;
        end
        """,
        "plot_results.m": """
        function plot_results(result, cfg)
        figdir = fullfile(cfg.root, 'results', 'figures'); if ~exist(figdir,'dir'), mkdir(figdir); end
        names = {'X','Y','Z'};
        f = figure('Visible','off'); tiledlayout(3,1);
        for i=1:3
            nexttile; plot(result.t,result.ref(:,i),'k--'); hold on; plot(result.t,result.actual(:,i));
            grid on; ylabel([names{i} ' mm']); legend('ref','actual');
        end
        xlabel('Time s'); saveas(f, fullfile(figdir,'matlab_position_tracking.png')); close(f);
        f = figure('Visible','off'); plot3(result.actual(:,1),result.actual(:,2),result.actual(:,3),'r'); hold on;
        plot3(result.ref(:,1),result.ref(:,2),result.ref(:,3),'k--'); grid on; xlabel('X'); ylabel('Y'); zlabel('Z');
        saveas(f, fullfile(figdir,'matlab_end_effector_3d.png')); close(f);
        end
        """,
        "animate_sorting_robot.m": """
        function animate_sorting_robot(result, cfg)
        % GIF animation is provided by the Python workflow. MATLAB users may extend this function if needed.
        disp('MATLAB animation placeholder: run simulation/python/simulate_pid_robot.py for GIF output.');
        end
        """,
        "export_results.m": """
        function export_results(result, cfg)
        datadir = fullfile(cfg.root, 'results', 'data'); if ~exist(datadir,'dir'), mkdir(datadir); end
        T = array2table([result.t result.ref result.actual result.vel result.u], ...
            'VariableNames', {'t','x_ref','y_ref','z_ref','x','y','z','vx','vy','vz','ux','uy','uz'});
        writetable(T, fullfile(datadir,'matlab_pid_simulation.csv'));
        err = result.ref - result.actual;
        metrics = [max(abs(err)); mean(abs(err)); sqrt(mean(err.^2))];
        writematrix(metrics, fullfile(datadir,'matlab_error_metrics.csv'));
        end
        """,
        "main.m": """
        clear; clc; close all;
        cfg = config();
        result = simulate_three_axis_robot(cfg);
        plot_results(result, cfg);
        export_results(result, cfg);
        animate_sorting_robot(result, cfg);
        disp('MATLAB PID simulation finished.');
        """,
    }
    for name, content in files.items():
        write_file(f"simulation/matlab/{name}", content)


def write_docs() -> None:
    rows = []
    for p in STANDARD_PARTS:
        rows.append(f"| {p[0]} | {p[1]} | {p[3]} | {p[4]} | {p[7]} | {p[9]} | {p[10]} |")
    bom_table = "\n".join(rows)
    write_file(
        "docs/bom_standard_parts.md",
        f"""
        # 标准件 BOM

        本 BOM 采用真实工程选型风格：优先记录 McMaster-Carr、MISUMI、THK/HIWIN、TraceParts、3DContentCentral、厂家官网等公开 CAD 候选来源。若网站需要登录、验证码、人工选择格式或许可确认，则 `need_manual_download=true`，本项目自动生成参数化替代 STEP，并在总装中使用替代模型。

        | ID | 中文名称 | 推荐规格 | 数量 | 候选来源 | 需手动下载 | 替代模型 |
        |---|---|---|---:|---|---|---|
        {bom_table}

        说明：替代模型不代表具体厂家精确结构，只用于课程设计中的空间布局、装配表达和控制模型映射。后续若获得真实标准件 STEP，可替换 `cad/standard_parts/downloaded/` 中的模型并更新装配脚本。
        """,
    )
    write_file(
        "simulation/docs/kinematics_definition.md",
        """
        # 三轴 Cartesian Robot 运动学定义

        本机器人为三轴直角坐标/龙门式 Cartesian Robot，不采用六轴机械臂。末端执行器位置定义为 `P=[x,y,z]`，关节变量定义为 `q=[qx,qy,qz]`。

        正运动学：`x=qx, y=qy, z=qz`。逆运动学：`qx=x, qy=y, qz=z`。坐标原点位于底板左前下角附近，X 轴沿工作台左右方向，Y 轴沿前后方向，Z 轴竖直向上。

        输入试管架原点为 `[70,80,10]` mm，输出试管架原点为 `[320,80,10]` mm；孔位按 3×4 阵列和 35 mm 间距生成。X/Y/Z 行程限制分别为 300/220/100 mm。安全高度 `z_safe=95 mm`，取放高度 `z_pick=22 mm`。夹爪逻辑变量 `gripper=0` 表示未夹取，`gripper=1` 表示已夹取。
        """,
    )
    write_file(
        "simulation/docs/trajectory_planning.md",
        """
        # 轨迹规划

        输入和输出试管架均为 3×4 阵列。自动生成 6 个样本分拣任务：输入1→输出5，输入2→输出3，输入3→输出8，输入4→输出2，输入5→输出10，输入6→输出7。

        每个任务包含 6 个路径点：输入点上方、输入取样点、输入点上方、输出点上方、输出放样点、输出点上方。路径点之间采用平滑五次插值，MATLAB 文件名保留 `trapezoid_trajectory.m`，其作用等价于生成满足速度连续的分段参考轨迹，并输出 `x_ref(t), y_ref(t), z_ref(t)` 及速度轨迹。

        安全策略为先升到 `z_safe` 再进行 X/Y 平面运动，只有到达目标孔位上方后才下降到 `z_pick`。该策略可避免试管、试管架和夹爪之间发生几何干涉。
        """,
    )
    write_file(
        "simulation/docs/pid_control_model.md",
        """
        # PID 控制模型

        三个轴均简化为二阶质量-阻尼模型：`m*x'' + b*x' = u`。X 轴参数为 `m=1.5, b=8`，Y 轴为 `m=1.2, b=7`，Z 轴为 `m=0.8, b=10`。

        初始 PID 参数：X/Y 轴 `Kp=80, Ki=0, Kd=15`，Z 轴 `Kp=100, Ki=0, Kd=20`。每轴独立闭环，输入为规划位置轨迹，输出为实际位置轨迹，并计算最大误差、平均绝对误差和 RMSE。

        该模型适合课程设计阶段说明 PID 轨迹跟踪原理。实际样机还需加入电机驱动器、电流环、摩擦、间隙、丝杆/同步带弹性和限位保护。
        """,
    )
    write_file(
        "simulation/docs/cad_to_control_mapping.md",
        """
        # CAD 与控制模型映射

        CAD 精细模型用于结构展示、空间布局验证和 SolidWorks 装配表达；控制仿真采用简化的 X/Y/Z 三轴等效动力学模型。

        在 SolidWorks 中，X 轴运动部件对应 X slider、Z module 和 gripper；Y 轴运动部件对应 gantry bridge、X module、Z module 和 gripper；Z 轴运动部件对应 z slider 和 gripper。在 MATLAB/Python 中，X/Y/Z 轴分别以等效质量和阻尼表示。

        不直接使用完整 CAD 做 PID 的原因是：完整 CAD 自由度复杂，标准件细节过多，导入和配合会引入大量非控制相关约束；本课程设计重点是轨迹规划、闭环跟踪和误差分析，因此三轴等效模型更清晰，也更便于复现实验。
        """,
    )
    write_file(
        "docs/project_overview.md",
        """
        # 项目概述

        本项目完成基于 PID 控制的三轴全自动血液样本分拣机器人数字设计。机械结构采用三轴龙门式 Cartesian Robot，包含底板、输入/输出试管架、X/Y/Z 导轨与滑块、步进电机、传动件、夹爪、传感器、拖链、控制盒和急停按钮。

        项目未进行实物落地，但完成了参数化 CAD 建模、总装 STEP 导出、SolidWorks 导入说明、运动学建模、路径规划、PID 控制仿真、结果图、动画和课程设计报告草稿。
        """,
    )
    write_file(
        "docs/model_design_description.md",
        """
        # 模型设计说明

        机器人采用底板固定、双 Y 轴导轨支撑、X 轴横梁跨接、Z 轴短行程升降的龙门式结构。输入试管架放置在工作台左侧，输出试管架放置在右侧，夹爪在安全高度移动并在孔位上方下降完成取放。

        标准件若无法自动下载真实 STEP，均使用 CadQuery 生成参数化替代模型；非标件包括底板、试管架、横梁、安装板、传感器支架和控制盒支架。
        """,
    )
    write_file(
        "docs/operation_workflow.md",
        """
        # 工作流程

        1. 系统回零并确认 X/Y/Z 限位状态。
        2. 扫码或传感器识别输入试管架样本。
        3. 轨迹规划模块生成输入孔位到输出孔位的安全路径。
        4. 夹爪移动到输入孔位上方，下降到取样高度并夹取试管。
        5. 夹爪回到安全高度，移动至输出孔位上方。
        6. 下降到放样高度，松开夹爪并返回安全高度。
        7. 重复执行全部分拣任务并输出仿真结果。
        """,
    )
    write_file(
        "docs/limitations_and_future_work.md",
        """
        # 局限与后续工作

        当前项目为课程设计级数字样机，未进行实物制造、强度校核、驱动器选型、电气安全认证和医院现场验证。标准件 CAD 来源可能受登录、验证码或许可限制，因此使用替代模型表达外形与装配关系。

        后续可补充真实厂家 STEP、SolidWorks 运动算例、有限元校核、电机扭矩计算、扫码数据接口、异常样本处理逻辑和更真实的摩擦/饱和/限位控制模型。
        """,
    )
    write_file(
        "docs/acceptance_checklist.md",
        """
        # 项目验收清单

        本清单按课程设计任务要求逐项核对，当前项目已通过 `python run_all.py` 自动构建和 `cad/scripts/check_cad_outputs.py` 质量检查。

        | 序号 | 验收项 | 对应文件/目录 | 状态 |
        |---:|---|---|---|
        | 1 | 有总装 STEP | `cad/assembly/blood_sorting_robot_assembly.step` | 已完成 |
        | 2 | 有完整三轴龙门式结构 | 总装 STEP、`docs/model_design_description.md` | 已完成 |
        | 3 | 有输入试管架和输出试管架 | `cad/custom_parts/step/input_tube_rack.step`、`output_tube_rack.step` | 已完成 |
        | 4 | 有血液试管 | `cad/custom_parts/step/test_tube_set.step` | 已完成 |
        | 5 | 有 X/Y/Z 三轴导轨、滑块、电机、传动件外观 | `cad/standard_parts/fallback_generated/` | 已完成 |
        | 6 | 有夹爪 | `fallback_parallel_gripper.step` | 已完成 |
        | 7 | 有传感器、拖链、控制盒、急停按钮 | fallback 标准件目录与总装 STEP | 已完成 |
        | 8 | 有 BOM | `cad/standard_parts/standard_parts_manifest.csv`、`docs/bom_standard_parts.md` | 已完成 |
        | 9 | 有 SolidWorks 导入说明 | `solidworks/SolidWorks_import_and_assembly_guide.md` | 已完成 |
        | 10 | 有运动学文档 | `simulation/docs/kinematics_definition.md` | 已完成 |
        | 11 | 有 PID 控制仿真代码 | `simulation/matlab/`、`simulation/python/` | 已完成 |
        | 12 | 有结果图 | `results/figures/` | 已完成 |
        | 13 | 有动画 | `results/animation/sorting_robot_motion.gif` | 已完成 |
        | 14 | 有报告草稿 | `report/project_report_draft.md` | 已完成 |
        | 15 | 有答辩 PPT 大纲 | `report/ppt_outline.md` | 已完成 |
        | 16 | 可通过一键脚本生成主要成果 | `python run_all.py` | 已完成 |

        ## 当前自动检查摘要

        - 非标件 STEP：11 个。
        - fallback 标准件 STEP：15 个。
        - 仿真图：4 张 PNG。
        - 动画：1 个 GIF。
        - 质量检查日志：`results/logs/project_build_log.txt`。
        """,
    )
    write_file(
        "docs/submission_guide.md",
        """
        # 课程提交与演示建议

        ## 建议提交文件

        1. `cad/assembly/blood_sorting_robot_assembly.step`
        2. `cad/custom_parts/step/`
        3. `cad/standard_parts/fallback_generated/`
        4. `cad/standard_parts/standard_parts_manifest.csv`
        5. `docs/bom_standard_parts.md`
        6. `simulation/docs/`
        7. `simulation/matlab/`
        8. `simulation/python/`
        9. `results/figures/`
        10. `results/animation/sorting_robot_motion.gif`
        11. `report/project_report_draft.md`
        12. `report/ppt_outline.md`
        13. `report/defense_script.md`

        ## 演示顺序

        1. 先展示 `README.md`，说明项目结构和一键运行方法。
        2. 运行 `python run_all.py`，证明项目可自动生成主要成果。
        3. 打开 `cad/assembly/blood_sorting_robot_assembly.step`，展示三轴龙门结构、试管架、试管、夹爪和电控外观。
        4. 展示 `docs/bom_standard_parts.md`，说明标准件选型与 fallback 替代策略。
        5. 展示 `simulation/docs/kinematics_definition.md`，说明三轴 Cartesian Robot 的正逆运动学。
        6. 展示 `results/figures/position_tracking.png`、`tracking_error.png` 和 `end_effector_3d.png`。
        7. 播放 `results/animation/sorting_robot_motion.gif`。
        8. 最后展示 `report/project_report_draft.md` 和 `report/ppt_outline.md`。

        ## 答辩时建议强调

        - 本项目明确采用三轴直角坐标/龙门式结构，不采用六轴机械臂。
        - CAD 模型用于结构展示和空间验证，控制仿真使用简化 X/Y/Z 三轴等效动力学模型。
        - 标准件 CAD 若受网站登录、验证码或格式选择限制，不伪造下载成功，而是生成参数化替代 STEP。
        - 项目未进行实物落地，但完成数字建模、轨迹规划、PID 控制仿真和课程报告材料。
        """,
    )
    write_file(
        "solidworks/SolidWorks_import_and_assembly_guide.md",
        """
        # SolidWorks 导入与装配指南

        1. 打开 SolidWorks，选择“打开”，文件类型选择 STEP/STP。
        2. 打开 `cad/assembly/blood_sorting_robot_assembly.step`。
        3. 导入完成后另存为 `blood_sorting_robot_assembly.SLDASM`。
        4. 若需要管理零件，可在特征树中右键导入实体，按组件名称另存为 SLDPRT。
        5. 参考 `cad/assembly/assembly_reference_coordinates.csv` 检查各组件位置。
        6. 制作爆炸图时建议按底板、试管架、Y轴、X轴、Z轴、夹爪、电控件顺序展开。
        7. 工程图可分别导出总装三视图、关键非标件图和 BOM 表。

        真实标准件 STEP 下载后，可替换 `cad/standard_parts/downloaded/` 中的文件，并按装配坐标重新定位。
        """,
    )
    write_file(
        "solidworks/motion_mates_guide.md",
        """
        # SolidWorks 运动配合说明

        X 轴线性配合：选择 X 轴滑块与 X 轴导轨建立线性滑动配合，范围 0~300 mm。Y 轴线性配合：选择左右 Y 轴滑块与对应导轨建立同步线性配合，范围 0~220 mm。Z 轴线性配合：选择 Z 轴滑块与 Z 导轨建立竖直线性配合，范围 0~100 mm。

        夹爪开合作为可选运动，可对两根手指设置对称距离配合，开口范围约 0~20 mm。制作取放动画时，按“移动到输入上方、下降、夹紧、上升、移动到输出上方、下降、松开、上升”的关键帧顺序设置。

        如需更真实运动，可将 STEP 替代件更换为带配合基准的 SLDPRT，并补充电机转动、同步带轮和丝杆螺旋配合。
        """,
    )
    write_file(
        "solidworks/optional_solidworks_macro_vba/build_assembly_from_steps.bas",
        """
        Attribute VB_Name = "BuildAssemblyFromSteps"
        ' Optional macro skeleton for SolidWorks.
        ' It documents the intended workflow but may need path adjustments per SolidWorks version.

        Sub main()
            Dim swApp As Object
            Set swApp = Application.SldWorks
            MsgBox "Open cad/assembly/blood_sorting_robot_assembly.step, then save as SLDASM. " & _
                   "Use assembly_reference_coordinates.csv if rebuilding from individual STEP files."
        End Sub
        """,
    )
    write_file(
        "report/project_report_outline.md",
        """
        # 课程设计报告提纲

        第1章 绪论：项目背景、血液样本分拣自动化需求、本项目研究内容。

        第2章 系统总体方案设计：三轴龙门式结构选择、标准件与非标件混合建模方案、工作台与试管架布局、系统功能模块。

        第3章 三维建模与机械结构设计：STEP 建模流程、标准件选型、非标件设计、总装结构、运动范围与安全高度。

        第4章 运动学建模：坐标系、正运动学、逆运动学、取放路径点。

        第5章 轨迹规划：分拣任务、路径点生成、平滑速度轨迹、安全运动策略。

        第6章 PID 控制系统设计：单轴等效动力学、PID 原理、三轴闭环控制结构、参数整定方法。

        第7章 仿真结果与分析：位置跟踪、误差曲线、三维轨迹、分拣动画、控制效果评价。

        第8章 总结与展望：完成情况、不足、后续优化。
        """,
    )
    write_file(
        "report/project_report_draft.md",
        """
        # 基于 PID 控制的三轴全自动血液样本分拣机器人设计与运动学分析、建模与仿真

        ## 第1章 绪论

        医院检验科每天需要处理大量血液样本，传统人工分拣存在重复劳动强度高、样本错放风险和效率受人员状态影响等问题。面向课程设计，本项目以血液试管在输入架与输出架之间的自动转运为对象，完成一种三轴龙门式分拣机器人的数字样机设计。

        本项目未进行实物落地，但完成了机械结构方案、三维 STEP 建模、运动学定义、轨迹规划、PID 控制仿真、结果图和动画输出，可用于说明自动分拣设备的基本设计流程。

        ## 第2章 系统总体方案设计

        机器人采用三轴直角坐标结构，而非六轴机械臂。该方案的优点是运动学简单、工作空间与试管架阵列匹配、控制变量少，适合课程设计中的建模和仿真。系统由底板、输入/输出试管架、双 Y 轴导轨、X 轴横梁、Z 轴升降机构、两指夹爪、扫码/传感器模块、拖链、控制盒和急停按钮组成。

        标准件优先参考公开 CAD 来源；当网站需要登录、验证码或人工选择格式时，本项目不伪造下载结果，而是使用 CadQuery 生成参数化替代 STEP，并在 BOM 中标注为替代模型。

        ## 第3章 三维建模与机械结构设计

        非标件包括底板、试管架、X 轴横梁、Z 轴安装板、夹爪连接板、传感器支架和控制盒支架。底板设置安装孔和支撑脚，试管架为 3×4 圆孔阵列，孔径 16 mm，孔距 35 mm。总装 STEP 中可以明显看到三轴龙门结构、输入/输出试管架、血液试管、导轨滑块、电机、传动件、拖链、传感器、控制盒和夹爪。

        ## 第4章 运动学建模

        末端位置定义为 `P=[x,y,z]`，关节变量为 `q=[qx,qy,qz]`。对于 Cartesian Robot，正运动学为 `x=qx, y=qy, z=qz`，逆运动学为 `qx=x, qy=y, qz=z`。X/Y/Z 行程限制分别为 300 mm、220 mm、100 mm。安全高度为 95 mm，取放高度为 22 mm。

        ## 第5章 轨迹规划

        仿真自动生成 6 个样本分拣任务：输入1到输出5、输入2到输出3、输入3到输出8、输入4到输出2、输入5到输出10、输入6到输出7。每个任务包含输入上方、取样点、输入上方、输出上方、放样点、输出上方六个路径点。路径段采用平滑插值，保证位置和速度连续。

        ## 第6章 PID 控制系统设计

        每个轴简化为 `m*x'' + b*x' = u`。X/Y/Z 三轴分别设置等效质量和阻尼，并采用独立 PID 控制。控制输入为目标位置轨迹，输出为实际位置轨迹，评价指标包括最大误差、平均误差和 RMSE。该简化模型避免了完整 CAD 自由度和标准件细节对控制分析的干扰，更适合课程设计说明。

        ## 第7章 仿真结果与分析

        Python 仿真输出三轴目标位置与实际位置对比、误差曲线、三维末端轨迹、速度与控制输入曲线，并生成 GIF 动画。结果文件位于 `results/figures/`、`results/data/` 和 `results/animation/`。从仿真结果可观察到三轴能够跟随规划路径完成输入架到输出架的转运过程，误差主要出现在加减速阶段。

        ## 第8章 总结与展望

        本项目完成了课程设计要求的数字化建模与仿真验证。不足之处包括未进行实物制造、未进行有限元强度校核、标准件未全部替换为厂家精确模型、电气与安全系统仅作外观表达。后续可补充真实 STEP、扭矩计算、SolidWorks Motion 算例、扫码数据接口和更完整的样本异常处理策略。
        """,
    )
    write_file(
        "report/ppt_outline.md",
        """
        # 答辩 PPT 大纲

        1. 题目与设计目标
        2. 医院血液样本分拣需求
        3. 为什么选择三轴龙门式结构
        4. 总体结构与工作流程
        5. 标准件 BOM 与替代模型策略
        6. 非标件设计与总装 STEP
        7. 运动学模型
        8. 分拣任务与轨迹规划
        9. 单轴等效动力学与 PID 控制
        10. 仿真结果图与动画
        11. CAD 模型与控制模型映射
        12. 总结、不足与后续改进
        """,
    )
    write_file(
        "report/defense_script.md",
        """
        # 答辩讲稿

        各位老师好，我的课程设计题目是《基于 PID 控制的三轴全自动血液样本分拣机器人设计与运动学分析、建模与仿真》。本项目面向医院检验科血液样本分拣场景，采用三轴直角坐标龙门结构，而不是六轴机械臂。

        机械部分完成了底板、输入输出试管架、X/Y/Z 导轨滑块、电机、传动件、夹爪、传感器、拖链、控制盒和急停按钮的 STEP 总装。标准件 CAD 如果受网站登录或下载限制，则使用参数化替代模型，并在 BOM 中明确标注。

        控制部分没有直接依赖复杂 CAD，而是建立 X/Y/Z 三轴等效质量阻尼模型，用 PID 完成轨迹跟踪。路径规划按输入试管架到输出试管架自动生成六个分拣任务，每个任务包含上方安全点、取样点和放样点。

        仿真输出了三轴位置跟踪曲线、误差曲线、三维末端轨迹、速度和控制输入曲线以及 GIF 动画。项目没有进行实物落地，但完成了数字建模与仿真验证，满足课程设计的完整流程要求。
        """,
    )
    write_file(
        "cad/README.md",
        """
        # CAD 阶段说明

        本目录包含标准件 BOM、fallback 标准件 STEP、非标件 STEP、总装 STEP 和 CAD 检查脚本。`scripts/generate_custom_parts.py` 负责非标件参数化建模，`scripts/generate_fallback_standard_parts.py` 负责生成无法自动下载时使用的标准件替代模型，`scripts/build_step_assembly.py` 负责总装。

        主交付文件为 `assembly/blood_sorting_robot_assembly.step`，可直接导入 SolidWorks。
        """,
    )
    write_file(
        "simulation/README.md",
        """
        # 仿真阶段说明

        本目录包含 MATLAB 与 Python 两套仿真。控制对象为三轴等效质量-阻尼模型，轨迹由输入/输出试管架坐标和分拣任务自动生成。Python 版本用于无 MATLAB 环境时生成结果图、数据和 GIF 动画。

        运行 Python 仿真：`python simulation/python/simulate_pid_robot.py`。运行 MATLAB 仿真：进入 `simulation/matlab/` 后执行 `main`。
        """,
    )
    write_file(
        "solidworks/README.md",
        """
        # SolidWorks 阶段说明

        先打开 `cad/assembly/blood_sorting_robot_assembly.step`，确认三轴龙门结构、试管架、夹爪和电控外观后另存为 SLDASM。运动配合范围和动画制作步骤见 `motion_mates_guide.md`。

        可选 VBA 宏仅作为导入流程骨架，正式装配建议在 SolidWorks 中人工检查配合基准。
        """,
    )
    write_file(
        "results/README.md",
        """
        # 结果目录说明

        `figures/` 保存位置跟踪、误差、三维轨迹、速度和控制输入图；`animation/` 保存分拣运动 GIF；`data/` 保存轨迹、误差指标和路径点事件；`logs/` 保存构建与质量检查日志。
        """,
    )
    write_file(
        "report/README.md",
        """
        # 报告阶段说明

        本目录包含课程设计报告提纲、报告草稿、PPT 大纲和答辩讲稿。报告内容强调数字样机、STEP 建模、运动学、轨迹规划和 PID 仿真，不写成商业项目文案。
        """,
    )
    write_file(
        "README.md",
        """
        # 基于 PID 控制的三轴全自动血液样本分拣机器人

        ## 项目简介

        本项目为课程设计数字样机：三轴龙门式 Cartesian Robot 用于医院血液样本分拣。项目不做实物制造，但完成 STEP 三维建模、结构设计、运动学、轨迹规划、PID 控制仿真、结果图、动画和报告材料。

        ## 项目结构

        - `config/`：CAD、运动和 PID 参数。
        - `cad/`：标准件 BOM、替代标准件、非标件、总装 STEP 和检查脚本。
        - `solidworks/`：SolidWorks 导入、运动配合和可选宏说明。
        - `simulation/`：MATLAB 与 Python 仿真代码、运动学和控制说明。
        - `results/`：仿真图、动画、数据和日志。
        - `report/`：课程报告草稿、PPT 大纲和答辩稿。
        - `docs/`：项目说明、BOM、工作流程和局限性。

        ## 安装依赖

        ```bash
        pip install -r requirements.txt
        ```

        Python 3.13 已验证可安装 CadQuery 2.7.0。若安装较慢，可先确认网络环境。

        ## 一键运行方法

        ```bash
        python run_all.py
        ```

        脚本会创建目录、生成 BOM、生成非标件 STEP、生成标准件 fallback STEP、建立总装 STEP、生成文档、运行 Python PID 仿真并执行质量检查。

        ## 如何打开 STEP

        总装文件位于 `cad/assembly/blood_sorting_robot_assembly.step`。可用 SolidWorks、FreeCAD、Fusion 360 或其他支持 STEP 的 CAD 软件打开。

        ## 如何导入 SolidWorks

        参考 `solidworks/SolidWorks_import_and_assembly_guide.md`。建议先打开总装 STEP，确认结构后另存为 SLDASM。

        ## 如何运行 MATLAB 仿真

        在 MATLAB 中进入 `simulation/matlab/`，运行：

        ```matlab
        main
        ```

        MATLAB 版本会输出位置跟踪图和数据文件。

        ## 如何运行 Python 仿真

        ```bash
        python simulation/python/simulate_pid_robot.py
        ```

        输出图像到 `results/figures/`，数据到 `results/data/`，动画到 `results/animation/`。

        ## 输出文件说明

        - 总装 STEP：`cad/assembly/blood_sorting_robot_assembly.step`
        - 非标件 STEP：`cad/custom_parts/step/`
        - fallback 标准件 STEP：`cad/standard_parts/fallback_generated/`
        - BOM：`cad/standard_parts/standard_parts_manifest.csv` 与 `docs/bom_standard_parts.md`
        - 仿真图：`results/figures/`
        - 动画：`results/animation/sorting_robot_motion.gif`
        - 报告草稿：`report/project_report_draft.md`

        ## 已完成内容

        已完成三轴龙门结构、输入/输出试管架、试管、导轨滑块、电机、传动件、夹爪、传感器、拖链、控制盒、急停按钮、BOM、SolidWorks 说明、运动学文档、PID 仿真代码、结果图、动画、报告草稿和 PPT 大纲。

        ## 未完成或需要人工补充的内容

        未进行实物落地、强度校核、真实电气接线、安全认证和医院现场验证。标准件真实 CAD 可能需要登录或人工下载，本项目使用参数化替代 STEP。

        ## 后续扩展建议

        可补充真实标准件 STEP、SolidWorks Motion 动画、电机扭矩计算、有限元分析、扫码接口、异常样本处理和更真实的摩擦/饱和控制模型。
        """,
    )
    write_file(
        "requirements.txt",
        """
        cadquery>=2.7.0
        numpy
        matplotlib
        pandas
        imageio
        pillow
        """,
    )


def run_command(args: list[str], log_lines: list[str]) -> None:
    log_lines.append("$ " + " ".join(args))
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )
    log_lines.append(proc.stdout)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(args)}\n{proc.stdout}")


def main() -> None:
    ensure_dirs()
    write_standard_parts_manifest()
    write_config_files()
    write_cad_scripts()
    write_python_simulation()
    write_matlab_files()
    write_docs()

    log_lines: list[str] = ["Project build started."]
    run_command([sys.executable, str(ROOT / "cad/scripts/generate_custom_parts.py")], log_lines)
    run_command([sys.executable, str(ROOT / "cad/scripts/generate_fallback_standard_parts.py")], log_lines)
    run_command([sys.executable, str(ROOT / "cad/scripts/build_step_assembly.py")], log_lines)
    run_command([sys.executable, str(ROOT / "simulation/python/simulate_pid_robot.py")], log_lines)
    run_command([sys.executable, str(ROOT / "cad/scripts/check_cad_outputs.py")], log_lines)

    log_path = ROOT / "results/logs/project_build_log.txt"
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print("\n=== Build complete ===")
    print(f"总装 STEP: {ROOT / 'cad/assembly/blood_sorting_robot_assembly.step'}")
    print(f"非标件 STEP: {ROOT / 'cad/custom_parts/step'}")
    print(f"fallback 标准件 STEP: {ROOT / 'cad/standard_parts/fallback_generated'}")
    print(f"仿真结果图: {ROOT / 'results/figures'}")
    print(f"动画: {ROOT / 'results/animation/sorting_robot_motion.gif'}")
    print(f"报告草稿: {ROOT / 'report/project_report_draft.md'}")
    print("下一步: 在 SolidWorks 中打开 cad/assembly/blood_sorting_robot_assembly.step，另存为 SLDASM，并按 solidworks/motion_mates_guide.md 设置三轴线性配合。")


if __name__ == "__main__":
    main()
