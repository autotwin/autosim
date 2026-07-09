# HPC

autosim submits jobs via SGE (`qsub`). `run_pipeline.py::run_abaqus()` generates a submit script and runs `qsub` on it — the pipeline call returns as soon as the job is queued, it does not wait for the solve to finish.

## Resource requests

Set via `[run]`: `n_cpus` (default 16), `h_rt` (default `"12:00:00"`), `mem_per_core` (default `"4G"`). These map directly onto SGE's `#$ -pe omp`, `#$ -l h_rt=`, and `#$ -l mem_per_core=` directives.

## Environment and modules

The generated submit script sources an environment setup script and loads scheduler modules before invoking Abaqus:

```bash
source {env_setup_script}
module load {simulia_module}
module load {intel_module}   # only if material_model = "upadhyay"
```

These default to Boston University Shared Computing Cluster's environment (`/ad/eng/bin/engenv.sh`, `simulia/2025`, `intel/2024.0`) but are overridable per config — set `env_setup_script`, `simulia_module`, and/or `intel_module` in `[run]` if you're on a different cluster.

## If you're not on SGE

The scheduler directives themselves (`#$ ...`, `qsub`) are hardcoded in `run_pipeline.py::run_abaqus()` — that function is written as an SGE example. If your cluster uses Slurm, PBS, or LSF, you'll need to adapt the submit-script template in that function to your scheduler's syntax; the config-driven env/module fields above will still apply.

## Checking job status

autosim doesn't poll job status itself. Check `{output_dir}/{subject_id}.log`, `.sta`, and `.dat` directly, or use your scheduler's own tools (`qstat`, etc.). See [Diagnose a Failed Simulation](tutorials/diagnose.md) for what to look for in each file.
