"""
Modèle de physique des réacteurs pour les calculs de neutronique
"""
import numpy as np
from . import config

class ReactorModel:
    """
    Modèle de réacteur de base implémentant les calculs de neutronique pour un REP
    """
    
    def __init__(self):
        # Paramètres par défaut
        self.control_rod_position = 0.0  # 0-100%
        self.boron_concentration = 500.0  # ppm
        self.moderator_temperature = 310.0  # °C
        self.power_level = 100.0 # %
        self.fuel_enrichment = 3.5  # %
        
        # Ceci est maintenant une valeur calculée, pas une entrée directe
        self.fuel_temperature = 0.0  # °C, sera calculée
        
        # Constantes physiques
        self.delayed_neutron_fraction = config.DELAYED_NEUTRON_FRACTION  # β
        
        # Variables de dynamique Xénon-135 (concentrations en atomes/cm³)
        self.iodine_concentration = 0.0  # I-135 concentration
        self.xenon_concentration = 0.0   # Xe-135 concentration
        self.simulation_time = 0.0       # temps de simulation en secondes
        self.time_step = 3600.0          # pas de temps par défaut : 1 heure
        
        # Paramètres calculés
        self.k_effective = 1.0
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
        
        # Dictionnaire des préréglages
        self.presets = config.PRESETS
        
        # Calcul initial et initialisation des concentrations Xénon à l'équilibre
        self._update_temperatures()
        self.calculate_xenon_equilibrium()  # Initialiser à l'équilibre pour le niveau de puissance actuel
        self.calculate_all()
    
    def _update_temperatures(self):
        """Calcule la température du combustible en fonction du niveau de puissance et de la température du modérateur."""
        self.fuel_temperature = self.moderator_temperature + (self.power_level * config.POWER_TO_FUEL_TEMP_COEFF)

    def calculate_all(self):
        """Calcule tous les paramètres du réacteur en fonction des entrées actuelles"""
        self.calculate_four_factors()
        self.calculate_k_effective()
        self.calculate_reactivity()
        self.calculate_doubling_time()
    
    def calculate_four_factors(self):
        """Calcule les quatre facteurs du cycle neutronique"""
        # Calcul simplifié à des fins pédagogiques
        
        # Eta (nombre moyen de neutrons par fission)
        # Dépend principalement de l'enrichissement du combustible
        self.eta = config.ETA_BASE + config.ETA_ENRICHMENT_COEFF * (self.fuel_enrichment - config.ETA_ENRICHMENT_REF) / config.ETA_ENRICHMENT_SCALE
        
        # Epsilon (facteur de fission rapide)
        # Typiquement constant pour une conception de réacteur donnée
        self.epsilon = config.EPSILON
        
        # Probabilité d'échapper aux résonances
        # Affectée par la température du combustible (élargissement Doppler) et la température du modérateur
        
        # 1. Effet Doppler (température du combustible)
        fuel_temp_K = self.fuel_temperature + config.CELSIUS_TO_KELVIN
        sqrt_T_diff = np.sqrt(fuel_temp_K) - np.sqrt(config.P_REF_TEMP_K)
        doppler_effect = np.exp(-config.P_DOPPLER_COEFF * sqrt_T_diff)
        
        # 2. Effet température du modérateur (densité et efficacité de ralentissement)
        mod_temp_deviation = self.moderator_temperature - config.P_REF_MOD_TEMP_C
        moderator_effect = 1.0 - config.P_MOD_TEMP_COEFF * mod_temp_deviation
        
        # 3. Combinaison des deux effets
        self.p = config.P_BASE * doppler_effect * moderator_effect
        
        # Facteur d'utilisation thermique (f)
        # Nouveau modèle basé sur les rapports d'absorption : f = 1 / (1 + A_non_fuel)
        # A_non_fuel est le rapport d'absorption dans les matériaux non-combustibles par rapport au combustible
        
        # 1. Rapport d'absorption de base, ajusté pour la température du modérateur
        temp_deviation = self.moderator_temperature - config.F_REF_MOD_TEMP_C
        mod_temp_effect = config.F_MOD_TEMP_ABS_COEFF * temp_deviation
        base_abs_ratio = config.F_BASE_ABS_RATIO * (1 + mod_temp_effect)
        
        # 2. Rapport d'absorption des barres de contrôle
        rod_abs_ratio = config.F_CONTROL_ROD_WORTH * (self.control_rod_position / 100.0)
        
        # 3. Rapport d'absorption du bore
        boron_abs_ratio = config.F_BORON_WORTH_PER_PPM * self.boron_concentration
        
        # 4. Rapport d'absorption du Xénon-135
        thermal_flux = config.THERMAL_FLUX_NOMINAL * (self.power_level / 100.0)
        xenon_abs_ratio = (config.XENON_ABSORPTION_CROSS_SECTION * 
                          self.xenon_concentration * thermal_flux * 1e-24) / (thermal_flux + 1e-10)
        
        # Rapport d'absorption total non-combustible
        total_non_fuel_abs_ratio = base_abs_ratio + rod_abs_ratio + boron_abs_ratio + xenon_abs_ratio
        
        self.f = 1.0 / (1.0 + total_non_fuel_abs_ratio)
    
    def calculate_k_effective(self):
        """
        Calculate k-effective using the analytical model.
        """
        self._calculate_k_effective_analytical()

    def _calculate_k_effective_analytical(self):
        """Calcul k-effectif avec le modèle analytique."""
        # --- Calcul analytique ---
        k_infinite = self.eta * self.epsilon * self.p * self.f
        
        # Nouveau calcul de fuite basé sur la théorie de diffusion à deux groupes
        # 1. Laplacien géométrique B^2
        R = config.CORE_DIAMETER_M / 2.0
        H = config.CORE_HEIGHT_M
        geometric_buckling = (np.pi / H)**2 + (config.BESSEL_J0_FIRST_ZERO / R)**2
        
        # 2. Effet de la température sur la densité du modérateur et les aires de diffusion
        # L^2 et L_s^2 sont proportionnels à (rho_ref/rho_T)^2
        temp_deviation = self.moderator_temperature - config.F_REF_MOD_TEMP_C
        density_ratio = 1.0 / (1.0 - config.MODERATOR_DENSITY_COEFF * temp_deviation)
        
        thermal_diffusion_area = config.THERMAL_DIFFUSION_AREA_M2 * (density_ratio**2)
        fast_diffusion_area = config.FAST_DIFFUSION_AREA_M2 * (density_ratio**2)
        
        # 3. Probabilités de non-fuite
        self.fast_non_leakage_prob = 1.0 / (1.0 + geometric_buckling * fast_diffusion_area)
        self.thermal_non_leakage_prob = 1.0 / (1.0 + geometric_buckling * thermal_diffusion_area)
        
        self.k_effective = k_infinite * self.fast_non_leakage_prob * self.thermal_non_leakage_prob

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
        thermal_flux = config.THERMAL_FLUX_NOMINAL * (self.power_level / 100.0)
        xenon_removal_rate = config.XENON_DECAY_CONSTANT + config.XENON_ABSORPTION_CROSS_SECTION * thermal_flux * 1e-24
        xenon_production_rate = (config.XENON_YIELD_DIRECT * fission_rate + 
                               config.IODINE_DECAY_CONSTANT * self.iodine_concentration)
        
        self.xenon_concentration = xenon_production_rate / xenon_removal_rate

    def update_xenon_dynamics(self, dt=None):
        """
        Met à jour les concentrations d'Iode-135 et de Xénon-135 
        selon les équations différentielles de Bateman.
        
        Args:
            dt: pas de temps en secondes (utilise self.time_step par défaut)
        """
        if dt is None:
            dt = self.time_step
            
        # Taux de fission actuel
        fission_rate = self.power_level * config.FISSION_RATE_COEFF * config.THERMAL_FLUX_NOMINAL
        thermal_flux = config.THERMAL_FLUX_NOMINAL * (self.power_level / 100.0)
        
        # Équation pour l'Iode-135: d[I]/dt = γI * Σf * Φ - λI * [I]
        iodine_production = config.IODINE_YIELD * fission_rate
        iodine_decay = config.IODINE_DECAY_CONSTANT * self.iodine_concentration
        d_iodine_dt = iodine_production - iodine_decay
        
        # Équation pour le Xénon-135: d[Xe]/dt = γXe * Σf * Φ + λI * [I] - λXe * [Xe] - σXe * Φ * [Xe]
        xenon_production_direct = config.XENON_YIELD_DIRECT * fission_rate
        xenon_production_from_iodine = config.IODINE_DECAY_CONSTANT * self.iodine_concentration
        xenon_decay = config.XENON_DECAY_CONSTANT * self.xenon_concentration
        xenon_burnup = config.XENON_ABSORPTION_CROSS_SECTION * thermal_flux * self.xenon_concentration * 1e-24
        
        d_xenon_dt = xenon_production_direct + xenon_production_from_iodine - xenon_decay - xenon_burnup
        
        # Intégration d'Euler (première approximation)
        self.iodine_concentration += d_iodine_dt * dt
        self.xenon_concentration += d_xenon_dt * dt
        self.simulation_time += dt
        
        # Assurer que les concentrations ne deviennent pas négatives
        self.iodine_concentration = max(0, self.iodine_concentration)
        self.xenon_concentration = max(0, self.xenon_concentration)

    def get_xenon_reactivity_effect(self):
        """
        Calcule l'effet du Xénon-135 sur la réactivité (en pcm).
        """
        # Calcul de l'anti-réactivité due au Xénon-135
        thermal_flux = config.THERMAL_FLUX_NOMINAL * (self.power_level / 100.0)
        xenon_absorption_rate = (config.XENON_ABSORPTION_CROSS_SECTION * 
                               self.xenon_concentration * thermal_flux * 1e-24)
        
        # Conversion approximative en pcm (cette formule dépend du réacteur)
        # Ici, nous utilisons une approximation basée sur l'importance neutronique
        xenon_reactivity_pcm = -xenon_absorption_rate * 1e5  # facteur de conversion approximatif
        
        return xenon_reactivity_pcm

    def advance_time(self, hours=1.0):
        """
        Fait avancer la simulation temporelle et met à jour la dynamique Xénon.
        
        Args:
            hours: nombre d'heures à simuler
        """
        dt_seconds = hours * 3600.0
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

    def update_control_rod_position(self, position):
        """Update control rod position and recalculate"""
        self._update_parameter('control_rod_position', position)
    
    def update_boron_concentration(self, concentration):
        """Update boron concentration and recalculate"""
        self._update_parameter('boron_concentration', concentration)
    
    def update_moderator_temperature(self, temperature):
        """Update moderator temperature and recalculate"""
        self._update_parameter('moderator_temperature', temperature, update_temperatures=True)
    
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
        if self.control_rod_position > 0:
            rod_depth = self.control_rod_position / 100
            rod_effect = np.exp(-config.CONTROL_ROD_EFFECT_COEFF * (height - (1 - rod_depth))**2)
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
        
        power_percentage = self.power_level

        return {"axial_offset": axial_offset, "power_percentage": power_percentage}
    
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
            "time_hours": self.simulation_time / 3600.0,
            "iodine_concentration": self.iodine_concentration,
            "xenon_concentration": self.xenon_concentration,
            "xenon_reactivity_pcm": self.get_xenon_reactivity_effect(),
            "power_level": self.power_level
        }
    
    def apply_preset(self, preset_name):
        """Apply a preset configuration"""
        if preset_name in self.presets:
            preset = self.presets[preset_name]
            self.control_rod_position = preset["control_rod_position"]
            self.boron_concentration = preset["boron_concentration"]
            self.moderator_temperature = preset["moderator_temperature"]
            self.fuel_enrichment = preset["fuel_enrichment"]
            if "power_level" in preset:
                self.power_level = preset["power_level"]
            self._update_temperatures()
            self.calculate_all()
            return True
        return False
    
    def get_preset_names(self):
        """Return a list of available preset names"""
        return list(self.presets.keys())
    
    def get_current_preset_name(self):
        """
        Get the name of the current preset if the current parameters match one.
        If no preset matches, return 'Personnalisé'.
        """
        current_config = {
            "control_rod_position": self.control_rod_position,
            "boron_concentration": self.boron_concentration,
            "moderator_temperature": self.moderator_temperature,
            "fuel_enrichment": self.fuel_enrichment,
            "power_level": self.power_level
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
                "fuel_enrichment": self.fuel_enrichment,
                "power_level": self.power_level
            }
            return True
        return False