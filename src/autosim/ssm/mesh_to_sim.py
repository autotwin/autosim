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

    exo_folder: str
    # decomp_folder: str
    ssm_folder: str  # Folder for ssm simulation input files
    n_processors: int  # Number of processors for mesh decomposition
    mesh_decompose: bool  # Whether to decompose the mesh
    run_sims: bool  # Whether to run simulations
    termination_time: float  # Termination time in seconds


# -------------------
# user settings begin
# -------------------
input_Chad = Input(
    exo_folder="~/scratch/ixi/exo/",  # Start point is this folder, followed by decomposition
    # decomp_folder="~/scratch/ixi/decomp/",  # Next, meshes get decomposed into decomp folder
    ssm_folder="~/scratch/ixi/ssm/",  # Next, input files get populated in this folder
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
EXO_FOLDER: Final[Path] = Path(ii.exo_folder).expanduser()
# DECOMP_FOLDER: Final[Path] = Path(ii.decomp_folder).expanduser()
SSM_FOLDER: Final[Path] = Path(ii.ssm_folder).expanduser()
N_PROCESSORS: Final[int] = ii.n_processors
DECOMP: Final[bool] = ii.mesh_decompose
RUN_SIMS: Final[bool] = ii.run_sims
TERMINATION_TIME: Final[float] = ii.termination_time

# Process all .exo files in the input folder
if not EXO_FOLDER.exists():
    print(f"Error: Non-existent folder: {EXO_FOLDER}")
    sys.exit(1)  # Exit the program with a non-zero status

exo_files = list(EXO_FOLDER.glob("*.exo"))
if not exo_files:
    raise ValueError(f"No .exo files found in {EXO_FOLDER}")

print(f"Number of .exo files found in {EXO_FOLDER}: {len(exo_files)}")

if DECOMP:
    print("Decomposing mesh files...")
    print(f"Number of processors: {N_PROCESSORS}")

    # # Create output folder if it doesn't exist
    # if not DECOMP_FOLDER.exists():
    #     DECOMP_FOLDER.mkdir(parents=True, exist_ok=True)
    #     print(f"Created decomp folder: {DECOMP_FOLDER}")

    # print(f"Decomp folder: {DECOMP_FOLDER}")

    breakpoint()

    for exo_file in exo_files:
        print("...")
        # Print the source file being processed
        print(f"Processing source:\n  {exo_file}")

        # Create a subfolder in the decomp folder for each .exo file
        decomp_subfolder = EXO_FOLDER / exo_file.stem
        print(f"Decomp subfolder:\n  {decomp_subfolder}")

        # Create the subfolder if it doesn't exist
        decomp_subfolder.mkdir(parents=True, exist_ok=True)

        # Move the .exo file into subfolder
        source_file = EXO_FOLDER / exo_file.name
        destination_file = decomp_subfolder / exo_file.name
        try:
            if not destination_file.exists():
                source_file.rename(destination_file)
                print(f"Moved {source_file} to {destination_file}")
            else:
                print(f"File {destination_file} already exists, skipping move.")
        except FileNotFoundError:
            print(f"Error: The file {source_file} does not exist.")
            raise
        except Exception as e:
            print(f"Error moving file: {e}")
            raise

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
            str(destination_file),
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
            os.chdir(EXO_FOLDER)
            print(f"Changed directory back to:\n  {os.getcwd()}")
        except FileNotFoundError:
            print(f"Error: The directory {EXO_FOLDER} does not exist.")
            raise
        except Exception as e:
            print(f"Error changing directory back to {EXO_FOLDER}: {e}")
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
    if not SSM_FOLDER.exists():
        SSM_FOLDER.mkdir(parents=True, exist_ok=True)
        print(f"Created sim folder: {SSM_FOLDER}")

    print(f"ssm folder: {SSM_FOLDER}")

    for exo_file in exo_files:
        # Create a subfolder in the sim folder for each .exo file
        ssm_subfolder = SSM_FOLDER / exo_file.stem
        print(f"Sim subfolder:\n  {ssm_subfolder}")

        # Create the subfolder if it doesn't exist
        ssm_subfolder.mkdir(parents=True, exist_ok=True)

        # Change into the sim subfolder
        try:
            os.chdir(ssm_subfolder)
        except FileNotFoundError:
            print(f"Error: The directory {ssm_subfolder} does not exist.")
            raise
        except Exception as e:
            print(f"Error changing directory to {ssm_subfolder}: {e}")
            raise

        # Print the current working directory
        print(f"Current working directory:\n  {Path.cwd()}")

        # Create the unique ssm input file
        ssm_command = [
            "cp",
            str((Path(__file__).resolve()).parent / "ssm_input_template.i"),
            str(ssm_subfolder / "ssm_input.i"),
        ]

        # Run the command to copy the template file
        result = subprocess.run(ssm_command, check=True)
        if result.returncode == 0:
            print(f"Copied template to:\n  {ssm_subfolder / 'ssm_input.i'}")
        else:
            print("Failed to copy template file.")
            print(result.stderr)

        replacements = {
            "# DATABASE_NAME": "database name = ../../exo/"
            + str(exo_file.stem)
            + "/"
            + str(exo_file.stem)
            + ".exo",
            "# TERMINATION_TIME": "termination time = "
            + str(TERMINATION_TIME)
            + "  # seconds",
        }

        # Read the contents of the input file
        with open(ssm_subfolder / "ssm_input.i", "r") as file:
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
        with open(ssm_subfolder / "ssm_input.i", "w") as file:
            file.write(modified_content)

        print(f"Created ssm input file:\n  {ssm_subfolder / 'ssm_input.i'}")


else:
    print("Skipping simulation runs.")
