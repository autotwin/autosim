from pathlib import Path

def write_text_file(output_dir: Path, formatted_text: list, ):

    """
    Creates a file at the designated path which will contain the formatted text

    Args:
        output_dir : Path which the file will be saved
        formatted_text : The list containing the formatted text that will be saved in this file
    """

    with open(output_dir, 'w') as f:
        f.write("\n".join(formatted_text) + "\n")
    

def write_initial_conditions_file(output_dir: Path, rotating_velocity_lines: list, ref_node_line: list):
    """
    Writes initial_conditions.inp using *INITIAL CONDITIONS, TYPE=ROTATING VELOCITY
    for all deformable nsets, plus a TYPE=VELOCITY line for the reference node's
    rotational DOF.

    Args:
        output_dir : Path to write the file
        rotating_velocity_lines : Lines from format_rotating_velocity_lines()
        ref_node_line : Line from format_ref_node_line()
    """
    lines = (
        rotating_velocity_lines
        + ["**", "*INITIAL CONDITIONS, TYPE=VELOCITY"]
        + ref_node_line
    )
    write_text_file(output_dir, lines)


def write_simulation_inp(output_path, mesh_inp, assembly_inp, loads_inp,
                         initial_conditions_inp, material_files: dict, step_inp):

    """
    Creates the master simulation.inp using *INCLUDE directives.

    Args:
        output_path : Path to write simulation.inp
        mesh_inp : Path to the subject-specific mesh file
        assembly_inp : Path to the assembly block (ref node, rigid body, sections)
        loads_inp : Path to the loads amplitude file
        initial_conditions_inp : Path to the initial conditions file
        material_files : Dict mapping tissue name to material .inp file path
        step_inp : Path to the step file
    """

    lines = [
        "** ============================================================",
        "** Abaqus Explicit — Subject-specific brain biomechanics model",
        "**",
        "** Unit system: mm | tonne | s | N | MPa",
        "**   Length   : mm",
        "**   Time     : s",
        "**   Mass     : tonne",
        "**   Force    : N",
        "**   Stress   : MPa (= N/mm²)",
        "**   Density  : tonne/mm³",
        "** ============================================================",
        f"*INCLUDE, INPUT={mesh_inp}",
        f"*INCLUDE, INPUT={assembly_inp}",
        f"*INCLUDE, INPUT={loads_inp}",
        f"*INCLUDE, INPUT={initial_conditions_inp}",
    ]

    for path in material_files.values():
        lines.append(f"*INCLUDE, INPUT={path}")

    lines.append(f"*INCLUDE, INPUT={step_inp}")

    with open(output_path, 'w') as f:
        f.write("\n".join(lines))