from pathlib import Path
from dataclasses import dataclass

VUMAT_PATH = Path(__file__).parent.parent / "vumat" / "vumat_O-USS_Model.f"

@dataclass
class Config:
    automesh: str
    abaqus: str
    npy_file: str
    mat_path: str
    output_dir: str
    material_model: str
    csf_model: str
    ref_dof: int
    time_interval_step: float
    subject_id: str
    motion_type: str
    algorithm: str
    brain_fidelity: str
    include_membranes: bool
    vumat_path: str | None = None
    n_cpus: int = 16
    h_rt: str = "12:00:00"
    mem_per_core: str = "4G"
    v_cutoff: float = 0.1
    dt_scale_factor: float = 1.0
    sim_end_ms: float = 0.0
    env_setup_script: str = "/ad/eng/bin/engenv.sh"
    simulia_module: str = "simulia/2025"
    intel_module: str = "intel/2024.0"


def parse_npy_filename(filename: str) -> dict:

    """
    Parses the Autovalidate_New output filename and extracts the encoded metadata.

    Args:
        filename : Filename of the .npy file (e.g. 'U01_HJF_0001_01-NR-synthseg-homogeneous-membranesON-combined.npy')

    Returns:
        A dict with keys: subject_id, motion_type, algorithm, brain_fidelity, include_membranes
    """

    string_list = filename.split("-")

    if len(string_list) != 6:
        raise ValueError("Filename has wrong name. Please rename file as 'subject_id-motion_type-algorithm-brain_fidelity-include_membranes-combined.npy")

    if string_list[4] == "membranesON":
        string_list[4] = True
    else:
        string_list[4] = False

    string_dict = {
        "subject_id": string_list[0],
        "motion_type": string_list[1],
        "algorithm": string_list[2],
        "brain_fidelity": string_list[3],
        "include_membranes": string_list[4]
    }

    return string_dict

def parse_config(raw_dict: dict) -> Config:

    """
    Parses and validates a raw config dict (as produced by tomllib) 
    and returns a Config dataclass. Raises ValueError if required 
    fields are missing or have invalid values.

    Args:
        raw_dict : A dict containing all the keywords to be passed in the config file

    Returns:
        A Config dataclass
    """

    if 'env' not in raw_dict:
        raise ValueError("Input Dict does not have the correct structure")

    if 'run' not in raw_dict:
        raise ValueError("Input Dict does not have the correct structure")

    if "automesh" not in raw_dict["env"]:
        raise ValueError("Automesh path has not been provided")

    if "abaqus" not in raw_dict["env"]:
        raise ValueError("Abaqus path has not been provided")

    if "npy_file" not in raw_dict["run"]:
        raise ValueError("Input .npy file has not been provided")

    if "mat_path" not in raw_dict["run"]:
        raise ValueError("Input .mat file has not been provided")

    if "output_dir" not in raw_dict["run"]:
        raise ValueError("Output directory has not been defined")

    if "material_model" not in raw_dict["run"]:
        raise ValueError("Material model has not been provided")

    material_model = raw_dict["run"]["material_model"].lower()
    valid_models = {
        "basilio", "menichetti", "alshareef", "upadhyay", "custom"
    }
    if material_model not in valid_models:
        raise ValueError(
            f"Wrong material model '{material_model}'. "
            "Please select one of: basilio, menichetti, alshareef, upadhyay, custom"
        )

    if "csf_model" not in raw_dict["run"]:
        raise ValueError("CSF model has not been provided")

    csf_model = raw_dict["run"]["csf_model"].lower()
    valid_csf_models = {"neo_hookean", "fluid"}
    if csf_model not in valid_csf_models:
        raise ValueError(
            f"Wrong csf_model '{csf_model}'. "
            "Please select one of: neo_hookean, fluid"
        )

    if "ref_dof" not in raw_dict["run"]:
        raise ValueError("Reference node DOF has not been provided")

    ref_dof = raw_dict["run"]["ref_dof"]
    if ref_dof not in {4, 5, 6}:
        raise ValueError("Wrong ref_dof! Must be 4 (X rotation), 5 (Y rotation), or 6 (Z rotation)")

    if "time_interval_step" not in raw_dict["run"]:
        raise ValueError("Time interval step has not been provided")

    npy_filename = Path(raw_dict["run"]["npy_file"]).name
    filename_fields = parse_npy_filename(npy_filename)

    return Config(
        automesh           = raw_dict["env"]["automesh"],
        abaqus             = raw_dict["env"]["abaqus"],
        npy_file           = raw_dict["run"]["npy_file"],
        mat_path           = raw_dict["run"]["mat_path"],
        output_dir         = raw_dict["run"]["output_dir"],
        material_model     = material_model,
        csf_model          = csf_model,
        ref_dof            = ref_dof,
        time_interval_step = raw_dict["run"]["time_interval_step"],
        subject_id         = filename_fields["subject_id"],
        motion_type        = filename_fields["motion_type"],
        algorithm          = filename_fields["algorithm"],
        brain_fidelity     = filename_fields["brain_fidelity"],
        include_membranes  = filename_fields["include_membranes"],
        vumat_path         = str(VUMAT_PATH) if material_model == "upadhyay" else None,
        n_cpus             = raw_dict["run"].get("n_cpus", 16),
        h_rt               = raw_dict["run"].get("h_rt", "12:00:00"),
        mem_per_core       = raw_dict["run"].get("mem_per_core", "4G"),
        v_cutoff           = raw_dict["run"].get("v_cutoff", 0.1),
        dt_scale_factor    = raw_dict["run"].get("dt_scale_factor", 1.0),
        sim_end_ms         = raw_dict["run"].get("sim_end_ms", 0.0),
        env_setup_script   = raw_dict["run"].get("env_setup_script", "/ad/eng/bin/engenv.sh"),
        simulia_module     = raw_dict["run"].get("simulia_module", "simulia/2025"),
        intel_module       = raw_dict["run"].get("intel_module", "intel/2024.0"),
    )
