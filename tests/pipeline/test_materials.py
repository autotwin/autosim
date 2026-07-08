import pytest

from pipeline.config import parse_config
from pipeline.materials import (
    get_materials,
    format_material,
    NeoHookeanPronyParams,
    OgdenPronyParams,
    LVEParams,
    ElasticParams,
    VUMATParams,
    GruneisenEOSParams,
)



def test_get_materials_membranesOFF():

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
        "voxel_size": 1.0,
        "ref_dof": 5,
        "n_frames": 81,
        "time_interval_step": 0.002,
    }
    }

    config_class = parse_config(VALID_RAW)

    properties = get_materials(config_class)

    assert properties["brain"].density == 1.04e-9
    assert properties["csf"].s == pytest.approx(2.1057)
    assert properties["skull"].nu == 0.3


def test_get_materials_membranesON():

    VALID_RAW_membranes_ON = {
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
        "voxel_size": 1.0,
        "ref_dof": 5,
        "n_frames": 81,
        "time_interval_step": 0.002,
    }
    }

    config_class = parse_config(VALID_RAW_membranes_ON)

    properties = get_materials(config_class)

    assert properties["brain"].density == 1.04e-9
    assert properties["csf"].s == pytest.approx(2.1057)
    assert properties["skull"].nu == 0.3
    assert properties["membranes"].E == 31.5


def test_get_materials_heterogeneous_membranesOFF():

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
        "voxel_size": 1.0,
        "ref_dof": 5,
        "n_frames": 81,
        "time_interval_step": 0.002,
    }
    }

    config_class = parse_config(VALID_RAW)

    properties = get_materials(config_class)

    assert properties["wm"].C10 == 3.815e-3
    assert properties["gm"].C10 == 3.22e-3
    assert properties["csf"].s == pytest.approx(2.1057)
    assert properties["skull"].nu == 0.3

def test_get_materials_heterogeneous_membranesON():

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
        "voxel_size": 1.0,
        "ref_dof": 5,
        "n_frames": 81,
        "time_interval_step": 0.002,
    }
    }

    config_class = parse_config(VALID_RAW)

    properties = get_materials(config_class)

    assert properties["wm"].C10 == 3.815e-3
    assert properties["gm"].C10 == 3.22e-3
    assert properties["csf"].s == pytest.approx(2.1057)
    assert properties["skull"].nu == 0.3
    assert properties["membranes"].E == 31.5



def test_alshareef_homogeneous_uses_whole_brain_average():
    """alshareef + homogeneous must use Table 3 whole-brain G0, not WM G0."""
    raw = {
        "env": {"automesh": "dummy", "abaqus": "dummy"},
        "run": {
            "npy_file": "U01_HJF_0001_01-NR-synthseg-homogeneous-membranesON-combined.npy",
            "mat_path": "dummy.mat",
            "output_dir": "out/",
            "material_model": "alshareef",
            "csf_model": "fluid",
            "ref_dof": 6,
            "time_interval_step": 0.002,
        },
    }
    config = parse_config(raw)
    props = get_materials(config)
    assert props["brain"].G0 == pytest.approx(6.94e-3)


def test_alshareef_heterogeneous_uses_region_specific_params():
    """alshareef + heterogeneous must use WM (Corona Radiata) and GM (Deep GM) params."""
    raw = {
        "env": {"automesh": "dummy", "abaqus": "dummy"},
        "run": {
            "npy_file": "U01_HJF_0001_01-NR-synthseg-heterogeneous-membranesON-combined.npy",
            "mat_path": "dummy.mat",
            "output_dir": "out/",
            "material_model": "alshareef",
            "csf_model": "fluid",
            "ref_dof": 6,
            "time_interval_step": 0.002,
        },
    }
    config = parse_config(raw)
    props = get_materials(config)
    assert props["wm"].G0 == pytest.approx(9.2e-3)
    assert props["gm"].G0 == pytest.approx(10.25e-3)


def test_format_material_neo_hookean_prony():

    params = NeoHookeanPronyParams(density=1.04e-9, C10=3.815e-3, D1=3.11e-2,
                                   prony=[(0.57, 0.020)])
    lines = format_material("BRAIN", params)
    assert lines[0] == "*MATERIAL, NAME=BRAIN"
    assert "*HYPERELASTIC, NEO HOOKE, MODULI=INSTANTANEOUS" in lines


