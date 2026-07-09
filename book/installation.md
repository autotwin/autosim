# Installation

## Requirements

- Python 3.11 or higher
- [automesh](https://github.com/autotwin/automesh) — builds the hexahedral mesh from the segmentation
- Abaqus/Explicit (2022 or later recommended) — runs the finite element solve
- An Intel compiler (e.g. `intel/2024.0`) — only needed if you use the `upadhyay` material model, which ships as a compiled VUMAT

## Install the package

Clone the repository and install in editable mode:

```bash
git clone https://github.com/autotwin/AutoSim.git
cd AutoSim
pip install -e .
```

This installs the `pipeline` package along with its Python dependencies: `numpy`, `scipy`, `nibabel`.

## Verify the installation

```bash
python -c "import pipeline; print('OK')"
```

Run the test suite to confirm everything works:

```bash
pytest tests/
```

## HPC environment

autosim submits Abaqus jobs via SGE (`qsub`) by default. The submit script it generates sources an environment setup script and loads scheduler modules before running Abaqus — these default to BU SCC's environment but are fully overridable per config (see [HPC](hpc.md)). No special installation step is needed beyond having Abaqus itself reachable on your cluster's compute nodes.
