"""
Controller module connecting the UI with the reactor model
"""
from src.model.reactor_model import ReactorModel
from src.model.preset_model import PresetCategory
from src.model import config
import copy


class ReactorController:
    """Contrôleur pour l'interface entre la vue et le modèle de réacteur"""
    
    def __init__(self):
        self.model = ReactorModel()

    def get_gui_settings(self):
        """Retourne les paramètres de configuration de l'interface graphique."""
        return config.gui_settings

    def get_parameter_config(self, param_name):
        """Retourne la configuration pour un paramètre spécifique."""
        return config.parameters_config.get(param_name, {})

    # Nouvelles méthodes pour les groupes de barres
    def update_rod_group_R_position(self, position):
        """Update R group position (0-228 steps)"""
        self.model.update_rod_group_R_position(position)
        return self.get_reactor_parameters()
    
    def update_rod_group_GCP_position(self, position):
        """Update GCP group position (0-228 steps)"""
        self.model.update_rod_group_GCP_position(position)
        return self.get_reactor_parameters()
    
    def get_rod_group_positions(self):
        """Get current positions of both rod groups"""
        return {
            "R": self.model.rod_group_R_position,
            "GCP": self.model.rod_group_GCP_position
        }
    
    def update_control_rod_position(self, position):
        """Méthode de rétrocompatibilité pour les anciens contrôles"""
        return self.model.update_control_rod_position(position)
    
    def update_boron_concentration(self, concentration):
        """Update boron concentration"""
        params = self.model.update_boron_concentration(concentration)
        return self.get_reactor_parameters()
    
    def update_average_temperature(self, temperature):
        """Update average temperature"""
        params = self.model.update_average_temperature(temperature)
        return self.get_reactor_parameters()
    
    def update_power_level(self, power_level):
        """Update power level"""
        params = self.model.update_power_level(power_level)
        return self.get_reactor_parameters()
    
    def update_fuel_enrichment(self, enrichment):
        """Update fuel enrichment"""
        params = self.model.update_fuel_enrichment(enrichment)
        return self.get_reactor_parameters()
    
    def get_reactor_parameters(self):
        """Récupérer tous les paramètres calculés du réacteur"""
        return {
            "k_effective": self.model.k_effective,
            "k_infinite": self.model.k_infinite,
            "reactivity": self.model.reactivity,
            "doubling_time": self.model.doubling_time,
            "delayed_neutron_fraction": self.model.delayed_neutron_fraction,
            "eta": self.model.eta,
            "epsilon": self.model.epsilon,
            "p": self.model.p,
            "f": self.model.f,
            "thermal_non_leakage_prob": self.model.thermal_non_leakage_prob,
            "fast_non_leakage_prob": self.model.fast_non_leakage_prob
        }
    
    def get_axial_flux_distribution(self):
        """Get axial flux distribution data"""
        return self.model.get_axial_flux_distribution()
    
    def get_four_factors_data(self):
        """Get four factors data for visualization"""
        return self.model.get_four_factors_data()
    
    def get_neutron_balance_data(self):
        """Get neutron balance data for visualization"""
        return self.model.get_neutron_balance_data()
    
    def get_neutron_cycle_data(self):
        """Get neutron cycle data for visualization"""
        return self.model.get_neutron_cycle_data()
    
    def get_current_configuration(self):
        """Get current reactor configuration"""
        return {
            "rod_group_R_position": self.model.rod_group_R_position,
            "rod_group_GCP_position": self.model.rod_group_GCP_position,
            "boron_concentration": self.model.boron_concentration,
            "average_temperature": self.model.average_temperature,
            "fuel_enrichment": self.model.fuel_enrichment,
            "power_level": self.model.power_level
        }
    
    def get_xenon_dynamics_data(self):
        """Get the xenon dynamics data from the model"""
        return self.model.get_xenon_dynamics_data()
    
    def advance_time(self, hours=1.0):
        """Advance simulation time and update xenon dynamics"""
        self.model.advance_time(hours)
        return self.get_reactor_parameters()
    
    def reset_xenon_to_equilibrium(self):
        """Reset xenon concentrations to equilibrium for current power level"""
        self.model.calculate_xenon_equilibrium()
        return self.get_reactor_parameters()
    
    def get_preset_names(self):
        """Get list of available presets"""
        return self.model.get_preset_names()
    
    def apply_preset(self, preset_name):
        """Apply a preset configuration"""
        success = self.model.apply_preset(preset_name)
        if success:
            return {
                "rod_group_R_position": self.model.rod_group_R_position,
                "rod_group_GCP_position": self.model.rod_group_GCP_position,
                "boron_concentration": self.model.boron_concentration,
                "average_temperature": self.model.average_temperature,
                "fuel_enrichment": self.model.fuel_enrichment,
                "power_level": self.model.power_level,
                "reactor_params": self.get_reactor_parameters()
            }
        return None
    
    def get_current_preset_name(self):
        """Get the name of the current preset if matching any"""
        return self.model.get_current_preset_name()
    
    def save_preset(self, name, description="", overwrite=False):
        """Save current configuration as a preset"""
        return self.model.save_preset(name, description, overwrite)
    
    # Nouvelles méthodes pour le système de presets avancé
    
    def get_preset_manager(self):
        """Retourne le gestionnaire de presets pour accès avancé"""
        return self.model.get_preset_manager()
    
    def get_presets_by_category(self, category: PresetCategory):
        """Retourne les presets d'une catégorie donnée"""
        return self.model.get_presets_by_category(category)
    
    def delete_preset(self, preset_name):
        """Supprime un preset utilisateur"""
        return self.model.delete_preset(preset_name)
    
    def get_current_state_as_preset_data(self):
        """Retourne l'état actuel sous forme de PresetData"""
        return self.model.get_current_state_as_preset_data()
    
    def create_preset_from_current_state(self, name, description="", category=None):
        """Crée un nouveau preset basé sur l'état actuel"""
        current_params = {
            "rod_group_R_position": self.model.rod_group_R_position,
            "rod_group_GCP_position": self.model.rod_group_GCP_position,
            "boron_concentration": self.model.boron_concentration,
            "average_temperature": self.model.average_temperature,
            "fuel_enrichment": self.model.fuel_enrichment,
            "power_level": self.model.power_level,
            "iodine_concentration": self.model.iodine_concentration,
            "xenon_concentration": self.model.xenon_concentration,
            "simulation_time": self.model.simulation_time
        }
        
        # Déterminer automatiquement la catégorie si non spécifiée
        if category is None:
            if self.model.simulation_time > 0 or self.model.xenon_concentration > 0:
                category = PresetCategory.TEMPOREL
            else:
                category = PresetCategory.PERSONNALISE
        
        try:
            preset = self.model.preset_manager.create_preset(
                name=name,
                description=description or f"Preset créé: {name}",
                parameters=current_params,
                category=category
            )
            return preset is not None
        except ValueError:
            return False
    
    def export_presets(self, file_path, preset_ids=None):
        """Exporte des presets vers un fichier"""
        return self.model.preset_manager.export_presets(file_path, preset_ids)
    
    def import_presets(self, file_path, overwrite=False):
        """Importe des presets depuis un fichier"""
        return self.model.preset_manager.import_presets(file_path, overwrite)
    
    def validate_preset_data(self, preset_data):
        """Valide les données d'un preset"""
        try:
            errors = preset_data.validate()
            return len(errors) == 0, errors
        except Exception as e:
            return False, [str(e)] 