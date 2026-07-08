def mesh_mapping(brain_fidelity: str, include_membranes: bool) -> dict:

    """
    Maps brain fidelity and membrane flag to Abaqus element set names.

    Args:
        brain_fidelity : "homogeneous" or "heterogeneous"
        include_membranes : Whether falx/tentorium membranes are included

    Returns:
        A dict with keys "wm", "gm", "csf", "skull", "membranes" mapping
        to element set name strings (e.g. "EB1") or None if not present
    """

    # automesh names each block after its label value: label N → EBN.
    # Autovalidate_New label schema: wm=1, gm=2, csf=3, skull=4, membranes=5.
    # For homogeneous, label 2 (gm) is absent from the .npy → no EB2 in the mesh.
    label_mapping = {
        "wm" : "EB1",
        "gm" : "EB2" if brain_fidelity == "heterogeneous" else None,
        "csf" : "EB3",
        "skull" : "EB4",
        "membranes" : "EB5" if include_membranes else None,
    }

    return label_mapping