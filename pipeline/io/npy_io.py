import numpy as np
from pathlib import Path


def load_npy(file_path: Path):

    """
    Loads the array saved in the .npy file

    Args:
        file_path: File to be loaded
    """

    return np.load(file_path) 