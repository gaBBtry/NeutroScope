"""
Implémentation de la fenêtre principale pour l'application Neutro_EDF
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QSlider, QComboBox, QGroupBox, QDoubleSpinBox,
    QPushButton
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeySequence, QShortcut

from src.controller.reactor_controller import ReactorController
from src.gui.visualization import VisualizationPanel
from src.gui.widgets.info_panel import InfoPanel

from src.gui.widgets.credits_button import CreditsButton
from .widgets.info_manager import InfoManager
from src.gui.widgets.enhanced_widgets import InfoGroupBox
from src.gui.widgets.info_dialog import InfoDialog
from src.gui.widgets.realtime_simulation import RealtimeSimulationEngine


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application avec panneau de contrôle et zone de visualisation"""
    
    def __init__(self):
        super().__init__()
        
        self.controller = ReactorController()
        self.realtime_engine = RealtimeSimulationEngine(self.controller)
        
        self.setWindowTitle("NeutroScope - Simulateur Dynamique de REP")
        self.setMinimumSize(1200, 800)
        
        self._setup_info_texts()
        
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        content_layout = QHBoxLayout()
        
        # --- Info & Panneau de Contrôle (Gauche) ---
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.info_manager = InfoManager()
        self.info_dialog = None
        self.info_panel = InfoPanel()
        self.credits_button = CreditsButton()
        
        self.control_panel = self._create_control_panel()
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.credits_button)
        
        left_layout.addWidget(self.control_panel)
        left_layout.addLayout(buttons_layout)
        left_layout.addWidget(self.info_panel)
        
        # --- Visualisations (Droite) ---
        self.visualization_panel = VisualizationPanel(info_manager=self.info_manager)
        
        # --- Contrôles Temps Réel (Haut) ---
        self.realtime_control_widget = self.realtime_engine.create_control_widget(self.info_manager)
        
        main_layout.addWidget(self.realtime_control_widget)
        
        content_layout.addWidget(left_container, 1)
        content_layout.addWidget(self.visualization_panel, 3)
        main_layout.addLayout(content_layout)
        
        self.setCentralWidget(central_widget)
        
        self._connect_signals()
        
        self.info_shortcut = QShortcut(QKeySequence("i"), self)
        self.info_shortcut.activated.connect(self._show_info_dialog)
        
        # Initialisation de l'UI
        self.on_preset_changed("Démarrage")
    
    def _setup_info_texts(self):
        self.info_texts = {
            "rod_control_R": (
                "Groupe de Régulation (R)\n\n"
                "Le groupe R est utilisé pour le contrôle fin de la réactivité. "
                "Sa position cible est définie par le slider/spinbox, et il se déplace à une vitesse finie.\n\n"
                "Position: 0 pas (extraites) à 228 pas (insérées)"
            ),
            "rod_control_GCP": (
                "Groupe de Compensation de Puissance (GCP)\n\n"
                "Le groupe GCP est utilisé pour la compensation des variations lentes de réactivité. "
                "Sa position cible est définie par le slider/spinbox.\n\n"
                "Position: 0 pas (extraites) à 228 pas (insérées)"
            ),
            "boron": (
                "Concentration en bore\n\n"
                "Le bore est un poison neutronique soluble. Sa concentration cible est définie "
                "par le slider/spinbox et évolue avec une certaine inertie.\n\n"
                "Plage typique: 0 à 2000 ppm"
            ),
            "fuel_temp": (
                "Température du combustible\n\n"
                "La température du combustible (UO2) affecte l'effet Doppler. "
                "C'est une SORTIE de la simulation, résultant de l'équilibre entre la puissance générée et le refroidissement."
            ),
            "moderator_temp": (
                "Température du modérateur\n\n"
                "La température de l'eau (modérateur) affecte la densité et l'absorption. "
                "C'est une SORTIE de la simulation, couplée à la température du combustible et au refroidissement."
            ),
             "power_level": (
                "Puissance et Flux Neutroniques\n\n"
                "- Puissance thermique: La puissance générée par les fissions, en pourcentage de la puissance nominale.\n"
                "- Flux neutronique: La densité de neutrons multipliée par leur vitesse.\n\n"
                "Ces valeurs sont des SORTIES dynamiques de la simulation, résultant de la réactivité."
            ),
            "fuel_enrichment": (
                "Enrichissement du combustible\n\n"
                "Le pourcentage d'uranium-235. Ce paramètre est fixe pendant une simulation "
                "et ne peut être changé qu'à l'arrêt."
            ),
            "reactor_params": (
                "Paramètres neutroniques du réacteur\n\n"
                "- Taux de neutrons retardés (β): Fraction des neutrons émis avec un délai.\n"
                "- Temps de doublement: Temps nécessaire pour doubler la puissance (si > 0).\n"
                "- Réactivité (ρ): Écart relatif par rapport à la criticité.\n"
                "- k-effectif: Facteur de multiplication effectif (k=1: critique)."
            ),
            "presets": (
                "Préréglages du réacteur\n\n"
                "Charge un état initial complet du réacteur (positions des barres, bore, etc.). "
                "Les presets ne peuvent être chargés que lorsque la simulation est arrêtée."
            )
        }

    def _create_control_panel(self):
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        # Presets, Rods, Boron, Enrichment
        self.presets_group = self._create_preset_controls()
        self.rod_R_group = self._create_rod_controls("R")
        self.rod_GCP_group = self._create_rod_controls("GCP")
        self.boron_group = self._create_boron_controls()
        self.fuel_enrichment_group = self._create_enrichment_controls()
        
        # Dynamic State & Reactor Params
        self.dynamic_state_group = self._create_dynamic_state_display()
        self.reactor_params_group = self._create_reactor_params_display()
        
        control_layout.addWidget(self.presets_group)
        control_layout.addWidget(self.rod_R_group)
        control_layout.addWidget(self.rod_GCP_group)
        control_layout.addWidget(self.boron_group)
        control_layout.addWidget(self.fuel_enrichment_group)
        control_layout.addWidget(self.dynamic_state_group)
        control_layout.addWidget(self.reactor_params_group)
        control_layout.addStretch(1)
        
        return control_panel

    def _create_preset_controls(self):
        group = self.create_info_groupbox("Préréglages", self.info_texts["presets"])
        layout = QHBoxLayout(group)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(self.controller.get_preset_names())
        self.reset_preset_button = QPushButton("Reset")
        self.reset_preset_button.setMaximumWidth(60)
        layout.addWidget(self.preset_combo)
        layout.addWidget(self.reset_preset_button)
        return group

    def _create_rod_controls(self, group_type):
        info_key = "rod_control_R" if group_type == "R" else "rod_control_GCP"
        title = "Groupe R (Régulation)" if group_type == "R" else "Groupe GCP (Compensation)"
        group = self.create_info_groupbox(title, self.info_texts[info_key])
        layout = QHBoxLayout(group)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 228)
        
        spinbox = QDoubleSpinBox()
        spinbox.setRange(0, 228)
        spinbox.setSuffix(" pas")
        
        target_label = QLabel("(Cible: 0)")
        
        step = 1 if group_type == "R" else 5
        plus_btn = QPushButton(f"+{step}")
        minus_btn = QPushButton(f"-{step}")
        
        layout.addWidget(slider)
        layout.addWidget(plus_btn)
        layout.addWidget(minus_btn)
        layout.addWidget(spinbox)
        layout.addWidget(target_label)
        
        if group_type == "R":
            self.rod_R_slider, self.rod_R_spinbox, self.rod_R_target_label, self.rod_R_plus_btn, self.rod_R_minus_btn = slider, spinbox, target_label, plus_btn, minus_btn
        else:
            self.rod_GCP_slider, self.rod_GCP_spinbox, self.rod_GCP_target_label, self.rod_GCP_plus_btn, self.rod_GCP_minus_btn = slider, spinbox, target_label, plus_btn, minus_btn
            
        return group

    def _create_boron_controls(self):
        group = self.create_info_groupbox("Concentration en Bore (ppm)", self.info_texts["boron"])
        layout = QHBoxLayout(group)
        self.boron_slider = QSlider(Qt.Orientation.Horizontal)
        self.boron_slider.setRange(0, 2000)
        self.boron_spinbox = QDoubleSpinBox()
        self.boron_spinbox.setRange(0, 2000)
        self.boron_spinbox.setSuffix(" ppm")
        self.boron_target_label = QLabel("(Cible: 0)")
        self.boron_plus_btn = QPushButton("+10")
        self.boron_minus_btn = QPushButton("-10")
        layout.addWidget(self.boron_slider)
        layout.addWidget(self.boron_minus_btn)
        layout.addWidget(self.boron_plus_btn)
        layout.addWidget(self.boron_spinbox)
        layout.addWidget(self.boron_target_label)
        return group
    
    def _create_enrichment_controls(self):
        group = self.create_info_groupbox("Enrichissement Combustible (%)", self.info_texts["fuel_enrichment"])
        layout = QHBoxLayout(group)
        self.fuel_enrichment_slider = QSlider(Qt.Orientation.Horizontal)
        self.fuel_enrichment_slider.setRange(10, 50)
        self.fuel_enrichment_spinbox = QDoubleSpinBox()
        self.fuel_enrichment_spinbox.setRange(1.0, 5.0)
        self.fuel_enrichment_spinbox.setSingleStep(0.1)
        self.fuel_enrichment_spinbox.setSuffix(" %")
        self.fuel_enrichment_plus_btn = QPushButton("+0.1")
        self.fuel_enrichment_minus_btn = QPushButton("-0.1")
        layout.addWidget(self.fuel_enrichment_slider)
        layout.addWidget(self.fuel_enrichment_minus_btn)
        layout.addWidget(self.fuel_enrichment_plus_btn)
        layout.addWidget(self.fuel_enrichment_spinbox)
        return group

    def _create_dynamic_state_display(self):
        group = self.create_info_groupbox("État Dynamique du Coeur", "")
        layout = QVBoxLayout(group)
        self.power_label = QLabel("Puissance: ... %")
        self.fuel_temp_label = QLabel("T° Combustible: ... °C")
        self.moderator_temp_label = QLabel("T° Modérateur: ... °C")
        layout.addWidget(self.power_label)
        layout.addWidget(self.fuel_temp_label)
        layout.addWidget(self.moderator_temp_label)
        return group

    def _create_reactor_params_display(self):
        group = self.create_info_groupbox("Paramètres du Réacteur", self.info_texts["reactor_params"])
        layout = QVBoxLayout(group)
        self.k_effective_label = QLabel("k-eff: ...")
        self.reactivity_label = QLabel("Réactivité (pcm): ...")
        self.doubling_time_label = QLabel("Temps de doublement: ...")
        beta = self.controller.get_reactor_parameters()['delayed_neutron_fraction']
        self.delayed_neutron_label = QLabel(f"β: {beta * 100:.3f}%")
        layout.addWidget(self.k_effective_label)
        layout.addWidget(self.reactivity_label)
        layout.addWidget(self.doubling_time_label)
        layout.addWidget(self.delayed_neutron_label)
        return group

    def _connect_signals(self):
        # Realtime Engine
        self.realtime_engine.time_advanced.connect(self.on_realtime_time_advance)
        self.realtime_engine.simulation_state_changed.connect(self.on_realtime_state_changed)
        
        # Presets
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        self.reset_preset_button.clicked.connect(self.reset_to_selected_preset)
        
        # Rods R
        self.rod_R_slider.valueChanged.connect(self.on_rod_R_slider_changed)
        self.rod_R_spinbox.valueChanged.connect(self.on_rod_R_spinbox_changed)
        self.rod_R_plus_btn.clicked.connect(lambda: self.adjust_rod_R(1))
        self.rod_R_minus_btn.clicked.connect(lambda: self.adjust_rod_R(-1))
        
        # Rods GCP
        self.rod_GCP_slider.valueChanged.connect(self.on_rod_GCP_slider_changed)
        self.rod_GCP_spinbox.valueChanged.connect(self.on_rod_GCP_spinbox_changed)
        self.rod_GCP_plus_btn.clicked.connect(lambda: self.adjust_rod_GCP(5))
        self.rod_GCP_minus_btn.clicked.connect(lambda: self.adjust_rod_GCP(-5))
        
        # Boron
        self.boron_slider.valueChanged.connect(self.on_boron_slider_changed)
        self.boron_spinbox.valueChanged.connect(self.on_boron_spinbox_changed)
        self.boron_plus_btn.clicked.connect(lambda: self.adjust_boron(10))
        self.boron_minus_btn.clicked.connect(lambda: self.adjust_boron(-10))
        
        # Enrichment
        self.fuel_enrichment_slider.valueChanged.connect(self.on_fuel_enrichment_slider_changed)
        self.fuel_enrichment_spinbox.valueChanged.connect(self.on_fuel_enrichment_spinbox_changed)
        self.fuel_enrichment_plus_btn.clicked.connect(lambda: self.adjust_fuel_enrichment(0.1))
        self.fuel_enrichment_minus_btn.clicked.connect(lambda: self.adjust_fuel_enrichment(-0.1))

        # Info Panel
        self.info_manager.info_requested.connect(self.info_panel.update_info)
        self.info_manager.info_cleared.connect(self.info_panel.clear_info)
        
        # Xenon Widget
        self.visualization_panel.xenon_widget.xenon_reset_requested.connect(self.on_xenon_reset)

    def create_info_groupbox(self, title, info_text):
        return InfoGroupBox(title, info_text, self.info_manager)

    # --- UI Update Logic ---
    
    def update_ui_from_model(self):
        """Met à jour l'ensemble de l'interface utilisateur à partir de l'état actuel du modèle."""
        config = self.controller.get_current_configuration()
        params = self.controller.get_reactor_parameters()
        
        # Block signals to prevent feedback loops
        widgets = [self.rod_R_slider, self.rod_R_spinbox, self.rod_GCP_slider, 
                   self.rod_GCP_spinbox, self.boron_slider, self.boron_spinbox, 
                   self.fuel_enrichment_slider, self.fuel_enrichment_spinbox]
        for w in widgets: w.blockSignals(True)

        # Update controls values
        self.rod_R_slider.setValue(228 - int(config["rod_group_R_position"]))
        self.rod_R_spinbox.setValue(config["rod_group_R_position"])
        self.rod_R_target_label.setText(f'(Cible: {config["target_rod_group_R_position"]:.0f})')
        
        self.rod_GCP_slider.setValue(228 - int(config["rod_group_GCP_position"]))
        self.rod_GCP_spinbox.setValue(config["rod_group_GCP_position"])
        self.rod_GCP_target_label.setText(f'(Cible: {config["target_rod_group_GCP_position"]:.0f})')
        
        self.boron_slider.setValue(int(config["boron_concentration"]))
        self.boron_spinbox.setValue(config["boron_concentration"])
        self.boron_target_label.setText(f'(Cible: {config["target_boron_concentration"]:.0f})')
        
        self.fuel_enrichment_slider.setValue(int(config["fuel_enrichment"] * 10))
        self.fuel_enrichment_spinbox.setValue(config["fuel_enrichment"])

        # Update dynamic state display
        self.power_label.setText(f"Puissance: {params['power_level']:.1f} %")
        self.fuel_temp_label.setText(f"T° Combustible: {params['fuel_temperature']:.1f} °C")
        self.moderator_temp_label.setText(f"T° Modérateur: {params['moderator_temperature']:.1f} °C")
        
        # Update reactor params display
        k_eff = params["k_effective"]
        reactivity_pcm = params["reactivity"] * 100000
        doubling_time = params["doubling_time"]
        self.k_effective_label.setText(f"k-eff: {k_eff:.4f}")
        self.reactivity_label.setText(f"Réactivité (pcm): {reactivity_pcm:.1f}")
        self.doubling_time_label.setText("Temps de doublement: ∞" if doubling_time == float('inf') else f"Temps de doublement: {doubling_time:.1f} s")

        for w in widgets: w.blockSignals(False)
        
        self.update_visualizations()
        self.check_for_custom_preset()

    def update_visualizations(self):
        height, flux = self.controller.get_axial_flux_distribution()
        equivalent_position = self.controller.model._get_equivalent_rod_position_percent()
        self.visualization_panel.update_flux_plot(height, flux, equivalent_position)
        self.visualization_panel.update_factors_plot(self.controller.get_four_factors_data())
        self.visualization_panel.update_neutron_balance_plot(self.controller.get_neutron_balance_data())
        self.visualization_panel.update_neutron_cycle_plot(self.controller.get_neutron_cycle_data())
        self.visualization_panel.update_xenon_plot(self.controller.get_xenon_dynamics_data())
    
    def check_for_custom_preset(self):
        current_preset_name = self.controller.get_current_preset_name()
        if self.preset_combo.currentText() != current_preset_name:
            self.preset_combo.setCurrentText(current_preset_name)
        self.update_reset_button_state()

    def update_reset_button_state(self):
        selected = self.preset_combo.currentText()
        is_custom = self.controller.get_current_preset_name() != selected
        self.reset_preset_button.setEnabled(selected and selected != "Personnalisé" and is_custom)

    # --- Slots ---

    def on_realtime_state_changed(self, state: str):
        is_playing = state != "stopped"
        self.presets_group.setEnabled(not is_playing)
        self.fuel_enrichment_group.setEnabled(not is_playing)
    
    def on_realtime_time_advance(self, hours_advanced: float):
        self.update_ui_from_model()
    
    def on_preset_changed(self, preset_name: str):
        if preset_name and preset_name != "Personnalisé":
            self.controller.apply_preset(preset_name)
            self.update_ui_from_model()
    
    def reset_to_selected_preset(self):
        preset_name = self.preset_combo.currentText()
        if preset_name and preset_name != "Personnalisé":
            self.controller.apply_preset(preset_name)
            self.update_ui_from_model()
            
    def on_xenon_reset(self):
        self.controller.reset_xenon_to_equilibrium()
        self.update_ui_from_model()
        self.visualization_panel.xenon_widget.clear_history()

    # Control Slots
    def on_rod_R_slider_changed(self, value):
        inverted_value = 228 - value
        self.rod_R_spinbox.blockSignals(True)
        self.rod_R_spinbox.setValue(inverted_value)
        self.rod_R_spinbox.blockSignals(False)
        self.controller.set_target_rod_group_R_position(inverted_value)
        self.rod_R_target_label.setText(f"(Cible: {inverted_value:.0f})")
    
    def on_rod_R_spinbox_changed(self, value):
        inverted_slider_value = 228 - int(value)
        self.rod_R_slider.blockSignals(True)
        self.rod_R_slider.setValue(inverted_slider_value)
        self.rod_R_slider.blockSignals(False)
        self.controller.set_target_rod_group_R_position(value)
        self.rod_R_target_label.setText(f"(Cible: {value:.0f})")
    
    def adjust_rod_R(self, step):
        new_value = self.rod_R_spinbox.value() + step
        self.rod_R_spinbox.setValue(max(0, min(228, new_value)))
    
    def on_rod_GCP_slider_changed(self, value):
        inverted_value = 228 - value
        self.rod_GCP_spinbox.blockSignals(True)
        self.rod_GCP_spinbox.setValue(inverted_value)
        self.rod_GCP_spinbox.blockSignals(False)
        self.controller.set_target_rod_group_GCP_position(inverted_value)
        self.rod_GCP_target_label.setText(f"(Cible: {inverted_value:.0f})")
    
    def on_rod_GCP_spinbox_changed(self, value):
        inverted_slider_value = 228 - int(value)
        self.rod_GCP_slider.blockSignals(True)
        self.rod_GCP_slider.setValue(inverted_slider_value)
        self.rod_GCP_slider.blockSignals(False)
        self.controller.set_target_rod_group_GCP_position(value)
        self.rod_GCP_target_label.setText(f"(Cible: {value:.0f})")
    
    def adjust_rod_GCP(self, step):
        new_value = self.rod_GCP_spinbox.value() + step
        self.rod_GCP_spinbox.setValue(max(0, min(228, new_value)))

    def on_boron_slider_changed(self, value):
        self.boron_spinbox.blockSignals(True)
        self.boron_spinbox.setValue(float(value))
        self.boron_spinbox.blockSignals(False)
        self.controller.set_target_boron_concentration(float(value))
        self.boron_target_label.setText(f"(Cible: {value:.0f})")
        
    def on_boron_spinbox_changed(self, value):
        self.boron_slider.blockSignals(True)
        self.boron_slider.setValue(int(value))
        self.boron_slider.blockSignals(False)
        self.controller.set_target_boron_concentration(float(value))
        self.boron_target_label.setText(f"(Cible: {value:.0f})")

    def adjust_boron(self, step):
        new_value = self.boron_spinbox.value() + step
        self.boron_spinbox.setValue(max(0, min(2000, new_value)))

    def on_fuel_enrichment_slider_changed(self, value):
        enrichment = value / 10.0
        self.fuel_enrichment_spinbox.blockSignals(True)
        self.fuel_enrichment_spinbox.setValue(enrichment)
        self.fuel_enrichment_spinbox.blockSignals(False)
        self.controller.update_fuel_enrichment(enrichment)
        
    def on_fuel_enrichment_spinbox_changed(self, value):
        slider_value = int(value * 10)
        self.fuel_enrichment_slider.blockSignals(True)
        self.fuel_enrichment_slider.setValue(slider_value)
        self.fuel_enrichment_slider.blockSignals(False)
        self.controller.update_fuel_enrichment(value)

    def adjust_fuel_enrichment(self, step):
        new_value = self.fuel_enrichment_spinbox.value() + step
        self.fuel_enrichment_spinbox.setValue(max(1.0, min(5.0, new_value)))

    # --- Info Dialog ---
    
    def _show_info_dialog(self):
        if self.info_dialog and self.info_dialog.isVisible():
            self.info_dialog.close()
            self.info_dialog = None
            return
            
        current_html = self.info_panel.get_current_info_html()
        if not self.info_panel.get_current_info_text().strip(): return
            
        self.info_dialog = InfoDialog("Informations Détaillées", current_html, self)
        self.info_dialog.finished.connect(self._on_info_dialog_closed)
        self.info_dialog.show()
    
    def _on_info_dialog_closed(self):
        self.info_dialog = None
    
    def closeEvent(self, event):
        if self.info_manager:
            for widget in list(self.info_manager.get_registered_widgets().keys()):
                self.info_manager.unregister_widget(widget)
        super().closeEvent(event) 