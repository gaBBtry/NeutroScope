"""
Reactor physics model for neutronics calculations
"""
import numpy as np

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
        self.delayed_neutron_fraction = 0.0065  # β
        
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
        self.thermal_leakage = 0.98
        self.fast_leakage = 0.97
        
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
        self.eta = 2.0 + 0.1 * (self.fuel_enrichment - 3.0) / 2.0
        
        # Epsilon (fast fission factor)
        # Typically constant for a given reactor design
        self.epsilon = 1.03
        
        # Resonance escape probability
        # Affected by fuel temperature (Doppler broadening)
        self.p = 0.75 - 0.01 * (self.fuel_temperature - 600) / 100
        
        # Thermal utilization factor
        # Affected by control rod position and boron concentration
        rod_effect = -0.1 * self.control_rod_position / 100
        boron_effect = -0.05 * self.boron_concentration / 1000
        self.f = 0.71 + rod_effect + boron_effect
    
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
                self.doubling_time = 80 / (self.reactivity * 100)  # seconds
    
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