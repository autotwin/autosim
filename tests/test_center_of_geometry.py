"""This module tests the center_of_geometry function with known data
from the letter_f.npy unit test of automesh.

To run:
pytest
pytest --cov --cov-report=term-missing
"""

from pathlib import Path
from typing import Final

import numpy as np
import pytest

from autosim.ssm.center_of_geometry import (
    center_of_geometry,
    cli,
    CliCommand,
    segmentation_and_remove_ids,
    Segmentation,
)


@pytest.fixture(scope="module", autouse=True)
def segmentation_file_fixture():
    """Fixture to the segmentation data from letter_f.npy"""
    # segmentation_file = Path(__file__).parent / "letter_f.npy"
    segmentation_file = Path(__file__).parent.joinpath("input", "letter_f.npy")

    # Check if the file exists
    if not segmentation_file.is_file():
        raise FileNotFoundError(
            f"Segmentation file {segmentation_file} not found."
        )

    return segmentation_file


def test_no_such_file():
    """Tests a non-existed file raises an error."""
    segmentation_file = Path(__file__).parent.joinpath(
        "input", "no_such_file.npy"
    )

    msg = f"File {segmentation_file} not found."
    with pytest.raises(FileNotFoundError, match=msg):
        cli(segmentation_file, remove=[])


def test_invalid_file_type():
    """Tests an invalid file type raises an error."""
    segmentation_file = Path(__file__).parent.joinpath("input", "letter_f.spn")

    msg = f"File {segmentation_file} must be a .npy file."
    with pytest.raises(ValueError, match=msg):
        cli(segmentation_file, remove=[])


def test_invalid_remove_ids(segmentation_file_fixture):
    """Tests invalid remove IDs raise an error."""
    msg = "Remove IDs must be integers."
    with pytest.raises(ValueError, match=msg):
        cli(segmentation_file_fixture, remove=[-1, 2.5])

    msg = "Remove IDs must be non-negative."
    with pytest.raises(ValueError, match=msg):
        cli(segmentation_file_fixture, remove=[-1, 2])


def test_cli_valid_input(segmentation_file_fixture):
    """Tests the CLI function with valid input from the fixture."""
    # segmentation_file = Path(__file__).parent / "letter_f.npy"
    gold_segmentation_file = Path(__file__).parent.joinpath(
        "input", "letter_f.npy"
    )
    gold_remove_ids = [0]

    # Call the CLI function
    cli_command = cli(
        input_file=segmentation_file_fixture, remove=gold_remove_ids
    )

    msg = "Instance is not of type CliCommand."
    assert isinstance(cli_command, CliCommand), msg
    assert cli_command.input_file == gold_segmentation_file, (
        f"Expected {gold_segmentation_file}, got {cli_command.input_file}"
    )
    assert cli_command.remove == gold_remove_ids, (
        f"Expected {gold_remove_ids}, got {cli_command.remove}"
    )


def test_cli_with_no_remove_ids(segmentation_file_fixture):
    """Tests the CLI function with no remove IDs."""
    remove_ids = None

    # Call the CLI function
    cli_instance = CliCommand(segmentation_file_fixture, remove=remove_ids)

    yy = segmentation_and_remove_ids(cli_instance)

    assert isinstance(yy, Segmentation)
    assert yy.remove == []


def test_remove_all_ids(segmentation_file_fixture):
    """Tests that a ValueError is raised when all IDs are removed."""
    # Call the CLI function with all IDs removed
    remove_ids = [0, 11]
    with pytest.raises(ValueError):
        center_of_geometry(
            segmentation_and_remove_ids(
                CliCommand(segmentation_file_fixture, remove=remove_ids)
            )
        )


def test_fill_volume_1(segmentation_file_fixture):
    """Test the center_of_geometry function with known data from the
    void fill (ID=0) of letter_f.npy."""

    # define the expected center of geometry
    EXPECTED_COG: Final[np.ndarray] = np.array([2.071429, 1.928571, 0.5])

    # call the center_of_geometry function
    cog = center_of_geometry(
        segmentation_and_remove_ids(
            CliCommand(segmentation_file_fixture, remove=[11])
        )
    )

    # check if the calculated cog matches the expected cog
    msg = f"expected {EXPECTED_COG}, got {cog}"
    assert np.allclose(cog, EXPECTED_COG), msg


def test_material_volume_2(segmentation_file_fixture):
    """Test the center_of_geometry function with known data from the
    material (ID=11) of letter_f.npy."""

    # define the expected center of geometry
    EXPECTED_COG: Final[np.ndarray] = np.array([1.0, 3.0, 0.5])

    # call the center_of_geometry function
    cog = center_of_geometry(
        segmentation_and_remove_ids(
            CliCommand(segmentation_file_fixture, remove=[0])
        )
    )

    # check if the calculated cog matches the expected cog
    msg = f"expected {EXPECTED_COG}, got {cog}"
    assert np.allclose(cog, EXPECTED_COG), msg


def test_center_assembly(segmentation_file_fixture):
    """test the center_of_geometry function with known data."""

    # define the expected center of geometry
    EXPECTED_COG: Final[np.ndarray] = np.array([1.5, 2.5, 0.5])

    # call the center_of_geometry function
    cog = center_of_geometry(
        segmentation_and_remove_ids(
            CliCommand(segmentation_file_fixture, remove=[])
        )
    )

    # check if the calculated cog matches the expected cog
    msg = f"expected {EXPECTED_COG}, got {cog}"
    assert np.allclose(cog, EXPECTED_COG), msg
