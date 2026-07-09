# CSF Material Models

Set via `csf_model` in your config. Two options:

| `csf_model` | Formulation | Source |
|---|---|---|
| `neo_hookean` | Neo-Hookean + Prony (CSF as a soft, nearly-incompressible viscoelastic solid) | Mao et al. 2013, DOI: [10.1115/1.4025101](https://doi.org/10.1115/1.4025101) |
| `fluid` | Mie-Gruneisen equation of state (CSF as an actual fluid) | Zhou, Li & Kleiven 2019, DOI: [10.1007/s10237-018-1074-z](https://doi.org/10.1007/s10237-018-1074-z) |

Both are genuinely independent papers' models, calibrated for different purposes — `neo_hookean` treats CSF as a soft solid (closer to how it behaves for small, fast motions), while `fluid` treats it as an actual fluid via a pressure-volume equation of state. Autovalidate's segmentation produces a single combined CSF label (it doesn't distinguish subarachnoid space from ventricles), so this is a choice of which single approximation to apply to that whole region — not a distinction the pipeline makes automatically.

## `fluid` implementation note

Abaqus's native `*EOS, TYPE=USUP` keyword only supports a linear Us-Up Hugoniot form (`c0`, `s`, `Γ0` — confirmed directly against the Abaqus Keywords Reference Manual). The source paper's equation of state is cubic (it has additional `S2`/`S3` curvature terms); those are dropped in this implementation since Abaqus has no keyword field for them. The linear terms used here match the paper's values exactly.

`csf_model` is a required field — there is no default.
