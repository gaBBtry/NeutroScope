"""
Main window implementation for the Neutro_EDF application
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QSlider, QComboBox, QGroupBox, QDoubleSpinBox,
    QPushButton
)
from PyQt6.QtCore import Qt, QEvent

from src.controller.reactor_controller import ReactorController
from src.gui.visualization import VisualizationPanel
from src.gui.widgets.info_panel import InfoPanel
from src.gui.widgets.info_button import InfoButton
from src.gui.widgets.credits_button import CreditsButton
from src.gui.widgets.info_widgets import InfoGroupBox


class MainWindow(QMainWindow):
    """Main application window with control panel and visualization area"""
    
    def __init__(self):
        super().__init__()
        
        # Create controller
        self.controller = ReactorController()
        
        self.setWindowTitle("Simulation Neutronique des REP")
        self.setMinimumSize(1200, 800)
        
        # Dictionary of information texts for different controls
        self.info_texts = {
            "rod_control": (
                "Barres de contrôle\n\n"
                "Les barres de contrôle sont des éléments absorbants de neutrons qui permettent "
                "de contrôler rapidement la réactivité du cœur. Leur insertion dans le cœur "
                "réduit le facteur de multiplication k et donc la puissance du réacteur.\n\n"
                "Plage: 0% (barres extraites) à 100% (barres complètement insérées)"
            ),
            "boron": (
                "Concentration en bore\n\n"
                "Le bore dissous dans l'eau du circuit primaire est un poison neutronique "
                "qui permet un contrôle fin et homogène de la réactivité du cœur. Une concentration "
                "plus élevée réduit la réactivité.\n\n"
                "Plage typique: 0 à 2000 ppm (parties par million)"
            ),
            "moderator_temp": (
                "Température du modérateur\n\n"
                "La température de l'eau (modérateur) affecte sa densité et donc son efficacité "
                "à ralentir les neutrons. Une augmentation de température réduit généralement "
                "la réactivité (coefficient de température modérateur négatif).\n\n"
                "Plage d'opération normale: 280°C à 350°C"
            ),
            "fuel_enrichment": (
                "Enrichissement du combustible\n\n"
                "Le pourcentage d'uranium-235 (isotope fissile) dans le combustible. "
                "Un enrichissement plus élevé augmente la réactivité et permet des "
                "cycles de combustible plus longs.\n\n"
                "Plage typique REP: 1.0% à 5.0%"
            ),
            "reactor_params": (
                "Paramètres neutroniques du réacteur\n\n"
                "- Taux de neutrons retardés (β): Fraction des neutrons émis avec un délai\n"
                "- Temps de doublement: Temps nécessaire pour doubler la puissance\n"
                "- Réactivité (ρ): Écart relatif par rapport à la criticité\n"
                "- k-effectif: Facteur de multiplication effectif (k=1: critique)"
            ),
            "presets": (
                "Préréglages du réacteur\n\n"
                "Sélectionnez un préréglage pour configurer rapidement le réacteur dans un état spécifique:\n\n"
                "- Démarrage: Configuration typique au démarrage du réacteur\n"
                "- Critique à puissance nominale: Réacteur en fonctionnement normal\n"
                "- Fin de cycle: Configuration typique en fin de cycle du combustible\n"
                "- Surcritique: État où le réacteur voit sa puissance augmenter\n"
                "- Sous-critique: État où le réacteur voit sa puissance diminuer\n\n"
                "Le préréglage 'Personnalisé' est automatiquement sélectionné lorsque vous modifiez manuellement les paramètres."
            )
        }
        
        # Create the central widget and main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        
        # Create left side container (controls + info panel)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create info panel and buttons for left side
        self.info_panel = InfoPanel()
        self.info_button = InfoButton()
        self.credits_button = CreditsButton()
        self.info_button.clicked.connect(self.toggle_info_panel)
        
        # Connect info panel closed signal
        self.info_panel.closed.connect(self.on_info_panel_closed)
        
        # Flag to control automatic showing of info panel
        self.auto_show_info = False
        
        # Create control panel (left side)
        control_panel = self.create_control_panel()
        
        # Create a layout for the buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.credits_button)
        buttons_layout.addWidget(self.info_button)
        
        # Add components to left container
        left_layout.addWidget(control_panel)
        left_layout.addLayout(buttons_layout)
        left_layout.addWidget(self.info_panel)
        
        # Create visualization area (right side)
        self.visualization_panel = VisualizationPanel(use_info_panel=False)
        # Connect visualization panel to the info panel
        self.visualization_panel.set_external_info_callback(self.show_info)
        
        # Add left and right containers to main layout
        main_layout.addWidget(left_container, 1)
        main_layout.addWidget(self.visualization_panel, 3)
        
        self.setCentralWidget(central_widget)
        
        # Connect signals
        self.connect_signals()
        
        # Initialize UI with a preset
        self.on_preset_changed("Démarrage")
    
    def connect_signals(self):
        """Connect all UI element signals to controller methods"""
        self.rod_slider.valueChanged.connect(self.on_rod_position_changed)
        self.boron_slider.valueChanged.connect(self.on_boron_slider_changed)
        self.boron_spinbox.valueChanged.connect(self.on_boron_spinbox_changed)
        self.moderator_temp_slider.valueChanged.connect(self.on_moderator_temperature_changed)
        self.fuel_enrichment_slider.valueChanged.connect(self.on_fuel_enrichment_changed)
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        
        # Connect info signals from group boxes
        self.rod_control_group.info_signal.connect(self.show_info)
        self.boron_group.info_signal.connect(self.show_info)
        self.moderator_temp_group.info_signal.connect(self.show_info)
        self.fuel_enrichment_group.info_signal.connect(self.show_info)
        self.reactor_params_group.info_signal.connect(self.show_info)
        self.presets_group.info_signal.connect(self.show_info)
    
    def create_control_panel(self):
        """Create the control panel with reactor parameter controls"""
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        control_panel.setLayout(control_layout)
        
        # Mode de calcul (indicateur)
        self.calculation_mode_group = QGroupBox("Mode de calcul")
        mode_layout = QVBoxLayout()
        
        # Récupérer les informations du mode actuel
        calc_info = self.controller.model.get_current_calculation_info()
        
        self.mode_label = QLabel(f"🔧 {calc_info['name']}")
        self.mode_label.setStyleSheet("font-weight: bold; color: #2E7D32; padding: 5px;")
        
        self.mode_description = QLabel(calc_info['description'])
        self.mode_description.setWordWrap(True)
        self.mode_description.setStyleSheet("color: #666; font-size: 10px; margin-top: 5px;")
        
        mode_layout.addWidget(self.mode_label)
        mode_layout.addWidget(self.mode_description)
        self.calculation_mode_group.setLayout(mode_layout)

        # Presets
        self.presets_group = self.create_info_groupbox("Préréglages", self.info_texts["presets"])
        preset_layout = QVBoxLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(self.controller.get_preset_names())
        self.preset_combo.setCurrentText(self.controller.get_current_preset_name())
        preset_layout.addWidget(self.preset_combo)
        self.presets_group.setLayout(preset_layout)
        
        # Control Rods
        self.rod_control_group = self.create_info_groupbox("Barres de contrôle", self.info_texts["rod_control"])
        rod_layout = QHBoxLayout()
        self.rod_slider = QSlider(Qt.Orientation.Horizontal)
        self.rod_slider.setRange(0, 100)
        self.rod_label = QLabel("0 %")
        rod_layout.addWidget(self.rod_slider)
        rod_layout.addWidget(self.rod_label)
        self.rod_control_group.setLayout(rod_layout)
        
        # Boron Concentration
        self.boron_group = self.create_info_groupbox("Concentration en Bore (ppm)", self.info_texts["boron"])
        boron_layout = QHBoxLayout()
        self.boron_slider = QSlider(Qt.Orientation.Horizontal)
        self.boron_slider.setRange(0, 2000)
        self.boron_spinbox = QDoubleSpinBox()
        self.boron_spinbox.setRange(0, 2000)
        self.boron_spinbox.setSuffix(" ppm")
        boron_layout.addWidget(self.boron_slider)
        boron_layout.addWidget(self.boron_spinbox)
        self.boron_group.setLayout(boron_layout)
        
        # Moderator Temperature
        self.moderator_temp_group = self.create_info_groupbox("Température Modérateur (°C)", self.info_texts["moderator_temp"])
        mod_temp_layout = QHBoxLayout()
        self.moderator_temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.moderator_temp_slider.setRange(280, 350)
        self.moderator_temp_label = QLabel("280 °C")
        mod_temp_layout.addWidget(self.moderator_temp_slider)
        mod_temp_layout.addWidget(self.moderator_temp_label)
        self.moderator_temp_group.setLayout(mod_temp_layout)
        
        # Fuel Enrichment
        self.fuel_enrichment_group = self.create_info_groupbox("Enrichissement Combustible (%)", self.info_texts["fuel_enrichment"])
        fuel_enrich_layout = QHBoxLayout()
        self.fuel_enrichment_slider = QSlider(Qt.Orientation.Horizontal)
        self.fuel_enrichment_slider.setRange(10, 50) # Using 10-50 for 1.0-5.0
        self.fuel_enrichment_label = QLabel("1.0 %")
        fuel_enrich_layout.addWidget(self.fuel_enrichment_slider)
        fuel_enrich_layout.addWidget(self.fuel_enrichment_label)
        self.fuel_enrichment_group.setLayout(fuel_enrich_layout)
        
        # Reactor Parameters Display
        self.reactor_params_group = self.create_info_groupbox("Paramètres du Réacteur", self.info_texts["reactor_params"])
        params_layout = QVBoxLayout()
        self.k_effective_label = QLabel("k-eff: 1.00000")
        self.reactivity_label = QLabel("Réactivité (pcm): 0.0")
        self.doubling_time_label = QLabel("Temps de doublement: ∞")
        self.delayed_neutron_label = QLabel(f"β: {self.controller.get_reactor_parameters()['delayed_neutron_fraction'] * 100:.3f}%")
        params_layout.addWidget(self.k_effective_label)
        params_layout.addWidget(self.reactivity_label)
        params_layout.addWidget(self.doubling_time_label)
        params_layout.addWidget(self.delayed_neutron_label)
        self.reactor_params_group.setLayout(params_layout)
        
        # Add all groups to control layout
        control_layout.addWidget(self.calculation_mode_group)
        control_layout.addWidget(self.presets_group)
        control_layout.addWidget(self.rod_control_group)
        control_layout.addWidget(self.boron_group)
        control_layout.addWidget(self.moderator_temp_group)
        control_layout.addWidget(self.fuel_enrichment_group)
        control_layout.addWidget(self.reactor_params_group)
        control_layout.addStretch(1)

        return control_panel
    
    def create_info_groupbox(self, title, info_text):
        """Helper to create a group box with info capabilities"""
        group_box = InfoGroupBox(title, info_text)
        return group_box

    def show_info(self, text):
        """Show information in the info panel"""
        # Automatically show/hide panel on hover
        if self.auto_show_info:
            if text:
                self.info_panel.update_info(text)
                self.info_panel.setVisible(True)
            else:
                self.info_panel.setVisible(False)
        else: # Manual mode
            if self.info_panel.isVisible():
                self.info_panel.update_info(text)
    
    def toggle_info_panel(self):
        """Toggle the visibility of the info panel"""
        self.info_panel.setVisible(not self.info_panel.isVisible())
        self.info_button.setChecked(self.info_panel.isVisible())
        self.info_button.update_tooltip(self.info_panel.isVisible())
        # When manually toggled, switch off auto-show
        self.auto_show_info = False

    def on_info_panel_closed(self):
        """Handle info panel being closed via its own button"""
        self.info_button.setChecked(False)
        self.info_button.update_tooltip(False)
    
    def on_preset_changed(self, preset_name):
        """Handle preset change from the combobox"""
        if preset_name == "Personnalisé":
            return
            
        config = self.controller.apply_preset(preset_name)
        if config:
            self.update_ui_from_preset(config)
            
    def update_ui_from_preset(self, config):
        """Update all UI controls from a preset configuration"""
        # Block signals to prevent feedback loops
        self.rod_slider.blockSignals(True)
        self.boron_slider.blockSignals(True)
        self.boron_spinbox.blockSignals(True)
        self.moderator_temp_slider.blockSignals(True)
        self.fuel_enrichment_slider.blockSignals(True)

        # Update sliders and labels
        self.rod_slider.setValue(int(config["control_rod_position"]))
        self.rod_label.setText(f"{config['control_rod_position']:.0f} %")
        
        self.boron_slider.setValue(int(config["boron_concentration"]))
        self.boron_spinbox.setValue(config["boron_concentration"])
        
        self.moderator_temp_slider.setValue(int(config["moderator_temperature"]))
        self.moderator_temp_label.setText(f"{config['moderator_temperature']:.0f} °C")
        
        self.fuel_enrichment_slider.setValue(int(config["fuel_enrichment"] * 10))
        self.fuel_enrichment_label.setText(f"{config['fuel_enrichment']:.1f} %")

        # Unblock signals
        self.rod_slider.blockSignals(False)
        self.boron_slider.blockSignals(False)
        self.boron_spinbox.blockSignals(False)
        self.moderator_temp_slider.blockSignals(False)
        self.fuel_enrichment_slider.blockSignals(False)
        
        # Update reactor parameters and visualizations
        self.update_reactor_params(config["reactor_params"])
        self.update_visualizations()
    
    def check_for_custom_preset(self):
        """Check if current settings match a preset, otherwise set to 'Personnalisé'."""
        current_preset_name = self.controller.get_current_preset_name()
        if self.preset_combo.currentText() != current_preset_name:
            self.preset_combo.setCurrentText(current_preset_name)

    def on_rod_position_changed(self, value):
        """Handle control rod position change"""
        self.rod_label.setText(f"{value} %")
        params = self.controller.update_control_rod_position(float(value))
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()

    def on_boron_slider_changed(self, value):
        """Sync spinbox with slider"""
        self.boron_spinbox.setValue(float(value))
        # on_boron_spinbox_changed will handle the rest
        
    def on_boron_spinbox_changed(self, value):
        """Sync slider with spinbox and update model"""
        self.boron_slider.setValue(int(value))
        self.on_boron_concentration_changed(value)

    def on_boron_concentration_changed(self, value):
        """Handle boron concentration change"""
        params = self.controller.update_boron_concentration(float(value))
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()

    def on_moderator_temperature_changed(self, value):
        """Handle moderator temperature change"""
        self.moderator_temp_label.setText(f"{value} °C")
        params = self.controller.update_moderator_temperature(float(value))
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()

    def on_fuel_enrichment_changed(self, value):
        """Handle fuel enrichment change"""
        enrichment = value / 10.0
        self.fuel_enrichment_label.setText(f"{enrichment:.1f} %")
        params = self.controller.update_fuel_enrichment(enrichment)
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()

    def update_calculation_mode_display(self):
        """Met à jour l'affichage du mode de calcul"""
        calc_info = self.controller.model.get_current_calculation_info()
        
        # Mettre à jour le label principal
        self.mode_label.setText(f"🔧 {calc_info['name']}")
        
        # Mettre à jour la description
        self.mode_description.setText(calc_info['description'])
        
        # Changer la couleur selon le mode
        if calc_info['mode'] == 'fast':
            color = "#1976D2"  # Bleu pour mode rapide
            icon = "⚡"
        elif calc_info['mode'] == 'precise':
            color = "#388E3C"  # Vert pour mode précis
            icon = "🎯"
        else:
            color = "#F57C00"  # Orange pour mode auto
            icon = "🔧"
        
        self.mode_label.setText(f"{icon} {calc_info['name']}")
        self.mode_label.setStyleSheet(f"font-weight: bold; color: {color}; padding: 5px;")

    def update_reactor_params(self, params):
        """Update the display of reactor parameters"""
        k_eff = params["k_effective"]
        reactivity_pcm = params["reactivity"] * 100000
        doubling_time = params["doubling_time"]
        
        self.k_effective_label.setText(f"k-eff: {k_eff:.5f}")
        self.reactivity_label.setText(f"Réactivité (pcm): {reactivity_pcm:.1f}")
        
        if doubling_time == float('inf'):
            self.doubling_time_label.setText("Temps de doublement: ∞")
        else:
            self.doubling_time_label.setText(f"Temps de doublement: {doubling_time:.1f} s")
        
        # Mettre à jour l'indicateur de mode (au cas où il aurait changé)
        self.update_calculation_mode_display()
            
    def update_visualizations(self):
        """Update all plots with the latest data from the model"""
        # Axial Flux
        height, flux = self.controller.get_axial_flux_distribution()
        rod_pos = self.rod_slider.value()
        self.visualization_panel.update_flux_plot(height, flux, rod_pos)
        
        # Four Factors
        factors_data = self.controller.get_four_factors_data()
        self.visualization_panel.update_factors_plot(factors_data)
        
        # Neutron Balance
        balance_data = self.controller.get_neutron_balance_data()
        self.visualization_panel.update_neutron_balance_plot(balance_data)
        
        # Pilotage Diagram
        ao_data = self.controller.get_axial_offset_data()
        self.visualization_panel.update_pilotage_diagram_plot(ao_data)

    def keyPressEvent(self, event):
        """Handle key press events for the main window"""
        if event.key() == Qt.Key.Key_I:
            self.toggle_info_panel()
        
        super().keyPressEvent(event) 