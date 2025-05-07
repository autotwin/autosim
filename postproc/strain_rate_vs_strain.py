# -*- coding: mbcs -*-
from odbAccess import openOdb
from abaqusConstants import INTEGRATION_POINT, MAX_PRINCIPAL
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# === Set ODB path manually ===
odb_path = "simulation_results/example1/example1.odb"
save_path = "simulation_results/example1/"
print "Opening ODB file:", odb_path
odb_basename  = os.path.splitext(os.path.basename(odb_path))[0]  # e.g., "example1"

# === Open ODB and get step/frame ===
odb = openOdb(odb_path)
instance_name = 'PART-1-1'
step = list(odb.steps.values())[-1]

# === Get frame closest to t = 0.02 s ===
target_time = 0.02
frame = min(step.frames, key=lambda f: abs(f.frameValue - target_time))
actual_time = frame.frameValue
print "Using frame at time = %.6f (closest to %.3f)" % (actual_time, target_time)

region = odb.rootAssembly.instances[instance_name]

# === Extract strain and strain rate (Max Principal) ===
print "Extracting LE and ER..."
LE = frame.fieldOutputs['LE'].getSubset(region=region, position=INTEGRATION_POINT)
ER = frame.fieldOutputs['ER'].getSubset(region=region, position=INTEGRATION_POINT)

LE_values = [v.data for v in LE.getScalarField(invariant=MAX_PRINCIPAL).values]
ER_values = [v.data for v in ER.getScalarField(invariant=MAX_PRINCIPAL).values]

LE_values = np.array(LE_values)
ER_values = np.array(ER_values)

print "Collected %d data points." % len(LE_values)

# === Compute 95th percentiles ===
LE_95 = np.percentile(LE_values, 95)
ER_95 = np.percentile(ER_values, 95)
LE_95_str = "%.3e" % LE_95
ER_95_str = "%.3e" % ER_95

# === Save strain + strain rate values to .txt ===
output_txt = save_path + odb_basename  + '_strain_vs_strainrate_at_%.0fms.txt' % (actual_time * 1000)
np.savetxt(output_txt, np.column_stack((LE_values, ER_values)),
           header='Strain\tStrainRate', fmt='%.6e')
print "Saved strain/strain rate data to:", output_txt

# === Scatter plot ===
plt.figure(figsize=(6, 6))
plt.scatter(LE_values, ER_values, s=10, alpha=0.5)
plt.axvline(LE_95, color='r', linestyle='--', label='95th %ile strain = ' + LE_95_str)
plt.axhline(ER_95, color='g', linestyle='--', label='95th %ile strain rate = ' + ER_95_str)
plt.xlabel('Max Principal Strain')
plt.ylabel('Max Principal Strain Rate')
plt.title('Strain Rate vs Strain at t = %.3f s' % actual_time)
plt.grid(True)
plt.legend()
plt.tight_layout()
scatter_file = save_path + odb_basename + '_scatter_strainrate_vs_strain_%.0fms.png' % (actual_time * 1000)
plt.savefig(scatter_file, dpi=150)
print "Saved:", scatter_file

# === Histogram: Strain ===
plt.figure(figsize=(8, 4))
plt.hist(LE_values, bins=50, color='gray', alpha=0.7)
plt.axvline(LE_95, color='r', linestyle='--', label='95th percentile = ' + LE_95_str)
plt.xlabel('Max Principal Strain')
plt.ylabel('Count')
plt.title('Histogram of Strain at t = %.3f s' % actual_time)
plt.legend()
plt.tight_layout()
hist_strain_file = save_path +  odb_basename + '_histogram_strain_%.0fms.png' % (actual_time * 1000)
plt.savefig(hist_strain_file, dpi=150)
print "Saved:", hist_strain_file

# === Histogram: Strain Rate ===
plt.figure(figsize=(8, 4))
plt.hist(ER_values, bins=50, color='gray', alpha=0.7)
plt.axvline(ER_95, color='g', linestyle='--', label='95th percentile = ' + ER_95_str)
plt.xlabel('Max Principal Strain Rate')
plt.ylabel('Count')
plt.title('Histogram of Strain Rate at t = %.3f s' % actual_time)
plt.legend()
plt.tight_layout()
hist_rate_file = save_path +  odb_basename + '_histogram_strainrate_%.0fms.png' % (actual_time * 1000)
plt.savefig(hist_rate_file, dpi=150)
print "Saved:", hist_rate_file

odb.close()
print "Done."
