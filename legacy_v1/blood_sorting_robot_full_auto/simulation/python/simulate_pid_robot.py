from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import imageio.v2 as imageio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import cad_config as C
from config import motion_config as M
from config import pid_config as P


def rack_positions(origin):
    positions = []
    for r in range(C.rack_rows):
        for c in range(C.rack_cols):
            x = origin[0] + C.rack_margin + c * C.tube_pitch
            y = origin[1] + C.rack_margin + r * C.tube_pitch
            positions.append(np.array([x, y, float(C.z_pick)]))
    return positions


def generate_waypoints():
    inputs = rack_positions(C.input_rack_origin)
    outputs = rack_positions(C.output_rack_origin)
    waypoints = []
    labels = []
    for input_idx, output_idx in M.sample_tasks:
        p_in = inputs[input_idx - 1].copy()
        p_out = outputs[output_idx - 1].copy()
        above_in = p_in.copy(); above_in[2] = C.z_safe
        pick = p_in.copy(); pick[2] = C.z_pick
        above_out = p_out.copy(); above_out[2] = C.z_safe
        place = p_out.copy(); place[2] = C.z_pick
        seq = [above_in, pick, above_in, above_out, place, above_out]
        lab = ["input_above", "pick", "input_above", "output_above", "place", "output_above"]
        waypoints.extend(seq)
        labels.extend([f"{input_idx}->{output_idx}:{x}" for x in lab])
    return np.array(waypoints, dtype=float), labels


def smooth_segment(p0, p1, dt):
    dist = np.linalg.norm(p1 - p0)
    duration = max(0.45, dist / M.max_velocity + 0.25)
    n = max(2, int(np.ceil(duration / dt)))
    tau = np.linspace(0, 1, n, endpoint=False)
    s = 10 * tau**3 - 15 * tau**4 + 6 * tau**5
    ds = (30 * tau**2 - 60 * tau**3 + 30 * tau**4) / duration
    pos = p0 + (p1 - p0) * s[:, None]
    vel = (p1 - p0) * ds[:, None]
    return pos, vel


def reference_trajectory():
    waypoints, labels = generate_waypoints()
    dt = M.dt
    pos_all = []
    vel_all = []
    event_rows = []
    t_cursor = 0.0
    current = np.array([waypoints[0, 0], waypoints[0, 1], C.z_safe], dtype=float)
    for i, target in enumerate(waypoints):
        pos, vel = smooth_segment(current, target, dt)
        pos_all.append(pos); vel_all.append(vel)
        event_rows.append([round(t_cursor, 3), labels[i], *target.tolist()])
        t_cursor += len(pos) * dt
        dwell_n = int(M.dwell_time / dt)
        if dwell_n > 0:
            pos_all.append(np.repeat(target[None, :], dwell_n, axis=0))
            vel_all.append(np.zeros((dwell_n, 3)))
            t_cursor += dwell_n * dt
        current = target
    ref = np.vstack(pos_all)
    vel = np.vstack(vel_all)
    t = np.arange(ref.shape[0]) * dt
    return t, ref, vel, event_rows


def simulate_axis(ref, cfg, dt):
    n = len(ref)
    y = np.zeros(n)
    v = np.zeros(n)
    u = np.zeros(n)
    y[0] = ref[0]
    integ = 0.0
    prev_err = 0.0
    for k in range(1, n):
        err = ref[k - 1] - y[k - 1]
        integ += err * dt
        deriv = (err - prev_err) / dt
        cmd = cfg["Kp"] * err + cfg["Ki"] * integ + cfg["Kd"] * deriv
        cmd = float(np.clip(cmd, -P.control_limit, P.control_limit))
        acc = (cmd - cfg["b"] * v[k - 1]) / cfg["m"]
        v[k] = v[k - 1] + acc * dt
        y[k] = y[k - 1] + v[k] * dt
        u[k] = cmd
        prev_err = err
    return y, v, u


def simulate_robot(t, ref):
    actual = np.zeros_like(ref)
    vel = np.zeros_like(ref)
    ctrl = np.zeros_like(ref)
    for i, axis in enumerate(["x", "y", "z"]):
        actual[:, i], vel[:, i], ctrl[:, i] = simulate_axis(ref[:, i], P.axes[axis], M.dt)
    return actual, vel, ctrl


def metrics(ref, actual):
    err = ref - actual
    out = {}
    for i, axis in enumerate(["x", "y", "z"]):
        e = err[:, i]
        out[axis] = {
            "max_abs_error_mm": float(np.max(np.abs(e))),
            "mean_abs_error_mm": float(np.mean(np.abs(e))),
            "rmse_mm": float(np.sqrt(np.mean(e**2))),
        }
    out["combined_rmse_mm"] = float(np.sqrt(np.mean(err**2)))
    return out


