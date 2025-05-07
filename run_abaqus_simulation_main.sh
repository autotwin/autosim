#!/bin/bash -l

# === SGE/Cluster Settings ===
#$ -P lejlab
#$ -pe omp 16

echo "NSLOTS is: $NSLOTS"

# === CONFIG ===
JOBNAME=example1
INPUT_FILE=abaqus_simulation_main.inp  # Relative or absolute path to your .inp file
OUTPUT_DIR=simulation_results/${JOBNAME}
CPUS=${NSLOTS:-4}

# === Create output directory and run inside it ===
mkdir -p "$OUTPUT_DIR"

cp "$INPUT_FILE" "$OUTPUT_DIR/"

cd "$OUTPUT_DIR"

echo "Running Abaqus job: $JOBNAME"
echo "Writing output to: $(pwd)"
echo "Using input file: $INPUT_FILE"
ls -l "$INPUT_FILE"

# === Load Abaqus environment ===
source /ad/eng/bin/engenv.sh
module load simulia/2022

# === Run Abaqus ===
abaqus cpus=$CPUS input=$INPUT_FILE job=$JOBNAME interactive double

echo "Abaqus job $JOBNAME finished."
