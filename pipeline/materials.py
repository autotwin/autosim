from dataclasses import dataclass
from pipeline.config import Config
from pipeline.preprocessing.inp_builder import (
    format_neo_hookean_prony_material_lines,
    format_ogden_prony_material_lines,
    format_lve_material_lines,
    format_elastic_material_lines,
    format_vumat_material_lines,
    format_gruneisen_eos_material_lines,
)


@dataclass
class NeoHookeanPronyParams:
    density: float
    C10: float
    D1: float
    prony: list[tuple[float, float]]
    moduli: str = "INSTANTANEOUS"

@dataclass
class OgdenPronyParams:
    density: float
    mu: float
    alpha: float
    D1: float
    prony: list[tuple[float, float]]

@dataclass
class LVEParams:
    density: float
    G0: float
    nu: float
    prony: list[tuple[float, float]]

@dataclass
class ElasticParams:
    density: float
    E: float
    nu: float

@dataclass
class VUMATParams:
    density: float
    mu_inf: float
    alpha: float
    k11: float
    k21: float
    c21: float
    Kbulk: float

@dataclass
class GruneisenEOSParams:
    density: float # tonne/mm^3
    c0: float # reference speed of sound (mm/s)
    s: float  # linear Hugoniot slope coefficient (dimensionless)
    gamma0: float # Gruneisen ratio at reference state (dimensionless)
    mu: float # dynamic viscosity (MPa*s)


# ── Fixed materials (mm | tonne | s | MPa) ────────────────────────────────────

CSF_MATERIAL_FLUID = GruneisenEOSParams(
    # Zhou, Li & Kleiven 2019
    # DOI: 10.1007/s10237-018-1074-z
    density = 1.0e-9,
    c0 = 1.4829e6,
    s = 2.1057,
    gamma0 = 1.2,
    mu = 1.0e-9,
)

CSF_MATERIAL_NH = NeoHookeanPronyParams(
    # Mao et al. 2013
    # DOI: 10.1115/1.4025101
    density = 1.133e-9,
    C10 = 5.0e-4,
    D1  = 9.132e-4,
    prony = [(0.8, 0.00125)],
    moduli = "LONG TERM",
)

SKULL_MATERIAL = ElasticParams(
    density = 2.07e-9,
    E = 3280.0,
    nu = 0.3
)

MEMBRANE_MATERIAL = ElasticParams(
    # Alshareef et al. 2021 — Falx & Tentorium
    # DOI: 10.1016/j.brain.2021.100038
    density = 1.133e-9,
    E = 31.5,
    nu = 0.45
)


BRAIN_WM = {

    "menichetti": NeoHookeanPronyParams(
        # Menichetti et al. 2020 — Corona Radiata
        # DOI: 10.1016/j.ijengsci.2020.103355
        density = 1.04e-9,
        C10 = 3.815e-3,
        D1 = 3.11e-2,
        prony = [(0.57, 0.020), (0.22, 0.31)]
    ),

    "alshareef": LVEParams(
        # Alshareef et al. 2021 — Corona Radiata (heterogeneous WM region)
        # DOI: 10.1016/j.brain.2021.100038
        density = 1.04e-9,
        G0 = 9.2e-3,
        nu = 0.49,
        prony = [(0.76, 9.0e-4), (0.04, 0.0289)]
    ),

    "alshareef_hom": LVEParams(
        # Alshareef et al. 2021 — whole-brain homogeneous average (Table 3)
        # DOI: 10.1016/j.brain.2021.100038
        density = 1.04e-9,
        G0 = 6.94e-3,
        nu = 0.49,
        prony = [(0.74, 1.00e-3), (0.050, 27.7e-3)]
    ),

    "basilio": OgdenPronyParams(
        # Basilio et al. 2024 — Cortex White Matter
        # DOI: 10.1007/s10439-023-03407-7
        density = 1.04e-9,
        mu = 4.265e-4,
        alpha = 17.6,
        D1 = 2.0,
        prony = [(0.6282, 0.0196), (0.2060, 0.5817), (0.1645, 38.5)]
    ),

    "upadhyay": VUMATParams(
        # Upadhyay et al. 2022 — Corona Radiata
        # DOI: 10.1098/rsif.2022.0561
        density = 1.04e-9,
        mu_inf = 1.84e-3,
        alpha = -3.47,
        k11 = -2.65e-6,
        k21 = 6.0969e-4,
        c21 = 0.62,
        Kbulk = 2190.0
    ),

    "custom": None,
}


