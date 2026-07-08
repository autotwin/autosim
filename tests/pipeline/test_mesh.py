import numpy as np

from pipeline.preprocessing.mesh import compute_cog, translation_to_origin, create_automesh_command

def test_compute_cog_uniform():

    dummy_array = np.array([[[1.0, 1.0], [1.0, 1.0]],
                            [[1.0, 1.0], [1.0, 1.0]]])
    dummy_background = [0]

    indices = compute_cog(dummy_array, dummy_background)

    assert len(indices) == 3
    assert indices[0] == 1
    assert indices[1] == 1
    assert indices[2] == 1


def test_compute_cog_removes_label():
    
    dummy_array = np.array([[[1.0, 1.0], [2.0, 2.0]],
                            [[1.0, 1.0], [2.0, 2.0]]])
    dummy_background = [1]

    indices = compute_cog(dummy_array, dummy_background)

    assert len(indices) == 3
    assert indices[0] == 1
    assert indices[1] == 1.5
    assert indices[2] == 1


def test_tranlation_to_origin():

    voxel_size = 1.0
    cog = (2.0, 3.0, 1.0)

    tx, ty, tz = translation_to_origin(voxel_size, cog)

    assert tx == -1.0
    assert ty == -3.0
    assert tz == -2.0


def test_create_automesh_command():

    automesh_path = "dummy/automesh"
    npy_file = "dummy/npy"
    output_mesh = "dummy/mesh"
    voxel_size = 1.0
    remove_ids = [0]
    tx = -1.0
    ty = -3.0
    tz = -2.0

    command = create_automesh_command(automesh_path, npy_file, output_mesh, remove_ids, voxel_size, tx, ty, tz)

    assert len(command) == 21
    assert command[0] == automesh_path
    assert command[12] == str(voxel_size)
    assert command[18] == str(ty)