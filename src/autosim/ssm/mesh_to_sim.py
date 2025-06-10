"""This module operates on mesh files in .exo format in preparation for
simulation with SSM.

Run:
# If on HPC
module purge
module load aue/anaconda3/2024.06-1
python --version  # Confirm Python 3.12
module load sierra
module load seacas

# For all platforms
cd ~/autotwin/autosim/

# Create virtual environment if not already done
python -m venv .venv

# Activate the virtual environment
source ~/autotwin/autosim/.venv/bin/activate

pip install -e .

python ~/autotwin/autosim/src/autosim/ssm/mesh_to_sim.py
"""

from pathlib import Path
import os
import subprocess
import sys
import time
from typing import NamedTuple, Final


class Input(NamedTuple):
    """Input class for the mesh_to_sim.py script."""

    source_folder: str
    decomp_folder: str
    sim_folder: str  # Folder for simulation input files
    n_processors: int  # Number of processors for mesh decomposition
    mesh_decompose: bool  # Whether to decompose the mesh
    run_sims: bool  # Whether to run simulations
    termination_time: float  # Termination time in seconds


# -------------------
# user settings begin
# -------------------
input_Chad = Input(
    source_folder="~/scratch/ixi/exo/",  # Start point is the mesh folder
    decomp_folder="~/scratch/ixi/decomp/",  # Next, meshes get decomposed into decomp folder
    sim_folder="~/scratch/ixi/sim/",  # Next, input files get populated in sim folder
    n_processors=160,  # Number of processors for mesh decomposition
    mesh_decompose=False,
    run_sims=True,
    termination_time=0.0001,  # Termination time in seconds
)
# -----------------
# user settings end
# -----------------
start_time = time.time()
ii = input_Chad

# Harvest constants from user input
SOURCE_FOLDER: Final[Path] = Path(ii.source_folder).expanduser()
DECOMP_FOLDER: Final[Path] = Path(ii.decomp_folder).expanduser()
SIM_FOLDER: Final[Path] = Path(ii.sim_folder).expanduser()
N_PROCESSORS: Final[int] = ii.n_processors
DECOMP: Final[bool] = ii.mesh_decompose
RUN_SIMS: Final[bool] = ii.run_sims
TERMINATION_TIME: Final[float] = ii.termination_time

# Process all .exo files in the input folder
if not SOURCE_FOLDER.exists():
    print(f"Error: Non-existent folder: {SOURCE_FOLDER}")
    sys.exit(1)  # Exit the program with a non-zero status

exo_files = list(SOURCE_FOLDER.glob("*.exo"))
if not exo_files:
    raise ValueError(f"No .exo files found in {SOURCE_FOLDER}")

print(f"Number of .exo files found in {SOURCE_FOLDER}: {len(exo_files)}")

print(f"Source folder: {SOURCE_FOLDER}")

