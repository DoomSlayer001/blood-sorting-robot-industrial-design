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
