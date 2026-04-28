function [y, v, u] = simulate_pid_axis(ref, axis_cfg, dt, limit)
n = length(ref); y = zeros(n,1); v = zeros(n,1); u = zeros(n,1);
y(1) = ref(1); integ = 0; prev_err = 0;
for k = 2:n
    err = ref(k-1) - y(k-1);
    integ = integ + err * dt;
    deriv = (err - prev_err) / dt;
    cmd = axis_cfg.Kp*err + axis_cfg.Ki*integ + axis_cfg.Kd*deriv;
    cmd = max(min(cmd, limit), -limit);
    acc = (cmd - axis_cfg.b * v(k-1)) / axis_cfg.m;
    v(k) = v(k-1) + acc * dt;
    y(k) = y(k-1) + v(k) * dt;
    u(k) = cmd; prev_err = err;
end
end
