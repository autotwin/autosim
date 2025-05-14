# Abaqus Brain Simulation + Postprocessing

This repository contains scripts and input files to run a finite element simulation of brain mechanics using Abaqus/Explicit, and postprocess the output. This repo and this README are both a work in progress. Immediate next steps involve full automation of the simulation + post processing pipeline.

> Note: See also the [SSM](ssm.md) simulation workflow.

## Running the Simulation

To submit an Abaqus simulation to the cluster via SGE (`qsub`), run:

```bash
qsub run_abaqus_simulation_main.sh
```

This will:
- Run the simulation using `abaqus_simulation_main.inp`
- Create a folder in `simulation_results/<jobname>/`
- Save all Abaqus output files (`.odb`, `.dat`, `.sta`, etc.) into that folder

Edit `run_abaqus_simulation_main.sh` to change the `JOBNAME` or input file path.

## Postprocessing

Once the simulation completes, submit the postprocessing job:

```bash
qsub run_abaqus_simulation_main_postproc.sh
```

This script:
- Run `postproc/contour_visualization.py` to read the `.odb` file and produce a contour plot
- Run `postproc/strain_rate_vs_strain.py` to read the `.odb` file, extracts max principal strain and strain rate, and generate:
  - A scatter plot (strain rate vs. strain)
  - Histograms of strain and strain rate
  - A `.txt` file with raw element-wise data

## Output Summary

- All simulation results go into: `simulation_results/<jobname>/`
- All plots and processed data are saved alongside the `.odb`

## Requirements

- Abaqus 2022 (or compatible version)
- `matplotlib` and `numpy` must be available in the Abaqus Python environment

## Notes

- You can change which frame to extract by editing `postproc/strain_rate_vs_strain.py` or `postproc/contour_visualization.py`