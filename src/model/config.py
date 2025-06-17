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
        # This file is in src/model/, so we go up three levels to the project root.
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

def setup_openmc_data():
    """
    Setup OpenMC cross sections path automatically if not already set.
    Returns True if successfully configured, False otherwise.
    """
    if 'OPENMC_CROSS_SECTIONS' in os.environ:
        return True
    
    project_root = get_project_root()
    openmc_config = _config.get("openmc", {})
    data_path = openmc_config.get("data_path", "data/endfb-vii.1-hdf5")
    cross_sections_file = openmc_config.get("cross_sections_file", "cross_sections.xml")
    
    cross_sections_path = project_root / data_path / cross_sections_file
    
    if cross_sections_path.exists():
        os.environ['OPENMC_CROSS_SECTIONS'] = str(cross_sections_path)
        print(f"✓ Configuration OpenMC automatique: {cross_sections_path}")
        return True
    else:
        print(f"⚠ Données OpenMC non trouvées dans: {cross_sections_path}")
        return False

_config = _load_config()

# --- OpenMC Configuration ---
_openmc_config = _config.get("openmc", {})
OPENMC_DATA_PATH = _openmc_config.get("data_path", "data/endfb-vii.1-hdf5")
OPENMC_CROSS_SECTIONS_FILE = _openmc_config.get("cross_sections_file", "cross_sections.xml")

# --- Unpack configuration into module-level variables for easy access ---

# Physical constants
_phys_const = _config.get("physical_constants", {})
DELAYED_NEUTRON_FRACTION = _phys_const.get("DELAYED_NEUTRON_FRACTION", 0.0065)
PROMPT_NEUTRON_LIFETIME = _phys_const.get("PROMPT_NEUTRON_LIFETIME", 2.0e-5)

# Four factors model coefficients
_four_factors = _config.get("four_factors", {})

_eta = _four_factors.get("eta", {})
ETA_BASE = _eta.get("BASE", 2.0)
ETA_ENRICHMENT_COEFF = _eta.get("ENRICHMENT_COEFF", 0.1)

EPSILON = _four_factors.get("epsilon", 1.03)

_p = _four_factors.get("p", {})
P_BASE = _p.get("BASE", 0.75)
P_REF_TEMP_K = _p.get("REF_TEMP_K", 873.15)
P_DOPPLER_COEFF = _p.get("DOPPLER_COEFF", 0.008)

_f = _four_factors.get("f", {})
F_BASE = _f.get("BASE", 0.71)
F_BASE_ABS_RATIO = _f.get("BASE_ABS_RATIO", 0.408)
F_REF_MOD_TEMP_C = _f.get("REF_MOD_TEMP_C", 300.0)
F_CONTROL_ROD_WORTH = _f.get("CONTROL_ROD_WORTH", 0.26)
F_BORON_WORTH_PER_PPM = _f.get("BORON_WORTH_PER_PPM", 2.8e-5)
F_MOD_TEMP_ABS_COEFF = _f.get("MOD_TEMP_ABS_COEFF", 0.003)

# --- Neutron Leakage Factors ---
_leakage = _config.get("neutron_leakage", {})
CORE_HEIGHT_M = _leakage.get("CORE_HEIGHT_M", 4.0)
CORE_DIAMETER_M = _leakage.get("CORE_DIAMETER_M", 3.0)
THERMAL_DIFFUSION_AREA_M2 = _leakage.get("THERMAL_DIFFUSION_AREA_M2", 0.0064)
FAST_DIFFUSION_AREA_M2 = _leakage.get("FAST_DIFFUSION_AREA_M2", 0.0097)
MODERATOR_DENSITY_COEFF = _leakage.get("MODERATOR_DENSITY_COEFF", 8.0e-4)

# Thermal-Hydraulics
_thermo = _config.get("thermal_hydraulics", {})
POWER_TO_FUEL_TEMP_COEFF = _thermo.get("POWER_TO_FUEL_TEMP_COEFF", 3.0)

# Doubling time calculation
_doubling = _config.get("doubling_time", {})
DOUBLING_TIME_COEFF = _doubling.get("DOUBLING_TIME_COEFF", 80.0)

# Default presets
PRESETS = _config.get("presets", {}) 