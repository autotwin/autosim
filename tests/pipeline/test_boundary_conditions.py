import pytest
from pipeline.preprocessing.boundary_conditions import format_boundary_conditions_lines


def test_bc_contains_amplitude_keyword():
    lines = format_boundary_conditions_lines(9999999, 6)
    combined = "\n".join(lines)
    assert "AMPLITUDE=AMP-1" in combined


def test_bc_prescribes_only_ref_dof():
    lines = format_boundary_conditions_lines(9999999, 6)
    combined = "\n".join(lines)
    assert "9999999, 6, 6, 1.0" in combined


def test_bc_no_translation_constraints():
    lines = format_boundary_conditions_lines(9999999, 6)
    combined = "\n".join(lines)
    assert ", 1, 1," not in combined
    assert ", 2, 2," not in combined
    assert ", 3, 3," not in combined


def test_bc_no_off_axis_rotation_constraints_dof6():
    lines = format_boundary_conditions_lines(9999999, 6)
    combined = "\n".join(lines)
    assert ", 4, 4," not in combined
    assert ", 5, 5," not in combined


def test_bc_no_off_axis_rotation_constraints_dof4():
    lines = format_boundary_conditions_lines(9999999, 4)
    combined = "\n".join(lines)
    assert ", 5, 5," not in combined
    assert ", 6, 6," not in combined


def test_bc_ref_dof4():
    lines = format_boundary_conditions_lines(9999999, 4)
    combined = "\n".join(lines)
    assert "9999999, 4, 4, 1.0" in combined


def test_bc_ref_dof5():
    lines = format_boundary_conditions_lines(9999999, 5)
    combined = "\n".join(lines)
    assert "9999999, 5, 5, 1.0" in combined
