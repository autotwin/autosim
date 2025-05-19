"""This module reads a segmentation in .npy format and returns the center
of geometry of the segmented assembly, allowing for certain segmentation
IDs to be ignored.

To run:
source ~/automesh/autosim/.venv/bin/activate
python ~/automesh/autosim/ssm/center_of_geometry.py \
    -i ~/automesh/autosim/ssm/letter_f.npy \
    -r 0

To test:
pytest --cov --cov-report=term-missing

References:
https://autotwin.github.io/automesh/examples/unit_tests/index.html#letter-f
"""

import argparse
from pathlib import Path
from typing import List, NamedTuple

import numpy as np


class CliCommand(NamedTuple):
    """A full command line with arguments, equilvalent to what the user would
    enter in the command line."""

    input_file: Path
    remove: List[int] | None


class Segmentation(NamedTuple):
    """Valid segmentation and valid remove IDs structure."""

    segmentation: np.ndarray
    remove: List[int]  # a list of non-negative integers, possibly empty


def center_of_geometry(xx: Segmentation) -> np.ndarray:
    """Calculate the center of geometry of a segmented assembly.

    Args:
        segmentation (numpy.ndarray): The segmentation array.
        ignore_ids (list): List of segmentation IDs to ignore, possibly
            and empty list for cases where all IDs are valid.

    Returns:
        numpy.ndarray: The center of geometry coordinates.
    """
    # Get the unique IDs in the segmentation
    unique_ids = np.unique(xx.segmentation)

    # Filter out the removed IDs
    included_ids = [ii for ii in unique_ids if ii not in xx.remove]

    # Get the coordinates of the valid IDs
    indices = np.argwhere(np.isin(xx.segmentation, included_ids))

    # Calculate the center of geometry
    if indices.size == 0:
        msg = "Segmentation does not include valid IDs."
        msg += f" Valid IDs: {included_ids}, remove IDs: {xx.remove}"
        raise ValueError(msg)

    # Get the coordinates of the valid IDs
    indices = np.argwhere(np.isin(xx.segmentation, included_ids))

    # Account for the offset of the indices
    # which is +0.5 in each of the (x, y, z) directions
    indices_offset = indices + 0.5

    cog = np.mean(indices_offset, axis=0)

    return cog


def segmentation_and_remove_ids(xx: CliCommand) -> Segmentation:
    """Load the segmentation and ignore IDs from the command line
    interface.

    Args:
        xx: The command line interface
            structure.

    Returns:
        SegWithRemoveIDs: The segmentation and ignore IDs structure.
    """

    # Load the segmentation
    segmentation = np.load(xx.input_file)

    # Get the ignore IDs
    remove = xx.remove

    if remove is None:
        remove = []  # overwrite with empty list

    return Segmentation(segmentation=segmentation, remove=remove)


def cli(input_file: Path, remove: list[int]) -> CliCommand:
    """Convert command line arguments to a command line interface structure.

    Args:
        input_file (Path): The path to the segmentation file.
        remove (list[int]): List of non-negative segmentation IDs to ignore.

    Returns:
        An instance of the CliCommand NamedTuple.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If the input file is not a .npy file or if remove IDs
            are invalid.
    """

    # Input file must exist
    if not input_file.is_file():
        raise FileNotFoundError(f"File {input_file} not found.")

    # Input must be a .npy file
    if input_file.suffix != ".npy":
        raise ValueError(f"File {input_file} must be a .npy file.")

    # Remove IDs must be integers
    if remove and not all(isinstance(i, int) for i in remove):
        raise ValueError("Remove IDs must be integers.")

    # Remove IDs must be non-negative integers
    if remove and not all(i >= 0 for i in remove):
        raise ValueError("Remove IDs must be non-negative.")

    # Create the cli structure
    yy = CliCommand(input_file=input_file, remove=remove)

    # Return the structure
    return yy


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate the center of geometry of a segmented assembly."
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help="Path to the segmentation file in .npy format.",
    )
    parser.add_argument(
        "-r",
        "--remove",
        required=False,
        type=int,
        nargs="*",
        # nargs="+",
        default=[],
        help="List of segmentation IDs to ignore.",
    )
    args = parser.parse_args()

    aa: CliCommand = cli(
        input_file=Path(args.input),
        remove=args.remove,
    )
    bb: Segmentation = segmentation_and_remove_ids(aa)
    # Calculate the center of geometry
    cc: np.ndarray = center_of_geometry(bb)
    print(f"Center of Geometry: {cc}")
