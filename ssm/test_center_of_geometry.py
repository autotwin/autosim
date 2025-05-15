"""This module tests the center_of_geometry function with known data
from the letter_f.npy unit test of automesh."""

from pathlib import Path
from typing import Final

import numpy as np
import pytest

from center_of_geometry import center_of_geometry


@pytest.fixture(scope="module", autouse=True)
def load_segmentation():
    """Fixture to load the segmentation data from letter_f.npy"""
    segmentation_file = Path(__file__).parent / "letter_f.npy"

    # Check if the file exists
    if not segmentation_file.is_file():
        raise FileNotFoundError(
            f"Segmentation file {segmentation_file} not found."
        )

    # Load the segmentation data
    segmentation = np.load(segmentation_file)
    return segmentation


def test_fill_volume_1(load_segmentation):
    """Test the center_of_geometry function with known data from the
    void fill (ID=0) of letter_f.npy."""

    # define the expected center of geometry
    EXPECTED_COG: Final[np.ndarray] = np.array([2.071429, 1.928571, 0.5])

    # call the center_of_geometry function
    cog = center_of_geometry(load_segmentation, ignore_ids=[11])

    # check if the calculated cog matches the expected cog
    msg = f"expected {EXPECTED_COG}, got {cog}"
    assert np.allclose(cog, EXPECTED_COG), msg


def test_material_volume_2(load_segmentation):
    """Test the center_of_geometry function with known data from the
    material (ID=11) of letter_f.npy."""

    # define the expected center of geometry
    EXPECTED_COG: Final[np.ndarray] = np.array([1.0, 3.0, 0.5])

    # call the center_of_geometry function
    cog = center_of_geometry(load_segmentation, ignore_ids=[0])

    # check if the calculated cog matches the expected cog
    msg = f"expected {EXPECTED_COG}, got {cog}"
    assert np.allclose(cog, EXPECTED_COG), msg


def test_center_assembly(load_segmentation):
    """test the center_of_geometry function with known data."""

    # define the expected center of geometry
    EXPECTED_COG: Final[np.ndarray] = np.array([1.5, 2.5, 0.5])

    # call the center_of_geometry function
    cog = center_of_geometry(load_segmentation, ignore_ids=[])

    # check if the calculated cog matches the expected cog
    msg = f"expected {EXPECTED_COG}, got {cog}"
    assert np.allclose(cog, EXPECTED_COG), msg
