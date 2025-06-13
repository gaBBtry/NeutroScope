"""
Configuration file for the ReactorModel
"""

# Physical constants
DELAYED_NEUTRON_FRACTION = 0.0065  # β

# Four factors model coefficients
# eta = ETA_BASE + ETA_ENRICHMENT_COEFF * (enrichment - 3.0) / 2.0
ETA_BASE = 2.0
ETA_ENRICHMENT_COEFF = 0.1

# epsilon is constant
EPSILON = 1.03

# p = P_BASE - P_TEMP_COEFF * (fuel_temp - 600) / 100
P_BASE = 0.75
P_TEMP_COEFF = 0.01

# f = F_BASE + F_ROD_COEFF * rod_pos / 100 + F_BORON_COEFF * boron_conc / 1000 + F_MOD_TEMP_COEFF * (mod_temp - 300)
F_BASE = 0.71
F_ROD_COEFF = -0.1
F_BORON_COEFF = -0.05
F_MOD_TEMP_COEFF = -0.005 # per 10°C change from 300°C

# Neutron leakage factors
THERMAL_LEAKAGE = 0.98
FAST_LEAKAGE = 0.97

# Thermal-Hydraulics
POWER_TO_FUEL_TEMP_COEFF = 3.0  # °C increase in fuel temp per % power, above moderator temp

# Doubling time calculation
DOUBLING_TIME_COEFF = 80.0  # s

# Default presets
PRESETS = {
    "Démarrage": {
        "control_rod_position": 50.0,
        "boron_concentration": 1500.0,
        "moderator_temperature": 290.0,
        "fuel_enrichment": 3.5
    },
    "Critique à puissance nominale": {
        "control_rod_position": 10.0,
        "boron_concentration": 800.0,
        "moderator_temperature": 310.0,
        "fuel_enrichment": 3.5
    },
    "Fin de cycle": {
        "control_rod_position": 5.0,
        "boron_concentration": 10.0,
        "moderator_temperature": 310.0,
        "fuel_enrichment": 3.5
    },
    "Surcritique": {
        "control_rod_position": 0.0,
        "boron_concentration": 400.0,
        "moderator_temperature": 305.0,
        "fuel_enrichment": 4.0
    },
    "Sous-critique": {
        "control_rod_position": 80.0,
        "boron_concentration": 1200.0,
        "moderator_temperature": 310.0,
        "fuel_enrichment": 3.0
    }
} 