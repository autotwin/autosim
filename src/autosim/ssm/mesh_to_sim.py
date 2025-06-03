"""This module operates on mesh files in .exo format in preparation for
simulation with SSM.

Run:
source ~/autotwin/autosim/.venv/bin/activate
python src/autosim/ssm/mesh_to_sim.py
"""

from pathlib import Path
import subprocess
import time
from typing import NamedTuple, Final


class Input(NamedTuple):
    """Input class for the mesh_to_sim.py script."""

    input_folder: str
    decomp_folder: str
    n_processors: int  # Number of processors for decomp
    hpc_run: bool = False  # Run on HPC or not


# -------------------
# user settings begin
# -------------------
input_Chad = Input(
    input_folder="~/scratch/ixi/exo/",
    decomp_folder="~/scratch/ixi/decomp/",
    n_processors=160,  # Number of processors for decomp
)
# -----------------
# user settings end
# -----------------
start_time = time.time()
ii = input_Chad

# Harvest constants from user input
EXO_FOLDER: Final[Path] = Path(ii.input_folder).expanduser()
DECOMP_FOLDER: Final[Path] = Path(ii.decomp_folder).expanduser()
N_PROCESSORS: Final[int] = ii.n_processors
HPC_RUN: Final[bool] = ii.hpc_run

# Create output folder if it doesn't exist
if not DECOMP_FOLDER.exists():
    DECOMP_FOLDER.mkdir(parents=True, exist_ok=True)

# Harvest all .exo files in the input folder
exo_files = list(EXO_FOLDER.glob("*.exo"))
if not exo_files:
    raise ValueError(f"No .exo files found in {EXO_FOLDER}")

print(f"Found {len(exo_files)} .exo files in {EXO_FOLDER}")

print(f"Input folder: {EXO_FOLDER}")
print(f"Decomp folder: {DECOMP_FOLDER}")

print(f"Number of processors: {N_PROCESSORS}")
print(f"Running on HPC: {HPC_RUN}")

# If on the HPC, run the decomp command for each .exo file
if HPC_RUN:
    # Load modules
    print("Loading modules...")
    module_commands = [
        [
            "module",
            "purge",
        ],
        [
            "module",
            "load",
            "sierra",
        ],
        [
            "module",
            "load",
            "seacase",
        ],
    ]

    for module_command in module_commands:
        # Print the command being run
        print(f"Running command: {' '.join(module_command)}")

        # Run the command
        subprocess.run(module_command, check=True)

    for exo_file in exo_files:
        # Create a subfolder in the decomp folder for each .exo file
        # decomp_subfolder = DECOMP_FOLDER.joinpath(exo_file.stem)
        decomp_subfolder = DECOMP_FOLDER / exo_file.stem
        decomp_subfolder.mkdir(parents=True, exist_ok=True)
        print(f"Processing {exo_file}...")
        print(f"Decomp subfolder: {decomp_subfolder}")

        # Construct the decomp command
        decomp_command = [
            "decomp",
            "--processors",
            str(exo_file),
            str(N_PROCESSORS),
            str(DECOMP_FOLDER / exo_file.stem),
        ]

        # Print the command being run
        print(f"Running command: {' '.join(decomp_command)}")

        # Run the command
        subprocess.run(decomp_command, check=True)

end_time = time.time()
delta_t = end_time - start_time
print("Done.")
print(f"Processed {len(exo_files)} file(s) in {delta_t:.2f} seconds.")
#
