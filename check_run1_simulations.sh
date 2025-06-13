#!/bin/bash

# File containing list of .inp filenames
input_list="abaqus_mesh/mesh_list_run1.txt"

while read inp_file; do
    # Remove ".inp" extension
    basename="${inp_file%.inp}"

    # Path to the 95th percentile file
    txt_file="simulation_results/${basename}/${basename}_strain_percentiles_95.txt"

    # Check if file exists
    if [[ -f "$txt_file" ]]; then
        # Count number of lines (skip header if present)
        num_lines=$(grep -cv '^#' "$txt_file")

        if [[ $num_lines -lt 81 ]]; then
            echo "$basename"
        fi
    else
        echo "Missing file for $basename"
    fi
done < "$input_list"
