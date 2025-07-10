"""
Configuration file for the ReactorModel.

This module loads the reactor's physical and operational parameters
from the 'config.json' file located in the project's root directory.
"""

import json
import os
from pathlib import Path

def _load_config():
    """
    Loads configuration from the project's root config.json file.
    The path is determined relative to this file's location.
    """
    try:
        # Ce fichier est dans src/model/, donc nous remontons de trois niveaux jusqu'à la racine du projet.
        config_path = Path(__file__).resolve().parent.parent.parent / 'config.json'
        with config_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Configuration file 'config.json' not found in project root. Make sure it exists. Original error: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file 'config.json'. Please check its syntax. Original error: {e}")

def get_project_root():
    """Get the project root directory path."""
    return Path(__file__).resolve().parent.parent.parent

_config = _load_config()

try:
    # --- Déballage de la configuration en variables au niveau du module pour un accès facile ---
    # Cette approche est stricte : si une clé est manquante dans config.json,
    # le programme lèvera une exception KeyError au démarrage, ce qui garantit
    # que config.json est la seule source de vérité et évite les erreurs silencieuses.

    # Constantes physiques
    _phys_const = _config["physical_constants"]
    DELAYED_NEUTRON_FRACTION = _phys_const["DELAYED_NEUTRON_FRACTION"]
    PROMPT_NEUTRON_LIFETIME = _phys_const["PROMPT_NEUTRON_LIFETIME"]
    EFFECTIVE_DECAY_CONSTANT = _phys_const["EFFECTIVE_DECAY_CONSTANT"]
    NEUTRONS_PER_THERMAL_FISSION_U235 = _phys_const["NEUTRONS_PER_THERMAL_FISSION_U235"]
    BESSEL_J0_FIRST_ZERO = _phys_const["BESSEL_J0_FIRST_ZERO"]
    CELSIUS_TO_KELVIN = _phys_const["CELSIUS_TO_KELVIN"]

    # Constantes de conversion d'unités
    _unit_conversions = _config["unit_conversions"]
    HOURS_TO_SECONDS = _unit_conversions["HOURS_TO_SECONDS"]
    BARNS_TO_CM2 = _unit_conversions["BARNS_TO_CM2"]
    REACTIVITY_TO_PCM = _unit_conversions["REACTIVITY_TO_PCM"]
    PERCENT_TO_FRACTION = _unit_conversions["PERCENT_TO_FRACTION"]

    # Coefficients du modèle des quatre facteurs
    _four_factors = _config["four_factors"]

    _eta = _four_factors["eta"]
    ETA_BASE = _eta["BASE"]
    ETA_ENRICHMENT_COEFF = _eta["ENRICHMENT_COEFF"]
    ETA_ENRICHMENT_REF = _eta["ENRICHMENT_REF"]
    ETA_ENRICHMENT_SCALE = _eta["ENRICHMENT_SCALE"]

    EPSILON = _four_factors["epsilon"]

    _p = _four_factors["p"]
    P_BASE = _p["BASE"]
    P_REF_TEMP_K = _p["REF_TEMP_K"]
    P_DOPPLER_COEFF = _p["DOPPLER_COEFF"]
    P_MOD_TEMP_COEFF = _p["MOD_TEMP_COEFF"]
    P_REF_MOD_TEMP_C = _p["REF_MOD_TEMP_C"]

    _f = _four_factors["f"]
    F_BASE = _f["BASE"]
    F_BASE_ABS_RATIO = _f["BASE_ABS_RATIO"]
    F_REF_MOD_TEMP_C = _f["REF_MOD_TEMP_C"]
    F_CONTROL_ROD_WORTH = _f["CONTROL_ROD_WORTH"]
    F_BORON_WORTH_PER_PPM = _f["BORON_WORTH_PER_PPM"]
    F_MOD_TEMP_ABS_COEFF = _f["MOD_TEMP_ABS_COEFF"]

    # --- Facteurs de fuite neutronique ---
    _leakage = _config["neutron_leakage"]
    CORE_HEIGHT_M = _leakage["CORE_HEIGHT_M"]
    CORE_DIAMETER_M = _leakage["CORE_DIAMETER_M"]
    THERMAL_DIFFUSION_AREA_M2 = _leakage["THERMAL_DIFFUSION_AREA_M2"]
    FAST_DIFFUSION_AREA_M2 = _leakage["FAST_DIFFUSION_AREA_M2"]
    MODERATOR_DENSITY_COEFF = _leakage["MODERATOR_DENSITY_COEFF"]
    CONTROL_ROD_EFFECT_COEFF = _leakage["CONTROL_ROD_EFFECT_COEFF"]

    # Thermo-hydraulique
    _thermo = _config["thermal_hydraulics"]
    POWER_TO_FUEL_TEMP_COEFF = _thermo["POWER_TO_FUEL_TEMP_COEFF"]

    # Calcul du temps de doublement
    _doubling = _config["doubling_time"]
    DOUBLING_TIME_COEFF = _doubling["DOUBLING_TIME_COEFF"]

    # Dynamique Xénon-135
    _xenon = _config["xenon_dynamics"]
    IODINE_YIELD = _xenon["IODINE_YIELD"]
    XENON_YIELD_DIRECT = _xenon["XENON_YIELD_DIRECT"]
    IODINE_DECAY_CONSTANT = _xenon["IODINE_DECAY_CONSTANT"]  # s^-1
    XENON_DECAY_CONSTANT = _xenon["XENON_DECAY_CONSTANT"]    # s^-1
    XENON_ABSORPTION_CROSS_SECTION = _xenon["XENON_ABSORPTION_CROSS_SECTION"]  # barns
    THERMAL_FLUX_NOMINAL = _xenon["THERMAL_FLUX_NOMINAL"]     # n/cm²/s
    FISSION_RATE_COEFF = _xenon["FISSION_RATE_COEFF"]
    XENON_REACTIVITY_CONVERSION_FACTOR = _xenon["XENON_REACTIVITY_CONVERSION_FACTOR"]

    # Configuration de l'interface et des paramètres
    gui_settings = _config["gui_settings"]
    parameters_config = _config["parameters_config"]

    # Préréglages par défaut
    PRESETS = _config["presets"]

    # État par défaut
    default_state = _config["default_state"]

except KeyError as e:
    raise KeyError(
        f"Clé de configuration manquante ou incorrecte dans config.json : {e}. "
        "Assurez-vous que la structure du fichier est complète et valide."
    ) 