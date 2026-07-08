import numpy as np


def compute_mps(e11, e22, e33, g12, g13, g23) -> float:
    
    """
    Compute Maximum Principal Strain from 6 Abaqus LE components.

    Abaqus reports shear as engineering strain (2x tensorial),
    so g12, g13, g23 are halved before assembling the tensor.
    Returns the largest eigenvalue.

    Args: 
        Each component of the 3x3 Strain Tensor

    Returns:
        The MAX eigenvalue of the Strain Tensor
    """

    e12, e13, e23 = g12 / 2, g13 / 2, g23 / 2
    tensor = np.array([
        [e11, e12, e13],
        [e12, e22, e23],
        [e13, e23, e33],
    ])
    return float(np.max(np.linalg.eigvalsh(tensor)))


def centroid_to_ijk(cx, cy, cz, tx, ty, tz) -> tuple:
    
    """
    Maps the centroid of each element in the voxel space

    Args:
        cx, cy, cz : Centroids of the elements in mm
        tx, ty, tz : Tranlsation in mm during meshing

    Returns:
        The coordinates of the centroid of elements in the voxel space

    Notice:
        Returns z,y,x 
    """

    x_idx = int(round(cx - tx - 0.5))
    y_idx = int(round(cy - ty - 0.5))
    z_idx = int(round(cz - tz - 0.5))

    return (z_idx, y_idx, x_idx)