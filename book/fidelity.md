# Brain Fidelity

Set via the segmentation filename (`brain_fidelity` is parsed from the `.npy` filename, not set directly in `[run]`) — see [Configuration Reference](configuration.md).

| `brain_fidelity` | Brain representation | Element sets |
|---|---|---|
| `homogeneous` | Single brain region | `EB1` (brain) |
| `heterogeneous` | Separate white matter / grey matter | `EB1` (WM), `EB2` (GM) |

CSF (`EB3`) and skull (`EB4`) are always present regardless of fidelity; membranes (`EB5`) are present only if `include_membranes` is true (see [Membranes](membranes.md)).

## Where this mapping comes from

`pipeline/preprocessing/mesh_schema.py::mesh_mapping()` assumes automesh names each mesh element block after the integer label value it came from in Autovalidate's segmentation (label `N` → element block `EBN`), and that Autovalidate's label schema is fixed: `wm=1, gm=2, csf=3, skull=4, membranes=5`. For a homogeneous segmentation, label 2 (GM) is simply absent from the `.npy`, so there's no `EB2` in the resulting mesh.

This is a hardcoded assumption shared between two separate repositories (autosim and Autovalidate) with no single shared source of truth — see [Keeping Autosim in Sync with Autovalidate](tutorials/sync_with_autovalidate.md) for what to check if that label schema ever changes.
