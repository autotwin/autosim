def format_assembly_lines(elset_to_material: dict, skull_elset: str, ref_node_id: int) -> list:

    """
    Creates the assembly block that must appear after the mesh *INCLUDE:
    reference node, REFNODE nset, skull rigid body, and solid section assignments.

    Args:
        elset_to_material : Dict mapping elset name to Abaqus material name
                            e.g. {"EB1": "BRAIN", "EB2": "CSF", "EB3": "SKULL"}
        skull_elset : Element set name for the skull rigid body (e.g. "EB3")
        ref_node_id : Rigid body reference node ID (e.g. 9999999)

    Returns:
        A list of formatted .inp lines
    """

    lines = [
        "** --- Rigid body reference node (skull) ---",
        "*NODE",
        f"{ref_node_id},  0.0,  0.0,  0.0",
        "**",
        "*NSET, NSET=REFNODE",
        f"{ref_node_id},",
        "**",
        f"** --- Skull rigid body ---",
        f"*RIGID BODY, ELSET={skull_elset}, REF NODE={ref_node_id}",
        "**",
        "** --- Section assignments ---",
    ]

    for elset, material_name in elset_to_material.items():
        lines.append(f"*SOLID SECTION, ELSET={elset}, MATERIAL={material_name}")
        lines.append(",")

    lines += [
        "**",
        "** --- Tissue node sets (for nodal output requests) ---",
    ]

    for elset, material_name in elset_to_material.items():
        if elset == skull_elset:
            continue
        nset_name = f"{material_name}_NODES"
        lines.append(f"*NSET, NSET={nset_name}, ELSET={elset}")

    lines.append("**")
    return lines


def format_output_field_lines(time_interval_step: float, elsets: list[str], nsets: list[str] | None = None) -> list:

    """
    Creates the lines for the output field for the simulation.inp ready to be used from the writer.
    Generates one *ELEMENT OUTPUT block per element set.

    Args:
        time_interval_step : Time step at which results are saved
        elsets : List of element set names to request field output for (e.g. ["EB1", "EB2"])

    Returns:
        A list of formatted .inp lines
    """

    lines = [
        "** --- Output requests ---",
        "**",
        f"** Field output: strain tensor every {time_interval_step * 1000} ms",
        f"*OUTPUT, FIELD, TIME INTERVAL={time_interval_step:.4f}",
    ]

    for elset in elsets:
        lines.append(f"*ELEMENT OUTPUT, ELSET={elset}")
        lines.append("LE, S, EVOL, COORD, ENER")

    if nsets:
        for nset in nsets:
            lines.append(f"*NODE OUTPUT, NSET={nset}")
            lines.append("U,")

    lines += [
        "**",
        "** History output: reference node kinematics only",
        f"*OUTPUT, HISTORY, TIME INTERVAL={time_interval_step:.4f}",
        "*NODE OUTPUT, NSET=REFNODE",
        "U, V, UR, A, AR",
        "**",
        "** History output: whole-model energy (hourglass/artificial energy check)",
        f"*OUTPUT, HISTORY, TIME INTERVAL={time_interval_step:.4f}",
        "*ENERGY OUTPUT",
        "ALLAE, ALLIE, ALLKE, ALLVD, ALLWK",
        "**",
    ]

    return lines


def format_elastic_material_lines(part_name, density, young_modulus, nu) -> list:

    """
    Creates the lines for the elastic materials for the simulation.inp
    ready to be used from the writer

    Args:
        part_name : Part name that will have this material properties
        density : Material Density
        young_modulus : Material Young Modulus
        nu : Poisson Ratio
    
    """

    line0 = f"*MATERIAL, NAME={part_name}"
    line1 = "*DENSITY"
    line2 = f"{density:.6e}"
    line3 = "*ELASTIC"
    line4 = f"{young_modulus:.6e},  {nu}"
    line5 = "**"

    formatted_lines = [line0, line1, line2, line3, line4, line5]

    return formatted_lines


