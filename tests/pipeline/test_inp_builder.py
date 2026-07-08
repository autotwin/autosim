import numpy as np
import pytest

from pipeline.preprocessing.boundary_conditions import format_boundary_conditions_lines
from pipeline.preprocessing.inp_builder import (
    format_output_field_lines,
    format_elastic_material_lines,
    format_step_lines,
    format_neo_hookean_prony_material_lines,
    format_ogden_prony_material_lines,
    format_lve_material_lines,
    format_vumat_material_lines,
    format_gruneisen_eos_material_lines,
    format_assembly_lines,
    format_time_points_lines,
    format_nodal_field_output_lines,
)

def test_format_gruneisen_eos_material_lines():
    lines = format_gruneisen_eos_material_lines("CSF", 1.0e-9, 1.4829e6, 2.1057, 1.2, 1.0e-9)

    assert lines[0] == "*MATERIAL, NAME=CSF"
    assert "*EOS, TYPE=USUP" in lines
    assert "*VISCOSITY" in lines

    eos_idx  = lines.index("*EOS, TYPE=USUP")
    visc_idx = lines.index("*VISCOSITY")

    assert lines[eos_idx + 1] == "1.482900e+06,  2.1057,  1.2000"
    assert lines[visc_idx + 1] == "1.000000e-09"


def test_format_boundary_conditions_lines():
    lines = format_boundary_conditions_lines(99999999, 5)
    combined = "\n".join(lines)
    assert "*BOUNDARY, TYPE=VELOCITY, AMPLITUDE=AMP-1" in combined
    assert "99999999, 5, 5, 1.0" in combined
    assert ", 1, 1," not in combined
    assert ", 3, 3," not in combined
    


def test_format_output_field_lines_homogeneous():
    # hom+memOFF: EB1=brain, EB2=CSF
    lines = format_output_field_lines(0.002, ["EB1", "EB2"])

    assert lines[3] == "*OUTPUT, FIELD, TIME INTERVAL=0.0020"
    assert lines[4] == "*ELEMENT OUTPUT, ELSET=EB1"
    assert lines[5] == "LE, S, EVOL, COORD, ENER"
    assert lines[6] == "*ELEMENT OUTPUT, ELSET=EB2"
    assert lines[7] == "LE, S, EVOL, COORD, ENER"
    assert lines[-1] == "**"


def test_format_output_field_lines_heterogeneous():
    # het+memOFF: EB1=WM, EB2=GM, EB3=CSF
    lines = format_output_field_lines(0.002, ["EB1", "EB2", "EB3"])

    assert lines[3] == "*OUTPUT, FIELD, TIME INTERVAL=0.0020"
    assert lines[4] == "*ELEMENT OUTPUT, ELSET=EB1"
    assert lines[5] == "LE, S, EVOL, COORD, ENER"
    assert lines[6] == "*ELEMENT OUTPUT, ELSET=EB2"
    assert lines[8] == "*ELEMENT OUTPUT, ELSET=EB3"
    assert "*NODE OUTPUT, NSET=REFNODE" in lines
    assert "U, V, UR, A, AR" in lines


def test_format_output_field_lines_with_nsets():
    lines = format_output_field_lines(0.002, ["EB1", "EB3"], nsets=["BRAIN_NODES", "CSF_NODES"])

    assert "*ELEMENT OUTPUT, ELSET=EB1" in lines
    assert "*ELEMENT OUTPUT, ELSET=EB3" in lines
    assert "*NODE OUTPUT, NSET=BRAIN_NODES" in lines
    assert "*NODE OUTPUT, NSET=CSF_NODES" in lines
    assert "U," in lines


def test_format_elastic_material_lines():

    part_name = "SKULL"
    density = 2.07e-9         
    young_modulus = 3280.0         
    nu = 0.3

    lines = format_elastic_material_lines(part_name, density, young_modulus, nu)

    assert lines[0] == "*MATERIAL, NAME=SKULL"
    assert lines[2] == "2.070000e-09"
    assert lines[4] == "3.280000e+03,  0.3"


