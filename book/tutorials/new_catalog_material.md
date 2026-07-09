# Add a New Material to the Catalog

This shows how to permanently add a paper-sourced brain material to autosim's catalog, so it becomes a normal, citable, `valid_models`-listed choice for every user — not a one-off override (see [Bring Your Own Material Model](custom_material.md) for that instead). We'll add a fictional example, **Smith et al. 2025**, using the existing linear viscoelastic (LVE) formulation.

Adding a material requires changes in three places.

## Step 1 — Add the parameters to `pipeline/materials.py`

If the paper's formulation matches an existing dataclass (`NeoHookeanPronyParams`, `OgdenPronyParams`, `LVEParams`, `ElasticParams`, `VUMATParams`), add entries to `BRAIN_WM` and `BRAIN_GM`:

```python
"smith": LVEParams(
    # Smith et al. 2025
    # DOI: 10.xxxx/xxxxx
    density = 1.04e-9,
    G0 = 7.5e-3,
    nu = 0.49,
    prony = [(0.70, 1.2e-3), (0.10, 25.0e-3)]
),
```

Comments on catalog entries are kept to just the citing paper + DOI — no derivation notes or unit-conversion commentary (see the existing entries for the convention).

If a homogeneous whole-brain calibration differs from the heterogeneous WM number (as with `alshareef`/`alshareef_hom`), add a second, internal-only entry and wire the substitution into `get_materials()` — see that function's `wm_key` logic for the existing example. Otherwise, homogeneous runs will just reuse the WM entry directly.

If the formulation doesn't match any existing dataclass, you'll also need a new `@dataclass` and a new `format_*_material_lines()` function in `pipeline/preprocessing/inp_builder.py` that emits the correct Abaqus keyword — follow the pattern of the existing formatters, and verify the exact Abaqus keyword data-line order against the actual Keywords Reference Manual before trusting it (a paraphrased summary cost real debugging time once already — see the CSF fluid model's implementation history for why).

## Step 2 — Register the name in `pipeline/config.py`

Add `"smith"` to `valid_models` in `parse_config()`:

```python
valid_models = {
    "basilio", "menichetti", "alshareef", "upadhyay", "smith", "custom"
}
```

Update the error message listing valid choices too.

## Step 3 — Write tests

Add assertions to `tests/pipeline/test_materials.py` following the existing pattern — at minimum:

- A `get_materials()` test confirming your model's parameters come back correctly for both homogeneous and heterogeneous fidelity
- A `format_material()` test confirming the right Abaqus keyword appears in the output lines

Run the suite:

```bash
pytest tests/
```

## Step 4 — Use it

```toml
material_model = "smith"
```
