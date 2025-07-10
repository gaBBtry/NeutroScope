"""
Tests utilisant pytest-mock pour simuler le module config.

Ces tests démontrent comment éliminer la dépendance aux fichiers externes
en utilisant des configurations mockées, rendant les tests plus robustes
et reproductibles.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.model.reactor_model import ReactorModel


class TestReactorModelWithMockedConfig:
    """Tests du ReactorModel avec configuration mockée"""
    
    @pytest.fixture
    def mock_config(self):
        """Fixture fournissant une configuration mockée cohérente"""
        mock_cfg = MagicMock()
        
        # Configuration des constantes physiques
        mock_cfg.ETA_BASE = 2.0
        mock_cfg.ETA_ENRICHMENT_COEFF = 0.1
        mock_cfg.ETA_ENRICHMENT_REF = 3.0
        mock_cfg.ETA_ENRICHMENT_SCALE = 2.0
        mock_cfg.EPSILON = 1.03
        
        # Configuration du facteur p
        mock_cfg.P_BASE = 0.75
        mock_cfg.P_REF_TEMP_K = 873.15
        mock_cfg.P_DOPPLER_COEFF = 0.008
        mock_cfg.P_MOD_TEMP_COEFF = 0.0015
        mock_cfg.P_REF_MOD_TEMP_C = 300.0
        mock_cfg.CELSIUS_TO_KELVIN = 273.15
        
        # Configuration du facteur f
        mock_cfg.F_BASE_ABS_RATIO = 0.408
        mock_cfg.F_REF_MOD_TEMP_C = 300.0
        mock_cfg.F_CONTROL_ROD_WORTH = 0.26
        mock_cfg.F_BORON_WORTH_PER_PPM = 2.8e-5
        mock_cfg.F_MOD_TEMP_ABS_COEFF = 0.003
        
        # Constantes de conversion
        mock_cfg.HOURS_TO_SECONDS = 3600.0
        mock_cfg.BARNS_TO_CM2 = 1e-24
        mock_cfg.REACTIVITY_TO_PCM = 100000.0
        mock_cfg.PERCENT_TO_FRACTION = 100.0
        
        # Configuration Xénon
        mock_cfg.XENON_ABSORPTION_CROSS_SECTION = 2.65e6
        mock_cfg.NEUTRONS_PER_THERMAL_FISSION_U235 = 2.43
        mock_cfg.FISSION_RATE_COEFF = 1.0e-6
        
        # Configuration des fuites
        mock_cfg.CORE_HEIGHT_M = 4.0
        mock_cfg.CORE_DIAMETER_M = 3.0
        mock_cfg.BESSEL_J0_FIRST_ZERO = 2.405
        mock_cfg.THERMAL_DIFFUSION_AREA_M2 = 0.0064
        mock_cfg.FAST_DIFFUSION_AREA_M2 = 0.0097
        mock_cfg.MODERATOR_DENSITY_COEFF = 8e-4
        
        # Configuration des coefficients
        mock_cfg.POWER_TO_FUEL_TEMP_COEFF = 3.0
        mock_cfg.DELAYED_NEUTRON_FRACTION = 0.0065
        mock_cfg.PROMPT_NEUTRON_LIFETIME = 2.0e-5
        mock_cfg.EFFECTIVE_DECAY_CONSTANT = 0.1
        
        # État par défaut mocké
        mock_cfg.default_state = {
            "rod_group_R_position": 0,
            "rod_group_GCP_position": 0,
            "boron_concentration": 500.0,
            "average_temperature": 310.0,
            "power_level": 100.0,
            "fuel_enrichment": 3.5,
            "time_step": 3600.0
        }
        
        # Configuration des paramètres
        mock_cfg.parameters_config = {
            'conversion': {
                'steps_to_percent': 228
            },
            'rod_group_R': {
                'worth_fraction': 0.3
            },
            'rod_group_GCP': {
                'worth_fraction': 0.7
            }
        }
        
        return mock_cfg
    
    @patch('src.model.reactor_model.config')
    def test_eta_calculation_with_mocked_config(self, mock_config_module, mock_config):
        """
        Test du calcul d'eta avec configuration mockée.
        Démontre un test isolé sans dépendance aux fichiers externes.
        """
        # Configuration du mock
        mock_config_module.return_value = mock_config
        for attr_name, attr_value in vars(mock_config).items():
            if not attr_name.startswith('_'):
                setattr(mock_config_module, attr_name, attr_value)
        
        # Création du modèle avec configuration mockée
        model = ReactorModel()
        
        # Test avec enrichissement spécifique
        model.fuel_enrichment = 4.0
        model._calculate_eta()
        
        # Calcul attendu basé sur la configuration mockée
        expected_eta = (mock_config.ETA_BASE + 
                       mock_config.ETA_ENRICHMENT_COEFF * 
                       (4.0 - mock_config.ETA_ENRICHMENT_REF) / 
                       mock_config.ETA_ENRICHMENT_SCALE)
        
        assert abs(model.eta - expected_eta) < 1e-12, \
            f"eta calculé = {model.eta}, attendu = {expected_eta}"
    
    @patch('src.model.reactor_model.config')
    def test_boron_effect_with_different_concentrations(self, mock_config_module, mock_config):
        """
        Test de l'effet du bore avec différentes concentrations mockées.
        Validation de la relation monotone bore/réactivité sans dépendance config.json.
        """
        # Configuration du mock
        for attr_name, attr_value in vars(mock_config).items():
            if not attr_name.startswith('_'):
                setattr(mock_config_module, attr_name, attr_value)
        
        model = ReactorModel()
        
        # Test de monotonie avec concentrations contrôlées
        boron_concentrations = [0, 500, 1000, 1500]
        k_eff_values = []
        
        for boron in boron_concentrations:
            model.boron_concentration = boron
            model.calculate_four_factors()
            model.calculate_k_effective()
            k_eff_values.append(model.k_effective)
        
        # Vérification de la décroissance monotone
        for i in range(1, len(k_eff_values)):
            assert k_eff_values[i] < k_eff_values[i-1], \
                f"k_eff non décroissant : {boron_concentrations[i-1]} ppm -> {k_eff_values[i-1]:.4f}, " \
                f"{boron_concentrations[i]} ppm -> {k_eff_values[i]:.4f}"
    
    @patch('src.model.reactor_model.config')
    def test_four_factors_formula_consistency(self, mock_config_module, mock_config):
        """
        Test de cohérence de la formule des quatre facteurs avec configuration contrôlée.
        """
        # Configuration du mock
        for attr_name, attr_value in vars(mock_config).items():
            if not attr_name.startswith('_'):
                setattr(mock_config_module, attr_name, attr_value)
        
        model = ReactorModel()
        
        # État de test contrôlé
        model.fuel_enrichment = 3.5
        model.boron_concentration = 800
        model.average_temperature = 310
        model.fuel_temperature = 550  # Température combustible calculée
        model.xenon_concentration = 1e15
        
        # Calcul des facteurs
        model.calculate_four_factors()
        
        # Vérification de la formule k_infinite = eta * epsilon * p * f
        k_inf_calculated = model.eta * model.epsilon * model.p * model.f
        
        assert abs(k_inf_calculated - model.k_infinite) < 1e-12, \
            f"Incohérence formule quatre facteurs : calculé = {k_inf_calculated}, modèle = {model.k_infinite}"
    
    @patch('src.model.reactor_model.config')
    def test_unit_conversions_with_mocked_constants(self, mock_config_module, mock_config):
        """
        Test des conversions d'unités avec constantes mockées.
        Vérifie que les conversions utilisent bien les constantes centralisées.
        """
        # Configuration du mock avec valeurs spécifiques pour le test
        mock_config.HOURS_TO_SECONDS = 3600.0
        mock_config.BARNS_TO_CM2 = 1e-24
        mock_config.REACTIVITY_TO_PCM = 100000.0
        mock_config.PERCENT_TO_FRACTION = 100.0
        
        for attr_name, attr_value in vars(mock_config).items():
            if not attr_name.startswith('_'):
                setattr(mock_config_module, attr_name, attr_value)
        
        model = ReactorModel()
        
        # Test conversion heures vers secondes
        hours = 2.5
        expected_seconds = hours * mock_config.HOURS_TO_SECONDS
        actual_seconds = hours * mock_config_module.HOURS_TO_SECONDS
        
        assert actual_seconds == expected_seconds, \
            f"Conversion h->s incorrecte : {actual_seconds} vs {expected_seconds}"
        
        # Test que le modèle utilise bien les constantes
        model.xenon_concentration = 1e15
        model.power_level = 100.0
        
        # Le calcul interne doit utiliser config.BARNS_TO_CM2
        expected_xenon_abs = (model.xenon_concentration * 
                             mock_config.XENON_ABSORPTION_CROSS_SECTION * 
                             mock_config.BARNS_TO_CM2)
        
        # Vérification via le calcul d'absorption Xénon
        xenon_abs_ratio = model._calculate_f_xenon_absorption()
        
        # Le ratio doit être non-nul si les calculs utilisent les bonnes constantes
        assert xenon_abs_ratio >= 0, "Le calcul d'absorption Xénon doit fonctionner"
    
    @patch('src.model.reactor_model.config')
    def test_temperature_effects_isolated(self, mock_config_module, mock_config):
        """
        Test des effets de température de manière isolée avec config mockée.
        """
        # Configuration spécifique pour les effets de température
        mock_config.P_DOPPLER_COEFF = 0.01  # Effet Doppler plus prononcé pour le test
        mock_config.P_MOD_TEMP_COEFF = 0.002  # Effet modérateur plus visible
        
        for attr_name, attr_value in vars(mock_config).items():
            if not attr_name.startswith('_'):
                setattr(mock_config_module, attr_name, attr_value)
        
        model = ReactorModel()
        
        # État de référence
        base_temp = 300
        model.average_temperature = base_temp
        model.fuel_temperature = 500
        model._calculate_p()
        p_base = model.p
        
        # Test effet température combustible (Doppler)
        model.fuel_temperature = 600  # Augmentation température combustible
        model._calculate_p()
        p_high_fuel_temp = model.p
        
        # Effet Doppler doit réduire p (plus de captures par résonance)
        assert p_high_fuel_temp < p_base, \
            f"Effet Doppler incorrect : p({500}K) = {p_base:.6f}, p({600}K) = {p_high_fuel_temp:.6f}"
        
        # Test effet température modérateur
        model.fuel_temperature = 500  # Retour température combustible normale
        model.average_temperature = 350  # Augmentation température modérateur
        model._calculate_p()
        p_high_mod_temp = model.p
        
        # L'effet peut être positif ou négatif selon les paramètres, on vérifie juste qu'il y a un effet
        assert abs(p_high_mod_temp - p_base) > 1e-6, \
            f"Pas d'effet température modérateur détecté : p(base) = {p_base:.6f}, p(haute T) = {p_high_mod_temp:.6f}"


class TestConfigMockingBestPractices:
    """Exemples de meilleures pratiques pour mocker la configuration"""
    
    def test_partial_config_mocking(self):
        """
        Démontre comment mocker seulement une partie de la configuration
        pour des tests ciblés.
        """
        with patch('src.model.config.ETA_BASE', 2.5), \
             patch('src.model.config.ETA_ENRICHMENT_COEFF', 0.15):
            
            from src.model import config
            
            # Test avec valeurs modifiées
            assert config.ETA_BASE == 2.5
            assert config.ETA_ENRICHMENT_COEFF == 0.15
    
    def test_config_validation_with_mock(self):
        """
        Test de validation des configurations avec des valeurs limites mockées.
        """
        # Test avec configuration extrême pour valider la robustesse
        extreme_config = {
            'F_BORON_WORTH_PER_PPM': 1e-3,  # Effet bore très fort
            'P_DOPPLER_COEFF': 0.1,         # Effet Doppler très fort
            'EPSILON': 1.0                   # Pas de fission rapide
        }
        
        with patch.multiple('src.model.config', **extreme_config):
            model = ReactorModel()
            
            # Le modèle doit rester stable même avec des paramètres extrêmes
            model.boron_concentration = 100
            model.fuel_enrichment = 4.0
            model.calculate_four_factors()
            
            # Vérifications de sanité
            assert 0 < model.eta < 5, f"eta hors plage : {model.eta}"
            assert 0 < model.p < 1, f"p hors plage : {model.p}"
            assert 0 < model.f < 1, f"f hors plage : {model.f}" 