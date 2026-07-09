# Configuration Reference

Config files are TOML, with two sections: `[env]` (tool paths) and `[run]` (everything else). See `example_config.toml` for a minimal working example.

## `[env]` — required

| Field | Description |
|---|---|
| `automesh` | Path to the `automesh` executable |
| `abaqus` | Path to the `abaqus` executable |

## `[run]` — required

| Field | Description |
|---|---|
| `npy_file` | Path to Autovalidate's `combined.npy` output. Its filename must follow `subject_id-motion_type-algorithm-brain_fidelity-membranes-combined.npy` — `subject_id`, `motion_type`, `algorithm`, `brain_fidelity`, and `include_membranes` are all parsed from this filename, not set directly |
| `mat_path` | Path to the kinematics `.mat` file for the same subject |
| `output_dir` | Directory where all generated `.inp` files and Abaqus output will be written |
| `material_model` | One of: `alshareef`, `menichetti`, `basilio`, `upadhyay`, `custom` — see [Brain Material Models](materials/brain.md) |
| `csf_model` | One of: `neo_hookean`, `fluid` — see [CSF Material Models](materials/csf.md) |
| `ref_dof` | Reference-node rotation DOF: `4` (X), `5` (Y), or `6` (Z) |
| `time_interval_step` | Time step (seconds) at which field/nodal output is saved |

## `[run]` — optional, with defaults

| Field | Default | Description |
|---|---|---|
| `n_cpus` | `16` | Number of cores requested from the scheduler |
| `h_rt` | `"12:00:00"` | Walltime limit |
| `mem_per_core` | `"4G"` | Memory per core |
| `v_cutoff` | `0.1` | Angular velocity (rad/s) below which trailing frames are trimmed from the simulation window |
| `dt_scale_factor` | `1.0` | Scales the Abaqus/Explicit stable time increment (mass scaling) |
| `sim_end_ms` | `0.0` | Caps the last comparison frame at this time (ms); `0.0` = no cap, run the full window |
| `env_setup_script` | `"/ad/eng/bin/engenv.sh"` | Shell script sourced before loading modules in the submit script — see [HPC](hpc.md) |
| `simulia_module` | `"simulia/2025"` | Module loaded for Abaqus |
| `intel_module` | `"intel/2024.0"` | Module loaded when `material_model = "upadhyay"` (VUMAT compilation) |

## Derived, not configurable

These come from parsing `npy_file`'s filename, not from `[run]` directly: `subject_id`, `motion_type`, `algorithm`, `brain_fidelity`, `include_membranes`. `vumat_path` is set automatically when `material_model = "upadhyay"`.
