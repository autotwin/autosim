import argparse
import os
import subprocess
import tomllib
from pathlib import Path

from pipeline.config import Config, parse_config
from pipeline.io.npy_io import load_npy
from pipeline.io.nifti_io import get_voxel_size_from_npy
from pipeline.io.mat_io import load_pva_mat
from pipeline.io.inp_writer import write_text_file, write_initial_conditions_file, write_simulation_inp
from pipeline.io.csv_io import write_frame_times_csv
from pipeline.preprocessing.mesh import compute_cog, translation_to_origin, create_automesh_command
from pipeline.preprocessing.mesh_schema import mesh_mapping
from pipeline.preprocessing.loads import extract_window, to_abaqus_time, compute_frame_times, format_amplitude_lines, find_last_active_frame
from pipeline.preprocessing.initial_conditions import format_rotating_velocity_lines, format_ref_node_line
from pipeline.preprocessing.boundary_conditions import format_boundary_conditions_lines
from pipeline.preprocessing.inp_builder import format_assembly_lines, format_output_field_lines, format_step_lines, format_time_points_lines, format_nodal_field_output_lines
from pipeline.materials import get_materials, format_material


REMOVE_IDS  = [0]
REF_NODE_ID = 9999999


def create_mesh(config: Config):

    npy_array = load_npy(config.npy_file)
    voxel_size = get_voxel_size_from_npy(Path(config.npy_file))

    print(f"[create_mesh] Voxel size from companion NIfTI: {voxel_size} mm")

    cog = compute_cog(npy_array, REMOVE_IDS)
    tx, ty, tz = translation_to_origin(voxel_size, cog)

    output_mesh = Path(config.output_dir) / f"{config.subject_id}.inp"

    command = create_automesh_command(
        config.automesh,
        config.npy_file,
        output_mesh,
        REMOVE_IDS,
        voxel_size,
        tx, ty, tz
    )

    subprocess.run(command, check=True)


def generate_inp(config: Config):

    out = Path(config.output_dir)
    print(f"\n[generate_inp] Subject: {config.subject_id} | {config.brain_fidelity} | membranes={'ON' if config.include_membranes else 'OFF'} | model: {config.material_model}")

    # ── 1. Load kinematics ────────────────────────────────────────────────────
    print("[1/6] Loading kinematics from .mat file...")
    time_ms, velocity, frame_center, frame_start, frame_end = load_pva_mat(config.mat_path)

    t_start_ms = frame_start[0]
    t_end_ms_orig = float(frame_end[-1])

    last_idx = find_last_active_frame(frame_start, frame_end, time_ms, velocity, config.v_cutoff)

    if config.sim_end_ms > 0:
        cap_idx = max((i for i in range(last_idx + 1) if frame_center[i] <= config.sim_end_ms), default=0)
        last_idx = min(last_idx, cap_idx)

    t_end_ms = float(frame_end[last_idx])
    n_trimmed = len(frame_center) - (last_idx + 1)

    print(f"      Simulation window: {t_start_ms:.1f} → {t_end_ms:.1f} ms  ({(t_end_ms - t_start_ms)/1000:.4f} s)", end="")
    if config.sim_end_ms > 0 and last_idx < len(frame_center) - 1:
        print(f"  [capped at sim_end_ms={config.sim_end_ms:.0f} ms]")
    elif n_trimmed > 0:
        print(f"  [trimmed {n_trimmed} dead frames, saved {t_end_ms_orig - t_end_ms:.1f} ms, v_cutoff={config.v_cutoff} rad/s]")
    else:
        print()

    # ── 2. Loads ──────────────────────────────────────────────────────────────
    print("[2/6] Writing loads.inp and frame_times.csv...")
    t_win_ms, v_win = extract_window(time_ms, velocity, t_start_ms, t_end_ms)
    t_abq_s = to_abaqus_time(t_win_ms, t_start_ms, t_end_ms)

    write_text_file(out / "loads.inp", format_amplitude_lines(t_abq_s, v_win))

    comp_frames = compute_frame_times(
        frame_center[:last_idx + 1],
        frame_start[:last_idx + 1],
        frame_end[:last_idx + 1],
        t_start_ms,
    )
    write_frame_times_csv(out, comp_frames)
    print(f"      {len(t_win_ms)} amplitude points | {last_idx + 1} of {len(frame_center)} comparison frames")

    # ── 3. Initial conditions ─────────────────────────────────────────────────
    print("[3/6] Writing initial_conditions.inp...")
    omega_0 = v_win[0]
    ic_lines = format_rotating_velocity_lines(["ALLNODES"], omega_0, config.ref_dof)
    ref_line = format_ref_node_line(REF_NODE_ID, config.ref_dof, omega_0)
    write_initial_conditions_file(out / "initial_conditions.inp", ic_lines, ref_line)
    print(f"      omega_0 = {omega_0:.6f} rad/s (DOF {config.ref_dof}) | ROTATING VELOCITY on ALLNODES")

    # ── 4. Material files ─────────────────────────────────────────────────────
    print("[4/6] Writing material .inp files...")
    materials = get_materials(config)
    material_files = {}
    for tissue, params in materials.items():
        lines = format_material(tissue.upper(), params)
        fpath = out / f"{tissue}.inp"
        write_text_file(fpath, lines)
        material_files[tissue] = str(fpath)
        print(f"      {tissue}.inp  ({type(params).__name__})")

    # ── 4b. Assembly block (ref node, rigid body, section assignments) ────────
    schema = mesh_mapping(config.brain_fidelity, config.include_membranes)
    skull_set = schema["skull"]

    elset_to_material = {}
    for tissue in materials:
        schema_key = "wm" if tissue == "brain" else tissue
        elset = schema[schema_key]
        if elset is not None:
            elset_to_material[elset] = tissue.upper()

    assembly_lines = format_assembly_lines(elset_to_material, skull_set, REF_NODE_ID)
    write_text_file(out / "assembly.inp", assembly_lines)

    # ── 5. Step ───────────────────────────────────────────────────────────────
    print("[5/6] Writing step.inp...")
    simulation_time = (t_end_ms - t_start_ms) / 1000.0

    elsets = [v for v in schema.values() if v is not None and v != skull_set]

    comparison_nsets = [
        f"{tissue.upper()}_NODES"
        for tissue in materials
        if tissue not in ("membranes", "skull")
    ]
    tp_lines = format_time_points_lines([f["abaqus_time_s"] for f in comp_frames])
    nodal_output_lines = format_nodal_field_output_lines(comparison_nsets)

    boundary_lines = format_boundary_conditions_lines(REF_NODE_ID, config.ref_dof)
    output_field_lines = format_output_field_lines(config.time_interval_step, elsets, nsets=comparison_nsets)
    step_lines = format_step_lines(simulation_time, boundary_lines,
                                           output_field_lines + nodal_output_lines,
                                           pre_step_lines=tp_lines,
                                           dt_scale_factor=config.dt_scale_factor)

    write_text_file(out / "step.inp", step_lines)
    print(f"      simulation time: {simulation_time:.4f} s | output every {config.time_interval_step*1000:.1f} ms | elsets: {elsets} | nodal nsets: {comparison_nsets}")

    # ── 6. Master simulation.inp ──────────────────────────────────────────────
    print("[6/6] Writing simulation.inp (master *INCLUDE file)...")
    mesh_inp = out / f"{config.subject_id}.inp"
    write_simulation_inp(
        output_path = out / "simulation.inp",
        mesh_inp = str(mesh_inp),
        assembly_inp = str(out / "assembly.inp"),
        loads_inp = str(out / "loads.inp"),
        initial_conditions_inp = str(out / "initial_conditions.inp"),
        material_files = material_files,
        step_inp = str(out / "step.inp"),
    )
    print(f"\n[generate_inp] Done. All files written to: {out}")


