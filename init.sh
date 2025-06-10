#/bin/bash

# This module is used as a preparatory environment setup on the HPC when running the
# mesh_to_sim.py module.

module purge
module load aue/anaconda3/2024.06-1
python --version
module load sierra
if [ $? -eq 0 ]; then
    echo "Module 'sierra' loaded successfully."
else
    echo "Failed to load module 'sierra'".
    exit 1
fi

module load seacas
source .venv/bin/activate
pip list

