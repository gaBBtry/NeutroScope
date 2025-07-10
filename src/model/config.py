"""
Configuration loader for NeutroScope.

This module provides a simple function to load configuration directly from config.json
without creating redundant variable definitions.
"""

import json
import os
from pathlib import Path

def load_config():
    """
    Loads configuration from the project's root config.json file.
    The path is determined relative to this file's location.
    
    Returns:
        dict: The complete configuration dictionary from config.json
    """
    try:
        # Ce fichier est dans src/model/, donc nous remontons de deux niveaux jusqu'à la racine du projet.
        config_path = Path(__file__).resolve().parent.parent.parent / 'config.json'
        with config_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Configuration file 'config.json' not found in project root. Make sure it exists. Original error: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file 'config.json'. Please check its syntax. Original error: {e}")

# Load configuration once at module import
_config = load_config()

def get_config():
    """
    Returns the loaded configuration dictionary.
    
    Returns:
        dict: The complete configuration dictionary
    """
    return _config

def get_physical_constants():
    """
    Returns the physical constants section.
    
    Returns:
        dict: Physical constants from config.json
    """
    return _config.get("physical_constants", {})

def get_four_factors():
    """
    Returns the four factors configuration section.
    
    Returns:
        dict: Four factors configuration from config.json
    """
    return _config.get("four_factors", {})

def get_neutron_leakage():
    """
    Returns the neutron leakage configuration section.
    
    Returns:
        dict: Neutron leakage configuration from config.json
    """
    return _config.get("neutron_leakage", {})

def get_control_kinetics():
    """
    Returns the control kinetics configuration section.
    
    Returns:
        dict: Control kinetics configuration from config.json
    """
    return _config.get("control_kinetics", {})

def get_thermal_kinetics():
    """
    Returns the thermal kinetics configuration section.
    
    Returns:
        dict: Thermal kinetics configuration from config.json
    """
    return _config.get("thermal_kinetics", {})

def get_doubling_time():
    """
    Returns the doubling time configuration section.
    
    Returns:
        dict: Doubling time configuration from config.json
    """
    return _config.get("doubling_time", {})

def get_xenon_dynamics():
    """
    Returns the xenon dynamics configuration section.
    
    Returns:
        dict: Xenon dynamics configuration from config.json
    """
    return _config.get("xenon_dynamics", {})

def get_control_rod_groups():
    """
    Returns the control rod groups configuration section.
    
    Returns:
        dict: Control rod groups configuration from config.json
    """
    return _config.get("control_rod_groups", {})

def get_presets():
    """
    Returns the presets configuration section.
    
    Returns:
        dict: Presets configuration from config.json
    """
    return _config.get("presets", {}) 