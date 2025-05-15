"""This module reads a segmentation in .npy format and returns the center
of geometry of the segmented assembly, allowing for certain segmentation
IDs to be ignored.

To run:
source ~/automesh/autotwin/.venv/bin/activate
python ~/automesh/autowin/ssm/center_of_geometry.py \
    -i ~/automesh/autotwin/ssm/segmentation.npy \
    -r 0 1 2
"""

import argparse
from pathlib import Path

import numpy as np


def center_of_geometry(
    segmentation: np.ndarray, ignore_ids: list[int] | None
) -> np.ndarray:
    """Calculate the center of geometry of a segmented assembly.

    Args:
        segmentation (numpy.ndarray): The segmentation array.
        ignore_ids (list, optional): List of segmentation IDs to ignore.

    Returns:
        numpy.ndarray: The center of geometry coordinates.
    """
    if ignore_ids is None:
        ignore_ids = []

    # Get the unique IDs in the segmentation
    unique_ids = np.unique(segmentation)

    # Filter out the ignored IDs
    valid_ids = [ii for ii in unique_ids if ii not in ignore_ids]

    # Get the coordinates of the valid IDs
    indices = np.argwhere(np.isin(segmentation, valid_ids))

    # Calculate the center of geometry
    if indices.size == 0:
        raise ValueError("No valid IDs found in the segmentation.")

    # Account for the offset of the indices
    # which is +0.5 in each of the (x, y, z) directions
    indices_offset = indices + 0.5

    cog = np.mean(indices_offset, axis=0)

    return cog


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

    # Check if the input file exists
    input_path = Path(args.input)
    breakpoint()
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file {args.input} does not exist.")

    # Check if the input file is a .npy file
    if input_path.suffix != ".npy":
        raise ValueError("Input file must be a .npy file.")

    # Check if the remove IDs are valid
    if args.remove and not all(isinstance(i, int) for i in args.remove):
        raise ValueError("Remove IDs must be integers.")

    # Load the segmentation
    data = np.load(input_path)

    # Calculate the center of geometry
    center_of_geometry = center_of_geometry(data, args.remove)
    print(f"Center of Geometry: {center_of_geometry}")
