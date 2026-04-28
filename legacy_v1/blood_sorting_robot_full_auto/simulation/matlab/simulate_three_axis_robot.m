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
