"""This module tests the center_of_geometry function with known data
from the letter_f.npy unit test of automesh.

To run:
pytest --cov=center_of_geometry --cov-report=term-missing test_center_of_geometry.py -v
"""

from pathlib import Path
from typing import Final

import numpy as np
import pytest

from center_of_geometry import (
    center_of_geometry,
    cli,
    CliTuple,
    segmentation_and_remove_ids,
    SegAndRemoveIDs,
)


# @pytest.fixture(scope="module", autouse=True)
# def load_segmentation():
#    """Fixture to load the segmentation data from letter_f.npy"""
#    segmentation_file = Path(__file__).parent / "letter_f.npy"
#
#    # Check if the file exists
#    if not segmentation_file.is_file():
#        raise FileNotFoundError(
#            f"Segmentation file {segmentation_file} not found."
#        )
#
#    # Load the segmentation data
#    segmentation = np.load(segmentation_file)
#    return segmentation


@pytest.fixture(scope="module", autouse=True)
def segmentation_file_fixture():
    """Fixture to the segmentation data from letter_f.npy"""
    segmentation_file = Path(__file__).parent / "letter_f.npy"

    # Check if the file exists
    if not segmentation_file.is_file():
        raise FileNotFoundError(
            f"Segmentation file {segmentation_file} not found."
        )

    return segmentation_file


def test_no_such_file():
    """Tests a non-existed file raises an error."""
    segmentation_file = Path(__file__).parent / "no_such_file.npy"

    msg = f"File {segmentation_file} not found."
    with pytest.raises(FileNotFoundError, match=msg):
        cli(segmentation_file, remove=[])


def test_invalid_file_type():
    """Tests an invalid file type raises an error."""
    segmentation_file = Path(__file__).parent / "letter_f.spn"

    msg = f"File {segmentation_file} must be a .npy file."
    with pytest.raises(ValueError, match=msg):
        cli(segmentation_file, remove=[])


def test_invalid_remove_ids():
    """Tests invalid remove IDs raise an error."""
    segmentation_file = Path(__file__).parent / "letter_f.npy"

    msg = "Remove IDs must be integers."
    with pytest.raises(ValueError, match=msg):
        cli(segmentation_file, remove=[-1, 2.5])

    msg = "Remove IDs must be non-negative."
    with pytest.raises(ValueError, match=msg):
        cli(segmentation_file, remove=[-1, 2])


def test_cli_valid_input(segmentation_file_fixture):
    """Tests the CLI function with valid input."""
    segmentation_file = Path(__file__).parent / "letter_f.npy"
    remove_ids = [0]

    # Call the CLI function
    cli_instance = cli(segmentation_file_fixture, remove=remove_ids)

    msg = "Instance is not of type CliTuple."
    assert isinstance(cli_instance, CliTuple), msg
    assert (
        cli_instance.input_file == segmentation_file
    ), f"Expected {segmentation_file}, got {cli_instance.input_file}"
    assert (
        cli_instance.remove == remove_ids
    ), f"Expected {remove_ids}, got {cli_instance.remove}"


def test_cli_with_no_remove_ids(segmentation_file_fixture):
    """Tests the CLI function with no remove IDs."""
    remove_ids = None

    # Call the CLI function
    cli_instance = CliTuple(segmentation_file_fixture, remove=remove_ids)

    yy = segmentation_and_remove_ids(cli_instance)

    assert isinstance(yy, SegAndRemoveIDs)
    assert yy.remove == []


def test_remove_all_ids(segmentation_file_fixture):
    """Tests that a ValueError is raised when all IDs are removed."""
    # Call the CLI function with all IDs removed
    remove_ids = [0, 11]
    with pytest.raises(ValueError):
        center_of_geometry(
            segmentation_and_remove_ids(
                CliTuple(segmentation_file_fixture, remove=remove_ids)
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
            CliTuple(segmentation_file_fixture, remove=[11])
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
            CliTuple(segmentation_file_fixture, remove=[0])
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
            CliTuple(segmentation_file_fixture, remove=[])
        )
    )

    # check if the calculated cog matches the expected cog
    msg = f"expected {EXPECTED_COG}, got {cog}"
    assert np.allclose(cog, EXPECTED_COG), msg