def format_neo_hookean_prony_material_lines(part_name, density, C10, D1, prony, moduli="INSTANTANEOUS") -> list:

    """
    Creates lines for a Neo-Hookean + Prony series material.

    Args:
        part_name : Material name
        density : Density (tonne/mm³)
        C10 : Neo-Hookean parameter (MPa)
        D1 : Compressibility parameter (MPa⁻¹)
        prony : [(g1, tau1), ...] — normalised shear relaxation pairs
    """

    lines = [
        f"*MATERIAL, NAME={part_name}",
        "*DENSITY",
        f"{density:.6e}",
        f"*HYPERELASTIC, NEO HOOKE, MODULI={moduli}",
        f"{C10:.6e},  {D1:.6e}",
        "** Normalised Prony series: (g_i, k_i=0, tau_i[s])",
        "*VISCOELASTIC, TIME=PRONY",
    ]
    for g, tau in prony:
        lines.append(f"{g:.4f},  0.0000,  {tau:.6e}")
    lines.append("**")

    return lines


def format_ogden_prony_material_lines(part_name, density, mu, alpha, D1, prony) -> list:

    """
    Creates lines for an Ogden N=1 + Prony series material.

    Args:
        part_name : Material name
        density : Density (tonne/mm³)
        mu : Abaqus Ogden mu (MPa)
        alpha : Ogden nonlinearity (dimensionless)
        D1 : Compressibility parameter (MPa^-1)
        prony : [(g1, tau1), ...] — normalised shear relaxation pairs
    """

    lines = [
        f"*MATERIAL, NAME={part_name}",
        "*DENSITY",
        f"{density:.6e}",
        "** Ogden N=1 + Prony series viscoelasticity",
        "*HYPERELASTIC, OGDEN, N=1, MODULI=INSTANTANEOUS",
        f"{mu:.6e},  {alpha:.4f},  {D1:.6e}",
        "** Normalised Prony series: (g_i, k_i=0, tau_i[s])",
        "*VISCOELASTIC, TIME=PRONY",
    ]
    for g, tau in prony:
        lines.append(f"{g:.4f},  0.0000,  {tau:.6e}")
    lines.append("**")

    return lines


def format_lve_material_lines(part_name, density, G0, nu, prony) -> list:

    """
    Creates lines for a Linear Viscoelastic material (*ELASTIC + Prony series).

    Args:
        part_name : Material name
        density : Density (tonne/mm^3)
        G0 : Instantaneous shear modulus (MPa)
        nu : Poisson's ratio
        prony : [(g1, tau1), ...] — normalised shear relaxation pairs
    """

    E = 2.0 * G0 * (1.0 + nu)

    lines = [
        f"*MATERIAL, NAME={part_name}",
        "*DENSITY",
        f"{density:.6e}",
        "** Linear Viscoelastic: E = 2*G0*(1+nu)",
        "*ELASTIC",
        f"{E:.6e},  {nu}",
        "** Normalised Prony series: (g_i, k_i=0, tau_i[s])",
        "*VISCOELASTIC, TIME=PRONY",
    ]
    for g, tau in prony:
        lines.append(f"{g:.4f},  0.0000,  {tau:.6e}")
    lines.append("**")

    return lines


def format_vumat_material_lines(part_name, density, mu_inf, Kbulk, alpha, k11, k21, c21) -> list:

    """
    Creates lines for the O-USS VUMAT material (Upadhyay et al. 2022).

    Args:
        part_name : Material name
        density : Density (tonne/mm³)
        mu_inf : Long-term shear modulus / Ginf (MPa)
        Kbulk : Bulk modulus (MPa)
        alpha : Ogden nonlinearity (dimensionless)
        k11 : Viscous parameter 1 (MPa·s)
        k21 : Viscous parameter 2 (MPa·s)
        c21 : Viscous nonlinearity (dimensionless)
    """

    lines = [
        f"*MATERIAL, NAME={part_name}",
        "*DENSITY",
        f"{density:.6e}",
        "** O-USS VUMAT: Upadhyay et al. 2022, DOI: 10.1098/rsif.2022.0561",
        "** Props: Ginf[MPa], Kbulk[MPa], alpha, k11[MPa·s], k21[MPa·s], c21",
        "*USER MATERIAL, CONSTANTS=6",
        f"{mu_inf:.6e},  {Kbulk:.6e},  {alpha:.4f},  {k11:.6e},  {k21:.6e},  {c21:.4f}",
        "*DEPVAR",
        "1",
        "**",
    ]

    return lines


