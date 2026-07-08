from pipeline.preprocessing.mesh_schema import mesh_mapping


def parse_mesh_lines(input_lines, brain_fidelity: str, include_membranes: bool):

    """
    Takes the mesh input file as a list of lines and returns the node coords
    and node IDs for all non-skull element sets.

    Args:
        input_lines : Mesh file as a list of lines
        brain_fidelity : "homogeneous" or "heterogeneous"
        include_membranes : Whether falx/tentorium membranes are included

    Returns:
        node_coords : dict {node_id (int): (x, y, z) (float)}
        brain_csf_nodes : set of int — union of all non-skull element set nodes
    """

    schema = mesh_mapping(brain_fidelity, include_membranes)
    skull_set = schema["skull"]
    collect_sets = {v for k, v in schema.items() if k != "skull" and v is not None}

    node_coords = {}
    brain_csf_nodes = set()

    STATE_NONE = 0
    STATE_NODES = 1
    STATE_ELEM_COLLECT = 2

    state = STATE_NONE

    for line in input_lines:
        if line.startswith("**"):
            continue
        if line.startswith("*NODE"):
            state = STATE_NODES
            continue
        if line.startswith("*ELEMENT"):
            elset = None
            for part in line.split():
                if "ELSET=" in part:
                    elset = part.split("=")[1].strip()
            state = STATE_ELEM_COLLECT if elset in collect_sets else STATE_NONE
            continue
        if line.startswith("*"):
            state = STATE_NONE
            continue

        if state == STATE_NODES:
            parts = line.split(",")
            if len(parts) < 4:
                continue
            nid = int(parts[0].strip())
            x   = float(parts[1].strip())
            y   = float(parts[2].strip())
            z   = float(parts[3].strip())
            node_coords[nid] = (x, y, z)

        elif state == STATE_ELEM_COLLECT:
            parts = line.split(",")
            if len(parts) < 2:
                continue
            for p in parts[1:]:
                p = p.strip()
                if p:
                    brain_csf_nodes.add(int(p))

    return node_coords, brain_csf_nodes