def test_format_neo_hookean_prony_material_lines():

    lines = format_neo_hookean_prony_material_lines(
        "BRAIN", 1.04e-9, 3.815e-3, 3.11e-2, [(0.57, 0.020), (0.22, 0.31)]
    )

    assert lines[0] == "*MATERIAL, NAME=BRAIN"
    assert lines[2] == "1.040000e-09"
    assert lines[3] == "*HYPERELASTIC, NEO HOOKE, MODULI=INSTANTANEOUS"
    assert lines[4] == "3.815000e-03,  3.110000e-02"
    assert lines[7] == "0.5700,  0.0000,  2.000000e-02"
    assert lines[8] == "0.2200,  0.0000,  3.100000e-01"


def test_format_ogden_prony_material_lines():

    lines = format_ogden_prony_material_lines(
        "BRAIN", 1.04e-9, -9.453e-5, -25.39, 9.13e-4, [(0.758, 14.85)]
    )

    assert lines[0] == "*MATERIAL, NAME=BRAIN"
    assert lines[4] == "*HYPERELASTIC, OGDEN, N=1, MODULI=INSTANTANEOUS"
    assert lines[5] == "-9.453000e-05,  -25.3900,  9.130000e-04"
    assert lines[8] == "0.7580,  0.0000,  1.485000e+01"


def test_format_lve_material_lines():

    # E = 2*G0*(1+nu) = 2*9.2e-3*1.49 = 2.741600e-02
    lines = format_lve_material_lines("BRAIN", 1.04e-9, 9.2e-3, 0.49, [(0.76, 9.0e-4)])

    assert lines[0] == "*MATERIAL, NAME=BRAIN"
    assert lines[4] == "*ELASTIC"
    assert lines[5] == "2.741600e-02,  0.49"
    assert lines[8] == "0.7600,  0.0000,  9.000000e-04"


def test_format_vumat_material_lines():
    # Kbulk=2190 — original upadhyay params
    lines = format_vumat_material_lines(
        "BRAIN", 1.04e-9, 1.84e-3, 2190.0, -3.47, -2.65e-6, 6.0969e-4, 0.62
    )

    assert lines[0] == "*MATERIAL, NAME=BRAIN"
    assert lines[2] == "1.040000e-09"
    assert "*ELASTIC" not in lines  # forbidden alongside *USER MATERIAL in Abaqus/Explicit
    assert "*USER MATERIAL, CONSTANTS=6" in lines
    assert "1.840000e-03,  2.190000e+03,  -3.4700,  -2.650000e-06,  6.096900e-04,  0.6200" in lines
    assert "*DEPVAR" in lines
    assert "1" in lines


def test_format_vumat_material_lines_no_elastic_for_updated_kbulk():
    # *ELASTIC must not appear regardless of Kbulk value
    lines = format_vumat_material_lines(
        "BRAIN", 1.04e-9, 1.84e-3, 0.49, -3.47, -2.65e-6, 6.0969e-4, 0.62
    )

    assert "*ELASTIC" not in lines
    assert "*USER MATERIAL, CONSTANTS=6" in lines


def test_format_assembly_lines_hom_memOFF():
    # hom+memOFF: EB1=brain(1), EB3=CSF(3), EB4=skull(4)
    elset_to_material = {"EB1": "BRAIN", "EB3": "CSF", "EB4": "SKULL"}

    lines = format_assembly_lines(elset_to_material, skull_elset="EB4", ref_node_id=9999999)

    assert "*NODE" in lines
    assert "9999999,  0.0,  0.0,  0.0" in lines
    assert "*NSET, NSET=REFNODE" in lines
    assert "9999999," in lines
    assert "*RIGID BODY, ELSET=EB4, REF NODE=9999999" in lines
    assert "*SOLID SECTION, ELSET=EB1, MATERIAL=BRAIN" in lines
    assert "*SOLID SECTION, ELSET=EB3, MATERIAL=CSF" in lines
    assert "*SOLID SECTION, ELSET=EB4, MATERIAL=SKULL" in lines
    # tissue node sets — used for nodal output requests (skull excluded)
    assert "*NSET, NSET=BRAIN_NODES, ELSET=EB1" in lines
    assert "*NSET, NSET=CSF_NODES, ELSET=EB3" in lines
    assert "*NSET, NSET=SKULL_NODES, ELSET=EB4" not in lines