def format_gruneisen_eos_material_lines(part_name, density, c0, s, gamma0, mu) -> list:

    """
    Creates lines for a Mie-Gruneisen EOS fluid material (e.g. CSF) via
    Abaqus *EOS, TYPE=USUP.

    Args:
        part_name : Material name
        density : Reference density (tonne/mm³)
        c0 : Reference speed of sound (mm/s)
        s : Linear Hugoniot slope coefficient (dimensionless)
        gamma0 : Gruneisen ratio at reference state (dimensionless)
        mu : Dynamic viscosity (MPa·s)
    """

    lines = [
        f"*MATERIAL, NAME={part_name}",
        "*DENSITY",
        f"{density:.6e}",
        "*EOS, TYPE=USUP",
        f"{c0:.6e},  {s:.4f},  {gamma0:.4f}",
        "*VISCOSITY",
        f"{mu:.6e}",
        "**",
    ]

    return lines


def format_time_points_lines(abaqus_times: list, name: str = "COMP_FRAMES") -> list:

    """
    Creates a *TIME POINTS block listing the exact Abaqus times at which
    field/nodal output will be saved (one per comparison frame).

    Args:
        abaqus_times : List of floats — Abaqus times in seconds
        name : Time-points set name used in the OUTPUT request

    Returns:
        A list of formatted .inp lines
    """

    lines = [f"*TIME POINTS, NAME={name}"]
    chunks = [abaqus_times[i:i + 8] for i in range(0, len(abaqus_times), 8)]
    for chunk in chunks:
        lines.append(", ".join(f"{t:.6f}" for t in chunk) + ",")
    return lines


def format_nodal_field_output_lines(nsets: list, timepoints_name: str = "COMP_FRAMES") -> list:

    """
    Creates *OUTPUT, FIELD + one *NODE OUTPUT block per nset, all gated
    to the named TIME POINTS set so only comparison-frame snapshots are saved.

    Args:
        nsets : List of node-set names (e.g. ["BRAIN_NODES", "CSF_NODES"])
        timepoints_name : Name of the *TIME POINTS set to reference

    Returns:
        A list of formatted .inp lines
    """

    lines = [
        "** --- Nodal displacement output at comparison frames only ---",
        f"*OUTPUT, FIELD, TIME POINTS={timepoints_name}",
    ]

    for nset in nsets:
        lines.append(f"*NODE OUTPUT, NSET={nset}")
        lines.append("U,")

    lines.append("**")
    return lines


def format_step_lines(simulation_time, boundary_lines, output_field_lines,
                      pre_step_lines=None, dt_scale_factor: float = 1.0) -> list:

    """
    Creates the lines for the step case for the simulation.inp
    ready to be used from the writer

    Args:
        simulation_time : Total simulation time
        boundary_lines : Formatted Boundary Conditions lines
        output_field_lines : Formatted Output Field Request Lines
        pre_step_lines : Lines to place before *Step (e.g. *TIME POINTS — model-level keyword)
    """

    line0 = "** STEP: Step-1"
    line1 = "** Define an explicit dynamic step with nonlinear geometry enabled."
    line2 = "**"
    line3 = "*Step, name=Step-1, nlgeom=YES"
    line4 = "** Enable nonlinear geometry (large deformation effects)."
    line5 = "** ORIGINAL CODE: Dynamic, Explicit"
    line6 = "**Dynamic, Explicit, scale factor=0.1"
    if dt_scale_factor != 1.0:
        line7 = f"*Dynamic, Explicit, scale factor={dt_scale_factor}"
    else:
        line7 = "*Dynamic, Explicit"
    line8 = f"0.0, {simulation_time}"
    line9 = "** Run this explicit step for 0.08 seconds total time."
    line10 = "*Bulk Viscosity"
    line11 = "0.06, 1.2"
    line12 = "** 0.1, 2.0"
    line13 = "** TYPICAL: 0.06, 1.2"
    line14 = "** Add numerical bulk viscosity to suppress spurious high-frequency oscillations."
    line15 = "** These are standard damping parameters for explicit simulations."
    
    pre = list(pre_step_lines) if pre_step_lines else []

    lines = [line0, line1, line2, line3, line4, line5,
             line6, line7, line8, line9, line2, line10,
             line11, line12, line13, line14, line15, line2]

    end_line = ["*End Step"]

    return pre + lines + boundary_lines + output_field_lines + end_line