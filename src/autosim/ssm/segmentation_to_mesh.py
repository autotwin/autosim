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
# MESH_OUTPUT_TYPE = ".inp"
MESH_OUTPUT_TYPE = ".exo"
IGNORE_IDS: Final[list[int]] = [0]  # remove void
MM_TO_M: Final[float] = 1e-3  # Convert mm to m
NPY_INPUT: Final[Path] = Path("~/scratch/ixi/input/").expanduser()
NPY_OUTPUT: Final[Path] = Path("~/scratch/ixi/output/").expanduser()
REMOVES = [
    item
    for pair in zip(["-r"] * len(IGNORE_IDS), map(str, IGNORE_IDS))
    for item in pair
]
RESOLUTION: Final[dict] = {
    "tiny": 12.0 / 20.0,  # voxel/cm
    "small": 42.0 / 20.0,  # voxel/cm
    "medium": 80.0 / 20.0,  # voxel/cm
    "large": 150.0 / 20.0,  # voxel/cm
}
LENGTH_SCALE: Final[str] = "mm"  # mm, cm, m
METRICS: Final[bool] = True  # Calculate metrics
# METRICS: Final[bool] = False  # Calculate metrics
SCALING: Final[dict] = {
    "mm": 10.0,  # mm/cm
    "cm": 1.0,  # cm/cm
    "m": 0.01,  # m/cm
}
SMOOTHING: Final[bool] = True  # Smooth the mesh
# SMOOTHING: Final[bool] = False  # Smooth the mesh
SMOOTHING_ITERATIONS: Final[int] = 4  # Number of smoothing iterations
TEST = False  # Perform a consistency validation against known data
# TEST = True  # Perform a consistency validation against known data
# ----------------
# input file end
# ----------------

print("Resolution: pixels per cm")
for item in RESOLUTION:
    print(f"  {item}: {RESOLUTION[item]} voxel/cm")

print(f"Output length scale: {LENGTH_SCALE}")
# print("Scaling:")
# for item in RESOLUTION:
#     print(f"  {item}: {SCALING[LENGTH_SCALE] / RESOLUTION[item]}")
SCALES: Final[dict] = {
    "tiny": SCALING[LENGTH_SCALE] / RESOLUTION["tiny"],
    "small": SCALING[LENGTH_SCALE] / RESOLUTION["small"],
    "medium": SCALING[LENGTH_SCALE] / RESOLUTION["medium"],
    "large": SCALING[LENGTH_SCALE] / RESOLUTION["large"],
}
print("Scaling factors:")
for k, v in SCALES.items():
    print(f"  {k}: {v:.6f} {LENGTH_SCALE}/voxel")

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

start_time = time.time()  # start time

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

    print(f"Processing: {npy_file}")
    print(f"  Center of Geometry: {cc} voxel")

    output_file = NPY_OUTPUT.joinpath(npy_file.stem + MESH_OUTPUT_TYPE)

    command = [
        str(AUTOMESH),
        "mesh",
        "hex",
        "-i",
        str(npy_file),
        "-o",
        str(output_file),
    ]
    command += REMOVES

    if "tiny" in str(npy_file):
        scale = SCALES["tiny"]
    elif "small" in str(npy_file):
        scale = SCALES["small"]
    elif "medium" in str(npy_file):
        scale = SCALES["medium"]
    elif "large" in str(npy_file):
        scale = SCALES["large"]
    else:
        scale = 1.0

    if METRICS:
        output_file_csv = NPY_OUTPUT.joinpath(npy_file.stem + ".csv")
        command += ["--metrics", str(output_file_csv)]

    print(f"  Scale used for automesh: {scale} {LENGTH_SCALE}/voxel")
    sk = ["--xscale", "--yscale", "--zscale"]  # scale strings
    sv = [str(scale) for _ in sk]  # scale values
    ss = [item for pair in zip(sk, sv) for item in pair]  # scale list
    command += ss

    tk = ["--xtranslate", "--ytranslate", "--ztranslate"]  # translate strings
    tv = [str(-1.0 * scale * item) for item in cc]  # translate values
    tt = [item for pair in zip(tk, tv) for item in pair]  # translate list
    command += tt

    if SMOOTHING:
        command += [
            "smooth",
            "--hierarchical",
            "--iterations",
            str(SMOOTHING_ITERATIONS),
        ]

    print("Command:")
    print(" ".join(command))

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        print(result.stdout)  # output of the command
    else:
        print("automesh command failed:")
        print(result.stderr)  # error message


end_time = time.time()
delta_t = end_time - start_time
n_files = len(npy_files)
print("Done.")
print(f"Processed {n_files} files in {delta_t:.6f} seconds")


# Visualization
# cd /Applications/Cubit-16.18
# ./cubit.command
# import abaqus "/Users/chovey/scratch/ixi/output/IXI012-HH-1211-T1_small.inp"
# or
# import mesh "/Users/chovey/scratch/ixi/output/IXI012-HH-1211-T1_small.exo" lite
# view iso
# view up 0 0 1  # z-axis up
# view from 100 -100 100
# graphics scale on
# graphics clip on
# graphics clip on location 7.55 9.25 7.75 direction -1 0 0 # center point of the domain in a001.log
# graphics clip manipulation off
# block 1 visibility off
