from pathlib import Path

from pipeline.io.inp_writer import write_simulation_inp


def test_write_simulation_inp_homogeneous(tmp_path):
    output = tmp_path / "simulation.inp"
    material_files = {"brain": "brain.inp", "csf": "csf.inp", "skull": "skull.inp"}

    write_simulation_inp(output, "mesh.inp", "assembly.inp", "loads.inp",
                         "initial_conditions.inp", material_files, "step.inp")

    content = output.read_text()
    assert "*INCLUDE, INPUT=mesh.inp" in content
    assert "*INCLUDE, INPUT=assembly.inp" in content
    assert "*INCLUDE, INPUT=loads.inp" in content
    assert "*INCLUDE, INPUT=initial_conditions.inp" in content
    assert "*INCLUDE, INPUT=brain.inp" in content
    assert "*INCLUDE, INPUT=csf.inp" in content
    assert "*INCLUDE, INPUT=skull.inp" in content
    assert "*INCLUDE, INPUT=step.inp" in content


def test_write_simulation_inp_assembly_before_loads(tmp_path):
    output = tmp_path / "simulation.inp"
    material_files = {"brain": "brain.inp", "csf": "csf.inp", "skull": "skull.inp"}

    write_simulation_inp(output, "mesh.inp", "assembly.inp", "loads.inp",
                         "initial_conditions.inp", material_files, "step.inp")

    content = output.read_text()
    assert content.index("assembly.inp") < content.index("loads.inp")


def test_write_simulation_inp_heterogeneous(tmp_path):
    output = tmp_path / "simulation.inp"
    material_files = {"wm": "wm.inp", "gm": "gm.inp", "csf": "csf.inp", "skull": "skull.inp"}

    write_simulation_inp(output, "mesh.inp", "assembly.inp", "loads.inp",
                         "initial_conditions.inp", material_files, "step.inp")

    content = output.read_text()
    assert "*INCLUDE, INPUT=wm.inp" in content
    assert "*INCLUDE, INPUT=gm.inp" in content
    assert "*INCLUDE, INPUT=csf.inp" in content
    assert "*INCLUDE, INPUT=skull.inp" in content
    assert "*INCLUDE, INPUT=brain.inp" not in content


def test_write_simulation_inp_with_membranes(tmp_path):
    output = tmp_path / "simulation.inp"
    material_files = {"brain": "brain.inp", "csf": "csf.inp",
                      "skull": "skull.inp", "membranes": "membranes.inp"}

    write_simulation_inp(output, "mesh.inp", "assembly.inp", "loads.inp",
                         "initial_conditions.inp", material_files, "step.inp")

    content = output.read_text()
    assert "*INCLUDE, INPUT=membranes.inp" in content
