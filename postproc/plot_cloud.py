import matplotlib.pyplot as plt
import numpy as np
import os

# --- File setup ---
basename = "IXI013-HH-1212-T1_run1"
basepath = os.path.join("simulation_results", basename)

percentile_fname = os.path.join(basepath, basename + "_strain_percentiles_95.txt")
time_fname = os.path.join(basepath, basename + "_frame_times.txt")
strain_data_fname = os.path.join(basepath, basename + '_strain_data.txt')
strain_rate_data_fname = os.path.join(basepath, basename + '_strainrate_data.txt')
cloud_viz_path = os.path.join(basepath, "cloud_viz")

# --- Create output folder ---
if not os.path.exists(cloud_viz_path):
    os.makedirs(cloud_viz_path)

# --- Load data ---
percentile_data = np.loadtxt(percentile_fname)
time_data = np.loadtxt(time_fname)
strain_data = np.loadtxt(strain_data_fname)
strain_rate_data = np.loadtxt(strain_rate_data_fname)

num_frames = strain_data.shape[0]

# --- Compute fixed axis limits ---
x_all = strain_rate_data.flatten()
y_all = strain_data.flatten()
x_min, x_max = np.min(x_all), np.max(x_all)
y_min, y_max = np.min(y_all), np.max(y_all)
x_pad = 0.05 * (x_max - x_min)
y_pad = 0.05 * (y_max - y_min)
x_limits = (x_min - x_pad, x_max + x_pad)
y_limits = (y_min - y_pad, y_max + y_pad)

# --- Loop through frames ---
for i in range(num_frames):
    x = strain_rate_data[i]
    y = strain_data[i]
    x95 = percentile_data[i, 1]
    y95 = percentile_data[i, 0]

    plt.figure(figsize=(6, 5), dpi=150)

    # Point cloud
    plt.scatter(x, y, color='gray', alpha=0.5)

    # 95th percentile lines
    plt.axhline(y95, color='red', linestyle='-')
    plt.axvline(x95, color='blue', linestyle='-')

    # Crosshair
    plt.scatter([x95], [y95], marker='o', color='white', edgecolor='black', s=120, zorder=3)
    plt.scatter([x95], [y95], marker='+', color='black', s=120, linewidths=2, zorder=4)

    # Labels and limits
    plt.xlabel("Strain Rate (Max Principal)")
    plt.ylabel("Strain (Max Principal)")
    plt.title("Frame %d (t = %.3f s)" % (i, time_data[i]))
    plt.grid(True)
    plt.xlim(x_limits)
    plt.ylim(y_limits)
    plt.tight_layout()

    # Save PNG
    fig_path = os.path.join(cloud_viz_path, "frame_%03d.png" % i)
    plt.savefig(fig_path)
    plt.close()

    print("Saved:", fig_path)
