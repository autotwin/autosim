import numpy as np
import pytest

from pipeline.io.npy_io import load_npy


def test_load_npy(tmp_path):

    file_path = tmp_path / "test.npy"

    input_array = np.zeros((3,3,3), dtype = np.uint8)
    input_array[0,0,0] = 1
    input_array[1,2,2] = 1
    input_array[2,1,2] = 1
    input_array[2,2,2] = 1

    np.save(file_path, input_array)

    loaded_array = load_npy(file_path)

    np.testing.assert_array_equal(loaded_array, input_array)