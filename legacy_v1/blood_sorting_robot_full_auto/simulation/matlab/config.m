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
