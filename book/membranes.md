# Membranes

Set via the segmentation filename (`include_membranes` is parsed from the `.npy` filename's `membranesON`/`membranesOFF` suffix — see [Configuration Reference](configuration.md)).

When enabled, the falx cerebri and tentorium cerebelli are meshed as a separate element set (`EB5`) and assigned a fixed linear elastic material (`MEMBRANE_MATERIAL` in `pipeline/materials.py`, Alshareef et al. 2021, DOI: [10.1016/j.brain.2021.100038](https://doi.org/10.1016/j.brain.2021.100038)). This isn't configurable per run — membranes always use the same material regardless of which `material_model` you selected for the brain.

If your Autovalidate output doesn't include membranes (`membranesOFF` in the filename), autosim simply omits `EB5` and the membrane material entirely — no extra configuration needed.
