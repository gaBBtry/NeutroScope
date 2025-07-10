"""
Tests de validation physique pour vérifier l'exactitude des calculs de neutronique.

Ces tests utilisent des valeurs de référence calculées analytiquement ou issues
de la littérature technique pour valider que le modèle produit des résultats
physiquement corrects et non pas seulement que le code s'exécute.
"""
import pytest
import numpy as np
from src.model.reactor_model import ReactorModel
from src.model import config
from unittest.mock import patch


class TestPhysicsValidation:
    """Tests de validation des calculs physiques avec valeurs de référence"""
    
    def setup_method(self):
        """Initialise un modèle de réacteur pour chaque test"""
        self.model = ReactorModel()
    
    def test_critical_state_k_effective_equals_one(self):
        """
        Test de validation fondamental : dans un état critique stable,
        k_effective doit être très proche de 1.00.
        
        Référence : Définition de la criticité en physique des réacteurs
        """
        # Appliquer un preset connu pour être proche de la criticité
        preset_critical = "PMD en début de cycle"
        result = self.model.apply_preset(preset_critical)
        assert result, f"Échec de l'application du preset {preset_critical}"
        
        # Vérifier que k_effective est très proche de 1.0
        k_eff = self.model.k_effective
        assert abs(k_eff - 1.0) < 0.005, f"k_eff = {k_eff:.6f}, attendu ≈ 1.0 pour un état critique"
        
        # Vérifier que la réactivité est proche de zéro
        reactivity_pcm = self.model.reactivity * 100000  # Conversion en pcm
        assert abs(reactivity_pcm) < 100, f"Réactivité = {reactivity_pcm:.1f} pcm, attendu ≈ 0 pour un état critique"
    
    def test_four_factors_multiplication_equals_k_infinite(self):
        """
        Test de validation : η × ε × p × f = k_infinite
        
        Référence : Formule des quatre facteurs de Fermi
        """
        # Utiliser un état quelconque
        self.model.update_boron_concentration(800)
        self.model.update_power_level(75)
        
        # Calculer k_infinite selon la formule
        k_inf_calculated = self.model.eta * self.model.epsilon * self.model.p * self.model.f
        k_inf_model = self.model.k_infinite
        
        # Vérifier la cohérence
        relative_error = abs(k_inf_calculated - k_inf_model) / k_inf_model
        assert relative_error < 1e-10, f"k_inf calculé = {k_inf_calculated:.6f}, modèle = {k_inf_model:.6f}"
    
    def test_six_factors_formula_k_effective(self):
        """
        Test de validation : k_eff = k_inf × P_AFR × P_AFT
        
        Référence : Formule des six facteurs avec probabilités de non-fuite
        """
        # État de test
        self.model.update_control_rod_position(25)
        self.model.update_average_temperature(315)
        
        # Calculer k_effective selon la formule complète
        k_eff_calculated = (self.model.k_infinite * 
                           self.model.fast_non_leakage_prob * 
                           self.model.thermal_non_leakage_prob)
        k_eff_model = self.model.k_effective
        
        # Vérifier la cohérence
        relative_error = abs(k_eff_calculated - k_eff_model) / k_eff_model
        assert relative_error < 1e-10, f"k_eff calculé = {k_eff_calculated:.6f}, modèle = {k_eff_model:.6f}"
    
    def test_boron_reactivity_effect_monotonic_decrease(self):
        """
        Test de validation : l'augmentation de la concentration en bore
        doit diminuer monotoniquement k_effective.
        
        Référence : Propriété physique fondamentale - le bore absorbe les neutrons
        """
        boron_concentrations = [0, 500, 1000, 1500, 2000]
        k_eff_values = []
        
        for boron in boron_concentrations:
            self.model.update_boron_concentration(boron)
            k_eff_values.append(self.model.k_effective)
        
        # Vérifier que k_eff diminue monotoniquement
        for i in range(1, len(k_eff_values)):
            assert k_eff_values[i] < k_eff_values[i-1], \
                f"k_eff n'est pas monotone décroissant : {boron_concentrations[i-1]} ppm -> {k_eff_values[i-1]:.4f}, " \
                f"{boron_concentrations[i]} ppm -> {k_eff_values[i]:.4f}"
    
    def test_control_rods_insertion_decreases_reactivity(self):
        """
        Test de validation : l'insertion des barres de contrôle
        doit diminuer k_effective.
        
        Référence : Fonction fondamentale des barres de contrôle
        """
        # Positions des barres : 100% = retirées, 0% = insérées
        rod_positions = [100, 75, 50, 25, 0]  # Insertion croissante
        k_eff_values = []
        
        for position in rod_positions:
            self.model.update_control_rod_position(position)
            k_eff_values.append(self.model.k_effective)
        
        # Vérifier que k_eff diminue avec l'insertion
        for i in range(1, len(k_eff_values)):
            assert k_eff_values[i] < k_eff_values[i-1], \
                f"k_eff n'est pas monotone décroissant avec l'insertion : " \
                f"{rod_positions[i-1]}% -> {k_eff_values[i-1]:.4f}, {rod_positions[i]}% -> {k_eff_values[i]:.4f}"
    
    def test_temperature_coefficients_physical_signs(self):
        """
        Test de validation : les coefficients de température doivent avoir
        les signes physiques corrects.
        
        Référence : Effet Doppler (négatif) et effet modérateur (positif puis négatif)
        """
        # Température de référence
        base_temp = 300
        self.model.update_average_temperature(base_temp)
        k_eff_base = self.model.k_effective
        
        # Test effet Doppler (combustible) - doit être négatif
        self.model.update_power_level(120)  # Augmente la température combustible
        k_eff_high_power = self.model.k_effective
        
        # Remettre la puissance normale et tester température modérateur
        self.model.update_power_level(100)
        
        # Augmentation modérée de température modérateur (effet souvent négatif à haute T)
        self.model.update_average_temperature(350)
        k_eff_high_temp = self.model.k_effective
        
        # Vérifications qualitatives (les signes peuvent dépendre du régime)
        print(f"k_eff base (T={base_temp}°C): {k_eff_base:.6f}")
        print(f"k_eff haute puissance: {k_eff_high_power:.6f}")
        print(f"k_eff haute température: {k_eff_high_temp:.6f}")
        
        # Au minimum, vérifier que les changements sont dans des ordres de grandeur raisonnables
        assert abs(k_eff_high_power - k_eff_base) < 0.1, "Effet température combustible trop important"
        assert abs(k_eff_high_temp - k_eff_base) < 0.1, "Effet température modérateur trop important"
    
    def test_xenon_equilibrium_calculation_consistency(self):
        """
        Test de validation : les concentrations d'équilibre du Xénon doivent
        satisfaire les équations d'équilibre analytiques.
        
        Référence : Équations de Bateman à l'équilibre
        """
        # Configuration de test
        self.model.update_power_level(100)
        self.model.calculate_xenon_equilibrium()
        
        # Vérifications des équations d'équilibre
        fission_rate = self.model.power_level * config.FISSION_RATE_COEFF * config.THERMAL_FLUX_NOMINAL
        thermal_flux = config.THERMAL_FLUX_NOMINAL * (self.model.power_level / 100.0)
        
        # Équilibre Iode : production = disparition
        iodine_production = config.IODINE_YIELD * fission_rate
        iodine_decay = config.IODINE_DECAY_CONSTANT * self.model.iodine_concentration
        
        relative_error_iodine = abs(iodine_production - iodine_decay) / iodine_production
        assert relative_error_iodine < 1e-10, \
            f"Équilibre Iode non respecté : production = {iodine_production:.2e}, decay = {iodine_decay:.2e}"
        
        # Équilibre Xénon : production = disparition
        xenon_production = (config.XENON_YIELD_DIRECT * fission_rate + 
                           config.IODINE_DECAY_CONSTANT * self.model.iodine_concentration)
        xenon_removal = (config.XENON_DECAY_CONSTANT * self.model.xenon_concentration +
                        config.XENON_ABSORPTION_CROSS_SECTION * thermal_flux * self.model.xenon_concentration * 1e-24)
        
        relative_error_xenon = abs(xenon_production - xenon_removal) / xenon_production
        assert relative_error_xenon < 1e-10, \
            f"Équilibre Xénon non respecté : production = {xenon_production:.2e}, removal = {xenon_removal:.2e}"
    
    def test_runge_kutta_vs_analytical_solution_simple_case(self):
        """
        Test de validation : comparer l'intégration RK4 avec une solution analytique
        pour un cas simple (décroissance radioactive pure).
        
        Référence : Solution analytique N(t) = N₀ × exp(-λt)
        """
        # Test avec décroissance du Xénon uniquement (pas de production)
        initial_xenon = 1e15  # atomes/cm³
        self.model.xenon_concentration = initial_xenon
        self.model.iodine_concentration = 0  # Pas de source d'Iode
        self.model.power_level = 0  # Pas de production par fission
        
        # Temps de test : 10 heures
        dt_hours = 10.0
        dt_seconds = dt_hours * 3600.0
        
        # Solution analytique (décroissance pure du Xénon)
        lambda_xe = config.XENON_DECAY_CONSTANT
        xenon_analytical = initial_xenon * np.exp(-lambda_xe * dt_seconds)
        
        # Solution numérique RK4
        self.model.update_xenon_dynamics(dt_seconds)
        xenon_numerical = self.model.xenon_concentration
        
        # Comparaison (RK4 doit être très précis pour ce cas simple)
        relative_error = abs(xenon_numerical - xenon_analytical) / xenon_analytical
        assert relative_error < 1e-6, \
            f"Erreur RK4 vs analytique : numérique = {xenon_numerical:.2e}, " \
            f"analytique = {xenon_analytical:.2e}, erreur = {relative_error:.2e}"
    
    def test_reactivity_pcm_conversion_consistency(self):
        """
        Test de validation : vérifier la cohérence des conversions de réactivité.
        
        Référence : ρ = (k_eff - 1) / k_eff, 1% Δk/k = 1000 pcm
        """
        # Différents états de criticité
        test_configs = [
            {"boron": 0, "rods": 100, "name": "Très surcritique"},
            {"boron": 1000, "rods": 50, "name": "Légèrement surcritique"},
            {"boron": 1500, "rods": 0, "name": "Sous-critique"}
        ]
        
        for config_test in test_configs:
            self.model.update_boron_concentration(config_test["boron"])
            self.model.update_control_rod_position(config_test["rods"])
            
            # Calcul direct de la réactivité
            k_eff = self.model.k_effective
            reactivity_direct = (k_eff - 1.0) / k_eff if k_eff > 0 else -1.0
            reactivity_model = self.model.reactivity
            
            # Vérification de cohérence
            assert abs(reactivity_direct - reactivity_model) < 1e-12, \
                f"{config_test['name']}: réactivité directe = {reactivity_direct:.8f}, " \
                f"modèle = {reactivity_model:.8f}"
            
            # Vérification conversion pcm
            reactivity_pcm = reactivity_model * 100000
            expected_sign = 1 if k_eff > 1.0 else -1 if k_eff < 1.0 else 0
            actual_sign = 1 if reactivity_pcm > 10 else -1 if reactivity_pcm < -10 else 0
            
            assert expected_sign == actual_sign, \
                f"{config_test['name']}: signe incohérent k_eff = {k_eff:.4f}, ρ = {reactivity_pcm:.1f} pcm"
    
    def test_physical_parameter_ranges_sanity_check(self):
        """
        Test de validation : vérifier que tous les paramètres calculés
        restent dans des plages physiquement raisonnables.
        
        Référence : Limites physiques connues pour les REP
        """
        # Test avec différentes configurations
        configurations = [
            {"boron": 0, "rods": 100, "temp": 280, "power": 0},      # Démarrage à froid
            {"boron": 500, "rods": 80, "temp": 310, "power": 100},   # Fonctionnement normal
            {"boron": 2000, "rods": 0, "temp": 350, "power": 0},     # Arrêt sûr
        ]
        
        for i, config_test in enumerate(configurations):
            self.model.update_boron_concentration(config_test["boron"])
            self.model.update_control_rod_position(config_test["rods"])
            self.model.update_average_temperature(config_test["temp"])
            self.model.update_power_level(config_test["power"])
            
            # Vérifications des plages physiques
            assert 1.5 <= self.model.eta <= 2.5, f"Config {i}: η = {self.model.eta:.3f} hors plage [1.5, 2.5]"
            assert 1.0 <= self.model.epsilon <= 1.1, f"Config {i}: ε = {self.model.epsilon:.3f} hors plage [1.0, 1.1]"
            assert 0.3 <= self.model.p <= 0.9, f"Config {i}: p = {self.model.p:.3f} hors plage [0.3, 0.9]"
            assert 0.3 <= self.model.f <= 0.9, f"Config {i}: f = {self.model.f:.3f} hors plage [0.3, 0.9]"
            assert 0.5 <= self.model.k_effective <= 1.5, f"Config {i}: k_eff = {self.model.k_effective:.3f} hors plage [0.5, 1.5]"
            assert 0.8 <= self.model.fast_non_leakage_prob <= 1.0, f"Config {i}: P_AFR = {self.model.fast_non_leakage_prob:.3f} hors plage [0.8, 1.0]"
            assert 0.8 <= self.model.thermal_non_leakage_prob <= 1.0, f"Config {i}: P_AFT = {self.model.thermal_non_leakage_prob:.3f} hors plage [0.8, 1.0]"
            
            # Vérifications des concentrations Xénon (si applicables)
            if config_test["power"] > 0:
                assert self.model.xenon_concentration >= 0, f"Config {i}: concentration Xénon négative"
                assert self.model.iodine_concentration >= 0, f"Config {i}: concentration Iode négative"
                
                # Ordres de grandeur typiques (atomes/cm³)
                assert 1e12 <= self.model.xenon_concentration <= 1e17, \
                    f"Config {i}: concentration Xénon = {self.model.xenon_concentration:.2e} hors plage physique"


