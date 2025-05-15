"""This module converts a segmentation in .npy format to a mesh in either
.exo or .inp format."""

from pathlib import Path
from typing import Final

import numpy as np

from center_of_geometry import (
    center_of_geometry,
    CliTuple,
    segmentation_and_remove_ids,
)

# ----------------
# input file begin
# ----------------
NPY_FILE: Final[Path] = Path(
    "~/scratch/ixi/IXI012-HH-1211-T1_tiny.npy"
).expanduser()
IGNORE_IDS: Final[list[int]] = [0]
# TEST = False  # Perform a consistency validation against known data
TEST = True  # Perform a consistency validation against known data
# ----------------
# input file end
# ----------------

if TEST:
    folder = Path(
        "~/autotwin/automesh/book/analysis/sphere_with_shells"
    ).expanduser()
    sp1 = folder.joinpath("spheres_resolution_1.npy")
    sp2 = folder.joinpath("spheres_resolution_2.npy")
    sp3 = folder.joinpath("spheres_resolution_3.npy")
    sp4 = folder.joinpath("spheres_resolution_4.npy")
    assert folder.is_dir(), f"Input folder {folder} not found."

    known_cogs = (
        (12.0, 12.0, 12.0),
        (24.0, 24.0, 24.0),
        (48.0, 48.0, 48.0),
        (120.0, 120.0, 120.0),
    )

    for ii, sp in enumerate([sp1, sp2, sp3, sp4]):
        assert sp.is_file(), f"Input file {sp} not found."
        cog = center_of_geometry(
            segmentation_and_remove_ids(CliTuple(input_file=sp, remove=[0]))
        )

        EXPECTED_COG = known_cogs[ii]
        # check if the calculated cog matches the expected cog
        msg = f"expected {EXPECTED_COG}, got {cog}"
        assert np.allclose(cog, EXPECTED_COG), msg


assert NPY_FILE.is_file(), f"Input file {NPY_FILE} not found."

cog = center_of_geometry(
    segmentation_and_remove_ids(
        CliTuple(input_file=NPY_FILE, remove=IGNORE_IDS)
    )
)

breakpoint()
aa = 4
