def format_boundary_conditions_lines(ref_node_id, ref_dof) -> list:
    """
    Creates boundary condition lines for the rigid body reference node.
    Only the prescribed rotational DOF is constrained.
    Translations and off-axis rotations are left free.

    Args:
        ref_node_id : Reference Node ID
        ref_dof : Rotational DOF to prescribe (4=X, 5=Y, 6=Z)
    """
    return [
        "** --- Boundary conditions on rigid body reference node ---",
        "**",
        "*BOUNDARY, TYPE=VELOCITY, AMPLITUDE=AMP-1",
        f"{ref_node_id}, {ref_dof}, {ref_dof}, 1.0",
        "**",
    ]