if DECOMP:
    print("Decomposing mesh files...")

    # Create output folder if it doesn't exist
    if not DECOMP_FOLDER.exists():
        DECOMP_FOLDER.mkdir(parents=True, exist_ok=True)
        print(f"Created decomp folder: {DECOMP_FOLDER}")

    print(f"Decomp folder: {DECOMP_FOLDER}")
    print(f"Number of processors: {N_PROCESSORS}")

    for exo_file in exo_files:
        print("...")
        # Print the source file being processed
        print(f"Processing source:\n  {exo_file}")

        # Create a subfolder in the decomp folder for each .exo file
        decomp_subfolder = DECOMP_FOLDER / exo_file.stem
        print(f"Decomp subfolder:\n  {decomp_subfolder}")

        # Create the subfolder if it doesn't exist
        decomp_subfolder.mkdir(parents=True, exist_ok=True)

        # Change into the decomp subfolder
        try:
            os.chdir(decomp_subfolder)
        except FileNotFoundError:
            print(f"Error: The directory {decomp_subfolder} does not exist.")
            raise
        except Exception as e:
            print(f"Error changing directory to {decomp_subfolder}: {e}")
            raise

        # Print the current working directory
        print(f"Current working directory:\n  {Path.cwd()}")

        # Construct the decomp command
        decomp_command = [
            "decomp",
            "--processors",
            str(N_PROCESSORS),
            str(exo_file),
        ]

        # Print the command being run
        print(f"Running command:\n  {' '.join(decomp_command)}")
        print(f"Current working directory: {os.getcwd()}")

        # Run the command
        result = subprocess.run(decomp_command, check=True)

        if result.returncode == 0:
            print(result.stdout)  # output of the command
        else:
            print("command failed:")
            print(result.stderr)  # error message

        # Change pack to original directory
        try:
            os.chdir(DECOMP_FOLDER)
            print(f"Changed directory back to:\n  {os.getcwd()}")
        except FileNotFoundError:
            print(f"Error: The directory {DECOMP_FOLDER} does not exist.")
            raise
        except Exception as e:
            print(f"Error changing directory back to {DECOMP_FOLDER}: {e}")
            raise

    end_time = time.time()
    delta_t = end_time - start_time
    print("Done.")
    print(f"Processed {len(exo_files)} file(s) in {delta_t:.2f} seconds.")
else:
    print("Skipping mesh decomposition.")

if RUN_SIMS:
    print("Running simulations...")

    # Create output folder if it doesn't exist
    if not SIM_FOLDER.exists():
        SIM_FOLDER.mkdir(parents=True, exist_ok=True)
        print(f"Created sim folder: {SIM_FOLDER}")

    print(f"Sim folder: {SIM_FOLDER}")

    for exo_file in exo_files:
        # Create a subfolder in the sim folder for each .exo file
        sim_subfolder = SIM_FOLDER / exo_file.stem
        print(f"Sim subfolder:\n  {sim_subfolder}")

        # Create the subfolder if it doesn't exist
        sim_subfolder.mkdir(parents=True, exist_ok=True)

        # Change into the sim subfolder
        try:
            os.chdir(sim_subfolder)
        except FileNotFoundError:
            print(f"Error: The directory {sim_subfolder} does not exist.")
            raise
        except Exception as e:
            print(f"Error changing directory to {sim_subfolder}: {e}")
            raise

        # Print the current working directory
        print(f"Current working directory:\n  {Path.cwd()}")

        # Create the unique ssm input file
        ssm_command = [
            "cp",
            str((Path(__file__).resolve()).parent / "ssm_input_template.i"),
            str(sim_subfolder / "ssm_input.i"),
        ]

        # Run the command to copy the template file
        result = subprocess.run(ssm_command, check=True)
        if result.returncode == 0:
            print(f"Copied template to:\n  {sim_subfolder / 'ssm_input.i'}")
        else:
            print("Failed to copy template file.")
            print(result.stderr)

        replacements = {
            "# DATABASE_NAME": "database name = ../../decomp/"
            + str(exo_file.stem)
            + "/"
            + str(exo_file.stem)
            + ".exo",
            "# TERMINATION_TIME": "termination time = "
            + str(TERMINATION_TIME)
            + "  # seconds",
        }

        # Read the contents of the input file
        with open(sim_subfolder / "ssm_input.i", "r") as file:
            content = file.read()

        # Replace the placeholders with actual values
        cc = content.split("\n")
        for i, line in enumerate(cc):
            for key, value in replacements.items():
                if key in line:
                    line = line.replace(key, value)
                    cc[i] = line
                    print(f"Replaced '{key}' with '{value}' in line {i + 1}")

        modified_content = "\n".join(cc)

        # Write the modified content back to the file
        with open(sim_subfolder / "ssm_input.i", "w") as file:
            file.write(modified_content)

        print(f"Created ssm input file:\n  {sim_subfolder / 'ssm_input.i'}")


else:
    print("Skipping simulation runs.")

