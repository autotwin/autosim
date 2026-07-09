# Material Models

autosim assigns material properties along two independent axes, chosen per run in your config:

- **`material_model`** — the constitutive model for brain tissue (white matter / grey matter)
- **`csf_model`** — the constitutive model for CSF

Skull and membranes (falx/tentorium) are fixed, linear elastic materials — not user-selectable.

See [Brain](brain.md) and [CSF](csf.md) for the available options and their sources.

## Homogeneous vs. heterogeneous

When `brain_fidelity = "homogeneous"`, the whole brain is one region and uses a single calibration. When `brain_fidelity = "heterogeneous"`, white matter and grey matter are separate element sets with separate, region-specific calibrations. Not every model distinguishes WM from GM the same way — see [Brain Fidelity](../fidelity.md) for how this interacts with the mesh.
