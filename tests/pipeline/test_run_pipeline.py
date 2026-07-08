import numpy as np
import pytest
from unittest.mock import patch, call

from pipeline.config import Config
from run_pipeline import generate_inp, run_abaqus, run_pipeline


FAKE_TIME_MS      = np.linspace(-9.0, 30.0, 20)
FAKE_VELOCITY     = np.ones(20) * 3.4
FAKE_FRAME_CENTER = np.array([0.0, 18.0])
FAKE_FRAME_START  = np.array([-9.0, 9.0])
FAKE_FRAME_END    = np.array([9.0, 27.0])

FAKE_MESH = """\
*NODE
1, 10.0, 5.0, 0.0
2, -5.0, 3.0, 0.0
3,  0.0, 0.0, 8.0
*ELEMENT, ELSET=EB1
1, 1, 2
*ELEMENT, ELSET=EB3
2, 3
*ELEMENT, ELSET=EB4
3, 1, 2, 3
"""


@pytest.fixture
def hom_config(tmp_path):
    mesh_path = tmp_path / "U01_HJF_0001_01.inp"
    mesh_path.write_text(FAKE_MESH)

    return Config(
        automesh="automesh",
        abaqus="abaqus",
        npy_file=str(tmp_path / "U01_HJF_0001_01-NR-synthseg-homogeneous-membranesOFF-combined.npy"),
        mat_path=str(tmp_path / "fake.mat"),
        output_dir=str(tmp_path),
        material_model="menichetti",
        csf_model="fluid",
        ref_dof=6,
        time_interval_step=0.002,
        subject_id="U01_HJF_0001_01",
        motion_type="NR",
        algorithm="synthseg",
        brain_fidelity="homogeneous",
        include_membranes=False,
        vumat_path=None,
        n_cpus=16,
        h_rt="12:00:00",
        mem_per_core="4G",
    )


def test_generate_inp_hom_memOFF(hom_config, tmp_path):
    with patch("run_pipeline.load_pva_mat", return_value=(
        FAKE_TIME_MS, FAKE_VELOCITY, FAKE_FRAME_CENTER, FAKE_FRAME_START, FAKE_FRAME_END
    )):
        generate_inp(hom_config)

    out = tmp_path

    # loads.inp
    loads = (out / "loads.inp").read_text()
    assert "*Amplitude, name=AMP-1" in loads

    # frame_times.csv — header + 2 data rows
    csv_lines = (out / "frame_times.csv").read_text().splitlines()
    assert len(csv_lines) == 3

    # initial_conditions.inp
    ic = (out / "initial_conditions.inp").read_text()
    assert "*INITIAL CONDITIONS, TYPE=VELOCITY" in ic

    # material files
    assert "*MATERIAL, NAME=BRAIN" in (out / "brain.inp").read_text()
    assert "*MATERIAL, NAME=CSF" in (out / "csf.inp").read_text()
    assert "*MATERIAL, NAME=SKULL" in (out / "skull.inp").read_text()

    # step.inp — TIME POINTS at model level (before *Step), nodal output inside step
    step = (out / "step.inp").read_text()
    assert "*Dynamic, Explicit" in step
    assert "*End Step" in step
    assert "*TIME POINTS, NAME=COMP_FRAMES" in step
    assert "*NODE OUTPUT, NSET=BRAIN_NODES" in step
    assert "*NODE OUTPUT, NSET=CSF_NODES" in step
    assert step.index("*TIME POINTS") < step.index("*Step,")

    # assembly.inp — hom+memOFF: EB1=brain(1), EB3=CSF(3), EB4=skull(4)
    assembly = (out / "assembly.inp").read_text()
    assert "*RIGID BODY" in assembly
    assert "*NSET, NSET=REFNODE" in assembly
    assert "*SOLID SECTION, ELSET=EB1, MATERIAL=BRAIN" in assembly
    assert "*SOLID SECTION, ELSET=EB3, MATERIAL=CSF" in assembly
    assert "*SOLID SECTION, ELSET=EB4, MATERIAL=SKULL" in assembly

    # simulation.inp — master *INCLUDE file
    sim = (out / "simulation.inp").read_text()
    assert "assembly.inp" in sim
    assert "loads.inp" in sim
    assert "initial_conditions.inp" in sim
    assert "brain.inp" in sim
    assert "csf.inp" in sim
    assert "skull.inp" in sim
    assert "step.inp" in sim


def test_run_abaqus_writes_submit_script(hom_config, tmp_path):
    with patch("run_pipeline.subprocess.run") as mock_run:
        mock_run.return_value.stdout = "Your job 12345 has been submitted"
        run_abaqus(hom_config)

    script = (tmp_path / "submit.sh").read_text()
    assert f"#$ -pe omp {hom_config.n_cpus}" in script
    assert f"#$ -l h_rt={hom_config.h_rt}" in script
    assert f"#$ -N {hom_config.subject_id}" in script
    assert "module load simulia/2025" in script
    assert f"job={hom_config.subject_id}" in script
    assert "input=simulation.inp" in script
    assert "double=both" in script

    cmd = mock_run.call_args.args[0]
    assert cmd[0] == "qsub"
    assert str(tmp_path / "submit.sh") in cmd


def test_run_abaqus_uses_configured_env_and_modules(hom_config, tmp_path):
    hom_config.env_setup_script = "/custom/site/env.sh"
    hom_config.simulia_module = "simulia/2024"
    with patch("run_pipeline.subprocess.run") as mock_run:
        mock_run.return_value.stdout = "Your job 1 has been submitted"
        run_abaqus(hom_config)

    script = (tmp_path / "submit.sh").read_text()
    assert "source /custom/site/env.sh" in script
    assert "module load simulia/2024" in script


def test_run_abaqus_includes_vumat_when_set(hom_config, tmp_path):
    hom_config.vumat_path = "/path/to/vumat.f"
    with patch("run_pipeline.subprocess.run") as mock_run:
        mock_run.return_value.stdout = "Your job 99 has been submitted"
        run_abaqus(hom_config)

    script = (tmp_path / "submit.sh").read_text()
    assert "user=/path/to/vumat.f" in script


def test_run_pipeline_calls_steps_in_order(hom_config):
    with patch("run_pipeline.create_mesh") as mock_mesh, \
         patch("run_pipeline.generate_inp") as mock_gen,  \
         patch("run_pipeline.run_abaqus") as mock_abq:
        run_pipeline(hom_config)

    mock_mesh.assert_called_once_with(hom_config)
    mock_gen.assert_called_once_with(hom_config)
    mock_abq.assert_called_once_with(hom_config)

    assert mock_mesh.call_args == call(hom_config)
    assert mock_gen.call_args  == call(hom_config)
    assert mock_abq.call_args  == call(hom_config)
