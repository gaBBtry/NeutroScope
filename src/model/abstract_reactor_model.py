"""
Interface abstraite pour les modèles de réacteur nucléaire.
Cette interface définit le contrat que tout modèle de physique de réacteur doit respecter
pour être compatible avec le contrôleur et l'interface utilisateur de NeutroScope.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
from .preset_model import PresetManager, PresetData, PresetCategory


class AbstractReactorModel(ABC):
    """
    Interface abstraite pour les modèles de réacteur nucléaire.
    
    Cette classe définit toutes les méthodes qu'un modèle de physique de réacteur
    doit implémenter pour être compatible avec NeutroScope.
    """
    
    # === MÉTHODES DE CONTRÔLE DES PARAMÈTRES ===
    
    @abstractmethod
    def set_target_rod_group_R_position(self, position: float) -> None:
        """Définit la position CIBLE pour le groupe de barres R (0-228 pas)."""
        pass
    
    @abstractmethod
    def set_target_rod_group_GCP_position(self, position: float) -> None:
        """Définit la position CIBLE pour le groupe de barres GCP (0-228 pas)."""
        pass
    
    @abstractmethod
    def set_target_boron_concentration(self, concentration: float) -> None:
        """Définit la concentration CIBLE pour le bore (ppm)."""
        pass
    
    @abstractmethod
    def update_fuel_enrichment(self, enrichment: float) -> None:
        """Met à jour l'enrichissement du combustible (%). L'effet est instantané."""
        pass
    
    @abstractmethod
    def update_control_rod_position(self, position: float) -> None:
        """Méthode de rétrocompatibilité. Définit les cibles des deux groupes de barres."""
        pass
    
    # === MÉTHODES DE RÉCUPÉRATION DES PARAMÈTRES CALCULÉS ===
    
    @abstractmethod
    def get_reactor_parameters(self) -> Dict[str, float]:
        """
        Récupère tous les paramètres calculés du réacteur.
        
        Returns:
            Dict contenant: k_effective, k_infinite, reactivity, doubling_time,
            delayed_neutron_fraction, eta, epsilon, p, f, thermal_non_leakage_prob,
            fast_non_leakage_prob, fuel_temperature, moderator_temperature,
            power_level, neutron_flux
        """
        pass
    
    @abstractmethod
    def get_current_configuration(self) -> Dict[str, float]:
        """
        Récupère la configuration actuelle du réacteur.
        
        Returns:
            Dict contenant les positions actuelles et cibles des barres, 
            concentrations de bore, températures, enrichissement, niveau de puissance
        """
        pass
    
    # === MÉTHODES DE VISUALISATION ===
    
    @abstractmethod
    def get_axial_flux_distribution(self) -> Tuple[Any, Any]:
        """
        Récupère la distribution axiale du flux neutronique.
        
        Returns:
            Tuple (height_array, flux_array) pour la visualisation
        """
        pass
    
    @abstractmethod
    def get_four_factors_data(self) -> Dict[str, float]:
        """
        Récupère les données des quatre facteurs neutroniques.
        
        Returns:
            Dict contenant eta, epsilon, p, f, k_infinite, thermal_non_leakage_prob,
            fast_non_leakage_prob, k_effective
        """
        pass
    
    @abstractmethod
    def get_neutron_balance_data(self) -> Dict[str, Any]:
        """
        Récupère les données de bilan neutronique pour la visualisation.
        
        Returns:
            Dict contenant les données pour le graphique en secteurs du bilan neutronique
        """
        pass
    
    @abstractmethod
    def get_neutron_cycle_data(self) -> Dict[str, Any]:
        """
        Récupère les données du cycle neutronique pour la visualisation.
        
        Returns:
            Dict contenant les données pour le diagramme de cycle neutronique
        """
        pass
    
    @abstractmethod
    def get_xenon_dynamics_data(self) -> Dict[str, Any]:
        """
        Récupère les données de dynamique du xénon.
        
        Returns:
            Dict contenant les concentrations d'iode et de xénon, temps de simulation
        """
        pass
    
    # === MÉTHODES DE SIMULATION TEMPORELLE ===
    
    @abstractmethod
    def advance_time(self, hours: float = 1.0) -> Dict[str, float]:
        """
        Fait avancer la simulation temporelle.
        
        Args:
            hours: nombre d'heures à simuler
            
        Returns:
            Dict des paramètres du réacteur après l'avancement temporel
        """
        pass
    
    @abstractmethod
    def reset_xenon_to_equilibrium(self) -> None:
        """Réinitialise les concentrations de xénon à l'équilibre et l'état temporel."""
        pass
    
    # === MÉTHODES DE GESTION DES PRESETS ===
    
    @abstractmethod
    def get_preset_names(self) -> List[str]:
        """Récupère la liste des noms de presets disponibles."""
        pass
    
    @abstractmethod
    def apply_preset(self, preset_name: str) -> bool:
        """
        Applique une configuration prédéfinie.
        
        Args:
            preset_name: nom du preset à appliquer
            
        Returns:
            True si le preset a été appliqué avec succès, False sinon
        """
        pass
    
    @abstractmethod
    def get_current_preset_name(self) -> Optional[str]:
        """Récupère le nom du preset actuel si il correspond à un preset existant."""
        pass
    
    @abstractmethod
    def save_preset(self, name: str, description: str = "", overwrite: bool = False) -> bool:
        """
        Sauvegarde la configuration actuelle comme preset.
        
        Args:
            name: nom du preset
            description: description du preset
            overwrite: si True, écrase un preset existant avec le même nom
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        pass
    
    # === MÉTHODES AVANCÉES DE GESTION DES PRESETS ===
    
    @abstractmethod
    def get_preset_manager(self) -> PresetManager:
        """Retourne le gestionnaire de presets pour accès avancé."""
        pass
    
    @abstractmethod
    def get_presets_by_category(self, category: PresetCategory) -> List[Any]:
        """Retourne les presets d'une catégorie donnée."""
        pass
    
    @abstractmethod
    def delete_preset(self, preset_name: str) -> bool:
        """Supprime un preset utilisateur."""
        pass
    
    @abstractmethod
    def get_current_state_as_preset_data(self) -> PresetData:
        """Retourne l'état actuel sous forme de PresetData."""
        pass
    
    # === MÉTHODES AUXILIAIRES ===
    
    @abstractmethod
    def _get_equivalent_rod_position_percent(self) -> float:
        """
        Calcule la position équivalente des barres en pourcentage.
        Méthode utilisée par les visualisations.
        """
        pass 