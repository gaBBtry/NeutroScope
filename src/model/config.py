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
# P_TEMP_COEFF = 0.01 # Original linear coefficient
P_REF_TEMP_K = 873.15  # 600°C
P_DOPPLER_COEFF = 0.008 # Doppler coefficient for sqrt(T) formula

# --- Thermal Utilization Factor (f) ---
# Original linear model:
# f = F_BASE + F_ROD_COEFF * rod_pos / 100 + F_BORON_COEFF * boron_conc / 1000 + F_MOD_TEMP_COEFF * (mod_temp - 300)
F_BASE = 0.71 # Base value for f, used for display and to derive F_BASE_ABS_RATIO
# F_ROD_COEFF = -0.1
# F_BORON_COEFF = -0.05
# F_MOD_TEMP_COEFF = -0.005 # per 10°C change from 300°C

# New model based on absorption ratios: f = 1 / (1 + A_non_fuel)
F_BASE_ABS_RATIO = 0.408  # Base non-fuel to fuel absorption ratio (A_mod + A_struct) at ref temp
F_REF_MOD_TEMP_C = 300.0  # Reference moderator temperature in °C
F_CONTROL_ROD_WORTH = 0.26 # Total worth of control rods on non-fuel absorption ratio
F_BORON_WORTH_PER_PPM = 2.8e-5 # Non-fuel absorption ratio increase per ppm of boron
F_MOD_TEMP_ABS_COEFF = 0.003 # Coefficient for moderator temperature effect on absorption ratio

# --- Neutron Leakage Factors ---
# Original constant leakage model
# THERMAL_LEAKAGE = 0.98
# FAST_LEAKAGE = 0.97

# New model based on two-group diffusion theory
CORE_HEIGHT_M = 4.0
CORE_DIAMETER_M = 3.0
# Reference values for diffusion and slowing-down areas, tuned for this model
THERMAL_DIFFUSION_AREA_M2 = 0.0064  # L^2
FAST_DIFFUSION_AREA_M2 = 0.0097    # L_s^2 or tau
MODERATOR_DENSITY_COEFF = 8.0e-4   # per °C, for water around 300°C

# Thermal-Hydraulics
POWER_TO_FUEL_TEMP_COEFF = 3.0  # °C increase in fuel temp per % power, above moderator temp

# Doubling time calculation
DOUBLING_TIME_COEFF = 80.0  # s
PROMPT_NEUTRON_LIFETIME = 2.0e-5  # seconds (l)

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
        "boron_concentration": 1240.0,
        "moderator_temperature": 310.0,
        "fuel_enrichment": 3.5,
        "power_level": 100.0
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