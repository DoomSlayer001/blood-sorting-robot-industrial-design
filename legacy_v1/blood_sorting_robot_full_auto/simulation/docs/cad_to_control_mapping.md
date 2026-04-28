# CAD 与控制模型映射

CAD 精细模型用于结构展示、空间布局验证和 SolidWorks 装配表达；控制仿真采用简化的 X/Y/Z 三轴等效动力学模型。

在 SolidWorks 中，X 轴运动部件对应 X slider、Z module 和 gripper；Y 轴运动部件对应 gantry bridge、X module、Z module 和 gripper；Z 轴运动部件对应 z slider 和 gripper。在 MATLAB/Python 中，X/Y/Z 轴分别以等效质量和阻尼表示。

不直接使用完整 CAD 做 PID 的原因是：完整 CAD 自由度复杂，标准件细节过多，导入和配合会引入大量非控制相关约束；本课程设计重点是轨迹规划、闭环跟踪和误差分析，因此三轴等效模型更清晰，也更便于复现实验。
