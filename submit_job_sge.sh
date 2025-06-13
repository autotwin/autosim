#!/bin/bash -l

# === SGE/Cluster Settings ===
#$ -P lejlab
#$ -pe omp 16


# === Get Mesh File from Argument ===
MESHFILE="$1"
if [ -z "$MESHFILE" ]; then
    echo "Error: No mesh file provided."
    exit 1
fi

# === Config ===
JOBNAME="${MESHFILE%.inp}"
TEMPLATE="base_template.inp"
OUTPUT_DIR="simulation_results/${JOBNAME}"
INPUT_FILE="${OUTPUT_DIR}/${JOBNAME}.inp"
MESH_PATH="../../abaqus_mesh/${MESHFILE}"
CPUS=${NSLOTS:-16}

# === Load Environment ===
source /ad/eng/bin/engenv.sh
module load simulia/2022

# === Prepare Job Directory ===
mkdir -p "$OUTPUT_DIR"
mkdir -p logs

# === Create Abaqus Input File from Template ===
sed "s|@MESHFILE@|$MESH_PATH|" "$TEMPLATE" > "$INPUT_FILE"

cd "$OUTPUT_DIR"

# === Run Abaqus ===
echo "Running Abaqus job: $JOBNAME"
echo "Using input file: $INPUT_FILE"
abaqus cpus=$CPUS input="$JOBNAME.inp" job="$JOBNAME" interactive double


echo "Job $JOBNAME completed."
