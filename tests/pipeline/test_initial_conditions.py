import pytest

from pipeline.io.inp_reader import parse_mesh_lines
from pipeline.preprocessing.initial_conditions import (
    format_rotating_velocity_lines,
    format_ref_node_line,
)


NODES = [
    "*NODE\n",
    "1, 10.0, 20.0, 30.0\n",
    "2,  5.0,  6.0,  7.0\n",
    "3, 15.0, 25.0, 35.0\n",
    "4,  0.0,  2.0,  3.0\n",
    "5,  1.0,  1.0,  1.0\n",
    "6,  2.0,  2.0,  2.0\n",
    "7,  3.0,  3.0,  3.0\n",
    "8,  4.0,  4.0,  4.0\n",
    "9,  5.0,  5.0,  5.0\n",
    "10, 6.0,  6.0,  6.0\n",
]

EB1_LINES = ["*ELEMENT, ELSET=EB1\n", "100, 1, 2\n"]
EB2_LINES = ["*ELEMENT, ELSET=EB2\n", "200, 3, 4\n"]
EB3_LINES = ["*ELEMENT, ELSET=EB3\n", "300, 5, 6\n"]
EB4_LINES = ["*ELEMENT, ELSET=EB4\n", "400, 7, 8\n"]
EB5_LINES = ["*ELEMENT, ELSET=EB5\n", "500, 9, 10\n"]


# ── parse_mesh_lines tests (inp_reader, kept here for coverage) ───────────────

def test_parse_mesh_lines_skull_excluded_hom_memOFF():
    dummy_input = NODES + EB1_LINES + EB3_LINES + EB4_LINES
    node_coords, brain_csf_nodes = parse_mesh_lines(dummy_input, "homogeneous", False)
    assert node_coords[1] == (10.0, 20.0, 30.0)
    assert brain_csf_nodes == {1, 2, 5, 6}


def test_parse_mesh_lines_skull_excluded_hom_memON():
    dummy_input = NODES + EB1_LINES + EB3_LINES + EB4_LINES + EB5_LINES
    node_coords, brain_csf_nodes = parse_mesh_lines(dummy_input, "homogeneous", True)
    assert brain_csf_nodes == {1, 2, 5, 6, 9, 10}


def test_parse_mesh_lines_skull_excluded_het_memOFF():
    dummy_input = NODES + EB1_LINES + EB2_LINES + EB3_LINES + EB4_LINES
    node_coords, brain_csf_nodes = parse_mesh_lines(dummy_input, "heterogeneous", False)
    assert brain_csf_nodes == {1, 2, 3, 4, 5, 6}


def test_parse_mesh_lines_skull_excluded_het_memON():
    dummy_input = NODES + EB1_LINES + EB2_LINES + EB3_LINES + EB4_LINES + EB5_LINES
    node_coords, brain_csf_nodes = parse_mesh_lines(dummy_input, "heterogeneous", True)
    assert brain_csf_nodes == {1, 2, 3, 4, 5, 6, 9, 10}


def test_parse_mesh_lines_nodes_parsed():
    dummy_input = NODES + EB1_LINES
    node_coords, _ = parse_mesh_lines(dummy_input, "homogeneous", False)
    assert node_coords[1] == (10.0, 20.0, 30.0)
    assert node_coords[3] == (15.0, 25.0, 35.0)


def test_parse_mesh_lines_unknown_elset_ignored():
    dummy_input = NODES + ["*ELEMENT, ELSET=EB99\n", "999, 1, 2\n"]
    node_coords, brain_csf_nodes = parse_mesh_lines(dummy_input, "homogeneous", False)
    assert node_coords[1] == (10.0, 20.0, 30.0)
    assert brain_csf_nodes == set()


# ── format_rotating_velocity_lines tests ─────────────────────────────────────

def test_rotating_velocity_contains_keyword():
    lines = format_rotating_velocity_lines(["EB1_NODES", "EB3_NODES"], 3.5, 6)
    combined = "\n".join(lines)
    assert "*INITIAL CONDITIONS, TYPE=ROTATING VELOCITY" in combined


def test_rotating_velocity_all_nsets_present():
    nsets = ["EB1_NODES", "EB2_NODES", "EB3_NODES", "EB5_NODES"]
    lines = format_rotating_velocity_lines(nsets, 3.5, 6)
    combined = "\n".join(lines)
    for nset in nsets:
        assert nset in combined


def test_rotating_velocity_separate_block_per_nset():
    lines = format_rotating_velocity_lines(["EB1_NODES", "EB3_NODES"], 3.5, 6)
    combined = "\n".join(lines)
    assert combined.count("*INITIAL CONDITIONS, TYPE=ROTATING VELOCITY") == 2


def test_rotating_velocity_no_nset_definitions():
    lines = format_rotating_velocity_lines(["ALLNODES"], 3.5, 6)
    combined = "\n".join(lines)
    assert "*NSET" not in combined


def test_rotating_velocity_two_data_lines_per_nset():
    """Each nset block must have exactly 2 data lines (Abaqus requirement)."""
    lines = format_rotating_velocity_lines(["ALLNODES"], 2.0, 6)
    kw_idx = [i for i, l in enumerate(lines) if "*INITIAL CONDITIONS" in l][0]
    data_lines = [l for l in lines[kw_idx + 1:] if not l.startswith("*") and not l.startswith("**")]
    assert len(data_lines) == 2


def test_rotating_velocity_z_axis_dof6():
    lines = format_rotating_velocity_lines(["ALLNODES"], 2.0, 6)
    omega_line = [l for l in lines if "2." in l and not l.startswith("*") and not l.startswith("ALLNODES")][0]
    assert omega_line.startswith("0., 0., 0., 0., 0.,")


def test_rotating_velocity_x_axis_dof4():
    lines = format_rotating_velocity_lines(["ALLNODES"], 2.0, 4)
    omega_line = [l for l in lines if "2." in l and not l.startswith("*") and not l.startswith("ALLNODES")][0]
    assert omega_line.startswith("2.")


def test_rotating_velocity_y_axis_dof5():
    lines = format_rotating_velocity_lines(["ALLNODES"], 2.0, 5)
    omega_line = [l for l in lines if "2." in l and not l.startswith("*") and not l.startswith("ALLNODES")][0]
    assert omega_line.startswith("0.,")
    assert "2." in omega_line.split(",")[1]


def test_rotating_velocity_omega_in_data_line():
    lines = format_rotating_velocity_lines(["ALLNODES"], 3.417835, 6)
    combined = "\n".join(lines)
    assert "3.417835" in combined


def test_rotating_velocity_invalid_dof_raises():
    with pytest.raises(ValueError):
        format_rotating_velocity_lines(["EB1_NODES"], 2.0, 7)


# ── format_ref_node_line tests ────────────────────────────────────────────────

def test_format_ref_node_line_correct_input():
    formatted_line = format_ref_node_line(99999999, 6, 13.05)
    assert len(formatted_line) == 1
    assert formatted_line[0] == "99999999, 6, 1.30500000e+01"


def test_format_ref_node_line_wrong_input():
    with pytest.raises(ValueError):
        format_ref_node_line(99999999, 7, 13.05)