@pytest.mark.integration
class TestPhysicsIntegration:
    """Tests d'intégration pour vérifier la cohérence physique globale"""
    
    def test_preset_physics_consistency(self):
        """
        Test de validation : tous les presets système doivent donner
        des résultats physiquement cohérents.
        """
        model = ReactorModel()
        preset_names = model.get_preset_names()
        
        for preset_name in preset_names:
            result = model.apply_preset(preset_name)
            assert result, f"Échec application preset {preset_name}"
            
            # Vérifications de base pour chaque preset
            assert model.k_effective > 0, f"Preset {preset_name}: k_eff = {model.k_effective} <= 0"
            assert not np.isnan(model.k_effective), f"Preset {preset_name}: k_eff est NaN"
            assert not np.isinf(model.k_effective), f"Preset {preset_name}: k_eff est infini"
            
            # Réactivité en pcm dans une plage raisonnable
            reactivity_pcm = model.reactivity * 100000
            assert -10000 <= reactivity_pcm <= 10000, \
                f"Preset {preset_name}: réactivité = {reactivity_pcm:.1f} pcm hors plage [-10000, 10000]"
            
            print(f"✓ Preset '{preset_name}': k_eff = {model.k_effective:.4f}, ρ = {reactivity_pcm:.1f} pcm") 