def test_format_material_ogden_prony():

    params = OgdenPronyParams(density=1.04e-9, mu=-9.453e-5, alpha=-25.39,
                              D1=9.13e-4, prony=[(0.758, 14.85)])
    lines = format_material("BRAIN", params)
    assert lines[0] == "*MATERIAL, NAME=BRAIN"
    assert "*HYPERELASTIC, OGDEN, N=1, MODULI=INSTANTANEOUS" in lines


def test_format_material_lve():

    params = LVEParams(density=1.04e-9, G0=9.2e-3, nu=0.49,
                       prony=[(0.76, 9.0e-4)])
    lines = format_material("BRAIN", params)
    assert lines[0] == "*MATERIAL, NAME=BRAIN"
    assert "*ELASTIC" in lines


def test_format_material_elastic():

    params = ElasticParams(density=2.07e-9, E=3280.0, nu=0.3)
    lines = format_material("SKULL", params)
    assert lines[0] == "*MATERIAL, NAME=SKULL"
    assert "*ELASTIC" in lines


def test_format_material_vumat():

    params = VUMATParams(density=1.04e-9, mu_inf=1.84e-3, alpha=-3.47,
                         k11=-2.65e-6, k21=6.0969e-4, c21=0.62, Kbulk=2190.0)
    lines = format_material("BRAIN", params)
    assert lines[0] == "*MATERIAL, NAME=BRAIN"
    assert "*USER MATERIAL, CONSTANTS=6" in lines


def test_csf_material_nh_is_tzoumaka_model():
    from pipeline.materials import CSF_MATERIAL_NH
    assert isinstance(CSF_MATERIAL_NH, NeoHookeanPronyParams)
    assert CSF_MATERIAL_NH.C10 == pytest.approx(5.0e-4)
    assert CSF_MATERIAL_NH.moduli == "LONG TERM"


def test_csf_material_fluid_is_zhou_kleiven_2019():
    from pipeline.materials import CSF_MATERIAL_FLUID
    assert isinstance(CSF_MATERIAL_FLUID, GruneisenEOSParams)
    assert CSF_MATERIAL_FLUID.density == pytest.approx(1.0e-9)
    assert CSF_MATERIAL_FLUID.c0      == pytest.approx(1.4829e6)
    assert CSF_MATERIAL_FLUID.s       == pytest.approx(2.1057)
    assert CSF_MATERIAL_FLUID.gamma0  == pytest.approx(1.2)
    assert CSF_MATERIAL_FLUID.mu      == pytest.approx(1.0e-9)


def test_format_material_gruneisen_eos():
    params = GruneisenEOSParams(density=1.0e-9, c0=1.4829e6, s=2.1057, gamma0=1.2, mu=1.0e-9)
    lines = format_material("CSF", params)
    assert lines[0] == "*MATERIAL, NAME=CSF"
    assert "*EOS, TYPE=USUP" in lines
    assert "*VISCOSITY" in lines


def test_get_materials_csf_model_fluid():
    from pipeline.materials import CSF_MATERIAL_FLUID
    raw = {
        "env": {"automesh": "dummy", "abaqus": "dummy"},
        "run": {
            "npy_file": "U01_HJF_0001_01-NR-synthseg-homogeneous-membranesON-combined.npy",
            "mat_path": "dummy/mat/path.mat",
            "output_dir": "path/to/output",
            "material_model": "alshareef",
            "voxel_size": 1.0,
            "ref_dof": 6,
            "n_frames": 81,
            "time_interval_step": 0.002,
            "csf_model": "fluid",
        },
    }
    config = parse_config(raw)
    props = get_materials(config)
    assert props["csf"] is CSF_MATERIAL_FLUID


def test_get_materials_csf_model_neo_hookean():
    from pipeline.materials import CSF_MATERIAL_NH
    raw = {
        "env": {"automesh": "dummy", "abaqus": "dummy"},
        "run": {
            "npy_file": "U01_HJF_0001_01-NR-synthseg-homogeneous-membranesON-combined.npy",
            "mat_path": "dummy/mat/path.mat",
            "output_dir": "path/to/output",
            "material_model": "alshareef",
            "voxel_size": 1.0,
            "ref_dof": 6,
            "n_frames": 81,
            "time_interval_step": 0.002,
            "csf_model": "neo_hookean",
        },
    }
    config = parse_config(raw)
    props = get_materials(config)
    assert props["csf"] is CSF_MATERIAL_NH


def test_format_material_none_raises():
    with pytest.raises(ValueError):
        format_material("BRAIN", None)