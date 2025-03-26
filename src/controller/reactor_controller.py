"""
Controller module connecting the UI with the reactor model
"""
from src.model.reactor_model import ReactorModel

class ReactorController:
    """
    Controller class that handles the communication between the UI and the reactor model
    """
    
    def __init__(self):
        """Initialize the controller with a new reactor model"""
        self.model = ReactorModel()
    
    def update_control_rod_position(self, position):
        """Update control rod position in the model"""
        self.model.update_control_rod_position(position)
        return self.get_reactor_parameters()
    
    def update_boron_concentration(self, concentration):
        """Update boron concentration in the model"""
        self.model.update_boron_concentration(concentration)
        return self.get_reactor_parameters()
    
    def update_moderator_temperature(self, temperature):
        """Update moderator temperature in the model"""
        self.model.update_moderator_temperature(temperature)
        return self.get_reactor_parameters()
    
    def update_fuel_enrichment(self, enrichment):
        """Update fuel enrichment in the model"""
        self.model.update_fuel_enrichment(enrichment)
        return self.get_reactor_parameters()
    
    def get_reactor_parameters(self):
        """Get the current reactor parameters from the model"""
        return {
            "k_effective": self.model.k_effective,
            "reactivity": self.model.reactivity,
            "doubling_time": self.model.doubling_time,
            "delayed_neutron_fraction": self.model.delayed_neutron_fraction
        }
    
    def get_axial_flux_distribution(self):
        """Get the axial flux distribution data from the model"""
        return self.model.get_axial_flux_distribution()
    
    def get_four_factors_data(self):
        """Get the four factors data from the model"""
        return self.model.get_four_factors_data()
    
    def get_neutron_balance_data(self):
        """Get the neutron balance data from the model"""
        return self.model.get_neutron_balance_data() 