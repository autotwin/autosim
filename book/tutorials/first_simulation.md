# Run Your First Simulation

This walks through a single-subject run end to end — what each step does, what files it produces, and how to tell whether it worked. See [Quick Start](../quick_start.md) for the terse version.

## Prerequisites

- A segmentation `.npy` file from Autovalidate, named `subject_id-motion_type-algorithm-brain_fidelity-membranes-combined.npy`, with its companion `*combined_labels.nii.gz` alongside it (autosim reads the voxel size from the companion NIfTI)
- A kinematics `.mat` file for the same subject (see [Bring Your Own Subject Data](own_data.md) for the expected structure)
- `automesh` and `abaqus` installed and reachable

## 1. Write a config

```toml
[env]
automesh = "/path/to/automesh"
abaqus   = "/path/to/abaqus"

[run]
npy_file       = "/data/U01_HJF_0001_01-NR-synthseg-homogeneous-membranesON-combined.npy"
mat_path       = "/data/U01_HJF_0001_01_NR.mat"
output_dir     = "/results/U01_HJF_0001_01-menichetti"
material_model = "menichetti"
csf_model      = "fluid"
ref_dof        = 6
time_interval_step = 0.002
```

## 2. Run it

```bash
python run_pipeline.py --config my_config.toml
```

Console output tracks three steps:

```
[Step 1/3] Meshing...
[Step 2/3] Building .inp files...
[Step 3/3] Running Abaqus...
```

### Step 1 — Meshing

Calls `automesh` to convert the segmentation into a hexahedral mesh, translated so its center of geometry sits at the origin. Produces `{output_dir}/{subject_id}.inp`.

### Step 2 — Building `.inp` files

Six sub-steps, each printed as it runs:

| File | Contents |
|---|---|
| `loads.inp` | The velocity amplitude curve (`*Amplitude`), trimmed to the active motion window |
| `frame_times.csv` | The comparison-frame timestamps used for output requests |
| `initial_conditions.inp` | Rotating velocity IC on all nodes, matching the amplitude curve's starting velocity |
| `{tissue}.inp` (one per material — `brain`/`wm`/`gm`/`csf`/`skull`/`membranes`) | Material cards for each tissue |
| `assembly.inp` | Reference node, skull rigid body, and solid section assignments |
| `step.inp` | The `*Step` block — boundary condition, field/history output requests |
| `simulation.inp` | Master file that `*INCLUDE`s all of the above |

### Step 3 — Running Abaqus

Writes `submit.sh` and submits it via `qsub`. This step **does not wait** for the solve to finish — it returns as soon as the job is queued.

## 3. Check on it

```bash
tail -f {output_dir}/{subject_id}.log
```

When the job finishes, check `{output_dir}/{subject_id}.sta` for:

```
THE ANALYSIS HAS COMPLETED SUCCESSFULLY
```

If it's missing or you see errors instead, see [Diagnose a Failed Simulation](diagnose.md).

## Expected runtime

Varies a lot by `material_model`. The `upadhyay` VUMAT model is substantially slower than the native-keyword models (`alshareef`, `menichetti`, `basilio`) because it runs as compiled user subroutine code evaluated at every integration point, every increment — budget accordingly when setting `h_rt`.
