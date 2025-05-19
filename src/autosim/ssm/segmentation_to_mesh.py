"""This module converts a segmentation in .npy format to a mesh in either
.exo or .inp format.

Run:
python segmentation_to_mesh.py
"""

from pathlib import Path
import subprocess
import time
from typing import Final

import numpy as np

from center_of_geometry import (
    cli,
    CliCommand,
    center_of_geometry,
    Segmentation,
    segmentation_and_remove_ids,
)

# ----------------
# input file begin
# ----------------
# Reference:
#
# NPY_FILE: Final[Path] = Path(
#     "~/scratch/ixi/IXI012-HH-1211-T1_tiny.npy"
# ).expanduser()
AUTOMESH: Final[Path] = Path(
    "~/autotwin/automesh/target/release/automesh"
).expanduser()
MM_TO_M: Final[float] = 1e-3  # Convert mm to m
NPY_INPUT: Final[Path] = Path("~/scratch/ixi/input/").expanduser()
NPY_OUTPUT: Final[Path] = Path("~/scratch/ixi/output/").expanduser()
IGNORE_IDS: Final[list[int]] = [0, 1]
# REMOVES: Final[str] = " ".join([f"-r {id_}" for id_ in IGNORE_IDS])
REMOVES: Final[list] = [item for rem in IGNORE_IDS for item in ("-r", rem)]
TEST = False  # Perform a consistency validation against known data
# TEST = True  # Perform a consistency validation against known data
# ----------------
# input file end
# ----------------

start_time = time.time()  # start time

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
            segmentation_and_remove_ids(CliCommand(input_file=sp, remove=[0]))
        )

        EXPECTED_COG = known_cogs[ii]
        # check if the calculated cog matches the expected cog
        msg = f"expected {EXPECTED_COG}, got {cog}"
        assert np.allclose(cog, EXPECTED_COG), msg

    print("All tests passed.")

assert NPY_INPUT.is_dir(), f"Input folder {NPY_INPUT} not found."
assert NPY_OUTPUT.is_dir(), f"Output folder {NPY_OUTPUT} not found."

# Get the list of .npy files in the input directory
npy_files = list(NPY_INPUT.glob("*.npy"))
if not npy_files:
    raise FileNotFoundError(f"No .npy files found in {NPY_INPUT}.")

for npy_file in npy_files:
    aa: CliCommand = cli(input_file=npy_file, remove=IGNORE_IDS)

    bb: Segmentation = segmentation_and_remove_ids(aa)

    cc: np.ndarray = center_of_geometry(bb)

    output_file = NPY_OUTPUT.joinpath(npy_file.stem + ".inp")

    command = [
        str(AUTOMESH),
        "mesh",
        "hex",
        "-i",
        str(npy_file),
        "-o",
        str(output_file),
    ] 
    breakpoint()
    command += REMOVES

    breakpoint()

    print(f"Command: {command}")

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        print(result.stdout)  # output of the command
    else:
        print("automesh command failed:")
        print(result.stderr)  # error message

    breakpoint()

    print(f"Processed file: {npy_file}")
    print(f"  Center of Geometry: {cc}")


end_time = time.time()
delta_t = end_time - start_time
n_files = len(npy_files)
print(f"Processed {n_files} files in {delta_t:.6f} seconds")


# Visualization
# cd /Applications/Cubit-16.18
# ./cubit.command
# import abaqus "/Users/chovey/scratch/ixi/output/IXI012-HH-1211-T1_small.inp"
# view iso
# graphics clip on
# graphics clip on location 7.55 9.25 7.75 direction -1 0 0 # center point of the domain in a001.log
# graphics clip manipulation off