def run_abaqus(config: Config):

    out = Path(config.output_dir)
    job = config.subject_id

    abaqus_cmd = f"abaqus job={job} input=simulation.inp double=both cpus=$NSLOTS interactive"
    if config.vumat_path:
        abaqus_cmd += f" user={config.vumat_path}"

    intel_module = f"module load {config.intel_module}" if config.vumat_path else ""

    # NOTE: This submit script targets SGE (qsub/#$) and BU SCC's module
    # environment. Other institutions will likely need to adapt the
    # scheduler directives below for their own system (e.g. Slurm/PBS).
    submit_script = out / "submit.sh"
    submit_script.write_text(f"""\
#!/bin/bash -l
#$ -pe omp {config.n_cpus}
#$ -l h_rt={config.h_rt}
#$ -l mem_per_core={config.mem_per_core}
#$ -N {job}
#$ -o {out}/{job}.log
#$ -e {out}/{job}.err
#$ -cwd

source {config.env_setup_script}
module load {config.simulia_module}
{intel_module}

cd {out}

{abaqus_cmd}
""")

    print(f"\n[run_abaqus] Submitting qsub job: {job}")
    print(f"             script : {submit_script}")
    print(f"             cpus   : {config.n_cpus}  |  h_rt: {config.h_rt}  |  mem: {config.mem_per_core}/core")

    result = subprocess.run(["qsub", str(submit_script)], check=True,
                            capture_output=True, text=True)
    print(f"             {result.stdout.strip()}")


def run_pipeline(config: Config):

    print(f"\n{'='*60}")
    print(f" autosim pipeline — {config.subject_id}")
    print(f"{'='*60}")

    print("\n[Step 1/3] Meshing...")
    create_mesh(config)

    print("\n[Step 2/3] Building .inp files...")
    generate_inp(config)

    print("\n[Step 3/3] Running Abaqus...")
    run_abaqus(config)

    print(f"\n{'='*60}")
    print(f" Done — {config.subject_id}")
    print(f"{'='*60}\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="autosim pipeline")
    parser.add_argument("--config", required=True, help="Path to TOML config file")
    args = parser.parse_args()

    with open(args.config, "rb") as f:
        raw = tomllib.load(f)

    cfg = parse_config(raw)
    Path(cfg.output_dir).mkdir(parents=True, exist_ok=True)

    run_pipeline(cfg)