BRAIN_GM = {

    "menichetti": NeoHookeanPronyParams(
        # Menichetti et al. 2020 — SFCx Cortex
        # DOI: 10.1016/j.ijengsci.2020.103355
        density = 1.04e-9,
        C10 = 3.22e-3,
        D1 = 3.11e-2,
        prony = [(0.49, 0.017), (0.20, 0.30)]
    ),

    "alshareef": LVEParams(
        # Alshareef et al. 2021 — Deep GM
        # DOI: 10.1016/j.brain.2021.100038
        density = 1.04e-9,
        G0 = 10.25e-3,
        nu = 0.49,
        prony = [(0.75, 9.4e-4), (0.05, 0.0293)]
    ),

    "basilio": OgdenPronyParams(
        # Basilio et al. 2024 — Cortex Grey Matter
        # DOI: 10.1007/s10439-023-03407-7
        density = 1.04e-9,
        mu = 2.313e-4,
        alpha = 15.0,
        D1 = 2.0,
        prony = [(0.6527, 0.0515), (0.3446, 26.9)]
    ),

    "upadhyay": VUMATParams(
        # Upadhyay et al. 2022 — Deep GM
        # DOI: 10.1098/rsif.2022.0561
        density = 1.04e-9,
        mu_inf = 2.05e-3,
        alpha = 4.92,
        k11 = -1.49e-6,
        k21 = 6.1505e-4,
        c21 = 0.61,
        Kbulk = 2190.0
    ),


    "custom": None,
}



def get_materials(config: Config) -> dict:

    """
    Returns material parameters for all element sets based on the Config.

    Args:
        config: Parsed Config dataclass

    Returns:
        dict with keys "brain" or ("wm", "gm"), plus "csf", "skull",
        and optionally "membranes"
    """

    materials = {}

    if config.brain_fidelity == "homogeneous":
        wm_key = "alshareef_hom" if config.material_model == "alshareef" else config.material_model
        materials["brain"] = BRAIN_WM[wm_key]
    else:
        materials["wm"] = BRAIN_WM[config.material_model]
        materials["gm"] = BRAIN_GM[config.material_model]

    if config.csf_model == "neo_hookean":
        materials["csf"] = CSF_MATERIAL_NH
    elif config.csf_model == "fluid":
        materials["csf"] = CSF_MATERIAL_FLUID
    else:
        raise ValueError(
            f"Wrong csf_model '{config.csf_model}'. "
            "Please select one of: neo_hookean, fluid"
        )
    materials["skull"] = SKULL_MATERIAL

    if config.include_membranes:
        materials["membranes"] = MEMBRANE_MATERIAL

    return materials


def format_material(part_name: str, params) -> list:

    """
    Dispatches to the correct Abaqus material formatting function
    based on the type of the params dataclass.

    Args:
        part_name : Abaqus material name (e.g. "BRAIN", "CSF", "SKULL")
        params : One of the material dataclass instances

    Returns:
        List of formatted .inp lines
    """

    if isinstance(params, NeoHookeanPronyParams):
        return format_neo_hookean_prony_material_lines(
            part_name, params.density, params.C10, params.D1, params.prony, params.moduli
        )
    elif isinstance(params, OgdenPronyParams):
        return format_ogden_prony_material_lines(
            part_name, params.density, params.mu, params.alpha, params.D1, params.prony
        )
    elif isinstance(params, LVEParams):
        return format_lve_material_lines(
            part_name, params.density, params.G0, params.nu, params.prony
        )
    elif isinstance(params, ElasticParams):
        return format_elastic_material_lines(
            part_name, params.density, params.E, params.nu
        )
    elif isinstance(params, VUMATParams):
        return format_vumat_material_lines(
            part_name, params.density, params.mu_inf, params.Kbulk,
            params.alpha, params.k11, params.k21, params.c21
        )
    elif isinstance(params, GruneisenEOSParams):
        return format_gruneisen_eos_material_lines(
            part_name, params.density, params.c0, params.s, params.gamma0, params.mu
        )
    elif params is None:
        raise ValueError(
            f"No material parameters defined for '{part_name}'. "
            "For custom models, provide your own material card."
        )
    else:
        raise ValueError(f"Unknown material params type: {type(params)}")
