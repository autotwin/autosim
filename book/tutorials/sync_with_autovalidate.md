# Keeping Autosim in Sync with Autovalidate

autosim and Autovalidate are separate repositories, but they share an assumption that isn't enforced by any shared code: the integer label schema in the segmentation `.npy` file.

## Where the coupling actually lives

Autovalidate's `combine_labels.py::_assign_labels()` hardcodes label values into the combined mask:

```python
labels[wm.astype(bool)] = 1
labels[gm.astype(bool)] = 2
labels[csf.astype(bool)] = 3
labels[skull.astype(bool)] = 4
labels[membranes.astype(bool)] = 5
```

autosim's `pipeline/preprocessing/mesh_schema.py::mesh_mapping()` independently hardcodes the *same* assumption, plus one more: that automesh preserves each label value as its mesh element block number (label `N` → `EBN`):

```python
label_mapping = {
    "wm":        "EB1",
    "gm":        "EB2" if brain_fidelity == "heterogeneous" else None,
    "csf":       "EB3",
    "skull":     "EB4",
    "membranes": "EB5" if include_membranes else None,
}
```

There is no shared constant, schema file, or test that ties these two together. If Autovalidate's label scheme changes and autosim isn't updated to match, **there is no error at import or config time** — meshing will succeed, but the wrong material will silently land on the wrong element set (e.g. brain material assigned to what's actually skull elements).

## Checklist: Autovalidate adds a new region (e.g. cerebellum as label 6)

1. **`mesh_schema.py::mesh_mapping()`** — add the new key and its `EBN` mapping, following the existing pattern (decide whether it's always present or conditional, like `gm`/`membranes` are).
2. **`materials.py`** — decide whether the new region needs its own material catalog (a new `BRAIN_CEREBELLUM`-style dict, or an entry in an existing one) and whether every `material_model` needs a value for it, or whether it can safely reuse an existing tissue's material.
3. **`get_materials()`** — wire the new tissue into the returned dict, matching the key naming `mesh_schema.py` expects (`run_pipeline.py::generate_inp()` derives `elset_to_material`, `elsets`, and `comparison_nsets` directly from whatever keys `get_materials()` and `mesh_mapping()` return — as long as both are updated consistently, `generate_inp()` itself shouldn't need changes).
4. **Tests** — add coverage in `tests/pipeline/test_mesh_schema.py` and `tests/pipeline/test_materials.py` for the new region, and a `test_run_pipeline.py` case if it changes the generated `.inp` structure.
5. **This book** — update [Brain Fidelity](../fidelity.md) and the material catalog pages to document the new region.

## Checklist: Autovalidate adds a new fidelity level (e.g. `"detailed"`)

`mesh_mapping()`'s `brain_fidelity` parameter only branches on `"heterogeneous"` today (anything else falls through to the homogeneous branch) — a new level needs an explicit branch, not just a new string value flowing through. Also check `get_materials()` in `materials.py`, which branches on `config.brain_fidelity == "homogeneous"` the same way.

## The honest summary

This coupling works today because both repos happen to agree, not because anything enforces it. If you're touching either repo's labeling scheme, grep the other repo for the label integers you're about to change before assuming it's safe.
