"""
Reactor physics model for neutronics calculations
"""
import numpy as np
from . import config
from .config import should_use_openmc, get_current_calculation_mode, get_calculation_modes
from .openmc_model import OpenMCModel

class ReactorModel:
    """
    Basic reactor model implementing neutronics calculations for a PWR
    """
    
    def __init__(self):
        # Default parameters
        self.control_rod_position = 0.0  # 0-100%
        self.boron_concentration = 500.0  # ppm
        self.moderator_temperature = 310.0  # °C
        self.power_level = 100.0 # %
        self.fuel_enrichment = 3.5  # %
        
        # This is now a calculated value, not a direct input
        self.fuel_temperature = 0.0  # °C, will be calculated
        
        # Physical constants
        self.delayed_neutron_fraction = config.DELAYED_NEUTRON_FRACTION  # β
        
        # Calculated parameters
        self.k_effective = 1.0
        self.reactivity = 0.0
        self.doubling_time = float('inf')  # seconds
        
        # Four factors
        self.eta = 2.0  # average number of neutrons per fission
        self.epsilon = 1.03  # fast fission factor
        self.p = 0.75  # resonance escape probability
        self.f = 0.71  # thermal utilization factor
        
        # OpenMC runner
        self.openmc_runner = None
        
        # Neutron leakage factors
        self.thermal_non_leakage_prob = 1.0
        self.fast_non_leakage_prob = 1.0
        
        # Presets dictionary
        self.presets = config.PRESETS
        
        # Calculation mode tracking
        self._last_calculation_mode = None
        
        # Initial calculation
        self._update_temperatures()
        self.calculate_all()
    
    def _update_temperatures(self):
        """Calculate fuel temperature based on power level and moderator temperature."""
        self.fuel_temperature = self.moderator_temperature + (self.power_level * config.POWER_TO_FUEL_TEMP_COEFF)

    def calculate_all(self):
        """Calculate all reactor parameters based on current inputs"""
        # The analytical four-factor calculation is kept for now for visualizations,
        # but the k_effective from it will be overwritten by OpenMC.
        self.calculate_four_factors()
        self.calculate_k_effective()
        self.calculate_reactivity()
        self.calculate_doubling_time()
    
    def calculate_four_factors(self):
        """Calculate the four factors of the neutron cycle"""
        # Simplified calculation for educational purposes
        
        # Eta (average number of neutrons per fission)
        # Depends primarily on fuel enrichment
        self.eta = config.ETA_BASE + config.ETA_ENRICHMENT_COEFF * (self.fuel_enrichment - 3.0) / 2.0
        
        # Epsilon (fast fission factor)
        # Typically constant for a given reactor design
        self.epsilon = config.EPSILON
        
        # Resonance escape probability
        # Affected by fuel temperature (Doppler broadening)
        fuel_temp_K = self.fuel_temperature + 273.15
        sqrt_T_diff = np.sqrt(fuel_temp_K) - np.sqrt(config.P_REF_TEMP_K)
        self.p = config.P_BASE * np.exp(-config.P_DOPPLER_COEFF * sqrt_T_diff)
        
        # Thermal utilization factor (f)
        # New model based on absorption ratios: f = 1 / (1 + A_non_fuel)
        # A_non_fuel is the ratio of absorption in non-fuel materials to fuel
        
        # 1. Base absorption ratio, adjusted for moderator temperature
        temp_deviation = self.moderator_temperature - config.F_REF_MOD_TEMP_C
        mod_temp_effect = config.F_MOD_TEMP_ABS_COEFF * temp_deviation
        base_abs_ratio = config.F_BASE_ABS_RATIO * (1 + mod_temp_effect)
        
        # 2. Control rod absorption ratio
        rod_abs_ratio = config.F_CONTROL_ROD_WORTH * (self.control_rod_position / 100.0)
        
        # 3. Boron absorption ratio
        boron_abs_ratio = config.F_BORON_WORTH_PER_PPM * self.boron_concentration
        
        # Total non-fuel absorption ratio
        total_non_fuel_abs_ratio = base_abs_ratio + rod_abs_ratio + boron_abs_ratio
        
        self.f = 1.0 / (1.0 + total_non_fuel_abs_ratio)
    
    def calculate_k_effective(self):
        """
        Calculate k-effective using the chosen calculation method.
        The method depends on the user's choice of calculation mode.
        """
        current_mode = get_current_calculation_mode()
        modes = get_calculation_modes()
        use_openmc_setting = should_use_openmc()
        
        # Track mode changes for user feedback
        if self._last_calculation_mode != current_mode:
            if current_mode in modes:
                print(f"🔄 Calcul avec {modes[current_mode]['name']}")
            self._last_calculation_mode = current_mode
        
        # --- Décision du mode de calcul ---
        if use_openmc_setting is False:
            # Mode rapide : utiliser uniquement le modèle analytique
            self._calculate_k_effective_analytical()
            
        elif use_openmc_setting is True:
            # Mode précis : utiliser uniquement OpenMC
            if not self._calculate_k_effective_openmc():
                raise RuntimeError(
                    "Mode précis sélectionné mais OpenMC n'est pas disponible. "
                    "Veuillez configurer OpenMC ou changer de mode de calcul."
                )
                
        else:
            # Mode auto : essayer OpenMC, fallback sur analytique
            if not self._calculate_k_effective_openmc():
                print("⚠ OpenMC non disponible, passage en mode analytique")
                self._calculate_k_effective_analytical()

    def _calculate_k_effective_openmc(self):
        """
        Calcul k-effectif avec OpenMC.
        Retourne True si réussi, False sinon.
        """
        try:
            params = self._get_params_for_openmc()
            self.openmc_runner = OpenMCModel(params)
            self.k_effective = self.openmc_runner.run_simulation()
            
            # Since we use OpenMC, leakage is implicitly handled.
            # We can set these to 1.0 or try to derive them from OpenMC tallies later.
            self.fast_non_leakage_prob = 1.0
            self.thermal_non_leakage_prob = 1.0
            return True
            
        except Exception as e:
            print(f"Échec du calcul OpenMC: {e}")
            return False

    def _calculate_k_effective_analytical(self):
        """Calcul k-effectif avec le modèle analytique."""
        # --- Analytical Calculation ---
        k_infinite = self.eta * self.epsilon * self.p * self.f
        
        # New leakage calculation based on two-group diffusion theory
        # 1. Geometric Buckling B^2
        R = config.CORE_DIAMETER_M / 2.0
        H = config.CORE_HEIGHT_M
        geometric_buckling = (np.pi / H)**2 + (2.405 / R)**2
        
        # 2. Temperature effect on moderator density and diffusion areas
        # L^2 and L_s^2 are proportional to (rho_ref/rho_T)^2
        temp_deviation = self.moderator_temperature - config.F_REF_MOD_TEMP_C
        density_ratio = 1.0 / (1.0 - config.MODERATOR_DENSITY_COEFF * temp_deviation)
        
        thermal_diffusion_area = config.THERMAL_DIFFUSION_AREA_M2 * (density_ratio**2)
        fast_diffusion_area = config.FAST_DIFFUSION_AREA_M2 * (density_ratio**2)
        
        # 3. Non-leakage probabilities
        self.fast_non_leakage_prob = 1.0 / (1.0 + geometric_buckling * fast_diffusion_area)
        self.thermal_non_leakage_prob = 1.0 / (1.0 + geometric_buckling * thermal_diffusion_area)
        
        self.k_effective = k_infinite * self.fast_non_leakage_prob * self.thermal_non_leakage_prob

    def _get_params_for_openmc(self):
        """Gathers the current reactor state into a dictionary for OpenMC."""
        return {
            "control_rod_position": self.control_rod_position,
            "boron_concentration": self.boron_concentration,
            "moderator_temperature": self.moderator_temperature + 273.15, # Convert to K
            "fuel_temperature": self.fuel_temperature + 273.15, # Convert to K
            "power_level": self.power_level,
            "fuel_enrichment": self.fuel_enrichment,
        }
    
    def calculate_reactivity(self):
        """Calculate reactivity (ρ) from k-effective"""
        if self.k_effective > 0:
            self.reactivity = (self.k_effective - 1.0) / self.k_effective
        else:
            self.reactivity = -float('inf')
    
    def calculate_doubling_time(self):
        """
        Calculate reactor period/doubling time using a standard approximation.
        The reactor period T is the time required for the neutron population to change by a factor of e.
        The doubling time is T * ln(2).
        """
        if self.reactivity <= 0:
            self.doubling_time = float('inf')
            return

        # Use reactivity in absolute units, not pcm or %
        rho = self.reactivity

        if rho >= self.delayed_neutron_fraction:
            # Prompt critical - very short period
            # Using prompt jump approximation: T = l / (ρ - β)
            prompt_reactivity = rho - self.delayed_neutron_fraction
            if prompt_reactivity > 0:
                period = config.PROMPT_NEUTRON_LIFETIME / prompt_reactivity
                self.doubling_time = period * np.log(2)
            else:
                # Exactly prompt critical, period is theoretically zero.
                self.doubling_time = 0.0
        else:
            # Delayed critical period calculation
            # T ≈ (β - ρ) / (λ_eff * ρ) - this is more accurate than the previous one
            # for ρ close to β. Let's stick to the simpler one for now.
            # Using one-group delayed neutron approximation T ≈ β / (λ * ρ)
            # where λ is the effective delayed neutron precursor decay constant.
            # A typical value for λ_eff is ~0.1 s⁻¹
            effective_decay_constant = 0.1  # lambda_eff (s^-1)
            
            # A simpler and more common approximation for small reactivity is T ≈ β / (λ * ρ)
            if rho > 0:
                period = self.delayed_neutron_fraction / (rho * effective_decay_constant)
                self.doubling_time = period * np.log(2)
            else:
                self.doubling_time = float('inf')

    def update_control_rod_position(self, position):
        """Update control rod position and recalculate"""
        self.control_rod_position = position
        self.calculate_all()
    
    def update_boron_concentration(self, concentration):
        """Update boron concentration and recalculate"""
        self.boron_concentration = concentration
        self.calculate_all()
    
    def update_moderator_temperature(self, temperature):
        """Update moderator temperature and recalculate"""
        self.moderator_temperature = temperature
        self._update_temperatures()
        self.calculate_all()
    
    def update_power_level(self, power_level):
        """Update power level and recalculate"""
        self.power_level = power_level
        self._update_temperatures()
        self.calculate_all()
    
    def update_fuel_enrichment(self, enrichment):
        """Update fuel enrichment and recalculate"""
        self.fuel_enrichment = enrichment
        self.calculate_all()
    
    def get_axial_flux_distribution(self):
        """
        Calculate axial flux distribution based on control rod position
        Returns array of values representing flux at different heights
        """
        # Simple cosine shape with depression at top if control rods inserted
        points = 100
        height = np.linspace(0, 1, points)
        
        # Base cosine shape
        flux = np.cos(np.pi * (height - 0.5))
        
        # Control rod effect (simplified)
        if self.control_rod_position > 0:
            rod_depth = self.control_rod_position / 100
            rod_effect = np.exp(-10 * (height - (1 - rod_depth))**2)
            rod_effect[height < (1 - rod_depth)] = 1
            flux = flux * rod_effect
        
        # Normalize
        flux = flux / np.max(flux)
        
        return height, flux
    
    def get_four_factors_data(self):
        """Get data for the four factors visualization"""
        return {
            "eta": self.eta,
            "epsilon": self.epsilon,
            "p": self.p,
            "f": self.f,
            "k_infinite": self.eta * self.epsilon * self.p * self.f,
            "thermal_non_leakage_prob": self.thermal_non_leakage_prob,
            "fast_non_leakage_prob": self.fast_non_leakage_prob,
            "k_effective": self.k_effective
        }
        
    def get_neutron_balance_data(self):
        """
        Get data for the neutron balance visualization (pie chart).
        This function tracks the fate of a generation of neutrons.
        """
        # Start with a generation of N fast neutrons produced by fission.
        # k_eff = (neutrons in gen N+1) / (neutrons in gen N)
        # Here we track how the N neutrons are lost or absorbed to create the N+1 generation.
        
        # Let's start with 1000 neutrons for calculation clarity.
        neutrons_start_generation = 1000.0

        # 1. Fast Leakage
        fast_leakage_neutrons = neutrons_start_generation * (1.0 - self.fast_non_leakage_prob)
        neutrons_after_fast_leakage = neutrons_start_generation - fast_leakage_neutrons

        # 2. Resonance Capture while slowing down
        resonance_capture_neutrons = neutrons_after_fast_leakage * (1.0 - self.p)
        neutrons_after_resonance_capture = neutrons_after_fast_leakage - resonance_capture_neutrons

        # 3. Thermal Leakage
        thermal_leakage_neutrons = neutrons_after_resonance_capture * (1.0 - self.thermal_non_leakage_prob)
        neutrons_after_thermal_leakage = neutrons_after_resonance_capture - thermal_leakage_neutrons

        # 4. Absorption in non-fuel materials
        non_fuel_absorptions = neutrons_after_thermal_leakage * (1.0 - self.f)
        
        # 5. Absorption in fuel (split into capture and fission)
        fuel_absorptions = neutrons_after_thermal_leakage * self.f
        
        # To split fuel absorptions, we use eta. eta = nu * Sigma_f / Sigma_a_fuel
        # Fraction of absorptions causing fission is eta/nu.
        nu = 2.43  # Neutrons per thermal fission in U-235
        fission_fraction_in_fuel = self.eta / nu
        fission_fraction_in_fuel = min(fission_fraction_in_fuel, 1.0) # Cannot be > 1

        thermal_fission_absorptions = fuel_absorptions * fission_fraction_in_fuel
        fertile_capture_absorptions = fuel_absorptions * (1.0 - fission_fraction_in_fuel)

        # The sum of all these "loss" and "absorption" terms should be the initial number of neutrons.
        total_lost_and_absorbed = (fast_leakage_neutrons + 
                                   resonance_capture_neutrons + 
                                   thermal_leakage_neutrons + 
                                   non_fuel_absorptions + 
                                   fertile_capture_absorptions + 
                                   thermal_fission_absorptions)

        # The visualization should show the fate of the initial 1000 neutrons.
        # The sum of percentages should be 100%.
        # Note: Epsilon (fast fission factor) is implicitly included in k_effective,
        # but showing it explicitly in a neutron lifecycle starting from *all* fast neutrons
        # is tricky. Epsilon = (total n from fission) / (n from thermal fission).
        # k_inf = epsilon * (eta * p * f). The eta*p*f part is the thermal part.
        # The current structure starting from a batch of fast neutrons is more intuitive for a lifecycle chart.

        return {
            # Values are absolute numbers of neutrons, the view can convert to %
            "sections": [
                {"name": "Fuites rapides", "value": fast_leakage_neutrons,
                 "color": "#e31a1c", "tooltip": "Fuites de neutrons rapides hors du cœur"},
                {"name": "Captures résonnantes", "value": resonance_capture_neutrons,
                 "color": "#6a3d9a", "tooltip": "Captures de neutrons dans les résonances de l'U-238"},
                {"name": "Fuites thermiques", "value": thermal_leakage_neutrons,
                 "color": "#fb9a99", "tooltip": "Fuites de neutrons thermiques hors du cœur"},
                {"name": "Absorption non-combustible", "value": non_fuel_absorptions,
                 "color": "#b2df8a", "tooltip": "Captures dans le modérateur, les structures, etc."},
                {"name": "Capture fertile", "value": fertile_capture_absorptions,
                 "color": "#33a02c", "tooltip": "Captures dans le combustible ne menant pas à une fission (ex: U-238)"},
                {"name": "Fission thermique", "value": thermal_fission_absorptions,
                 "color": "#1f78b4", "tooltip": "Fissions causées par des neutrons thermiques dans le combustible"}
            ],
            "neutrons_produced_new": neutrons_start_generation * self.k_effective
        }
    
    def get_axial_offset_data(self):
        """
        Calculate axial offset and reactor power data for the pilotage diagram
        
        Axial Offset (AO) = (Flux_haut - Flux_bas) / (Flux_haut + Flux_bas)
        Where:
        - Flux_haut is the average flux in the upper half of the core
        - Flux_bas is the average flux in the lower half of the core
        
        Returns: A dict with axial_offset and power_percentage
        """
        # Get current flux distribution
        height, flux = self.get_axial_flux_distribution()
        
        # Calculate axial offset
        upper_flux = np.mean(flux[height > 0.5])
        lower_flux = np.mean(flux[height <= 0.5])
        axial_offset = 100 * (upper_flux - lower_flux) / (upper_flux + lower_flux)
        
        power_percentage = self.power_level

        return {"axial_offset": axial_offset, "power_percentage": power_percentage}
    
    def apply_preset(self, preset_name):
        """Apply a preset configuration"""
        if preset_name in self.presets:
            preset = self.presets[preset_name]
            self.control_rod_position = preset["control_rod_position"]
            self.boron_concentration = preset["boron_concentration"]
            self.moderator_temperature = preset["moderator_temperature"]
            self.fuel_enrichment = preset["fuel_enrichment"]
            if "power_level" in preset:
                self.power_level = preset["power_level"]
            self._update_temperatures()
            self.calculate_all()
            return True
        return False
    
    def get_preset_names(self):
        """Return a list of available preset names"""
        return list(self.presets.keys())
    
    def get_current_preset_name(self):
        """
        Get the name of the current preset if the current parameters match one.
        If no preset matches, return 'Personnalisé'.
        """
        current_config = {
            "control_rod_position": self.control_rod_position,
            "boron_concentration": self.boron_concentration,
            "moderator_temperature": self.moderator_temperature,
            "fuel_enrichment": self.fuel_enrichment,
            "power_level": self.power_level
        }
        for name, preset_config in self.presets.items():
            # Use np.isclose for robust floating point comparison
            if all(np.isclose(current_config.get(key, 0), preset_config.get(key, 0)) for key in preset_config):
                return name
        return "Personnalisé"
    
    def save_preset(self, name, overwrite=False):
        """Save current configuration as a preset"""
        if name not in self.presets or overwrite:
            self.presets[name] = {
                "control_rod_position": self.control_rod_position,
                "boron_concentration": self.boron_concentration,
                "moderator_temperature": self.moderator_temperature,
                "fuel_enrichment": self.fuel_enrichment,
                "power_level": self.power_level
            }
            return True
        return False

    def get_current_calculation_info(self):
        """
        Retourne des informations sur le mode de calcul actuel.
        """
        current_mode = get_current_calculation_mode()
        modes = get_calculation_modes()
        
        if current_mode in modes:
            return {
                "mode": current_mode,
                "name": modes[current_mode]["name"],
                "description": modes[current_mode]["description"],
                "uses_openmc": modes[current_mode]["use_openmc"]
            }
        else:
            return {
                "mode": "unknown",
                "name": "Mode inconnu",
                "description": "Mode de calcul non reconnu",
                "uses_openmc": False
            } 