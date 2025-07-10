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

# --- Déballage de la configuration en variables au niveau du module pour un accès facile ---

# Constantes physiques
_phys_const = _config.get("physical_constants", {})
DELAYED_NEUTRON_FRACTION = _phys_const.get("DELAYED_NEUTRON_FRACTION", 0.0065)
PROMPT_NEUTRON_LIFETIME = _phys_const.get("PROMPT_NEUTRON_LIFETIME", 2.0e-5)
EFFECTIVE_DECAY_CONSTANT = _phys_const.get("EFFECTIVE_DECAY_CONSTANT", 0.1)
NEUTRONS_PER_THERMAL_FISSION_U235 = _phys_const.get("NEUTRONS_PER_THERMAL_FISSION_U235", 2.43)
BESSEL_J0_FIRST_ZERO = _phys_const.get("BESSEL_J0_FIRST_ZERO", 2.405)
CELSIUS_TO_KELVIN = _phys_const.get("CELSIUS_TO_KELVIN", 273.15)

# Coefficients du modèle des quatre facteurs
_four_factors = _config.get("four_factors", {})

_eta = _four_factors.get("eta", {})
ETA_BASE = _eta.get("BASE", 2.0)
ETA_ENRICHMENT_COEFF = _eta.get("ENRICHMENT_COEFF", 0.1)
ETA_ENRICHMENT_REF = _eta.get("ENRICHMENT_REF", 3.0)
ETA_ENRICHMENT_SCALE = _eta.get("ENRICHMENT_SCALE", 2.0)

EPSILON = _four_factors.get("epsilon", 1.03)

_p = _four_factors.get("p", {})
P_BASE = _p.get("BASE", 0.75)
P_REF_TEMP_K = _p.get("REF_TEMP_K", 873.15)
P_DOPPLER_COEFF = _p.get("DOPPLER_COEFF", 0.008)
P_MOD_TEMP_COEFF = _p.get("MOD_TEMP_COEFF", 0.0015)
P_REF_MOD_TEMP_C = _p.get("REF_MOD_TEMP_C", 300.0)

_f = _four_factors.get("f", {})
F_BASE = _f.get("BASE", 0.71)
F_BASE_ABS_RATIO = _f.get("BASE_ABS_RATIO", 0.408)
F_REF_MOD_TEMP_C = _f.get("REF_MOD_TEMP_C", 300.0)
F_CONTROL_ROD_WORTH = _f.get("CONTROL_ROD_WORTH", 0.26)
F_BORON_WORTH_PER_PPM = _f.get("BORON_WORTH_PER_PPM", 2.8e-5)
F_MOD_TEMP_ABS_COEFF = _f.get("MOD_TEMP_ABS_COEFF", 0.003)

# --- Facteurs de fuite neutronique ---
_leakage = _config.get("neutron_leakage", {})
CORE_HEIGHT_M = _leakage.get("CORE_HEIGHT_M", 4.0)
CORE_DIAMETER_M = _leakage.get("CORE_DIAMETER_M", 3.0)
THERMAL_DIFFUSION_AREA_M2 = _leakage.get("THERMAL_DIFFUSION_AREA_M2", 0.0064)
FAST_DIFFUSION_AREA_M2 = _leakage.get("FAST_DIFFUSION_AREA_M2", 0.0097)
MODERATOR_DENSITY_COEFF = _leakage.get("MODERATOR_DENSITY_COEFF", 8.0e-4)
CONTROL_ROD_EFFECT_COEFF = _leakage.get("CONTROL_ROD_EFFECT_COEFF", 10.0)

# Thermo-hydraulique
_thermo = _config.get("thermal_hydraulics", {})
POWER_TO_FUEL_TEMP_COEFF = _thermo.get("POWER_TO_FUEL_TEMP_COEFF", 3.0)

# Calcul du temps de doublement
_doubling = _config.get("doubling_time", {})
DOUBLING_TIME_COEFF = _doubling.get("DOUBLING_TIME_COEFF", 80.0)

# Dynamique Xénon-135
_xenon = _config.get("xenon_dynamics", {})
IODINE_YIELD = _xenon.get("IODINE_YIELD", 0.064)
XENON_YIELD_DIRECT = _xenon.get("XENON_YIELD_DIRECT", 0.003)
IODINE_DECAY_CONSTANT = _xenon.get("IODINE_DECAY_CONSTANT", 2.87e-5)  # s^-1
XENON_DECAY_CONSTANT = _xenon.get("XENON_DECAY_CONSTANT", 2.11e-5)    # s^-1
XENON_ABSORPTION_CROSS_SECTION = _xenon.get("XENON_ABSORPTION_CROSS_SECTION", 2.65e6)  # barns
THERMAL_FLUX_NOMINAL = _xenon.get("THERMAL_FLUX_NOMINAL", 3.0e13)     # n/cm²/s
FISSION_RATE_COEFF = _xenon.get("FISSION_RATE_COEFF", 1.0e-6)
XENON_REACTIVITY_CONVERSION_FACTOR = _xenon.get("XENON_REACTIVITY_CONVERSION_FACTOR", 1e5)

# Configuration de l'interface et des paramètres
gui_settings = _config.get("gui_settings", {})
parameters_config = _config.get("parameters_config", {})

# Préréglages par défaut
PRESETS = _config.get("presets", {})

# État par défaut
default_state = _config.get("default_state", {}) 