def save_data(t, ref, actual, vel_ref, vel_actual, ctrl, event_rows, met):
    data_dir = ROOT / "results/data"
    data_dir.mkdir(parents=True, exist_ok=True)
    header = ["t", "x_ref", "y_ref", "z_ref", "x", "y", "z", "vx_ref", "vy_ref", "vz_ref", "vx", "vy", "vz", "ux", "uy", "uz"]
    with (data_dir / "python_pid_simulation.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        for row in zip(t, *ref.T, *actual.T, *vel_ref.T, *vel_actual.T, *ctrl.T):
            w.writerow([round(float(x), 6) for x in row])
    with (data_dir / "waypoint_events.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["time_s", "event", "x_mm", "y_mm", "z_mm"])
        w.writerows(event_rows)
    (data_dir / "pid_metrics.json").write_text(json.dumps(met, indent=2, ensure_ascii=False), encoding="utf-8")


def plot_results(t, ref, actual, vel_ref, vel_actual, ctrl):
    fig_dir = ROOT / "results/figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    axes = ["X", "Y", "Z"]
    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for i, ax in enumerate(axs):
        ax.plot(t, ref[:, i], "k--", lw=1.2, label=f"{axes[i]} ref")
        ax.plot(t, actual[:, i], lw=1.0, label=f"{axes[i]} actual")
        ax.set_ylabel("mm")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")
    axs[-1].set_xlabel("Time (s)")
    fig.suptitle("X/Y/Z Position Tracking")
    fig.tight_layout()
    fig.savefig(fig_dir / "position_tracking.png", dpi=160)
    plt.close(fig)

    err = ref - actual
    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for i, ax in enumerate(axs):
        ax.plot(t, err[:, i], lw=1.0)
        ax.set_ylabel(f"{axes[i]} err (mm)")
        ax.grid(True, alpha=0.3)
    axs[-1].set_xlabel("Time (s)")
    fig.suptitle("Tracking Error")
    fig.tight_layout()
    fig.savefig(fig_dir / "tracking_error.png", dpi=160)
    plt.close(fig)

    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(ref[:, 0], ref[:, 1], ref[:, 2], "k--", lw=1.0, label="reference")
    ax.plot(actual[:, 0], actual[:, 1], actual[:, 2], color="#d62728", lw=1.1, label="actual")
    ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)"); ax.set_zlabel("Z (mm)")
    ax.set_title("3D End Effector Trajectory")
    ax.legend()
    fig.tight_layout()
    fig.savefig(fig_dir / "end_effector_3d.png", dpi=160)
    plt.close(fig)

    fig, axs = plt.subplots(3, 2, figsize=(12, 8), sharex=True)
    for i in range(3):
        axs[i, 0].plot(t, vel_ref[:, i], "k--", lw=1, label="ref")
        axs[i, 0].plot(t, vel_actual[:, i], lw=1, label="actual")
        axs[i, 0].set_ylabel(f"{axes[i]} vel")
        axs[i, 0].grid(True, alpha=0.3)
        axs[i, 1].plot(t, ctrl[:, i], lw=1, color="#9467bd")
        axs[i, 1].set_ylabel(f"{axes[i]} u")
        axs[i, 1].grid(True, alpha=0.3)
    axs[-1, 0].set_xlabel("Time (s)")
    axs[-1, 1].set_xlabel("Time (s)")
    axs[0, 0].legend(loc="upper right")
    fig.suptitle("Velocity and PID Control Input")
    fig.tight_layout()
    fig.savefig(fig_dir / "velocity_control.png", dpi=160)
    plt.close(fig)


def animate(t, ref, actual):
    anim_dir = ROOT / "results/animation"
    anim_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    step = max(1, len(t) // 90)
    for idx in range(0, len(t), step):
        fig = plt.figure(figsize=(6, 5))
        ax = fig.add_subplot(111, projection="3d")
        ax.plot(ref[:idx + 1, 0], ref[:idx + 1, 1], ref[:idx + 1, 2], "k--", lw=0.8)
        ax.plot(actual[:idx + 1, 0], actual[:idx + 1, 1], actual[:idx + 1, 2], color="#d62728", lw=1.3)
        ax.scatter(actual[idx, 0], actual[idx, 1], actual[idx, 2], s=45, color="#d62728")
        ax.set_xlim(40, 470); ax.set_ylim(60, 230); ax.set_zlim(0, 110)
        ax.set_xlabel("X mm"); ax.set_ylabel("Y mm"); ax.set_zlabel("Z mm")
        ax.set_title(f"Blood Sample Sorting Robot t={t[idx]:.1f}s")
        ax.view_init(elev=24, azim=-55)
        fig.tight_layout()
        fig.canvas.draw()
        w, h = fig.canvas.get_width_height()
        img = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(h, w, 4)[:, :, :3]
        frames.append(img.copy())
        plt.close(fig)
    imageio.mimsave(anim_dir / "sorting_robot_motion.gif", frames, duration=0.08)


def main():
    t, ref, vel_ref, event_rows = reference_trajectory()
    actual, vel_actual, ctrl = simulate_robot(t, ref)
    met = metrics(ref, actual)
    save_data(t, ref, actual, vel_ref, vel_actual, ctrl, event_rows, met)
    plot_results(t, ref, actual, vel_ref, vel_actual, ctrl)
    animate(t, ref, actual)
    print("Python PID simulation complete.")
    print(json.dumps(met, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
