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
import time
from typing import NamedTuple, Final


class Input(NamedTuple):
    """Input class for the mesh_to_sim.py script."""

    input_folder: str
    decomp_folder: str
    n_processors: int  # Number of processors for decomp
    hpc_run: bool = True  # Run on HPC or not


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
    print(f"Created decomp folder: {DECOMP_FOLDER}")

# Harvest all .exo files in the input folder
exo_files = list(EXO_FOLDER.glob("*.exo"))
if not exo_files:
    raise ValueError(f"No .exo files found in {EXO_FOLDER}")

print(f"Number of .exo files found in {EXO_FOLDER}: {len(exo_files)}")

print(f"Input folder: {EXO_FOLDER}")
print(f"Decomp folder: {DECOMP_FOLDER}")

print(f"Number of processors: {N_PROCESSORS}")
print(f"Running on HPC: {HPC_RUN}")

# If on the HPC, run the decomp command for each .exo file
if HPC_RUN:
    # Load modules
    # print("Loading modules...")
    # module_commands = [
    #     [
    #         "module",
    #         "purge",
    #     ],
    #     [
    #         "module",
    #         "load",
    #         "sierra",
    #     ],
    #     [
    #         "module",
    #         "load",
    #         "seacas",
    #     ],
    # ]

    # for module_command in module_commands:
    #     # Print the command being run
    #     print(f"Running command: {' '.join(module_command)}")

    #     try:
    #         # Run the command
    #         subprocess.run(module_command, check=True)
    #     except subprocess.CalledProcessError as e:
    #         print(f"Error running command {' '.join(module_command)}: {e}")
    #         raise

    for exo_file in exo_files:
        print("...")
        # Create a subfolder in the decomp folder for each .exo file
        decomp_subfolder = DECOMP_FOLDER / exo_file.stem
        print(f"Decomp subfolder: {decomp_subfolder}")

        # Create the subfolder if it doesn't exist
        decomp_subfolder.mkdir(parents=True, exist_ok=True)

        # Print the source file being processed
        print(f"Processing source: {exo_file}")

        # Change into the decomp subfolder
        try:
            os.chdir(decomp_subfolder)
            print(f"Changed directory to: {os.getcwd()}")
        except FileNotFoundError:
            print(f"Error: The directory {decomp_subfolder} does not exist.")
            raise
        except Exception as e:
            print(f"Error changing directory to {decomp_subfolder}: {e}")
            raise

        #     subprocess.run(["cd", str(decomp_subfolder)], check=True, shell=True)
        # except subprocess.CalledProcessError as e:
        #     print(f"Error changing directory to {decomp_subfolder}: {e}")
        #     raise

        # Print the current working directory
        print(f"Current working directory: {Path.cwd()}")

        # Construct the decomp command
        decomp_command = [
            "decomp",
            "--processors",
            str(N_PROCESSORS),
            str(exo_file),
        ]

        # Print the command being run
        print(f"Running command: {' '.join(decomp_command)}")

        # Run the command
        subprocess.run(decomp_command, check=True)

        # Change pack to original directory
        try:
            os.chdir(DECOMP_FOLDER)
            print(f"Changed directory back to: {os.getcwd()}")
        except FileNotFoundError:
            print(f"Error: The directory {DECOMP_FOLDER} does not exist.")
            raise
        except Exception as e:
            print(f"Error changing directory back to {DECOMP_FOLDER}: {e}")
            raise

        # # Change back to the original directory
        # try:
        #     subprocess.run(["cd", str(DECOMP_FOLDER)], check=True, shell=True)
        # except subprocess.CalledProcessError as e:
        #     print(f"Error changing directory back to {DECOMP_FOLDER}: {e}")
        #     raise

end_time = time.time()
delta_t = end_time - start_time
print("Done.")
print(f"Processed {len(exo_files)} file(s) in {delta_t:.2f} seconds.")
#
