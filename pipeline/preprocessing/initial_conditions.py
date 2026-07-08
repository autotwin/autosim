# Line 2 of ROTATING VELOCITY data: [vx, vy, vz, omega_x, omega_y, omega_z]
# For pure rotation about one axis, only that component of omega is non-zero.
_OMEGA_VEC = {
    4: lambda w: f"{w:.10e}, 0., 0., 0., 0., 0.",
    5: lambda w: f"0., {w:.10e}, 0., 0., 0., 0.",
    6: lambda w: f"0., 0., 0., 0., 0., {w:.10e}",
}


def format_rotating_velocity_lines(nsets: list, omega_0: float, ref_dof: int) -> list:
    """
    Generates *INITIAL CONDITIONS, TYPE=ROTATING VELOCITY lines.
    Applies v = omega_0 x r to all nodes in each nset.

    Abaqus requires two data lines per entry:
      Line 1: nset, omega_magnitude, blank, blank, blank
      Line 2: vx, vy, vz, omega_x, omega_y, omega_z

    Args:
        nsets : Nset names (e.g. ["ALLNODES"])
        omega_0 : Initial angular speed (rad/s)
        ref_dof : Rotational DOF (4=X, 5=Y, 6=Z)
    """
    if ref_dof not in _OMEGA_VEC:
        raise ValueError(f"ref_dof must be 4, 5, or 6; got {ref_dof}")
    omega_vec = _OMEGA_VEC[ref_dof](omega_0)
    lines = ["** Initial rotating velocity: all nodes"]
    for nset in nsets:
        lines += [
            "*INITIAL CONDITIONS, TYPE=ROTATING VELOCITY",
            f"{nset}, {omega_0:.10e},  ,  ,  ,",
            f"{omega_vec},",
        ]
    return lines


def format_ref_node_line(ref_node_id, ref_dof, omega_0) -> list:
    """
    Creates the *INITIAL CONDITIONS, TYPE=VELOCITY line for the reference node's
    rotational DOF.

    Args:
        ref_node_id : Reference Node ID
        ref_dof : Rotational DOF (4, 5, or 6)
        omega_0 : Initial angular velocity (rad/s)
    """
    if ref_dof not in (4, 5, 6):
        raise ValueError(
            "Use appropriate value for rotational DOF. "
            "If X axis: DOF=4, if Y axis: DOF=5, if Z axis: DOF=6"
        )
    return [f"{ref_node_id:d}, {ref_dof}, {omega_0:.8e}"]
