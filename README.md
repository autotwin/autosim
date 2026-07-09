![Python 3.11 and 3.12 supported](https://img.shields.io/badge/Python-3.11_|_3.12-blue)

# autosim

`autosim` builds and submits patient-specific brain biomechanics finite element
simulations (Abaqus/Explicit) from segmented MRI data. It is part of the
[autotwin](https://github.com/autotwin) project and is designed to consume the
`combined.npy` output of [Autovalidate](https://github.com/autotwin/autovalidate)
directly.

Given a segmentation `.npy` file and a kinematics `.mat` file, `autosim`:

1. Meshes the segmentation into hexahedral elements (via
   [automesh](https://github.com/autotwin/automesh))
2. Builds the full Abaqus `.inp` deck — materials, boundary/initial
   conditions, loads, assembly, and output requests
3. Submits the job to an HPC scheduler (SGE by default)

Full documentation: [autotwin.github.io/AutoSim](https://autotwin.github.io/AutoSim)

## Material models

**Brain (WM/GM):** `alshareef` (linear viscoelastic), `menichetti`
(Neo-Hookean + Prony), `basilio` (Ogden + Prony), `upadhyay` (custom VUMAT,
O-USS model). `custom` is available as an escape hatch for bringing your own
material card.

**CSF:** `neo_hookean` (CSF as a soft viscoelastic solid) or `fluid`
(Mie-Gruneisen equation of state).

## Quick start

```bash
pip install .

cp example_config.toml my_config.toml
# edit my_config.toml: paths to automesh/abaqus, your .npy + .mat files,
# output directory, and your chosen material_model / csf_model

python run_pipeline.py --config my_config.toml
```

This meshes the subject, writes the `.inp` deck to `output_dir`, and submits
the Abaqus job via `qsub`. See `example_config.toml` for all available
fields — HPC scheduler settings (cores, walltime, module names) are optional
and default to BU SCC's environment; override them for your own cluster.

## Running tests

```bash
pytest tests/
```

## License

MIT — see [LICENSE](LICENSE).