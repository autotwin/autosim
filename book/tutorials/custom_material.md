# Bring Your Own Material Model

`material_model = "custom"` is accepted by config validation, but out of the box it's a placeholder, not a working material. `BRAIN_WM["custom"]` and `BRAIN_GM["custom"]` are both `None` in `pipeline/materials.py`, and `format_material()` raises immediately when it hits `None`:

```
ValueError: No material parameters defined for 'BRAIN'. For custom models, provide your own material card.
```

This tutorial shows how to actually supply parameters for a one-off material without editing `materials.py` (see [Add a New Material to the Catalog](new_catalog_material.md) instead if you want to contribute a permanent, citable addition).

## Option 1 — reuse an existing formulation

If your material fits one of the five existing parameter dataclasses (`NeoHookeanPronyParams`, `OgdenPronyParams`, `LVEParams`, `ElasticParams`, `VUMATParams`), you can populate the catalog's `"custom"` slot at runtime before calling the pipeline:

```python
from pipeline.materials import BRAIN_WM, BRAIN_GM, LVEParams
from pipeline.config import parse_config
from run_pipeline import run_pipeline
import tomllib

my_material = LVEParams(density=1.04e-9, G0=8.0e-3, nu=0.49, prony=[(0.7, 1.0e-3)])

BRAIN_WM["custom"] = my_material
BRAIN_GM["custom"] = my_material   # only needed if brain_fidelity = heterogeneous

with open("my_config.toml", "rb") as f:
    cfg = parse_config(tomllib.load(f))   # material_model = "custom" in the TOML

run_pipeline(cfg)
```

`get_materials()` will now find a real dataclass instance instead of `None`, and `format_material()`'s existing dispatch handles the rest — no changes to `materials.py` or `inp_builder.py` needed.

## Option 2 — a formulation not in the catalog

If your material needs an Abaqus keyword none of the five formatters produce, you need a new dataclass and formatter, exactly as described in [Add a New Material to the Catalog](new_catalog_material.md) — the only difference is you assign the result to `BRAIN_WM["custom"]` at runtime (as above) instead of giving it a permanent name in the catalog.

## Note

There is currently no `csf_model = "custom"` equivalent — the CSF axis only accepts `neo_hookean` or `fluid`.
