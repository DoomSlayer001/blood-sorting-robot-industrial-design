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
