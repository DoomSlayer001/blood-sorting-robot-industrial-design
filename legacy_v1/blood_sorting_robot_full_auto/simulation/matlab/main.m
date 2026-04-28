clear; clc; close all;
cfg = config();
result = simulate_three_axis_robot(cfg);
plot_results(result, cfg);
export_results(result, cfg);
animate_sorting_robot(result, cfg);
disp('MATLAB PID simulation finished.');
