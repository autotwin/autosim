import matplotlib.pyplot as plt
import numpy as np
import os

# --- File setup ---
basename = "IXI013-HH-1212-T1_run1"
basepath = os.path.join("simulation_results", basename)

percentile_fname = os.path.join(basepath, basename + "_strain_percentiles_95.txt")
time_fname = os.path.join(basepath, basename + "_frame_times.txt")
fig_fname = os.path.join(basepath, basename + "_strain_percentiles_95.png")

# --- Load data ---
percentile = np.loadtxt(percentile_fname)
time = np.loadtxt(time_fname)

strain_rate_95 = percentile[:, 1]
strain_95 = percentile[:, 0]

# --- Plot setup ---
plt.figure(figsize=(6, 5), dpi=150)

# Light gray line connecting points
plt.plot(strain_rate_95, strain_95, color='lightgray', linewidth=1, zorder=1)


# Background filled circles with black edge
sc = plt.scatter(strain_rate_95, strain_95,
                 c=time, cmap='plasma_r',
                 marker='o', s=60,
                 edgecolor='k', linewidths=0.8,
                 zorder=2)

# Overlay black crosshairs
plt.scatter(strain_rate_95, strain_95,
            marker='+', color='k',
            linewidths=1.0, s=60,
            zorder=3)

# Arrows between all consecutive points
for i in range(len(time) - 1):
    plt.annotate(
        '',
        xy=(strain_rate_95[i+1], strain_95[i+1]),
        xytext=(strain_rate_95[i], strain_95[i]),
        arrowprops=dict(
            arrowstyle='->',
            color='gray',
            lw=0.8,
            shrinkA=1,
            shrinkB=1
        ),
        zorder=3
    )

# Colorbar
cbar = plt.colorbar(sc)
cbar.set_label("Time (s)")

# Labels and style
plt.xlabel("95th Percentile Strain Rate")
plt.ylabel("95th Percentile Strain")
plt.title("Frame-wise 95th Percentile Strain vs Strain Rate")
plt.grid(True)
plt.tight_layout()

# Save
plt.savefig(fig_fname)
print("Saved figure to:", fig_fname)
