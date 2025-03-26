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
    
    def get_axial_offset_data(self):
        """Get the axial offset and power data for the pilotage diagram"""
        return self.model.get_axial_offset_data()
        
    def get_preset_names(self):
        """Get list of available presets"""
        return self.model.get_preset_names()
    
    def apply_preset(self, preset_name):
        """Apply a preset configuration"""
        success = self.model.apply_preset(preset_name)
        if success:
            return {
                "control_rod_position": self.model.control_rod_position,
                "boron_concentration": self.model.boron_concentration,
                "moderator_temperature": self.model.moderator_temperature,
                "fuel_enrichment": self.model.fuel_enrichment,
                "reactor_params": self.get_reactor_parameters()
            }
        return None
    
    def get_current_preset_name(self):
        """Get the name of the current preset if matching any"""
        return self.model.get_current_preset_name()
    
    def save_preset(self, name, overwrite=False):
        """Save current configuration as a preset"""
        return self.model.save_preset(name, overwrite)
    
    def get_current_configuration(self):
        """Get current reactor configuration"""
        return {
            "control_rod_position": self.model.control_rod_position,
            "boron_concentration": self.model.boron_concentration,
            "moderator_temperature": self.model.moderator_temperature,
            "fuel_enrichment": self.model.fuel_enrichment
        } 