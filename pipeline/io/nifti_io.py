import numpy as np
import nibabel as nib
from pathlib import Path


def load_nifti(file_path: Path) -> tuple[np.ndarray, np.array]:

    """
    Loads a NIfTI image and returns the image array and affine

    Args:
        file_path : Path to the input file

    Returns:
        A tuple of the image array and affine matrix 
    """
 
    try:
        img = nib.load(file_path)
        img_data = img.get_fdata()

        return img_data.astype(np.int16), img.affine.astype(np.float64)

    except nib.filebasedimages.ImageFileError:
        raise ValueError("Please provide a valid NIfTI file")


def get_voxel_size_from_npy(npy_path: Path) -> float:

    """
    Reads the voxel size from the NIfTI companion file of an Autovalidate_New .npy labelmap.
    The companion is expected at the same path with 'combined.npy' replaced by
    'combined_labels.nii.gz'.

    Args:
        npy_path : Path to the .npy labelmap file

    Returns:
        Isotropic voxel size in mm
    """

    nii_path = Path(str(npy_path).replace("combined.npy", "combined_labels.nii.gz"))

    if not nii_path.exists():
        raise FileNotFoundError(
            f"Companion NIfTI not found: {nii_path}\n"
            "Expected a '*combined_labels.nii.gz' alongside the .npy file."
        )

    img = nib.load(nii_path)
    voxel_size = float(img.header.get_zooms()[0])

    return voxel_size


def save_nifti(input_array: np.ndarray, affine_array: np.array, file_path: Path):

    """
    Saves the input array and affine in a specified file as a .nii.gz file

    Args:
        input_array : Input array of the mask
        affine_array : Input affine of the mask
        file_path : File path to be saved

    """

    file = nib.Nifti1Image(input_array,affine_array)
    
    nib.save(file,file_path)