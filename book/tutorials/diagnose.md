# Diagnose a Failed Simulation

Covers the most common failure modes, from config-time errors through to Abaqus solve failures.

## 1. Invalid config value

**Error:**
```
ValueError: Wrong material model 'zhao'. Please select one of: basilio, menichetti, alshareef, upadhyay, custom
```
or
```
ValueError: Wrong csf_model 'gruneisen'. Please select one of: neo_hookean, fluid
```
or
```
ValueError: Wrong ref_dof! Must be 4 (X rotation), 5 (Y rotation), or 6 (Z rotation)
```

**Cause:** A `[run]` field has a value outside what `parse_config()` accepts. `material_model` and `csf_model` are case-insensitive but must match exactly.

**Fix:** Check [Configuration Reference](../configuration.md) for the allowed values.

---

## 2. Companion NIfTI not found

**Error:**
```
FileNotFoundError: Companion NIfTI not found: /path/to/..._combined_labels.nii.gz
Expected a '*combined_labels.nii.gz' alongside the .npy file.
```

**Cause:** autosim reads voxel size from a companion NIfTI, not the `.npy` array itself (`get_voxel_size_from_npy()`) — it must exist at the same path with `combined.npy` replaced by `combined_labels.nii.gz`.

**Fix:** Confirm both files are present alongside each other. See [Bring Your Own Subject Data](own_data.md).

---

## 3. OFI MPI error at solve time

**Symptom:** The Abaqus job fails early with an OFI (libfabric) MPI initialization error, typically on certain SCC compute nodes.

**Cause:** Abaqus/Explicit's default MPI-based parallelization can fail on nodes where the OFI network fabric isn't set up as Abaqus expects. This has been observed most often with the `upadhyay` VUMAT model.

**Fix:** `run_pipeline.py::run_abaqus()` doesn't currently set an MPI mode — if you hit this, edit the generated `submit.sh` to add `mp_mode=threads` to the `abaqus` command (switches to OpenMP threading, which doesn't need the network fabric) and resubmit with `qsub`:

```bash
abaqus job=... input=simulation.inp double=both cpus=$NSLOTS mp_mode=threads interactive
```

---

## 4. VUMAT fails to compile

**Symptom:** The job fails immediately with a Fortran compilation error, only when `material_model = "upadhyay"`.

**Cause:** The VUMAT (`vumat/vumat_O-USS_Model.f`) is compiled by Abaqus at submission time using an Intel Fortran compiler, loaded via the `intel_module` config field (default `"intel/2024.0"`). If that module doesn't exist on your cluster, or Abaqus isn't configured to find that compiler, the build fails before the solve even starts.

**Fix:** Confirm the module name in `intel_module` matches what's actually available on your cluster (`module avail intel`), and that your Abaqus installation is configured with a matching compiler (see your Abaqus installation's `abaqus_v6.env` or site config). See [HPC](../hpc.md).

---

## 5. Element distortion / negative Jacobian

**Error (in `.sta` or `.msg`):**
```
***ERROR: ELEMENT ... HAS NEGATIVE VOLUME/JACOBIAN
```
or the job runs but crashes partway through the simulation time, well before it was expected to.

**Cause:** Elements are deforming so severely that Abaqus can no longer compute a valid element formulation — usually a real physics problem, not a bug: material too soft for the loading rate, insufficient hourglass control, or (rarely) mesh quality issues from the automesh step.

**Fix:**
- Check `.sta` for the exact time and element/set where the crash occurs
- Cross-check whether the chosen `material_model`/`csf_model` combination has been validated at this loading rate — see [Material Models](../materials/README.md) for what's actually been tested
- Try reducing `dt_scale_factor` below `1.0` if the increment size looks like a factor (smaller time increments reduce per-step deformation)
- Whole-model energy history output (`ALLAE`/`ALLIE` in the `.odb`'s history region) can help distinguish a hyperglassing artifact from genuine large-strain failure

---

## 6. Job never appears to finish / stuck at a `.lck` file

**Symptom:** `{output_dir}/{subject_id}.odb` exists, but the run doesn't look complete.

**Cause:** Abaqus creates the `.odb` the moment the job starts solving, not when it finishes — its mere existence doesn't mean the job is done. A `{subject_id}.lck` file is present while Abaqus is actively running and is removed when it finishes (successfully or not).

**Fix:** Check for `{subject_id}.lck` — if present, the job is still running. Check `.sta` for `THE ANALYSIS HAS COMPLETED SUCCESSFULLY` once `.lck` is gone; if it's absent and `.lck` is gone too, the job ended without completing — check `.dat` and `.msg` for the actual error.
