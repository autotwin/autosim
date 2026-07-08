import numpy as np


def compute_cog(npy_array, remove_ids) -> tuple:

    """
    Computes the cog of the whole head and removes the defined IDs

    Args:
        npy_array : Contains the head + background mask in the voxel space
        remove_ids : Contains the IDs that are to be removed

    Returns:
        z,y,x coordinates of the cog of the head
    """

    data = npy_array
    mask = ~np.isin(data, remove_ids)
    indices = np.argwhere(mask).astype(float) + 0.5
    return np.mean(indices, axis=0)  


def translation_to_origin(voxel_size, cog) -> tuple:

    """
    Computes the translation in each axis to shift the cog to 0,0,0

    Args:
        voxel_size : Voxel size
        cog : Tuple containing the z,y,x coords of the cog

    Returns:
        Tuple containing how much the cog has to be translated to match the 0,0,0 
    """

    tx = -voxel_size * cog[2]   # x
    ty = -voxel_size * cog[1]   # y
    tz = -voxel_size * cog[0]   # z

    return (tx,ty,tz)


def create_automesh_command(automesh_path, npy_file, output_mesh, remove_ids, voxel_size, tx, ty, tz) -> list:

    """
    Returns a list containing the automesh command to be executed

    Args:
        automesh_path : The path to the AUTOMESH folder
        npy_file : The path for the input .npy file
        output_mesh : The path for where the mesh file to be saved
        remove_ids : The label IDs to be removed from the mask 
        voxel_size : Desired element size
        tx, ty, tz : Translations in the x,y,z axis for the CoG to match the 0,0,0

        Returns: 
            A list containing the command to run
    """

    remove_args = []
    for rid in remove_ids:
        remove_args += ["-r", str(rid)]

    command = [
        str(automesh_path), "mesh", "hex",
        "-i", str(npy_file),
        "-o", str(output_mesh),
        *remove_args,
        "--xscale",     str(voxel_size),
        "--yscale",     str(voxel_size),
        "--zscale",     str(voxel_size),
        "--xtranslate", str(tx),
        "--ytranslate", str(ty),
        "--ztranslate", str(tz),
    ]

    return command
