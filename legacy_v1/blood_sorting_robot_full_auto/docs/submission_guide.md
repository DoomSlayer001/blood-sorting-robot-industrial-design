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
