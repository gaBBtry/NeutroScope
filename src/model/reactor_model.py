"""
Reactor physics model for neutronics calculations
"""
import numpy as np
from . import config

class ReactorModel:
    """
    Basic reactor model implementing neutronics calculations for a PWR
    """
    
    def __init__(self):
        # Default parameters
        self.control_rod_position = 0.0  # 0-100%
        self.boron_concentration = 500.0  # ppm
        self.moderator_temperature = 310.0  # °C
        self.fuel_temperature = 600.0  # °C
        self.fuel_enrichment = 3.5  # %
        self.coolant_flow_rate = 100.0  # %
        
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
        
        # Neutron leakage factors
        self.thermal_leakage = config.THERMAL_LEAKAGE
        self.fast_leakage = config.FAST_LEAKAGE
        
        # Presets dictionary
        self.presets = config.PRESETS
        
        # Initial calculation
        self.calculate_all()
    
    def calculate_all(self):
        """Calculate all reactor parameters based on current inputs"""
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
        self.p = config.P_BASE - config.P_TEMP_COEFF * (self.fuel_temperature - 600) / 100
        
        # Thermal utilization factor
        # Affected by control rod position and boron concentration
        rod_effect = config.F_ROD_COEFF * self.control_rod_position / 100
        boron_effect = config.F_BORON_COEFF * self.boron_concentration / 1000
        self.f = config.F_BASE + rod_effect + boron_effect
    
    def calculate_k_effective(self):
        """Calculate k-effective from the four factors and leakage"""
        k_infinite = self.eta * self.epsilon * self.p * self.f
        self.k_effective = k_infinite * self.thermal_leakage * self.fast_leakage
    
    def calculate_reactivity(self):
        """Calculate reactivity (ρ) from k-effective"""
        self.reactivity = (self.k_effective - 1.0) / self.k_effective
    
    def calculate_doubling_time(self):
        """Calculate reactor period/doubling time"""
        if self.reactivity <= 0:
            self.doubling_time = float('inf')
        else:
            # Simplified period calculation for educational purposes
            prompt_reactivity = self.reactivity - self.delayed_neutron_fraction
            if prompt_reactivity > 0:
                # Prompt critical - very fast
                self.doubling_time = 0.1  # arbitrary small value
            else:
                # Delayed critical
                self.doubling_time = config.DOUBLING_TIME_COEFF / (self.reactivity * 100)  # seconds
    
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
            "thermal_leakage": self.thermal_leakage,
            "fast_leakage": self.fast_leakage,
            "k_effective": self.k_effective
        }
        
    def get_neutron_balance_data(self):
        """Get data for the neutron balance visualization (pie chart)"""
        # Ces valeurs sont des approximations simplifiées pour un REP typique
        # et varient en fonction des paramètres du réacteur
        
        # Calcul des proportions de neutrons en fonction de leur devenir
        
        # Neutrons de fission (divisés entre rapides et thermiques)
        fissions_neutrons_lents_pct = 39
        fissions_neutrons_rapides_pct = 2
        
        # Captures fertiles (U-238 -> Pu-239)
        captures_fertiles_pct = 18
        
        # Captures stériles (dans le combustible)
        captures_steriles_pct = 13
        
        # Fuites
        fuites_neutrons_lents_pct = 2
        fuites_neutrons_rapides_pct = 11
        
        # Captures dans le modérateur, gaines, etc.
        captures_moderateur_pct = 4
        
        # Captures dans le combustible sans fission
        captures_combustible_pct = 6
        
        # Poisons, barres de contrôle
        poisons_barres_pct = 6
        
        # Ajuster ces valeurs en fonction des paramètres du réacteur
        effect_rod = self.control_rod_position / 100
        effect_boron = self.boron_concentration / 2000
        
        # Augmenter l'absorption par les barres et le bore
        poisons_barres_pct += 4 * effect_rod
        captures_steriles_pct += 3 * effect_boron
        
        # Réduire les fissions en conséquence
        fissions_reduction = (4 * effect_rod + 3 * effect_boron)
        fissions_neutrons_lents_pct -= fissions_reduction
        
        # Renvoyer les données dans un format utilisable par le graphique
        return {
            "sections": [
                {"name": "Fissions", "value": fissions_neutrons_lents_pct + fissions_neutrons_rapides_pct, 
                 "color": "#33a02c", "tooltip": f"Fissions neutrons\n(lents {fissions_neutrons_lents_pct}%, rapides {fissions_neutrons_rapides_pct}%)"},
                {"name": "Captures fertiles", "value": captures_fertiles_pct, 
                 "color": "#1f78b4", "tooltip": "Captures fertiles\nU-238 → Pu-239"},
                {"name": "Captures stériles", "value": captures_steriles_pct, 
                 "color": "#ffff33", "tooltip": "Captures stériles"},
                {"name": "Fuites", "value": fuites_neutrons_lents_pct + fuites_neutrons_rapides_pct, 
                 "color": "#e31a1c", "tooltip": f"Fuites\n(N. lents {fuites_neutrons_lents_pct}%, N. rapides {fuites_neutrons_rapides_pct}%)"},
                {"name": "Modérateur", "value": captures_moderateur_pct, 
                 "color": "#a6cee3", "tooltip": "Modérateur, gaines, etc."},
                {"name": "Combustible", "value": captures_combustible_pct, 
                 "color": "#b2df8a", "tooltip": "Combustible"},
                {"name": "Poisons/Barres", "value": poisons_barres_pct, 
                 "color": "#fb9a99", "tooltip": "Poisons, Barres de contrôle"}
            ],
            "total": 100
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
        
        # Calculate power percentage based on effective multiplication factor
        # For a simplified model, we'll assume power is proportional to k_effective
        # In a real reactor with control systems, power would be more complex to calculate
        base_k = 1.0  # Critical reactor
        power_percentage = 100 * (self.k_effective / base_k)
        
        # Adjust power based on control rod position to simulate load following
        # In a real reactor, this would be controlled by external demand
        if self.control_rod_position > 0:
            # Deeper rod insertion generally means lower power operation
            rod_effect = 1.0 - (0.3 * self.control_rod_position / 100)
            power_percentage *= rod_effect
        
        # Constrain power to realistic range (0-100%)
        power_percentage = max(0, min(100, power_percentage))
        
        return {
            "axial_offset": axial_offset,
            "power_percentage": power_percentage
        }
    
    def apply_preset(self, preset_name):
        """Apply a predefined preset configuration to the reactor"""
        if preset_name in self.presets:
            preset = self.presets[preset_name]
            self.control_rod_position = preset["control_rod_position"]
            self.boron_concentration = preset["boron_concentration"]
            self.moderator_temperature = preset["moderator_temperature"]
            self.fuel_enrichment = preset["fuel_enrichment"]
            self.calculate_all()
            return True
        return False
    
    def get_preset_names(self):
        """Return a list of available preset names"""
        return list(self.presets.keys())
    
    def get_current_preset_name(self):
        """
        Get the name of the current preset if matching any. 
        If no preset matches, return 'Personnalisé'.
        """
        current_config = {
            "control_rod_position": self.control_rod_position,
            "boron_concentration": self.boron_concentration,
            "moderator_temperature": self.moderator_temperature,
            "fuel_enrichment": self.fuel_enrichment
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
                "fuel_enrichment": self.fuel_enrichment
            }
            return True
        return False 