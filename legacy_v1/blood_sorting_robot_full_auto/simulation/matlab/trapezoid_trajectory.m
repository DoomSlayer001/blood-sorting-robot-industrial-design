function [p, v, t] = trapezoid_trajectory(p0, p1, dt, vmax)
d = norm(p1 - p0);
T = max(0.45, d / vmax + 0.25);
t = (0:dt:T-dt)';
tau = t / T;
s = 10*tau.^3 - 15*tau.^4 + 6*tau.^5;
ds = (30*tau.^2 - 60*tau.^3 + 30*tau.^4) / T;
p = p0 + s .* (p1 - p0);
v = ds .* (p1 - p0);
end
