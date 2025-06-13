#!/bin/bash
#$ -l h_rt=24:00:00

MESH_LIST="abaqus_mesh/mesh_list_run1.txt"
BATCH_SIZE=5
WAIT_TIME=900  # 15 minutes in seconds

mkdir -p logs

# Read all mesh files into an array
mapfile -t ALL_MESHES < "$MESH_LIST"
TOTAL=${#ALL_MESHES[@]}
i=0

while [ $i -lt $TOTAL ]; do
    echo "[$(date)] Submitting jobs $((i+1)) to $((i+BATCH_SIZE))..."

    # Submit up to BATCH_SIZE jobs
    for ((j = 0; j < BATCH_SIZE && i < TOTAL; j++, i++)); do
        MESHFILE="${ALL_MESHES[$i]}"
        echo "  Submitting: $MESHFILE"
        qsub submit_job_sge.sh "$MESHFILE"
        sleep 5  # Stagger slightly to avoid overload
    done

    echo "[$(date)] Batch submitted. Pausing for 15 minutes..."
    sleep $WAIT_TIME
done

echo "[$(date)] All jobs submitted."