def test_format_assembly_lines_hom_memON():
    # hom+memON: EB1=brain(1), EB3=CSF(3), EB4=skull(4), EB5=membranes(5)
    elset_to_material = {"EB1": "BRAIN", "EB3": "CSF", "EB4": "SKULL", "EB5": "MEMBRANES"}

    lines = format_assembly_lines(elset_to_material, skull_elset="EB4", ref_node_id=9999999)

    assert "*SOLID SECTION, ELSET=EB5, MATERIAL=MEMBRANES" in lines
    assert "*RIGID BODY, ELSET=EB4, REF NODE=9999999" in lines


def test_format_assembly_lines_het_memOFF():
    elset_to_material = {"EB1": "WM", "EB2": "GM", "EB3": "CSF", "EB4": "SKULL"}

    lines = format_assembly_lines(elset_to_material, skull_elset="EB4", ref_node_id=9999999)

    assert "*SOLID SECTION, ELSET=EB1, MATERIAL=WM" in lines
    assert "*SOLID SECTION, ELSET=EB2, MATERIAL=GM" in lines
    assert "*RIGID BODY, ELSET=EB4, REF NODE=9999999" in lines


def test_format_step_lines():

    simulation_time = 0.198
    boundary_lines = ["This is formatted", "Boundary Conditions text"]
    output_field_lines = ["Formatted Output Field Text", "Can be found in this line"]

    formatted_lines = format_step_lines(simulation_time, boundary_lines, output_field_lines)

    assert formatted_lines[8] == "0.0, 0.198"
    assert formatted_lines[19] == "Boundary Conditions text"
    assert formatted_lines[20] == "Formatted Output Field Text"
    assert formatted_lines[-1] == "*End Step"


def test_format_step_lines_dt_scale_factor():
    lines = format_step_lines(0.198, [], [], dt_scale_factor=0.5)
    dynamic_line = next(l for l in lines if l.startswith("*Dynamic, Explicit"))
    assert "scale factor=0.5" in dynamic_line


def test_format_step_lines_pre_step_lines_before_step_keyword():
    pre_step_lines = ["*TIME POINTS, NAME=COMP_FRAMES", "0.009000, 0.027000,"]

    formatted_lines = format_step_lines(0.198, [], [], pre_step_lines=pre_step_lines)

    step_idx = formatted_lines.index("*Step, name=Step-1, nlgeom=YES")
    tp_idx = formatted_lines.index("*TIME POINTS, NAME=COMP_FRAMES")
    assert tp_idx < step_idx


def test_format_time_points_lines():
    abaqus_times = [0.009, 0.027, 0.045, 0.063]

    lines = format_time_points_lines(abaqus_times)

    assert lines[0] == "*TIME POINTS, NAME=COMP_FRAMES"
    assert "0.009000" in lines[1]
    assert "0.027000" in lines[1]
    assert "0.045000" in lines[1]
    assert "0.063000" in lines[1]


def test_format_time_points_lines_splits_at_8():

    abaqus_times = [0.009 * (i + 1) for i in range(11)]

    lines = format_time_points_lines(abaqus_times)

    assert lines[0] == "*TIME POINTS, NAME=COMP_FRAMES"
    assert len(lines) == 3 
    assert lines[1].count(",") == 8 
    assert "0.099000" in lines[2]


def test_format_nodal_field_output_lines():
    nsets = ["BRAIN_NODES", "CSF_NODES"]

    lines = format_nodal_field_output_lines(nsets)

    assert "*OUTPUT, FIELD, TIME POINTS=COMP_FRAMES" in lines
    assert "*NODE OUTPUT, NSET=BRAIN_NODES" in lines
    assert "U," in lines
    assert "*NODE OUTPUT, NSET=CSF_NODES" in lines