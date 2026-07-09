# Bring Your Own Subject Data

autosim expects two inputs per subject: a segmentation `.npy` file (normally from Autovalidate) and a kinematics `.mat` file. This tutorial covers what each must contain if you're not using Autovalidate directly.

## The segmentation `.npy` file

### Filename

The filename itself is parsed for metadata — it must follow exactly:

```
subject_id-motion_type-algorithm-brain_fidelity-membranes-combined.npy
```

For example: `U01_HJF_0001_01-NR-synthseg-heterogeneous-membranesON-combined.npy`. `parse_npy_filename()` (`pipeline/config.py`) splits on `-` and expects exactly 6 fields; `membranesON`/`membranesOFF` (anything else is treated as OFF) sets `include_membranes`.

### Array contents

An integer-labeled 3D array (any of the usual NumPy integer dtypes; automesh has been observed to reject `int16` in some cases — `uint8` is the safe choice) using this label schema:

| Label | Region |
|---|---|
| 0 | Background |
| 1 | White matter |
| 2 | Grey matter (only used if `brain_fidelity = heterogeneous`) |
| 3 | CSF |
| 4 | Skull |
| 5 | Membranes (only used if `include_membranes = true`) |

This must match exactly — `pipeline/preprocessing/mesh_schema.py::mesh_mapping()` assumes automesh preserves these label values as its element block numbers (label `N` → `EBN`). See [Keeping Autosim in Sync with Autovalidate](sync_with_autovalidate.md) if you're generating this schema from a different pipeline.

### Companion NIfTI

autosim reads the voxel size from a companion file at the same path with `combined.npy` replaced by `combined_labels.nii.gz` (`pipeline/io/nifti_io.py::get_voxel_size_from_npy()`). This file must exist alongside the `.npy` even though the `.npy` array itself is what actually gets meshed.

## The kinematics `.mat` file

Loaded via `scipy.io.loadmat` and expected to contain a struct named `PVA` (`pipeline/io/mat_io.py::load_pva_mat()`) with these fields:

| Field | Meaning |
|---|---|
| `time` | Time vector (ms) |
| `velocity` | Angular velocity vector (rad/s), same length as `time` |
| `frameCenter_ms` | Center timestamp (ms) of each comparison frame |
| `frameStart_ms` | Start timestamp (ms) of each comparison frame |
| `frameEnd_ms` | End timestamp (ms) of each comparison frame |

The three `frame*_ms` arrays define the comparison frames used for output requests (see [Run Your First Simulation](first_simulation.md)) — they don't need to be evenly spaced, but must be monotonically increasing and consistent with each other (`frameStart_ms[i] <= frameCenter_ms[i] <= frameEnd_ms[i]`).

## Once you have both files

Point `npy_file` and `mat_path` at them in your config and proceed as in [Quick Start](../quick_start.md).
