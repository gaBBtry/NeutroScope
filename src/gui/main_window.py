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
from src.gui.widgets.info_manager import InfoManager
from src.gui.widgets.enhanced_widgets import InfoGroupBox
from src.gui.widgets.info_dialog import InfoDialog
from src.model import config


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application avec panneau de contrôle et zone de visualisation"""

    def __init__(self):
        super().__init__()

        # Create controller
        self.controller = ReactorController()
        
        # Get GUI settings from config
        gui_settings = self.controller.get_gui_settings()
        
        self.setWindowTitle(gui_settings.get("window_title", "NeutroScope"))
        self.setMinimumSize(*gui_settings.get("minimum_size", [1200, 800]))

        # Create the central widget and main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # Create left side container (controls + info panel)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Create the new centralized info management system
        self.info_manager = InfoManager()

        # Track the info dialog state for toggling
        self.info_dialog = None

        # Create info panel and buttons for left side
        self.info_panel = InfoPanel()
        self.credits_button = CreditsButton()

        # Connect the new info management system
        self.info_manager.info_requested.connect(self.info_panel.update_info)
        self.info_manager.info_cleared.connect(self.info_panel.clear_info)

        # Create control panel (left side)
        control_panel = self.create_control_panel()

        # Create a layout for the buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.credits_button)

        # Add components to left container
        left_layout.addWidget(control_panel)
        left_layout.addLayout(buttons_layout)
        left_layout.addWidget(self.info_panel)

        # Create visualization area (right side)
        self.visualization_panel = VisualizationPanel(info_manager=self.info_manager)

        # Add left and right containers to main layout
        main_layout.addWidget(left_container, gui_settings.get("control_panel_ratio", 1))
        main_layout.addWidget(self.visualization_panel, gui_settings.get("visualization_ratio", 3))

        self.setCentralWidget(central_widget)

        # Connect signals
        self.connect_signals()

        # Connect xenon dynamics controls
        self.connect_xenon_signals()

        # Initialize UI with a preset
        self.on_preset_changed("PMD en début de cycle")
        
        # Initialize reset button state
        self.update_reset_button_state()

        # Add QShortcut for 'i' key to show info dialog
        self.info_shortcut = QShortcut(QKeySequence("i"), self)
        self.info_shortcut.activated.connect(self._show_info_dialog)

    def connect_signals(self):
        """Connecte tous les signaux des éléments UI aux méthodes du contrôleur"""
        # Get step values from config
        config_r = self.controller.get_parameter_config('rod_group_R')
        config_gcp = self.controller.get_parameter_config('rod_group_GCP')
        config_boron = self.controller.get_parameter_config('boron')

        # Groupe R signals
        self.rod_R_slider.valueChanged.connect(self.on_rod_R_slider_changed)
        self.rod_R_spinbox.valueChanged.connect(self.on_rod_R_spinbox_changed)

        # Groupe GCP signals
        self.rod_GCP_slider.valueChanged.connect(self.on_rod_GCP_slider_changed)
        self.rod_GCP_spinbox.valueChanged.connect(self.on_rod_GCP_spinbox_changed)

        # Other controls
        self.boron_slider.valueChanged.connect(self.on_boron_slider_changed)
        self.boron_spinbox.valueChanged.connect(self.on_boron_spinbox_changed)
        self.power_slider.valueChanged.connect(self.on_power_slider_changed)
        self.power_spinbox.valueChanged.connect(self.on_power_spinbox_changed)

        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)

    def connect_xenon_signals(self):
        """Connecte les signaux des contrôles de dynamique Xénon"""
        xenon_controls = self.visualization_panel.get_xenon_controls()
        xenon_controls.time_advance_requested.connect(self.on_time_advance)
        xenon_controls.reset_requested.connect(self.on_xenon_reset)

    def create_control_panel(self):
        """Crée le panneau de contrôle avec les contrôles des paramètres du réacteur"""
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        control_panel.setLayout(control_layout)

        # Get settings for widgets
        gui_settings = self.controller.get_gui_settings()
        widths = gui_settings.get("widths", {})

        # Presets
        presets_config = self.controller.get_parameter_config('presets_info')
        self.presets_group = self.create_info_groupbox(presets_config.get('label', 'Préréglages'), presets_config.get('info_text', ''))
        preset_layout = QVBoxLayout()
        preset_controls_layout = QHBoxLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(self.controller.get_preset_names())
        self.preset_combo.setCurrentText(self.controller.get_current_preset_name())
        preset_controls_layout.addWidget(self.preset_combo)
        self.reset_preset_button = QPushButton("Reset")
        self.reset_preset_button.setMaximumWidth(widths.get('reset_button', 60))
        self.reset_preset_button.setEnabled(False)
        self.reset_preset_button.setToolTip("Revenir aux paramètres du preset sélectionné")
        self.reset_preset_button.clicked.connect(self.reset_to_selected_preset)
        preset_controls_layout.addWidget(self.reset_preset_button)
        preset_layout.addLayout(preset_controls_layout)
        self.presets_group.setLayout(preset_layout)

        # Parameter controls
        self.rod_R_group, self.rod_R_slider, self.rod_R_spinbox, _, _ = self._create_parameter_control('rod_group_R')
        self.rod_GCP_group, self.rod_GCP_slider, self.rod_GCP_spinbox, _, _ = self._create_parameter_control('rod_group_GCP')
        self.boron_group, self.boron_slider, self.boron_spinbox, _, _ = self._create_parameter_control('boron')
        self.power_group, self.power_slider, self.power_spinbox, _, _ = self._create_parameter_control('power_level')

        # Reactor Parameters Display
        params_info_config = self.controller.get_parameter_config('reactor_params_info')
        self.reactor_params_group = self.create_info_groupbox(params_info_config.get('label', "Paramètres"), params_info_config.get('info_text', ''))
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
        control_layout.addWidget(self.presets_group)
        control_layout.addWidget(self.rod_R_group)
        control_layout.addWidget(self.rod_GCP_group)
        control_layout.addWidget(self.boron_group)
        control_layout.addWidget(self.power_group)
        control_layout.addWidget(self.reactor_params_group)
        control_layout.addStretch(1)

        return control_panel

    def _create_parameter_control(self, param_name):
        """Helper to create a standardized parameter control group."""
        config = self.controller.get_parameter_config(param_name)
        gui_settings = self.controller.get_gui_settings()
        widths = gui_settings.get("widths", {})

        group = self.create_info_groupbox(config.get('label', ''), config.get('info_text', ''))
        layout = QHBoxLayout()

        slider = QSlider(Qt.Orientation.Horizontal)
        min_val, max_val = config.get('range', [0, 100])
        
        # Special handling for enrichment slider
        multiplier = config.get('slider_range_multiplier', 1)
        slider.setRange(int(min_val * multiplier), int(max_val * multiplier))
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(config.get('tick_interval', 10))

        spinbox = QDoubleSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setDecimals(config.get('decimals', 0))
        spinbox.setSuffix(config.get('suffix', ''))
        spinbox.setMinimumWidth(widths.get(f"{param_name.split('_')[0]}_spinbox", 80))
        spinbox.setSingleStep(1)
        
        # Ajout des widgets dans l'ordre adapté (sans boutons + et -)
        layout.addWidget(slider)
        layout.addWidget(spinbox)
        group.setLayout(layout)

        return group, slider, spinbox, None, None

    def create_info_groupbox(self, title, info_text):
        """Aide pour créer une boîte de groupe avec capacités d'information"""
        group_box = InfoGroupBox(title, info_text, self.info_manager)
        return group_box

    def _show_info_dialog(self):
        """Toggle the info dialog - show if closed, close if open. Only opens if there's content to show."""
        if self.info_dialog and self.info_dialog.isVisible():
            self.info_dialog.close()
            self.info_dialog = None
            return
            
        current_html = self.info_panel.get_current_info_html()
        current_text = self.info_panel.get_current_info_text()
        
        if not current_text or not current_text.strip():
            return
            
        self.info_dialog = InfoDialog("Informations Détaillées", current_html, self)
        self.info_dialog.finished.connect(self._on_info_dialog_closed)
        self.info_dialog.show()
    
    def _on_info_dialog_closed(self):
        """Clean up when info dialog is closed."""
        self.info_dialog = None
    
    def reset_to_selected_preset(self):
        """Reset tous les paramètres au preset actuellement sélectionné dans le combo"""
        selected_preset = self.preset_combo.currentText()
        if selected_preset and selected_preset != "Personnalisé":
            config = self.controller.apply_preset(selected_preset)
            if config:
                self.update_ui_from_preset(config)
    
    def update_reset_button_state(self):
        """Met à jour l'état du bouton Reset selon si l'état actuel correspond au preset sélectionné"""
        selected_preset = self.preset_combo.currentText()
        current_preset = self.controller.get_current_preset_name()
        
        should_enable = (selected_preset and 
                        selected_preset != "Personnalisé" and
                        current_preset != selected_preset)
        
        self.reset_preset_button.setEnabled(should_enable)
    
    def on_preset_changed(self, preset_name):
        """Handle preset change from the combobox"""
        if preset_name == "Personnalisé":
            self.update_reset_button_state()
            return
            
        config = self.controller.apply_preset(preset_name)
        if config:
            self.update_ui_from_preset(config)
            self.update_reset_button_state()
            
    def update_ui_from_preset(self, config):
        """Update all UI controls from a preset configuration"""
        # Block signals to prevent feedback loops
        widgets = [
            self.rod_R_slider, self.rod_R_spinbox, self.rod_GCP_slider, self.rod_GCP_spinbox,
            self.boron_slider, self.boron_spinbox, self.power_slider, self.power_spinbox
        ]
        for widget in widgets:
            widget.blockSignals(True)

        # Update rod group controls
        rod_r_config = self.controller.get_parameter_config('rod_group_R')
        max_steps = rod_r_config.get('range', [0, 228])[1]
        
        inverted_R_slider = max_steps - int(config["rod_group_R_position"])
        inverted_GCP_slider = max_steps - int(config["rod_group_GCP_position"])
        
        self.rod_R_slider.setValue(inverted_R_slider)
        self.rod_R_spinbox.setValue(config["rod_group_R_position"])
        
        self.rod_GCP_slider.setValue(inverted_GCP_slider)
        self.rod_GCP_spinbox.setValue(config["rod_group_GCP_position"])
        
        self.boron_slider.setValue(int(config["boron_concentration"]))
        self.boron_spinbox.setValue(config["boron_concentration"])
        
        self.power_slider.setValue(int(config["power_level"]))
        self.power_spinbox.setValue(config["power_level"])

        # Unblock signals
        for widget in widgets:
            widget.blockSignals(False)
        
        self.update_reactor_params(config["reactor_params"])
        self.update_visualizations()
        self.check_for_custom_preset()
    
    def check_for_custom_preset(self):
        """Check if current settings match a preset, otherwise set to 'Personnalisé'."""
        current_preset_name = self.controller.get_current_preset_name()
        if self.preset_combo.currentText() != current_preset_name:
            self.preset_combo.setCurrentText(current_preset_name)
        
        self.update_reset_button_state()

    def _update_parameter_and_ui(self, controller_method, value):
        params = controller_method(float(value))
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()

    def on_rod_R_slider_changed(self, value):
        """Handle R group slider change"""
        rod_config = self.controller.get_parameter_config('rod_group_R')
        max_steps = rod_config.get('range', [0, 228])[1]
        inverted_value = max_steps - value
        
        self.rod_R_spinbox.blockSignals(True)
        self.rod_R_spinbox.setValue(inverted_value)
        self.rod_R_spinbox.blockSignals(False)
        
        self._update_parameter_and_ui(self.controller.update_rod_group_R_position, inverted_value)
    
    def on_rod_R_spinbox_changed(self, value):
        """Handle R group spinbox change"""
        rod_config = self.controller.get_parameter_config('rod_group_R')
        max_steps = rod_config.get('range', [0, 228])[1]
        inverted_slider_value = max_steps - int(value)
        
        self.rod_R_slider.blockSignals(True)
        self.rod_R_slider.setValue(inverted_slider_value)
        self.rod_R_slider.blockSignals(False)
        
        self._update_parameter_and_ui(self.controller.update_rod_group_R_position, value)
    
    def on_rod_GCP_slider_changed(self, value):
        """Handle GCP group slider change"""
        rod_config = self.controller.get_parameter_config('rod_group_GCP')
        max_steps = rod_config.get('range', [0, 228])[1]
        inverted_value = max_steps - value
        
        self.rod_GCP_spinbox.blockSignals(True)
        self.rod_GCP_spinbox.setValue(inverted_value)
        self.rod_GCP_spinbox.blockSignals(False)
        
        self._update_parameter_and_ui(self.controller.update_rod_group_GCP_position, inverted_value)
    
    def on_rod_GCP_spinbox_changed(self, value):
        """Handle GCP group spinbox change"""
        rod_config = self.controller.get_parameter_config('rod_group_GCP')
        max_steps = rod_config.get('range', [0, 228])[1]
        inverted_slider_value = max_steps - int(value)
        
        self.rod_GCP_slider.blockSignals(True)
        self.rod_GCP_slider.setValue(inverted_slider_value)
        self.rod_GCP_slider.blockSignals(False)
        
        self._update_parameter_and_ui(self.controller.update_rod_group_GCP_position, value)

    def on_boron_slider_changed(self, value):
        """Met à jour le spinbox depuis le slider."""
        self.boron_spinbox.blockSignals(True)
        self.boron_spinbox.setValue(float(value))
        self.boron_spinbox.blockSignals(False)
        self._update_parameter_and_ui(self.controller.update_boron_concentration, value)
        
    def on_boron_spinbox_changed(self, value):
        """Met à jour le slider depuis le spinbox."""
        self.boron_slider.blockSignals(True)
        self.boron_slider.setValue(int(value))
        self.boron_slider.blockSignals(False)
        self._update_parameter_and_ui(self.controller.update_boron_concentration, value)
    
    def on_power_slider_changed(self, value):
        """Met à jour le spinbox depuis le slider de puissance."""
        self.power_spinbox.blockSignals(True)
        self.power_spinbox.setValue(float(value))
        self.power_spinbox.blockSignals(False)
        self._update_parameter_and_ui(self.controller.update_power_level, value)
        
    def on_power_spinbox_changed(self, value):
        """Met à jour le slider depuis le spinbox de puissance."""
        self.power_slider.blockSignals(True)
        self.power_slider.setValue(int(value))
        self.power_slider.blockSignals(False)
        self._update_parameter_and_ui(self.controller.update_power_level, value)

    def on_time_advance(self, hours):
        """Handle time advancement for xenon dynamics"""
        params = self.controller.advance_time(hours)
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()
    
    def on_xenon_reset(self):
        """Handle xenon reset to equilibrium"""
        params = self.controller.reset_xenon_to_equilibrium()
        self.update_reactor_params(params)
        self.update_visualizations()
        self.visualization_panel.xenon_widget.clear_history()
        self.check_for_custom_preset()

    def update_reactor_params(self, params):
        """Update the display of reactor parameters"""
        k_eff = params["k_effective"]
        reactivity_pcm = params["reactivity"] * config.REACTIVITY_TO_PCM
        doubling_time = params["doubling_time"]
        
        self.k_effective_label.setText(f"k-eff: {k_eff:.4f}")
        self.reactivity_label.setText(f"Réactivité (pcm): {reactivity_pcm:.1f}")
        
        if doubling_time == float('inf'):
            self.doubling_time_label.setText("Temps de doublement: ∞")
        else:
            self.doubling_time_label.setText(f"Temps de doublement: {doubling_time:.1f} s")
            
    def update_visualizations(self):
        """Update all plots with the latest data from the model"""
        height, flux = self.controller.get_axial_flux_distribution()
        equivalent_position = self.controller.model._get_equivalent_rod_position_percent()
        self.visualization_panel.update_flux_plot(height, flux, equivalent_position)
        
        factors_data = self.controller.get_four_factors_data()
        self.visualization_panel.update_factors_plot(factors_data)
        
        balance_data = self.controller.get_neutron_balance_data()
        self.visualization_panel.update_neutron_balance_plot(balance_data)
        
        cycle_data = self.controller.get_neutron_cycle_data()
        self.visualization_panel.update_neutron_cycle_plot(cycle_data)
        
        xenon_data = self.controller.get_xenon_dynamics_data()
        self.visualization_panel.update_xenon_plot(xenon_data)

    def keyPressEvent(self, event):
        """Handle key press events for the main window"""
        if event.key() == Qt.Key.Key_I:
            self._show_info_dialog()
        
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Ensure proper cleanup on close"""
        if self.info_manager:
            widgets_to_unregister = list(self.info_manager.get_registered_widgets().keys())
            for widget in widgets_to_unregister:
                self.info_manager.unregister_widget(widget)
        
        super().closeEvent(event) 