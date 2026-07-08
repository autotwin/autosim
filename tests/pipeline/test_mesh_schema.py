import pytest


from pipeline.config import parse_config
from pipeline.preprocessing.mesh_schema import mesh_mapping


def test_mesh_mapping_hom_memOFF():

    VALID_RAW = {
    "env": {
        "automesh": "dummy/automesh/path",
        "abaqus": "dummy/abaqus/path",
    },
    "run": {
        "npy_file": "U01_HJF_0001_01-NR-synthseg-homogeneous-membranesOFF-combined.npy",
        "mat_path": "dummy/mat/path.mat",
        "output_dir": "path/to/output",
        "material_model": "menichetti",
        "csf_model": "fluid",
        "ref_dof": 5,
        "time_interval_step": 0.002,
    }
    }
    
    config_class = parse_config(VALID_RAW)

    output_dict = mesh_mapping(config_class.brain_fidelity, config_class.include_membranes)

    assert output_dict["wm"] == "EB1"
    assert output_dict["gm"] is None
    assert output_dict["csf"] == "EB3"
    assert output_dict["skull"] == "EB4"
    assert output_dict["membranes"] is None


def test_mesh_mapping_hom_memON():

    VALID_RAW = {
    "env": {
        "automesh": "dummy/automesh/path",
        "abaqus": "dummy/abaqus/path",
    },
    "run": {
        "npy_file": "U01_HJF_0001_01-NR-synthseg-homogeneous-membranesON-combined.npy",
        "mat_path": "dummy/mat/path.mat",
        "output_dir": "path/to/output",
        "material_model": "menichetti",
        "csf_model": "fluid",
        "ref_dof": 5,
        "time_interval_step": 0.002,
    }
    }
    
    config_class = parse_config(VALID_RAW)

    output_dict = mesh_mapping(config_class.brain_fidelity, config_class.include_membranes)

    assert output_dict["wm"] == "EB1"
    assert output_dict["gm"] is None
    assert output_dict["csf"] == "EB3"
    assert output_dict["skull"] == "EB4"
    assert output_dict["membranes"] == "EB5"


def test_mesh_mapping_het_memOFF():

    VALID_RAW = {
    "env": {
        "automesh": "dummy/automesh/path",
        "abaqus": "dummy/abaqus/path",
    },
    "run": {
        "npy_file": "U01_HJF_0001_01-NR-synthseg-heterogeneous-membranesOFF-combined.npy",
        "mat_path": "dummy/mat/path.mat",
        "output_dir": "path/to/output",
        "material_model": "menichetti",
        "csf_model": "fluid",
        "ref_dof": 5,
        "time_interval_step": 0.002,
    }
    }
    
    config_class = parse_config(VALID_RAW)

    output_dict = mesh_mapping(config_class.brain_fidelity, config_class.include_membranes)

    assert output_dict["wm"] == "EB1"
    assert output_dict["gm"] == "EB2"
    assert output_dict["csf"] == "EB3"
    assert output_dict["skull"] == "EB4"
    assert output_dict["membranes"] is None


def test_mesh_mapping_het_memON():

    VALID_RAW = {
    "env": {
        "automesh": "dummy/automesh/path",
        "abaqus": "dummy/abaqus/path",
    },
    "run": {
        "npy_file": "U01_HJF_0001_01-NR-synthseg-heterogeneous-membranesON-combined.npy",
        "mat_path": "dummy/mat/path.mat",
        "output_dir": "path/to/output",
        "material_model": "menichetti",
        "csf_model": "fluid",
        "ref_dof": 5,
        "time_interval_step": 0.002,
    }
    }
    
    config_class = parse_config(VALID_RAW)

    output_dict = mesh_mapping(config_class.brain_fidelity, config_class.include_membranes)

    assert output_dict["wm"] == "EB1"
    assert output_dict["gm"] == "EB2"
    assert output_dict["csf"] == "EB3"
    assert output_dict["skull"] == "EB4"
    assert output_dict["membranes"] == "EB5"