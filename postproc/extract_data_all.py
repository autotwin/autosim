import numpy as np
import subprocess

# Load list of input filenames
input_list = np.loadtxt("abaqus_mesh/mesh_list_run1.txt", dtype=str)

for input_file in input_list:
    odb_basename = input_file[:-4]  # remove ".inp"

    # Construct the command to run Abaqus Python script
    cmd = ["abaqus", "python", "postproc/extract_data_strain_vs_strain_rate.py", odb_basename]

    # Run the command and wait for it to finish
    subprocess.call(cmd)

    # Print confirmation
    print(odb_basename + " completed")
