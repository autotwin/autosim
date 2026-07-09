# Brain Material Models

Set via `material_model` in your config. Five options:

| `material_model` | Formulation | Source |
|---|---|---|
| `alshareef` | Linear viscoelastic (LVE) | Alshareef et al. 2021, DOI: [10.1016/j.brain.2021.100038](https://doi.org/10.1016/j.brain.2021.100038) |
| `menichetti` | Neo-Hookean + Prony | Menichetti et al. 2020, DOI: [10.1016/j.ijengsci.2020.103355](https://doi.org/10.1016/j.ijengsci.2020.103355) |
| `basilio` | Ogden + Prony | Basilio et al. 2024, DOI: [10.1007/s10439-023-03407-7](https://doi.org/10.1007/s10439-023-03407-7) |
| `upadhyay` | Custom VUMAT (O-USS viscous dissipation model) | Upadhyay et al. 2022, DOI: [10.1098/rsif.2022.0561](https://doi.org/10.1098/rsif.2022.0561) |
| `custom` | Bring your own | — (see [Bring Your Own Material Model](../tutorials/custom_material.md)) |

## `alshareef` and homogeneous runs

`alshareef` is calibrated separately for white matter (Corona Radiata) and grey matter (Deep GM) in `pipeline/materials.py`'s `BRAIN_WM`/`BRAIN_GM` dictionaries. For a **homogeneous** run there's no separate WM/GM element set, so `alshareef` automatically falls back to a whole-brain average calibration (from the same paper's Table 3) instead of the WM-specific numbers — this happens internally in `get_materials()` and isn't something you configure.

## `upadhyay` and the VUMAT

`upadhyay` is the only model implemented as a compiled Abaqus VUMAT (Fortran, in `vumat/vumat_O-USS_Model.f`) rather than a native Abaqus material keyword. Selecting it automatically wires in the VUMAT path and requires an Intel compiler module at submission time — see [HPC](../hpc.md).

## `custom`

Selecting `custom` tells autosim you'll supply your own material card — see [Bring Your Own Material Model](../tutorials/custom_material.md).
