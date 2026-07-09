# Quick Start

This assumes you already have a segmentation `.npy` file from Autovalidate and a kinematics `.mat` file for the same subject.

## 1. Copy the example config

```bash
cp example_config.toml my_config.toml
```

## 2. Edit the config

```toml
[env]
automesh = "/path/to/automesh"
abaqus   = "/path/to/abaqus"

[run]
npy_file        = "/path/to/U01_HJF_0001_01-NR-synthseg-heterogeneous-membranesON-combined.npy"
mat_path        = "/path/to/U01_HJF_0001_01_NR.mat"
output_dir      = "/path/to/output/U01_HJF_0001_01-NR-synthseg-heterogeneous-membranesON-menichetti"
material_model  = "menichetti"
csf_model       = "fluid"
ref_dof         = 6
time_interval_step = 0.002
```

At minimum you need paths to `automesh` and `abaqus`, your `.npy`/`.mat` files, an `output_dir`, and your chosen `material_model`/`csf_model`. See [Material Models](materials/README.md) for what's available and [Configuration Reference](configuration.md) for every field.

## 3. Run the pipeline

```bash
python run_pipeline.py --config my_config.toml
```

This will:
1. Mesh the segmentation (`create_mesh`)
2. Build the full `.inp` deck (`generate_inp`)
3. Submit the Abaqus job via `qsub` (`run_abaqus`)

The command returns as soon as the job is submitted — it does not wait for Abaqus to finish. Check `{output_dir}/{subject_id}.log` and `.sta` for progress, and look for `THE ANALYSIS HAS COMPLETED SUCCESSFULLY` in the `.sta` file when it's done.

## Next steps

- [Run Your First Simulation](tutorials/first_simulation.md) for a fuller walkthrough, including what each generated file is and how to tell a run succeeded
- [Diagnose a Failed Simulation](tutorials/diagnose.md) if something goes wrong
