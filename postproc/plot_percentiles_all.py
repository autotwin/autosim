import matplotlib.pyplot as plt
import numpy as np
import os

# --- Parameters ---
highlight_basename = "IXI013-HH-1212-T1_run1"
#highlight_basename = "IXI012-HH-1211-T1_run1"  # Set to None if no highlight desired

# Load list of input filenames
input_list = np.loadtxt("abaqus_mesh/mesh_list_run1.txt", dtype=str)

# --- Containers ---
all_strain = []
all_strain_rate = []
labels = []

highlight_strain = None
highlight_strain_rate = None
highlight_time = None

# --- Loop through all models ---
for input_file in input_list:
    odb_basename = input_file[:-4]  # remove ".inp"
    basepath = os.path.join("simulation_results", odb_basename)

    percentile_fname = os.path.join(basepath, odb_basename + "_strain_percentiles_95.txt")
    time_fname = os.path.join(basepath, odb_basename + "_frame_times.txt")

    if not os.path.isfile(percentile_fname):
        print("Missing:", percentile_fname)
        continue

    try:
        percentile = np.loadtxt(percentile_fname)

        # Skip simulations with <81 frames
        if percentile.shape[0] < 81:
            print("Skipping %s (only %d frames)" % (odb_basename, percentile.shape[0]))
            continue

        strain_rate_95 = percentile[:, 1]
        strain_95 = percentile[:, 0]

        if highlight_basename == odb_basename:
            if os.path.isfile(time_fname):
                highlight_time = np.loadtxt(time_fname)
            highlight_strain_rate = strain_rate_95
            highlight_strain = strain_95
        else:
            all_strain_rate.append(strain_rate_95)
            all_strain.append(strain_95)
            labels.append(odb_basename)

    except Exception as e:
        print("Error reading %s: %s" % (percentile_fname, str(e)))
        continue

# --- Plotting ---
plt.figure(figsize=(8, 6), dpi=150)

# Background: light gray lines with dot markers
for i in range(len(all_strain)):
    plt.plot(all_strain_rate[i], all_strain[i], color='lightgray', marker='.', markersize=3, linewidth=0.5)

# Highlighted simulation with time-colored points
if highlight_strain is not None and highlight_strain_rate is not None and highlight_time is not None:
    sc = plt.scatter(highlight_strain_rate, highlight_strain,
                     c=highlight_time, cmap='plasma_r',
                     marker='o', s=60, edgecolor='k', linewidths=0.8, zorder=2)
    plt.scatter(highlight_strain_rate, highlight_strain,
                marker='+', color='k', linewidths=1.2, s=60, zorder=3)
    
    for i in range(len(highlight_time) - 1):
        plt.annotate(
            '',
            xy=(highlight_strain_rate[i+1], highlight_strain[i+1]),
            xytext=(highlight_strain_rate[i], highlight_strain[i]),
            arrowprops=dict(arrowstyle='->', color='gray', lw=0.8, shrinkA=1, shrinkB=1),
            zorder=1
        )

    cbar = plt.colorbar(sc)
    cbar.set_label("Time (s)")

# Labels and style
plt.xlabel("95th Percentile Max Principle Logarithmic Strain Rate")
plt.ylabel("95th Percentile Max Principle Logarithmic Strain")
plt.title("Strain vs Strain Rate Trajectories\n(%s highlighted)"%(highlight_basename))
plt.grid(True)
plt.tight_layout()

# Save
output_fig = "postproc/strain_percentile_summary_%s.png"%(highlight_basename)
plt.savefig(output_fig)
print("Saved figure to:", output_fig)
