# SolidWorks 导入与装配指南

1. 打开 SolidWorks，选择“打开”，文件类型选择 STEP/STP。
2. 打开 `cad/assembly/blood_sorting_robot_assembly.step`。
3. 导入完成后另存为 `blood_sorting_robot_assembly.SLDASM`。
4. 若需要管理零件，可在特征树中右键导入实体，按组件名称另存为 SLDPRT。
5. 参考 `cad/assembly/assembly_reference_coordinates.csv` 检查各组件位置。
6. 制作爆炸图时建议按底板、试管架、Y轴、X轴、Z轴、夹爪、电控件顺序展开。
7. 工程图可分别导出总装三视图、关键非标件图和 BOM 表。

真实标准件 STEP 下载后，可替换 `cad/standard_parts/downloaded/` 中的文件，并按装配坐标重新定位。
