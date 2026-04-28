        # 标准件 BOM

        本 BOM 采用真实工程选型风格：优先记录 McMaster-Carr、MISUMI、THK/HIWIN、TraceParts、3DContentCentral、厂家官网等公开 CAD 候选来源。若网站需要登录、验证码、人工选择格式或许可确认，则 `need_manual_download=true`，本项目自动生成参数化替代 STEP，并在总装中使用替代模型。

        | ID | 中文名称 | 推荐规格 | 数量 | 候选来源 | 需手动下载 | 替代模型 |
        |---|---|---|---:|---|---|---|
        | SP-001 | X轴步进电机 | NEMA17, 42 mm frame, 1.8 deg, 40 mm body | 1 | McMaster-Carr / 3DContentCentral / GrabCAD | true | fallback_nema17_motor.step |
| SP-002 | Y轴步进电机 | NEMA17, 42 mm frame, 1.8 deg, 40 mm body | 1 | McMaster-Carr / 3DContentCentral / GrabCAD | true | fallback_nema17_motor.step |
| SP-003 | Z轴步进电机 | NEMA17 compact, 42 mm frame | 1 | 3DContentCentral / TraceParts | true | fallback_nema17_motor.step |
| SP-004 | X轴直线导轨 | MGN12H/MGN15H rail, 320 mm | 1 | HIWIN / THK / TraceParts | true | fallback_mgn12_rail.step |
| SP-005 | Y轴左侧直线导轨 | MGN12H rail, 280 mm | 1 | HIWIN / THK / TraceParts | true | fallback_mgn12_rail.step |
| SP-006 | Y轴右侧直线导轨 | MGN12H rail, 280 mm | 1 | HIWIN / THK / TraceParts | true | fallback_mgn12_rail.step |
| SP-007 | Z轴短行程直线导轨 | MGN12H rail, 120 mm | 1 | HIWIN / TraceParts | true | fallback_mgn12_rail.step |
| SP-008 | X轴滑块 | MGN12H carriage | 1 | HIWIN / TraceParts | true | fallback_mgn12_slider.step |
| SP-009 | Y轴滑块 | MGN12H carriage | 2 | HIWIN / TraceParts | true | fallback_mgn12_slider.step |
| SP-010 | Z轴滑块 | MGN12H carriage | 1 | HIWIN / TraceParts | true | fallback_mgn12_slider.step |
| SP-011 | T8丝杆或GT2同步带组件 | T8 lead screw 8 mm pitch or GT2 belt, simplified | 3 | MISUMI / McMaster-Carr / TraceParts | true | fallback_t8_lead_screw.step; fallback_gt2_belt.step |
| SP-012 | 联轴器 | 5 mm to 8 mm flexible coupling | 3 | McMaster-Carr / MISUMI | true | fallback_coupling.step |
| SP-013 | 轴承座 | KP08/BK style small bearing block | 6 | McMaster-Carr / TraceParts | true | fallback_bearing_block.step |
| SP-014 | 2020或2040铝型材 | 2020 profile, 20 mm square | 8 | MISUMI / McMaster-Carr / GrabCAD | true | fallback_2020_profile.step |
| SP-015 | 拖链 | Small plastic drag chain, 10 x 15 mm inner | 1 | IGUS / TraceParts / McMaster-Carr | true | fallback_cable_chain.step |
| SP-016 | 限位开关 | Micro switch with lever | 6 | Omron / TraceParts / 3DContentCentral | true | fallback_limit_switch.step |
| SP-017 | 扫码/传感器模块外观 | Compact barcode scanner or photoelectric sensor mockup | 1 | SICK / Keyence / TraceParts | true | fallback_sensor_module.step |
| SP-018 | 急停按钮 | 22 mm panel mount mushroom button | 1 | Schneider / TraceParts | true | fallback_emergency_stop.step |
| SP-019 | 控制盒 | Plastic/electrical enclosure, approx. 140 x 90 x 55 mm | 1 | McMaster-Carr / Hammond / TraceParts | true | fallback_control_box.step |
| SP-020 | 螺栓、螺母、垫片 | M3/M4 socket head screws, nuts and washers | 1 | McMaster-Carr | true | fallback_fasteners.step |
| SP-021 | 两指平行夹爪 | Small electric/pneumatic parallel gripper, simplified | 1 | SMC / Festo / TraceParts | true | fallback_parallel_gripper.step |

        说明：替代模型不代表具体厂家精确结构，只用于课程设计中的空间布局、装配表达和控制模型映射。后续若获得真实标准件 STEP，可替换 `cad/standard_parts/downloaded/` 中的模型并更新装配脚本。
