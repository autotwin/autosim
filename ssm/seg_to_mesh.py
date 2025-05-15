"""This module converts a segmentation in .npy format to a mesh in either
.exo or .inp format."""

from pathlib import Path
from typing import Final

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
# ----------------
# input file end
# ----------------

assert NPY_FILE.is_file(), f"Input file {NPY_FILE} not found."

cog = center_of_geometry(
    segmentation_and_remove_ids(
        CliTuple(input_file=NPY_FILE, remove=IGNORE_IDS)
    )
)

breakpoint()
aa = 4
