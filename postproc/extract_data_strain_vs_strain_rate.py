# -*- coding: mbcs -*-
from odbAccess import openOdb
from abaqusConstants import INTEGRATION_POINT, MAX_PRINCIPAL
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys

# --- Get command-line arguments ---
if len(sys.argv) < 2:
    print("Usage: python scriptname.py <odb_basename> [save_full_txt_file]")
    sys.exit(1)

odb_basename = sys.argv[1]

# Optional argument: save_full_txt_file
save_full_txt_file = "false"  # default
if len(sys.argv) >= 3:
    save_full_txt_file = sys.argv[2].lower()

odb_path = "simulation_results/" + odb_basename + "/" + odb_basename + ".odb"
save_path = "simulation_results/" + odb_basename + "/"
print "Opening ODB file:", odb_path
odb_basename  = os.path.splitext(os.path.basename(odb_path))[0]  # e.g., "example1"

# === Open ODB ===
odb = openOdb(odb_path)
instance_name = 'PART-1-1'
step = list(odb.steps.values())[-1]
frames = step.frames
num_frames = len(frames)

region = odb.rootAssembly.instances[instance_name].elementSets['EB1']

# === Initialize data arrays ===
# We determine number of elements from the first frame
first_LE = frames[0].fieldOutputs['LE'].getSubset(region=region, position=INTEGRATION_POINT)
num_elements = len(first_LE.getScalarField(invariant=MAX_PRINCIPAL).values)

strain_data = np.zeros((num_frames, num_elements))
strain_rate_data = np.zeros((num_frames, num_elements))
perc_95_data = np.zeros((num_frames, 2))  # Column 0: strain, Column 1: strain rate
frame_times = np.zeros((num_frames,))

# === Loop through frames ===
print "Extracting data from %d frames..." % num_frames
for i, frame in enumerate(frames):
    frame_times[i] = frame.frameValue

    LE = frame.fieldOutputs['LE'].getSubset(region=region, position=INTEGRATION_POINT)
    ER = frame.fieldOutputs['ER'].getSubset(region=region, position=INTEGRATION_POINT)
    
    LE_values = [v.data for v in LE.getScalarField(invariant=MAX_PRINCIPAL).values]
    ER_values = [v.data for v in ER.getScalarField(invariant=MAX_PRINCIPAL).values]
    
    strain_data[i, :] = LE_values
    strain_rate_data[i, :] = ER_values
    
    perc_95_data[i, 0] = np.percentile(LE_values, 95)
    perc_95_data[i, 1] = np.percentile(ER_values, 95)

    print "Processed frame %d/%d (time = %.6f)" % (i+1, num_frames, frame.frameValue)

# === Save arrays ===
if save_full_txt_file:
    np.savetxt(save_path + odb_basename + '_strain_data.txt', strain_data, fmt='%.6e')
    np.savetxt(save_path + odb_basename + '_strainrate_data.txt', strain_rate_data, fmt='%.6e')

np.savetxt(save_path + odb_basename + '_strain_percentiles_95.txt', perc_95_data,
           header='95thPercentileStrain\t95thPercentileStrainRate', fmt='%.6e')

np.savetxt(save_path + odb_basename + '_frame_times.txt', frame_times,
           header='TimePerFrame (s)', fmt='%.8e')

print "Saved strain_data, strain_rate_data, and 95th percentile arrays to: ", save_path

odb.close()
print "Done."
