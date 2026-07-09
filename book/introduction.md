# Introduction

autosim builds and submits patient-specific brain biomechanics finite element simulations (Abaqus/Explicit) from segmented MRI data.

## What it does

Given a segmentation `.npy` file and a kinematics `.mat` file, autosim:

1. Meshes the segmentation into hexahedral elements (via [automesh](https://github.com/autotwin/automesh))
2. Builds the full Abaqus `.inp` deck — materials, boundary/initial conditions, loads, assembly, and output requests
3. Submits the job to an HPC scheduler (SGE by default)

## Where it fits

```
T1 MRI
  └── autovalidate  →  combined label map (.npy)
        └── automesh     →  finite element mesh (.inp)
              └── autosim      →  simulation results (.odb)
```

autosim consumes [Autovalidate](https://github.com/autotwin/autovalidate)'s `combined.npy` output directly — the filename itself encodes the subject ID, motion type, segmentation algorithm, brain fidelity, and membrane inclusion, and autosim parses that filename to configure the run.

## What you choose per run

- **Brain material model** — which paper's calibration to use for white/grey matter (see [Material Models](materials/README.md))
- **CSF material model** — solid-like viscoelastic or fluid EOS
- **Brain fidelity** — homogeneous (single brain region) or heterogeneous (separate WM/GM)
- **Membranes** — whether to include falx/tentorium
- **HPC settings** — cores, walltime, and scheduler environment (see [HPC](hpc.md))

## Next steps

- [Installation](installation.md) to set up autosim and its dependencies
- [Quick Start](quick_start.md) to run your first simulation in a few commands
