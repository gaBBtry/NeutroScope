"""
Controller module connecting the UI with the reactor model
"""
from src.model.reactor_model import ReactorModel
from src.model.abstract_reactor_model import AbstractReactorModel
from src.model.preset_model import PresetCategory
from src.model import config
import copy
from typing import Type


class ReactorController:
    """Contrôleur pour l'interface entre la vue et le modèle de réacteur"""
    
    def __init__(self, model_class: Type[AbstractReactorModel] = ReactorModel):
        """
        Initialise le contrôleur avec un modèle de réacteur.
        
        Args:
            model_class: Classe du modèle de réacteur à utiliser (doit hériter d'AbstractReactorModel)
        """
        self.model: AbstractReactorModel = model_class()
    
    # --- MÉTHODES DE CONTRÔLE CIBLÉ ---
    def set_target_rod_group_R_position(self, position):
        """Définit la position CIBLE pour le groupe R (0-228 pas)"""
        self.model.set_target_rod_group_R_position(position)
    
    def set_target_rod_group_GCP_position(self, position):
        """Définit la position CIBLE pour le groupe GCP (0-228 pas)"""
        self.model.set_target_rod_group_GCP_position(position)
    
    def set_target_boron_concentration(self, concentration):
        """Définit la concentration CIBLE pour le bore"""
        self.model.set_target_boron_concentration(concentration)

    def update_fuel_enrichment(self, enrichment):
        """Met à jour l'enrichissement du combustible. L'effet est instantané."""
        self.model.update_fuel_enrichment(enrichment)
        # Ne retourne rien, la mise à jour se voit au prochain tick

    # --- MÉTHODES DE RÉCUPÉRATION DE DONNÉES ---
    def get_rod_group_positions(self):
        """Get current positions of both rod groups"""
        return {
            "R": self.model.rod_group_R_position,
            "GCP": self.model.rod_group_GCP_position
        }
    
    def get_rod_groups_info(self):
        """Get information about rod groups configuration"""
        return {
            "R": {
                "position": self.model.rod_group_R_position,
                "target_position": self.model.target_rod_group_R_position,
                "description": config.control_rod_groups['R']['description'],
                "worth_fraction": config.control_rod_groups['R']['worth_fraction'],
                "min_step": config.control_rod_groups['R']['min_step'],
                "max_step": config.control_rod_groups['R']['max_step'],
                "normal_step": config.control_rod_groups['R']['normal_step'],
                "speed_steps_per_sec": config.control_rod_groups['R']['speed_steps_per_sec'],
                "position_range": config.control_rod_groups['R']['position_range']
            },
            "GCP": {
                "position": self.model.rod_group_GCP_position,
                "target_position": self.model.target_rod_group_GCP_position,
                "description": config.control_rod_groups['GCP']['description'],
                "worth_fraction": config.control_rod_groups['GCP']['worth_fraction'],
                "min_step": config.control_rod_groups['GCP']['min_step'],
                "max_step": config.control_rod_groups['GCP']['max_step'],
                "normal_step": config.control_rod_groups['GCP']['normal_step'],
                "speed_steps_per_sec": config.control_rod_groups['GCP']['speed_steps_per_sec'],
                "position_range": config.control_rod_groups['GCP']['position_range']
            },
            "conversion": config.control_rod_groups['conversion']
        }

    def update_control_rod_position(self, position):
        """Méthode de rétrocompatibilité. Définit les cibles des deux groupes."""
        self.model.update_control_rod_position(position)
    
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
            "fast_non_leakage_prob": self.model.fast_non_leakage_prob,
            "fuel_temperature": self.model.fuel_temperature,
            "moderator_temperature": self.model.moderator_temperature,
            "power_level": self.model.power_level,
            "neutron_flux": self.model.neutron_flux
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
            "target_rod_group_R_position": self.model.target_rod_group_R_position,
            "target_rod_group_GCP_position": self.model.target_rod_group_GCP_position,
            "boron_concentration": self.model.boron_concentration,
            "target_boron_concentration": self.model.target_boron_concentration,
            "moderator_temperature": self.model.moderator_temperature,
            "fuel_temperature": self.model.fuel_temperature,
            "fuel_enrichment": self.model.fuel_enrichment,
            "power_level": self.model.power_level
        }
    
    def get_xenon_dynamics_data(self):
        """Get the xenon dynamics data from the model"""
        return self.model.get_xenon_dynamics_data()
    
    def advance_time(self, hours=1.0):
        """Fait avancer la simulation temporelle."""
        self.model.advance_time(hours)
        return self.get_reactor_parameters()
    
    def reset_xenon_to_equilibrium(self):
        """Réinitialise les concentrations de xénon à l'équilibre et l'état temporel."""
        self.model.simulation_time = 0.0
        self.model.calculate_xenon_equilibrium()
        # Il faut aussi réinitialiser les températures à l'équilibre
        self.model._calculate_equilibrium_temperatures()
        self.model.calculate_all()
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
                "moderator_temperature": self.model.moderator_temperature,
                "fuel_temperature": self.model.fuel_temperature,
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
        current_state_data = self.model.get_current_state_as_preset_data()
        
        # Le PresetManager s'attend à un dictionnaire de paramètres
        parameters = {
            "rod_group_R_position": current_state_data.rod_group_R_position,
            "rod_group_GCP_position": current_state_data.rod_group_GCP_position,
            "boron_concentration": current_state_data.boron_concentration,
            "average_temperature": current_state_data.average_temperature,
            "fuel_enrichment": current_state_data.fuel_enrichment,
            "power_level": current_state_data.power_level,
            "iodine_concentration": current_state_data.iodine_concentration,
            "xenon_concentration": current_state_data.xenon_concentration,
            "simulation_time": current_state_data.simulation_time
        }

        # Déterminer automatiquement la catégorie si non spécifiée
        if category is None:
            category = current_state_data.category
        
        try:
            preset = self.model.preset_manager.create_preset(
                name=name,
                description=description or f"Preset créé: {name}",
                parameters=parameters,
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