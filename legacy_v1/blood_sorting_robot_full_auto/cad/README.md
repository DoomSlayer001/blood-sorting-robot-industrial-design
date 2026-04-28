# CAD 阶段说明

本目录包含标准件 BOM、fallback 标准件 STEP、非标件 STEP、总装 STEP 和 CAD 检查脚本。`scripts/generate_custom_parts.py` 负责非标件参数化建模，`scripts/generate_fallback_standard_parts.py` 负责生成无法自动下载时使用的标准件替代模型，`scripts/build_step_assembly.py` 负责总装。

主交付文件为 `assembly/blood_sorting_robot_assembly.step`，可直接导入 SolidWorks。
