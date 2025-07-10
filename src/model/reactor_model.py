"""
Modèle de physique des réacteurs pour les calculs de neutronique
"""
import numpy as np
from . import config
from .preset_model import PresetManager, PresetData, PresetCategory, PresetType

class ReactorModel:
    """
    Modèle de réacteur de base implémentant les calculs de neutronique pour un REP
    """
    
    def __init__(self):
        # Paramètres par défaut chargés depuis la configuration
        defaults = config.default_state
        self.rod_group_R_position = defaults.get("rod_group_R_position", 0)
        self.rod_group_GCP_position = defaults.get("rod_group_GCP_position", 0)
        self.boron_concentration = defaults.get("boron_concentration", 500.0)
        self.average_temperature = defaults.get("average_temperature", 310.0)
        self.power_level = defaults.get("power_level", 100.0)
        self.fuel_enrichment = defaults.get("fuel_enrichment", 3.5)
        self.time_step = defaults.get("time_step", config.HOURS_TO_SECONDS)

        # Ceci est maintenant une valeur calculée, pas une entrée directe
        self.fuel_temperature = 0.0  # °C, sera calculée
        
        # Constantes physiques
        self.delayed_neutron_fraction = config.DELAYED_NEUTRON_FRACTION  # β
        
        # Variables de dynamique Xénon-135 (concentrations en atomes/cm³)
        self.iodine_concentration = 0.0  # I-135 concentration
        self.xenon_concentration = 0.0   # Xe-135 concentration
        self.simulation_time = 0.0       # temps de simulation en secondes
        
        # Paramètres calculés
        self.k_effective = 1.0
        self.k_infinite = 1.0
        self.reactivity = 0.0
        self.doubling_time = float('inf')  # secondes
        
        # Quatre facteurs
        self.eta = 2.0  # nombre moyen de neutrons par fission
        self.epsilon = 1.03  # facteur de fission rapide
        self.p = 0.75  # probabilité d'échapper aux résonances
        self.f = 0.71  # facteur d'utilisation thermique
        
        # Facteurs de fuite neutronique
        self.thermal_non_leakage_prob = 1.0
        self.fast_non_leakage_prob = 1.0
        
        # Nouveau système de gestion des presets avancé
        self.preset_manager = PresetManager()
        
        # Calcul initial et initialisation des concentrations Xénon à l'équilibre
        self._update_temperatures()
        self.calculate_xenon_equilibrium()  # Initialiser à l'équilibre pour le niveau de puissance actuel
        self.calculate_all()

    def _update_temperatures(self):
        """Calcule la température du combustible en fonction du niveau de puissance et de la température du modérateur."""
        self.fuel_temperature = self.average_temperature + (self.power_level * config.POWER_TO_FUEL_TEMP_COEFF)

    def calculate_all(self):
        """Calcule tous les paramètres du réacteur en fonction des entrées actuelles"""
        self.calculate_four_factors()
        self.calculate_k_effective()
        self.calculate_reactivity()
        self.calculate_doubling_time()
    
    def _calculate_eta(self):
        """
        Calcule le facteur de reproduction (η) - nombre moyen de neutrons par fission.
        Dépend principalement de l'enrichissement du combustible.
        """
        self.eta = (config.ETA_BASE + 
                   config.ETA_ENRICHMENT_COEFF * 
                   (self.fuel_enrichment - config.ETA_ENRICHMENT_REF) / 
                   config.ETA_ENRICHMENT_SCALE)
    
    def _calculate_epsilon(self):
        """
        Calcule le facteur de fission rapide (ε) - rapport entre neutrons produits 
        par toutes les fissions et ceux produits par fissions thermiques uniquement.
        Typiquement constant pour une conception de réacteur donnée.
        """
        self.epsilon = config.EPSILON
    
    def _calculate_p(self):
        """
        Calcule la probabilité d'échapper aux résonances (p).
        Affectée par la température du combustible (effet Doppler) et 
        la température du modérateur (densité et efficacité de ralentissement).
        """
        # 1. Effet Doppler (température du combustible)
        fuel_temp_K = self.fuel_temperature + config.CELSIUS_TO_KELVIN
        sqrt_T_diff = np.sqrt(fuel_temp_K) - np.sqrt(config.P_REF_TEMP_K)
        doppler_effect = np.exp(-config.P_DOPPLER_COEFF * sqrt_T_diff)
        
        # 2. Effet température du modérateur (densité et efficacité de ralentissement)
        mod_temp_deviation = self.average_temperature - config.P_REF_MOD_TEMP_C
        moderator_effect = 1.0 - config.P_MOD_TEMP_COEFF * mod_temp_deviation
        
        # 3. Combinaison des deux effets
        self.p = config.P_BASE * doppler_effect * moderator_effect
    
    def _calculate_f_base_absorption(self):
        """
        Calcule le rapport d'absorption de base (structures, modérateur, etc.)
        ajusté pour la température du modérateur.
        """
        temp_deviation = self.average_temperature - config.F_REF_MOD_TEMP_C
        mod_temp_effect = config.F_MOD_TEMP_ABS_COEFF * temp_deviation
        return config.F_BASE_ABS_RATIO * (1 + mod_temp_effect)
    
    def _calculate_f_control_rods_absorption(self):
        """
        Calcule le rapport d'absorption des barres de contrôle.
        Convention: 0% = insérées, 100% = retirées.
        """
        rod_insertion_fraction = (config.PERCENT_TO_FRACTION - self._get_equivalent_rod_position_percent()) / config.PERCENT_TO_FRACTION
        return config.F_CONTROL_ROD_WORTH * rod_insertion_fraction
    
    def _calculate_f_boron_absorption(self):
        """
        Calcule le rapport d'absorption du bore soluble.
        """
        return config.F_BORON_WORTH_PER_PPM * self.boron_concentration
    
    def _calculate_f_xenon_absorption(self):
        """
        Calcule le rapport d'absorption du Xénon-135.
        Utilise le rapport Σa_xenon / Σa_fuel pour assurer la cohérence dimensionnelle.
        """
        # Section efficace d'absorption du Xénon
        sigma_a_xenon = self.xenon_concentration * config.XENON_ABSORPTION_CROSS_SECTION * config.BARNS_TO_CM2

        # Calcul de Σa_fuel à partir de la définition de eta = nu * Σf / Σa_fuel
        sigma_f_nominal = config.FISSION_RATE_COEFF * 100.0  # Valeur de Σf à 100% puissance

        if self.eta > 1e-9:  # Prévenir la division par zéro
            sigma_a_fuel_nominal = (sigma_f_nominal * config.NEUTRONS_PER_THERMAL_FISSION_U235) / self.eta
        else:
            sigma_a_fuel_nominal = 1.0  # Fallback sécuritaire

        if sigma_a_fuel_nominal > 1e-9:
            return sigma_a_xenon / sigma_a_fuel_nominal
        else:
            return 0.0
    
    def _calculate_f(self):
        """
        Calcule le facteur d'utilisation thermique (f).
        Modèle basé sur les rapports d'absorption : f = 1 / (1 + A_non_fuel)
        où A_non_fuel est le rapport d'absorption totale dans les matériaux non-combustibles.
        """
        # Calcul des différentes contributions à l'absorption non-combustible
        base_abs_ratio = self._calculate_f_base_absorption()
        rod_abs_ratio = self._calculate_f_control_rods_absorption()
        boron_abs_ratio = self._calculate_f_boron_absorption()
        xenon_abs_ratio = self._calculate_f_xenon_absorption()
        
        # Rapport d'absorption total non-combustible
        total_non_fuel_abs_ratio = (base_abs_ratio + rod_abs_ratio + 
                                   boron_abs_ratio + xenon_abs_ratio)
        
        self.f = 1.0 / (1.0 + total_non_fuel_abs_ratio)
    
    def calculate_four_factors(self):
        """
        Calcule les quatre facteurs du cycle neutronique en utilisant 
        des méthodes dédiées pour chaque facteur.
        
        Ordre de calcul important : eta avant f pour les calculs de Xénon.
        """
        self._calculate_eta()      # η - facteur de reproduction
        self._calculate_epsilon()  # ε - facteur de fission rapide  
        self._calculate_p()        # p - probabilité d'échapper aux résonances
        self._calculate_f()        # f - facteur d'utilisation thermique
    
    def calculate_k_effective(self):
        """
        Calculate k-effective using the analytical model.
        """
        self._calculate_k_effective_analytical()

    def _calculate_k_effective_analytical(self):
        """Calcul k-effectif avec le modèle analytique."""
        # --- Calcul analytique ---
        self.k_infinite = self.eta * self.epsilon * self.p * self.f
        
        # Nouveau calcul de fuite basé sur la théorie de diffusion à deux groupes
        # 1. Laplacien géométrique B^2
        R = config.CORE_DIAMETER_M / 2.0
        H = config.CORE_HEIGHT_M
        geometric_buckling = (np.pi / H)**2 + (config.BESSEL_J0_FIRST_ZERO / R)**2
        
        # 2. Effet de la température sur la densité du modérateur et les aires de diffusion
        # L^2 et L_s^2 sont proportionnels à (rho_ref/rho_T)^2
        temp_deviation = self.average_temperature - config.F_REF_MOD_TEMP_C
        density_ratio = 1.0 / (1.0 - config.MODERATOR_DENSITY_COEFF * temp_deviation)
        
        thermal_diffusion_area = config.THERMAL_DIFFUSION_AREA_M2 * (density_ratio**2)
        fast_diffusion_area = config.FAST_DIFFUSION_AREA_M2 * (density_ratio**2)
        
        # 3. Probabilités de non-fuite
        self.fast_non_leakage_prob = 1.0 / (1.0 + geometric_buckling * fast_diffusion_area)
        self.thermal_non_leakage_prob = 1.0 / (1.0 + geometric_buckling * thermal_diffusion_area)
        
        self.k_effective = self.k_infinite * self.fast_non_leakage_prob * self.thermal_non_leakage_prob

    def calculate_reactivity(self):
        """Calculate reactivity (ρ) from k-effective"""
        if self.k_effective > 0:
            self.reactivity = (self.k_effective - 1.0) / self.k_effective
        else:
            self.reactivity = -float('inf')
    
    def calculate_doubling_time(self):
        """
        Calcule la période du réacteur/temps de doublement en utilisant une approximation standard.
        La période du réacteur T est le temps nécessaire pour que la population de neutrons change d'un facteur e.
        Le temps de doublement est T * ln(2).
        """
        if self.reactivity <= 0:
            self.doubling_time = float('inf')
            return

        # Utiliser la réactivité en unités absolues, pas en pcm ou %
        rho = self.reactivity

        if rho >= self.delayed_neutron_fraction:
            # Critique prompt - période très courte
            # Utilisation de l'approximation du saut prompt : T = l / (ρ - β)
            prompt_reactivity = rho - self.delayed_neutron_fraction
            if prompt_reactivity > 0:
                period = config.PROMPT_NEUTRON_LIFETIME / prompt_reactivity
                self.doubling_time = period * np.log(2)
            else:
                # Exactement critique prompt, la période est théoriquement zéro.
                self.doubling_time = 0.0
        else:
            # Calcul de la période critique retardée
            # T ≈ (β - ρ) / (λ_eff * ρ) - ceci est plus précis que l'approximation précédente
            # pour ρ proche de β. Restons avec la plus simple pour l'instant.
            # Utilisation de l'approximation à un groupe de neutrons retardés T ≈ β / (λ * ρ)
            # où λ est la constante de décroissance effective des précurseurs de neutrons retardés.
            # Une valeur typique pour λ_eff est ~0.1 s⁻¹
            effective_decay_constant = config.EFFECTIVE_DECAY_CONSTANT  # lambda_eff (s^-1)
            
            # Une approximation plus simple et plus courante pour une petite réactivité est T ≈ β / (λ * ρ)
            if rho > 0:
                period = self.delayed_neutron_fraction / (rho * effective_decay_constant)
                self.doubling_time = period * np.log(2)
            else:
                self.doubling_time = float('inf')

    def calculate_xenon_equilibrium(self):
        """
        Calcule les concentrations d'équilibre de l'Iode-135 et du Xénon-135
        pour le niveau de puissance actuel.
        """
        # Taux de fission basé sur le niveau de puissance
        fission_rate = self.power_level * config.FISSION_RATE_COEFF * config.THERMAL_FLUX_NOMINAL
        
        # Concentrations d'équilibre
        # Iode: λI * [I] = γI * Σf * Φ (production = disparition)
        self.iodine_concentration = (config.IODINE_YIELD * fission_rate) / config.IODINE_DECAY_CONSTANT
        
        # Xénon: λX * [Xe] + σXe * Φ * [Xe] = γXe * Σf * Φ + λI * [I]
        thermal_flux = config.THERMAL_FLUX_NOMINAL * (self.power_level / config.PERCENT_TO_FRACTION)
        xenon_removal_rate = config.XENON_DECAY_CONSTANT + config.XENON_ABSORPTION_CROSS_SECTION * thermal_flux * config.BARNS_TO_CM2
        xenon_production_rate = (config.XENON_YIELD_DIRECT * fission_rate + 
                               config.IODINE_DECAY_CONSTANT * self.iodine_concentration)
        
        self.xenon_concentration = xenon_production_rate / xenon_removal_rate

    def _xenon_derivatives(self, concentrations, power_level):
        """
        Calcule les dérivées temporelles des concentrations I-135 et Xe-135.
        
        Args:
            concentrations: [iodine_concentration, xenon_concentration]
            power_level: niveau de puissance (%)
            
        Returns:
            [d_iodine_dt, d_xenon_dt]: dérivées temporelles
        """
        iodine_conc, xenon_conc = concentrations
        
        # Taux de fission pour ce niveau de puissance
        fission_rate = power_level * config.FISSION_RATE_COEFF * config.THERMAL_FLUX_NOMINAL
        thermal_flux = config.THERMAL_FLUX_NOMINAL * (power_level / config.PERCENT_TO_FRACTION)
        
        # Équation pour l'Iode-135: d[I]/dt = γI * Σf * Φ - λI * [I]
        iodine_production = config.IODINE_YIELD * fission_rate
        iodine_decay = config.IODINE_DECAY_CONSTANT * iodine_conc
        d_iodine_dt = iodine_production - iodine_decay
        
        # Équation pour le Xénon-135: d[Xe]/dt = γXe * Σf * Φ + λI * [I] - λXe * [Xe] - σXe * Φ * [Xe]
        xenon_production_direct = config.XENON_YIELD_DIRECT * fission_rate
        xenon_production_from_iodine = config.IODINE_DECAY_CONSTANT * iodine_conc
        xenon_decay = config.XENON_DECAY_CONSTANT * xenon_conc
        xenon_burnup = config.XENON_ABSORPTION_CROSS_SECTION * thermal_flux * xenon_conc * config.BARNS_TO_CM2
        
        d_xenon_dt = xenon_production_direct + xenon_production_from_iodine - xenon_decay - xenon_burnup
        
        return np.array([d_iodine_dt, d_xenon_dt])

    def update_xenon_dynamics(self, dt=None):
        """
        Met à jour les concentrations d'Iode-135 et de Xénon-135 
        selon les équations différentielles de Bateman en utilisant 
        l'intégration Runge-Kutta 4 pour une meilleure précision.
        
        Args:
            dt: pas de temps en secondes (utilise self.time_step par défaut)
        """
        if dt is None:
            dt = self.time_step
            
        # Concentrations actuelles
        y0 = np.array([self.iodine_concentration, self.xenon_concentration])
        
        # Méthode Runge-Kutta 4
        k1 = self._xenon_derivatives(y0, self.power_level)
        k2 = self._xenon_derivatives(y0 + 0.5 * dt * k1, self.power_level)
        k3 = self._xenon_derivatives(y0 + 0.5 * dt * k2, self.power_level)
        k4 = self._xenon_derivatives(y0 + dt * k3, self.power_level)
        
        # Intégration RK4
        y_new = y0 + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        
        # Mise à jour des concentrations
        self.iodine_concentration, self.xenon_concentration = y_new
        self.simulation_time += dt
        
        # Assurer que les concentrations ne deviennent pas négatives
        self.iodine_concentration = max(0, self.iodine_concentration)
        self.xenon_concentration = max(0, self.xenon_concentration)

    def get_xenon_reactivity_effect(self):
        """
        Calcule l'effet du Xénon-135 sur la réactivité (en pcm).
        """
        # Calcul de l'anti-réactivité due au Xénon-135
        thermal_flux = config.THERMAL_FLUX_NOMINAL * (self.power_level / config.PERCENT_TO_FRACTION)
        xenon_absorption_rate = (config.XENON_ABSORPTION_CROSS_SECTION * 
                               self.xenon_concentration * thermal_flux * config.BARNS_TO_CM2)
        
        # Conversion approximative en pcm (cette formule dépend du réacteur)
        # Ici, nous utilisons une approximation basée sur l'importance neutronique
        xenon_reactivity_pcm = -xenon_absorption_rate * config.XENON_REACTIVITY_CONVERSION_FACTOR
        
        return xenon_reactivity_pcm

    def advance_time(self, hours=1.0):
        """
        Fait avancer la simulation temporelle et met à jour la dynamique Xénon.
        
        Args:
            hours: nombre d'heures à simuler
        """
        dt_seconds = hours * config.HOURS_TO_SECONDS
        self.update_xenon_dynamics(dt_seconds)
        # Recalcul de tous les paramètres après la mise à jour Xénon
        self.calculate_all()

    def _update_parameter(self, param_name, value, update_temperatures=False):
        """Méthode générique pour mettre à jour un paramètre et recalculer le modèle
        
        Args:
            param_name: Nom de l'attribut à mettre à jour
            value: Nouvelle valeur
            update_temperatures: Si True, met à jour les températures avant de recalculer
        """
        setattr(self, param_name, value)
        if update_temperatures:
            self._update_temperatures()
        self.calculate_all()

    def update_rod_group_R_position(self, position):
        """Update R group position and recalculate"""
        self._update_parameter('rod_group_R_position', position)
    
    def update_rod_group_GCP_position(self, position):
        """Update GCP group position and recalculate"""
        self._update_parameter('rod_group_GCP_position', position)
    
    def update_control_rod_position(self, position):
        """Méthode de rétrocompatibilité - convertit % en positions équivalentes R et GCP"""
        # Conversion approximative pour maintenir la rétrocompatibilité
        steps_max = config.parameters_config['conversion']['steps_to_percent']
        equivalent_steps = (config.PERCENT_TO_FRACTION - position) * steps_max / config.PERCENT_TO_FRACTION
        self.rod_group_R_position = equivalent_steps
        self.rod_group_GCP_position = equivalent_steps
        self.calculate_all()
    
    def update_boron_concentration(self, concentration):
        """Update boron concentration and recalculate"""
        self._update_parameter('boron_concentration', concentration)
    
    def update_average_temperature(self, temperature):
        """Update moderator temperature and recalculate"""
        self._update_parameter('average_temperature', temperature, update_temperatures=True)
    
    def update_power_level(self, power_level):
        """Update power level and recalculate"""
        self._update_parameter('power_level', power_level, update_temperatures=True)
    
    def update_fuel_enrichment(self, enrichment):
        """Update fuel enrichment and recalculate"""
        self._update_parameter('fuel_enrichment', enrichment)
    
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
        # Nouvelle convention: 0% = insérées, 100% = retirées
        if self._get_equivalent_rod_position_percent() > 0 and self._get_equivalent_rod_position_percent() < 100:
            rod_withdrawal_fraction = self._get_equivalent_rod_position_percent() / config.PERCENT_TO_FRACTION  # Fraction de retrait
            rod_insertion_depth = 1.0 - rod_withdrawal_fraction  # Profondeur d'insertion réelle
            rod_insertion_point = 1 - rod_insertion_depth  # Position des pointes des barres
            
            # Calculer l'effet des barres avec atténuation progressive aux fortes insertions
            rod_effect = np.ones_like(height)
            
            # Zone affectée par les barres (au-dessus de leur position)
            affected_zone = height > rod_insertion_point
            
            if np.any(affected_zone):
                # Distance normalisée par rapport aux barres
                distance_from_rods = height - rod_insertion_point
                distance_from_rods[~affected_zone] = 0
                
                # Effet d'écrasement avec atténuation progressive et fluide
                # Transition fluide commençant vers 85% d'insertion (donc 15% de retrait)
                if rod_insertion_depth > 0.85:
                    # Fonction de transition en S (sigmoïde) pour une fluidité maximale
                    # Transformation pour avoir une transition de 85% à 100% d'insertion
                    relative_depth = (rod_insertion_depth - 0.85) / 0.15  # Normalise 0.85-1.0 vers 0-1
                    
                    # Fonction sigmoïde inverse pour transition fluide
                    # À 85% d'insertion : attenuation_factor ≈ 1.0 (effet complet)
                    # À 100% d'insertion : attenuation_factor = 0.0 (aucun effet)
                    # Transition en forme de S pour fluidité maximale
                    sigmoid_factor = 1.0 / (1.0 + np.exp(-12 * (relative_depth - 0.5)))
                    attenuation_factor = 1.0 - sigmoid_factor
                    
                    effect_coeff = config.CONTROL_ROD_EFFECT_COEFF * attenuation_factor
                else:
                    effect_coeff = config.CONTROL_ROD_EFFECT_COEFF
                
                # Application de l'effet gaussien atténué
                if effect_coeff > 0:
                    rod_effect[affected_zone] = np.exp(-effect_coeff * distance_from_rods[affected_zone]**2)
            
            flux = flux * rod_effect
        
        # À 0% (100% insertion) ou 100% (0% insertion), le flux reste parfaitement symétrique (cosinus pur)
        
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
            "k_infinite": self.k_infinite,
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
        nu = config.NEUTRONS_PER_THERMAL_FISSION_U235  # Neutrons per thermal fission in U-235
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
    

    
    def get_neutron_cycle_data(self):
        """
        Get data for the neutron cycle visualization.
        This calculates the neutron population at each step of the 6-factor formula.
        """
        # Start with a reference population of fast neutrons
        n_start = 1000.0

        # 1. Fast Fission Factor (epsilon)
        n_after_epsilon = n_start * self.epsilon

        # 2. Fast Non-Leakage Probability (P_AFR)
        n_after_p_afr = n_after_epsilon * self.fast_non_leakage_prob

        # 3. Resonance Escape Probability (p)
        n_after_p = n_after_p_afr * self.p

        # 4. Thermal Non-Leakage Probability (P_AFT)
        n_after_p_aft = n_after_p * self.thermal_non_leakage_prob

        # 5. Thermal Utilization Factor (f)
        n_after_f = n_after_p_aft * self.f

        # 6. Reproduction Factor (eta)
        n_final = n_after_f * self.eta

        return {
            "factors": {
                "eta": self.eta,
                "epsilon": self.epsilon,
                "p": self.p,
                "f": self.f,
                "P_AFR": self.fast_non_leakage_prob,
                "P_AFT": self.thermal_non_leakage_prob,
                "k_eff": self.k_effective,
            },
            "populations": {
                "start": n_start,
                "after_epsilon": n_after_epsilon,
                "after_P_AFR": n_after_p_afr,
                "after_p": n_after_p,
                "after_P_AFT": n_after_p_aft,
                "after_f": n_after_f,
                "final": n_final
            }
        }
    
    def get_xenon_dynamics_data(self):
        """
        Get data for the xenon dynamics visualization.
        Returns concentrations and reactivity effects.
        """
        return {
            "time_hours": self.simulation_time / config.HOURS_TO_SECONDS,
            "iodine_concentration": self.iodine_concentration,
            "xenon_concentration": self.xenon_concentration,
            "xenon_reactivity_pcm": self.get_xenon_reactivity_effect(),
            "power_level": self.power_level
        }
    
    def apply_preset(self, preset_name):
        """Apply a preset configuration using the new advanced system"""
        preset = self.preset_manager.get_preset_by_name(preset_name)
        if not preset:
            return False
        
        # Appliquer les paramètres de base
        self.rod_group_R_position = preset.rod_group_R_position
        self.rod_group_GCP_position = preset.rod_group_GCP_position
        self.boron_concentration = preset.boron_concentration
        self.average_temperature = preset.average_temperature
        self.fuel_enrichment = preset.fuel_enrichment
        self.power_level = preset.power_level
        
        # Appliquer les états temporels si disponibles
        if preset.iodine_concentration is not None:
            self.iodine_concentration = preset.iodine_concentration
        
        if preset.xenon_concentration is not None:
            self.xenon_concentration = preset.xenon_concentration
        else:
            # Si pas de concentration Xénon spécifiée, calculer l'équilibre
            self.calculate_xenon_equilibrium()
        
        if preset.simulation_time is not None:
            self.simulation_time = preset.simulation_time
        
        # Mettre à jour tous les calculs
        self._update_temperatures()
        self.calculate_all()
        return True
    
    def get_preset_names(self):
        """Return a list of available preset names"""
        return self.preset_manager.get_preset_names()
    
    def get_current_preset_name(self):
        """
        Get the name of the current preset if the current parameters match one.
        If no preset matches, return 'Personnalisé'.
        """
        tolerances = config.gui_settings.get("preset_matching_tolerances", {})
        
        for preset in self.preset_manager.get_all_presets().values():
            # Comparer les paramètres de base
            if (np.isclose(self.rod_group_R_position, preset.rod_group_R_position, atol=tolerances.get("rod_position", 1)) and
                np.isclose(self.rod_group_GCP_position, preset.rod_group_GCP_position, atol=tolerances.get("rod_position", 1)) and
                np.isclose(self.boron_concentration, preset.boron_concentration, atol=tolerances.get("boron_concentration", 1.0)) and
                np.isclose(self.average_temperature, preset.average_temperature, atol=tolerances.get("average_temperature", 0.5)) and
                np.isclose(self.fuel_enrichment, preset.fuel_enrichment, atol=tolerances.get("fuel_enrichment", 0.01)) and
                np.isclose(self.power_level, preset.power_level, atol=tolerances.get("power_level", 0.1))):
                
                # Pour les presets temporels, vérifier aussi les concentrations Xénon
                if preset.category == PresetCategory.TEMPOREL:
                    if (preset.xenon_concentration is not None and
                        not np.isclose(self.xenon_concentration, preset.xenon_concentration, atol=tolerances.get("xenon_concentration", 1e12))):
                        continue
                    if (preset.iodine_concentration is not None and
                        not np.isclose(self.iodine_concentration, preset.iodine_concentration, atol=tolerances.get("xenon_concentration", 1e12))):
                        continue
                
                return preset.name
        
        return "Personnalisé"
    
    def save_preset(self, name, description="", overwrite=False):
        """Save current configuration as a preset using the advanced system"""
        try:
            # Préparer les paramètres actuels
            current_params = {
                "rod_group_R_position": self.rod_group_R_position,
            "rod_group_GCP_position": self.rod_group_GCP_position,
                "boron_concentration": self.boron_concentration,
                "average_temperature": self.average_temperature,
                "fuel_enrichment": self.fuel_enrichment,
                "power_level": self.power_level,
                "iodine_concentration": self.iodine_concentration,
                "xenon_concentration": self.xenon_concentration,
                "simulation_time": self.simulation_time
            }
            
            # Déterminer la catégorie basée sur l'état temporel
            category = PresetCategory.PERSONNALISE
            if self.simulation_time > 0 or self.xenon_concentration > 0:
                category = PresetCategory.TEMPOREL
            
            # Vérifier si un preset avec ce nom existe déjà
            existing_preset = self.preset_manager.get_preset_by_name(name)
            if existing_preset and not overwrite:
                return False
            
            if existing_preset and overwrite:
                # Mettre à jour le preset existant
                return self.preset_manager.update_preset(
                    existing_preset.id,
                    description=description or existing_preset.description,
                    **current_params
                )
            else:
                # Créer un nouveau preset
                preset = self.preset_manager.create_preset(
                    name=name,
                    description=description or f"Preset personnalisé: {name}",
                    parameters=current_params,
                    category=category
                )
                return preset is not None
                
        except ValueError as e:
            print(f"Erreur lors de la sauvegarde du preset: {e}")
            return False
    
    def get_preset_manager(self):
        """Retourne le gestionnaire de presets pour l'interface avancée"""
        return self.preset_manager
    
    def get_presets_by_category(self, category: PresetCategory):
        """Retourne les presets d'une catégorie donnée"""
        return self.preset_manager.get_presets_by_category(category)
    
    def delete_preset(self, preset_name):
        """Supprime un preset utilisateur par son nom"""
        preset = self.preset_manager.get_preset_by_name(preset_name)
        if preset and preset.preset_type == PresetType.UTILISATEUR:
            return self.preset_manager.delete_preset(preset.id)
        return False
    
    def get_current_state_as_preset_data(self):
        """Retourne l'état actuel sous forme de PresetData temporaire"""
        from datetime import datetime
        
        return PresetData(
            id="temp_current_state",
            name="État Actuel",
            description="État actuel du réacteur",
            category=PresetCategory.TEMPOREL if self.simulation_time > 0 else PresetCategory.BASE,
            preset_type=PresetType.UTILISATEUR,
            created_date=datetime.now(),
            modified_date=datetime.now(),
            rod_group_R_position=self.rod_group_R_position,
            rod_group_GCP_position=self.rod_group_GCP_position,
            boron_concentration=self.boron_concentration,
            average_temperature=self.average_temperature,
            fuel_enrichment=self.fuel_enrichment,
            power_level=self.power_level,
            iodine_concentration=self.iodine_concentration,
            xenon_concentration=self.xenon_concentration,
            simulation_time=self.simulation_time
        )

    def _get_total_rod_worth_fraction(self):
        """
        Calcule la valeur totale d'anti-réactivité des barres basée sur leurs positions
        et leurs worth relatives.
        
        Returns:
            float: Fraction totale d'anti-réactivité (0.0 à 1.0)
        """
        # Conversion des positions en fractions d'insertion (0 = extrait, 1 = inséré)
        steps_max = config.parameters_config['conversion']['steps_to_percent']
        
        r_insertion_fraction = (steps_max - self.rod_group_R_position) / steps_max
        gcp_insertion_fraction = (steps_max - self.rod_group_GCP_position) / steps_max
        
        # Calcul des contributions pondérées
        r_worth = config.parameters_config['rod_group_R']['worth_fraction']
        gcp_worth = config.parameters_config['rod_group_GCP']['worth_fraction']
        
        total_worth_fraction = (r_insertion_fraction * r_worth + 
                               gcp_insertion_fraction * gcp_worth)
        
        return total_worth_fraction

    def _get_equivalent_rod_position_percent(self):
        """
        Calcule une position équivalente en pourcentage pour rétrocompatibilité
        avec les visualisations existantes.
        
        Returns:
            float: Position équivalente en % (0-100, où 0% = inséré, 100% = extrait)
        """
        total_insertion_fraction = self._get_total_rod_worth_fraction()
        return (1.0 - total_insertion_fraction) * 100.0