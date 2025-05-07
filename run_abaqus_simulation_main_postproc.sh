#!/bin/bash -l

# === SGE/Cluster Settings ===
#$ -P lejlab

# === Load Abaqus environment ===
source /ad/eng/bin/engenv.sh
module load simulia/2022

# === Run Abaqus Post Processing===
abaqus cae noGUI=postproc/contour_visualization.py

abaqus python postproc/strain_rate_vs_strain.py
