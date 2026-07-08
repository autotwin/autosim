import pytest

from pipeline.config import parse_npy_filename, parse_config


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


def test_parse_npy_filename():

    dummy_filename = "U01_HJF_0001_01-NR-synthseg-homogeneous-membranesON-combined.npy"

    strings = parse_npy_filename(dummy_filename)

    assert strings["subject_id"] == "U01_HJF_0001_01"
    assert strings["motion_type"] == "NR"
    assert strings["algorithm"] == "synthseg"
    assert strings["brain_fidelity"] == "homogeneous"
    assert strings["include_membranes"] == True


def test_parse_npy_filename_wrong_length():

    dummy_filename = "U01_HJF_0001_01-NR-synthseg-homogeneous-combined.npy"

    with pytest.raises(ValueError):
        strings = parse_npy_filename(dummy_filename)


def test_parse_config():

    config_class = parse_config(VALID_RAW)

    assert config_class.automesh == "dummy/automesh/path"
    assert config_class.abaqus == "dummy/abaqus/path"
    assert config_class.npy_file == "U01_HJF_0001_01-NR-synthseg-homogeneous-membranesON-combined.npy"
    assert config_class.mat_path == "dummy/mat/path.mat"
    assert config_class.output_dir == "path/to/output"
    assert config_class.material_model == "menichetti"
    assert config_class.csf_model == "fluid"
    assert config_class.ref_dof == 5
    assert config_class.ref_dof == 5
    assert config_class.ref_dof == 5
    assert config_class.time_interval_step == 0.002
    assert config_class.subject_id == "U01_HJF_0001_01"
    assert config_class.motion_type == "NR"
    assert config_class.algorithm == "synthseg"
    assert config_class.brain_fidelity == "homogeneous"
    assert config_class.include_membranes == True


def test_parse_config_missing_env():

    raw_lines = {"run": VALID_RAW["run"]}

    with pytest.raises(ValueError):
        parse_config(raw_lines)


def test_parse_config_missing_run():

    raw_lines = {"env": VALID_RAW["env"]}

    with pytest.raises(ValueError):
        parse_config(raw_lines)


def test_parse_config_missing_automesh():

    raw_lines = {
        "env": {"abaqus": "dummy/abaqus/path"},
        "run": VALID_RAW["run"],
    }

    with pytest.raises(ValueError):
        parse_config(raw_lines)


def test_parse_config_missing_abaqus():

    raw_lines = {
        "env": {"automesh": "dummy/automesh/path"},
        "run": VALID_RAW["run"],
    }

    with pytest.raises(ValueError):
        parse_config(raw_lines)


def test_parse_config_missing_npy_file():

    run = {k: v for k, v in VALID_RAW["run"].items() if k != "npy_file"}
    with pytest.raises(ValueError):
        parse_config({"env": VALID_RAW["env"], "run": run})


def test_parse_config_missing_mat_path():

    run = {k: v for k, v in VALID_RAW["run"].items() if k != "mat_path"}
    with pytest.raises(ValueError):
        parse_config({"env": VALID_RAW["env"], "run": run})


def test_parse_config_missing_output_dir():

    run = {k: v for k, v in VALID_RAW["run"].items() if k != "output_dir"}
    with pytest.raises(ValueError):
        parse_config({"env": VALID_RAW["env"], "run": run})


def test_parse_config_missing_material_model():

    run = {k: v for k, v in VALID_RAW["run"].items() if k != "material_model"}
    with pytest.raises(ValueError):
        parse_config({"env": VALID_RAW["env"], "run": run})


def test_parse_config_wrong_material_model():

    run = {**VALID_RAW["run"], "material_model": "fsl"}
    with pytest.raises(ValueError):
        parse_config({"env": VALID_RAW["env"], "run": run})


def test_parse_config_giudice_removed():

    run = {**VALID_RAW["run"], "material_model": "giudice"}
    with pytest.raises(ValueError):
        parse_config({"env": VALID_RAW["env"], "run": run})


def test_parse_config_missing_csf_model():

    run = {k: v for k, v in VALID_RAW["run"].items() if k != "csf_model"}
    with pytest.raises(ValueError):
        parse_config({"env": VALID_RAW["env"], "run": run})


def test_parse_config_wrong_csf_model():

    run = {**VALID_RAW["run"], "csf_model": "gruneisen"}
    with pytest.raises(ValueError):
        parse_config({"env": VALID_RAW["env"], "run": run})


def test_parse_config_missing_ref_dof_raises():

    run = {k: v for k, v in VALID_RAW["run"].items() if k != "ref_dof"}
    with pytest.raises(ValueError):
        parse_config({"env": VALID_RAW["env"], "run": run})


def test_parse_config_missing_ref_dof():

    run = {k: v for k, v in VALID_RAW["run"].items() if k != "ref_dof"}
    with pytest.raises(ValueError):
        parse_config({"env": VALID_RAW["env"], "run": run})


def test_parse_config_wrong_ref_dof():

    run = {**VALID_RAW["run"], "ref_dof": 3}
    with pytest.raises(ValueError):
        parse_config({"env": VALID_RAW["env"], "run": run})


def test_parse_config_missing_time_interval_raises():

    run = {k: v for k, v in VALID_RAW["run"].items() if k != "time_interval_step"}
    with pytest.raises(ValueError):
        parse_config({"env": VALID_RAW["env"], "run": run})


def test_parse_config_missing_time_interval_step():

    run = {k: v for k, v in VALID_RAW["run"].items() if k != "time_interval_step"}
    with pytest.raises(ValueError):
        parse_config({"env": VALID_RAW["env"], "run": run})


def test_parse_config_v_cutoff_default():
    config = parse_config(VALID_RAW)
    assert config.v_cutoff == 0.1


def test_parse_config_v_cutoff_override():
    run = {**VALID_RAW["run"], "v_cutoff": 0.5}
    config = parse_config({"env": VALID_RAW["env"], "run": run})
    assert config.v_cutoff == 0.5


def test_parse_config_v_cutoff_zero_disables_trimming():
    run = {**VALID_RAW["run"], "v_cutoff": 0.0}
    config = parse_config({"env": VALID_RAW["env"], "run": run})
    assert config.v_cutoff == 0.0


def test_parse_config_sim_end_ms_default():
    config = parse_config(VALID_RAW)
    assert config.sim_end_ms == 0.0


def test_parse_config_sim_end_ms_override():
    run = {**VALID_RAW["run"], "sim_end_ms": 90.0}
    config = parse_config({"env": VALID_RAW["env"], "run": run})
    assert config.sim_end_ms == 90.0
