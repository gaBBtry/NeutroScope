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


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application avec panneau de contrôle et zone de visualisation"""
    
    def __init__(self):
        super().__init__()
        
        # Create controller
        self.controller = ReactorController()
        
        self.setWindowTitle("Simulation Neutronique des REP")
        self.setMinimumSize(1200, 800)
        
        # Dictionary of information texts for different controls
        self.info_texts = {
            "rod_control_R": (
                "Groupe de Régulation (R)\n\n"
                "Le groupe R est utilisé pour le contrôle fin de la réactivité et les ajustements "
                "de puissance. Il représente environ 30% de la valeur totale des barres de contrôle.\n\n"
                "Position: 0 pas (barres extraites) à 228 pas (barres insérées)\n"
                "Curseur: gauche = extraites, droite = insérées\n"
                "Pas recommandés: 1-10 pas pour les ajustements fins"
            ),
            "rod_control_GCP": (
                "Groupe de Compensation de Puissance (GCP)\n\n"
                "Le groupe GCP est utilisé pour la compensation des variations de réactivité dues "
                "au burn-up et aux effets xénon. Il représente environ 70% de la valeur totale.\n\n"
                "Position: 0 pas (barres extraites) à 228 pas (barres insérées)\n"
                "Curseur: gauche = extraites, droite = insérées\n"
                "Pas recommandés: 5-50 pas pour les ajustements significatifs"
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
                "Le préréglage 'Personnalisé' est automatiquement sélectionné lorsque vous modifiez manuellement les paramètres.\n\n"
                "Bouton 'Reset': Permet de revenir aux paramètres originaux du preset sélectionné si des modifications ont été apportées."
            )
        }
        
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
        
        # Connect UI signals
        
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
        main_layout.addWidget(left_container, 1)
        main_layout.addWidget(self.visualization_panel, 3)
        
        self.setCentralWidget(central_widget)
        
        # Connect signals
        self.connect_signals()
        
        # Connect xenon dynamics controls
        self.connect_xenon_signals()
        
        # Initialize UI with a preset
        self.on_preset_changed("Démarrage")
        
        # Initialize reset button state
        self.update_reset_button_state()
        
        # Add QShortcut for 'i' key to show info dialog
        self.info_shortcut = QShortcut(QKeySequence("i"), self)
        self.info_shortcut.activated.connect(self._show_info_dialog)
    
    def connect_signals(self):
        """Connecte tous les signaux des éléments UI aux méthodes du contrôleur"""
        # Groupe R signals
        self.rod_R_slider.valueChanged.connect(self.on_rod_R_slider_changed)
        self.rod_R_spinbox.valueChanged.connect(self.on_rod_R_spinbox_changed)
        self.rod_R_plus_btn.clicked.connect(lambda: self.adjust_rod_R(1))
        self.rod_R_minus_btn.clicked.connect(lambda: self.adjust_rod_R(-1))
        
        # Groupe GCP signals
        self.rod_GCP_slider.valueChanged.connect(self.on_rod_GCP_slider_changed)
        self.rod_GCP_spinbox.valueChanged.connect(self.on_rod_GCP_spinbox_changed)
        self.rod_GCP_plus_btn.clicked.connect(lambda: self.adjust_rod_GCP(5))
        self.rod_GCP_minus_btn.clicked.connect(lambda: self.adjust_rod_GCP(-5))
        
        # Other controls
        self.boron_slider.valueChanged.connect(self.on_boron_slider_changed)
        self.boron_spinbox.valueChanged.connect(self.on_boron_spinbox_changed)
        self.boron_plus_btn.clicked.connect(lambda: self.adjust_boron(10))
        self.boron_minus_btn.clicked.connect(lambda: self.adjust_boron(-10))
        
        self.moderator_temp_slider.valueChanged.connect(self.on_moderator_temp_slider_changed)
        self.moderator_temp_spinbox.valueChanged.connect(self.on_moderator_temp_spinbox_changed)
        self.moderator_temp_plus_btn.clicked.connect(lambda: self.adjust_moderator_temp(1))
        self.moderator_temp_minus_btn.clicked.connect(lambda: self.adjust_moderator_temp(-1))
        
        self.fuel_enrichment_slider.valueChanged.connect(self.on_fuel_enrichment_slider_changed)
        self.fuel_enrichment_spinbox.valueChanged.connect(self.on_fuel_enrichment_spinbox_changed)
        self.fuel_enrichment_plus_btn.clicked.connect(lambda: self.adjust_fuel_enrichment(0.1))
        self.fuel_enrichment_minus_btn.clicked.connect(lambda: self.adjust_fuel_enrichment(-0.1))
        
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        
        # Info connections are now handled automatically by the InfoManager
        # No need for manual signal connections
    
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
        
        # Presets
        self.presets_group = self.create_info_groupbox("Préréglages", self.info_texts["presets"])
        preset_layout = QVBoxLayout()
        
        # Première ligne : ComboBox + Bouton Gérer
        preset_controls_layout = QHBoxLayout()
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(self.controller.get_preset_names())
        self.preset_combo.setCurrentText(self.controller.get_current_preset_name())
        preset_controls_layout.addWidget(self.preset_combo)
        

        
        # Bouton de reset pour revenir au preset sélectionné
        self.reset_preset_button = QPushButton("Reset")
        self.reset_preset_button.setMaximumWidth(60)
        self.reset_preset_button.setEnabled(False)  # Désactivé par défaut
        self.reset_preset_button.setToolTip("Revenir aux paramètres du preset sélectionné")
        self.reset_preset_button.clicked.connect(self.reset_to_selected_preset)
        preset_controls_layout.addWidget(self.reset_preset_button)
        
        preset_layout.addLayout(preset_controls_layout)
        self.presets_group.setLayout(preset_layout)
        
        # Groupe R (Régulation)
        self.rod_R_group = self.create_info_groupbox("Groupe R (Régulation)", self.info_texts["rod_control_R"])
        rod_R_layout = QHBoxLayout()
        
        # Contrôles pour groupe R
        self.rod_R_slider = QSlider(Qt.Orientation.Horizontal)
        self.rod_R_slider.setRange(0, 228)
        self.rod_R_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.rod_R_slider.setTickInterval(50)
        
        self.rod_R_spinbox = QDoubleSpinBox()
        self.rod_R_spinbox.setRange(0, 228)
        self.rod_R_spinbox.setDecimals(0)
        self.rod_R_spinbox.setSuffix(" pas")
        self.rod_R_spinbox.setMinimumWidth(80)
        
        # Boutons d'ajustement fin pour groupe R
        self.rod_R_plus_btn = QPushButton("+1")
        self.rod_R_plus_btn.setMaximumWidth(30)
        self.rod_R_plus_btn.setToolTip("Insérer davantage (+1 pas d'insertion)")
        self.rod_R_minus_btn = QPushButton("-1")
        self.rod_R_minus_btn.setMaximumWidth(30)
        self.rod_R_minus_btn.setToolTip("Extraire davantage (-1 pas d'insertion)")
        
        rod_R_layout.addWidget(self.rod_R_slider)
        rod_R_layout.addWidget(self.rod_R_plus_btn)
        rod_R_layout.addWidget(self.rod_R_minus_btn)
        rod_R_layout.addWidget(self.rod_R_spinbox)
        self.rod_R_group.setLayout(rod_R_layout)
        
        # Groupe GCP (Compensation de Puissance)
        self.rod_GCP_group = self.create_info_groupbox("Groupe GCP (Compensation)", self.info_texts["rod_control_GCP"])
        rod_GCP_layout = QHBoxLayout()
        
        # Contrôles pour groupe GCP
        self.rod_GCP_slider = QSlider(Qt.Orientation.Horizontal)
        self.rod_GCP_slider.setRange(0, 228)
        self.rod_GCP_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.rod_GCP_slider.setTickInterval(50)
        
        self.rod_GCP_spinbox = QDoubleSpinBox()
        self.rod_GCP_spinbox.setRange(0, 228)
        self.rod_GCP_spinbox.setDecimals(0)
        self.rod_GCP_spinbox.setSuffix(" pas")
        self.rod_GCP_spinbox.setMinimumWidth(80)
        
        # Boutons d'ajustement pour groupe GCP (pas plus grands)
        self.rod_GCP_plus_btn = QPushButton("+5")
        self.rod_GCP_plus_btn.setMaximumWidth(30)
        self.rod_GCP_plus_btn.setToolTip("Insérer davantage (+5 pas d'insertion)")
        self.rod_GCP_minus_btn = QPushButton("-5")
        self.rod_GCP_minus_btn.setMaximumWidth(30)
        self.rod_GCP_minus_btn.setToolTip("Extraire davantage (-5 pas d'insertion)")
        
        rod_GCP_layout.addWidget(self.rod_GCP_slider)
        rod_GCP_layout.addWidget(self.rod_GCP_plus_btn)
        rod_GCP_layout.addWidget(self.rod_GCP_minus_btn)
        rod_GCP_layout.addWidget(self.rod_GCP_spinbox)
        self.rod_GCP_group.setLayout(rod_GCP_layout)
        
        # Boron Concentration
        self.boron_group = self.create_info_groupbox("Concentration en Bore (ppm)", self.info_texts["boron"])
        boron_layout = QHBoxLayout()
        
        self.boron_slider = QSlider(Qt.Orientation.Horizontal)
        self.boron_slider.setRange(0, 2000)
        self.boron_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.boron_slider.setTickInterval(250)
        
        self.boron_spinbox = QDoubleSpinBox()
        self.boron_spinbox.setRange(0, 2000)
        self.boron_spinbox.setDecimals(0)
        self.boron_spinbox.setSuffix(" ppm")
        self.boron_spinbox.setMinimumWidth(80)
        
        # Boutons d'ajustement pour bore (pas de 10 ppm)
        self.boron_plus_btn = QPushButton("+10")
        self.boron_plus_btn.setMaximumWidth(35)
        self.boron_plus_btn.setToolTip("Augmenter concentration bore (+10 ppm)")
        self.boron_minus_btn = QPushButton("-10")
        self.boron_minus_btn.setMaximumWidth(35)
        self.boron_minus_btn.setToolTip("Diminuer concentration bore (-10 ppm)")
        
        boron_layout.addWidget(self.boron_slider)
        boron_layout.addWidget(self.boron_minus_btn)
        boron_layout.addWidget(self.boron_plus_btn)
        boron_layout.addWidget(self.boron_spinbox)
        self.boron_group.setLayout(boron_layout)
        
        # Moderator Temperature
        self.moderator_temp_group = self.create_info_groupbox("Température Moyenne (°C)", self.info_texts["moderator_temp"])
        mod_temp_layout = QHBoxLayout()
        
        self.moderator_temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.moderator_temp_slider.setRange(280, 350)
        self.moderator_temp_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.moderator_temp_slider.setTickInterval(10)
        
        self.moderator_temp_spinbox = QDoubleSpinBox()
        self.moderator_temp_spinbox.setRange(280, 350)
        self.moderator_temp_spinbox.setDecimals(1)
        self.moderator_temp_spinbox.setSuffix(" °C")
        self.moderator_temp_spinbox.setMinimumWidth(80)
        
        # Boutons d'ajustement pour température (pas de 1°C)
        self.moderator_temp_plus_btn = QPushButton("+1")
        self.moderator_temp_plus_btn.setMaximumWidth(30)
        self.moderator_temp_plus_btn.setToolTip("Augmenter température (+1°C)")
        self.moderator_temp_minus_btn = QPushButton("-1")
        self.moderator_temp_minus_btn.setMaximumWidth(30)
        self.moderator_temp_minus_btn.setToolTip("Diminuer température (-1°C)")
        
        mod_temp_layout.addWidget(self.moderator_temp_slider)
        mod_temp_layout.addWidget(self.moderator_temp_minus_btn)
        mod_temp_layout.addWidget(self.moderator_temp_plus_btn)
        mod_temp_layout.addWidget(self.moderator_temp_spinbox)
        self.moderator_temp_group.setLayout(mod_temp_layout)
        
        # Fuel Enrichment
        self.fuel_enrichment_group = self.create_info_groupbox("Enrichissement Combustible (%)", self.info_texts["fuel_enrichment"])
        fuel_enrich_layout = QHBoxLayout()
        
        self.fuel_enrichment_slider = QSlider(Qt.Orientation.Horizontal)
        self.fuel_enrichment_slider.setRange(10, 50)  # Using 10-50 for 1.0-5.0
        self.fuel_enrichment_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.fuel_enrichment_slider.setTickInterval(5)
        
        self.fuel_enrichment_spinbox = QDoubleSpinBox()
        self.fuel_enrichment_spinbox.setRange(1.0, 5.0)
        self.fuel_enrichment_spinbox.setDecimals(1)
        self.fuel_enrichment_spinbox.setSingleStep(0.1)
        self.fuel_enrichment_spinbox.setSuffix(" %")
        self.fuel_enrichment_spinbox.setMinimumWidth(80)
        
        # Boutons d'ajustement pour enrichissement (pas de 0.1%)
        self.fuel_enrichment_plus_btn = QPushButton("+0.1")
        self.fuel_enrichment_plus_btn.setMaximumWidth(40)
        self.fuel_enrichment_plus_btn.setToolTip("Augmenter enrichissement (+0.1%)")
        self.fuel_enrichment_minus_btn = QPushButton("-0.1")
        self.fuel_enrichment_minus_btn.setMaximumWidth(40)
        self.fuel_enrichment_minus_btn.setToolTip("Diminuer enrichissement (-0.1%)")
        
        fuel_enrich_layout.addWidget(self.fuel_enrichment_slider)
        fuel_enrich_layout.addWidget(self.fuel_enrichment_minus_btn)
        fuel_enrich_layout.addWidget(self.fuel_enrichment_plus_btn)
        fuel_enrich_layout.addWidget(self.fuel_enrichment_spinbox)
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
        control_layout.addWidget(self.presets_group)
        control_layout.addWidget(self.rod_R_group)
        control_layout.addWidget(self.rod_GCP_group)
        control_layout.addWidget(self.boron_group)
        control_layout.addWidget(self.moderator_temp_group)
        control_layout.addWidget(self.fuel_enrichment_group)
        control_layout.addWidget(self.reactor_params_group)
        control_layout.addStretch(1)

        return control_panel
    
    def create_info_groupbox(self, title, info_text):
        """Aide pour créer une boîte de groupe avec capacités d'information"""
        group_box = InfoGroupBox(title, info_text, self.info_manager)
        return group_box

    def _show_info_dialog(self):
        """Toggle the info dialog - show if closed, close if open. Only opens if there's content to show."""
        # If dialog is open, close it
        if self.info_dialog and self.info_dialog.isVisible():
            self.info_dialog.close()
            self.info_dialog = None
            return
            
        # Check if there's actual content to show
        current_html = self.info_panel.get_current_info_html()
        current_text = self.info_panel.get_current_info_text()
        
        # Don't open dialog if there's no meaningful content
        if not current_text or not current_text.strip():
            return
            
        # If dialog is closed or doesn't exist, open it with content
        self.info_dialog = InfoDialog(
            "Informations Détaillées",
            current_html,
            self
        )
        
        # Connect close event to cleanup
        self.info_dialog.finished.connect(self._on_info_dialog_closed)
        
        # Show the dialog non-modal so user can interact with the main window
        self.info_dialog.show()
    
    def _on_info_dialog_closed(self):
        """Clean up when info dialog is closed."""
        self.info_dialog = None
    
    def reset_to_selected_preset(self):
        """Reset tous les paramètres au preset actuellement sélectionné dans le combo"""
        selected_preset = self.preset_combo.currentText()
        if selected_preset and selected_preset != "Personnalisé":
            # Appliquer le preset sélectionné
            config = self.controller.apply_preset(selected_preset)
            if config:
                self.update_ui_from_preset(config)
    
    def update_reset_button_state(self):
        """Met à jour l'état du bouton Reset selon si l'état actuel correspond au preset sélectionné"""
        selected_preset = self.preset_combo.currentText()
        current_preset = self.controller.get_current_preset_name()
        
        # Le bouton est activé seulement si :
        # 1. Un preset non-personnalisé est sélectionné ET
        # 2. L'état actuel ne correspond pas au preset sélectionné
        should_enable = (selected_preset and 
                        selected_preset != "Personnalisé" and
                        current_preset != selected_preset)
        
        self.reset_preset_button.setEnabled(should_enable)
    
    def on_preset_changed(self, preset_name):
        """Handle preset change from the combobox"""
        if preset_name == "Personnalisé":
            # Mettre à jour l'état du bouton quand on passe en mode personnalisé
            self.update_reset_button_state()
            return
            
        config = self.controller.apply_preset(preset_name)
        if config:
            self.update_ui_from_preset(config)
            # Mettre à jour l'état du bouton après avoir appliqué le preset
            self.update_reset_button_state()
            
    def update_ui_from_preset(self, config):
        """Update all UI controls from a preset configuration"""
        # Block signals to prevent feedback loops
        self.rod_R_slider.blockSignals(True)
        self.rod_R_spinbox.blockSignals(True)
        self.rod_GCP_slider.blockSignals(True)
        self.rod_GCP_spinbox.blockSignals(True)
        self.boron_slider.blockSignals(True)
        self.boron_spinbox.blockSignals(True)
        self.moderator_temp_slider.blockSignals(True)
        self.moderator_temp_spinbox.blockSignals(True)
        self.fuel_enrichment_slider.blockSignals(True)
        self.fuel_enrichment_spinbox.blockSignals(True)

        # Update rod group controls
        # Inverser les valeurs pour les sliders : 0 pas → slider=228, 228 pas → slider=0
        inverted_R_slider = 228 - int(config["rod_group_R_position"])
        inverted_GCP_slider = 228 - int(config["rod_group_GCP_position"])
        
        self.rod_R_slider.setValue(inverted_R_slider)
        self.rod_R_spinbox.setValue(config["rod_group_R_position"])
        
        self.rod_GCP_slider.setValue(inverted_GCP_slider)
        self.rod_GCP_spinbox.setValue(config["rod_group_GCP_position"])
        
        self.boron_slider.setValue(int(config["boron_concentration"]))
        self.boron_spinbox.setValue(config["boron_concentration"])
        
        self.moderator_temp_slider.setValue(int(config["average_temperature"]))
        self.moderator_temp_spinbox.setValue(config["average_temperature"])
        
        self.fuel_enrichment_slider.setValue(int(config["fuel_enrichment"] * 10))
        self.fuel_enrichment_spinbox.setValue(config["fuel_enrichment"])

        # Unblock signals
        self.rod_R_slider.blockSignals(False)
        self.rod_R_spinbox.blockSignals(False)
        self.rod_GCP_slider.blockSignals(False)
        self.rod_GCP_spinbox.blockSignals(False)
        self.boron_slider.blockSignals(False)
        self.boron_spinbox.blockSignals(False)
        self.moderator_temp_slider.blockSignals(False)
        self.moderator_temp_spinbox.blockSignals(False)
        self.fuel_enrichment_slider.blockSignals(False)
        self.fuel_enrichment_spinbox.blockSignals(False)
        
        # Update reactor parameters and visualizations
        self.update_reactor_params(config["reactor_params"])
        self.update_visualizations()
        self.check_for_custom_preset()
    
    def check_for_custom_preset(self):
        """Check if current settings match a preset, otherwise set to 'Personnalisé'."""
        current_preset_name = self.controller.get_current_preset_name()
        if self.preset_combo.currentText() != current_preset_name:
            self.preset_combo.setCurrentText(current_preset_name)
        
        # Mettre à jour l'état du bouton Reset
        self.update_reset_button_state()

    def _update_parameter_and_ui(self, controller_method, value, label_update_func=None):
        """Méthode générique pour mettre à jour un paramètre et l'interface
        
        Args:
            controller_method: Méthode du contrôleur à appeler
            value: Valeur à passer à la méthode
            label_update_func: Fonction optionnelle pour mettre à jour un label
        """
        # Mettre à jour l'affichage si nécessaire
        if label_update_func:
            label_update_func()
            
        # Mettre à jour le modèle via le contrôleur
        params = controller_method(float(value))
        
        # Mettre à jour l'interface
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()

    # Nouvelles méthodes pour les groupes de barres
    def on_rod_R_slider_changed(self, value):
        """Handle R group slider change"""
        # Inverser la valeur du slider : slider=0 → 228 pas (extrait), slider=228 → 0 pas (inséré)
        inverted_value = 228 - value
        
        self.rod_R_spinbox.blockSignals(True)
        self.rod_R_spinbox.setValue(inverted_value)
        self.rod_R_spinbox.blockSignals(False)
        
        # Update the model via the controller
        params = self.controller.update_rod_group_R_position(inverted_value)
        
        # Update the interface
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()
    
    def on_rod_R_spinbox_changed(self, value):
        """Handle R group spinbox change"""
        # Inverser la valeur pour le slider : 0 pas → slider=228, 228 pas → slider=0
        inverted_slider_value = 228 - int(value)
        
        self.rod_R_slider.blockSignals(True)
        self.rod_R_slider.setValue(inverted_slider_value)
        self.rod_R_slider.blockSignals(False)
        
        # Update the model via the controller
        params = self.controller.update_rod_group_R_position(value)
        
        # Update the interface
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()
    
    def adjust_rod_R(self, step):
        """Adjust R group position by step amount"""
        current_value = self.rod_R_spinbox.value()
        new_value = max(0, min(228, current_value + step))
        self.rod_R_spinbox.setValue(new_value)
    
    def on_rod_GCP_slider_changed(self, value):
        """Handle GCP group slider change"""
        # Inverser la valeur du slider : slider=0 → 228 pas (extrait), slider=228 → 0 pas (inséré)
        inverted_value = 228 - value
        
        self.rod_GCP_spinbox.blockSignals(True)
        self.rod_GCP_spinbox.setValue(inverted_value)
        self.rod_GCP_spinbox.blockSignals(False)
        
        # Update the model via the controller
        params = self.controller.update_rod_group_GCP_position(inverted_value)
        
        # Update the interface
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()
    
    def on_rod_GCP_spinbox_changed(self, value):
        """Handle GCP group spinbox change"""
        # Inverser la valeur pour le slider : 0 pas → slider=228, 228 pas → slider=0
        inverted_slider_value = 228 - int(value)
        
        self.rod_GCP_slider.blockSignals(True)
        self.rod_GCP_slider.setValue(inverted_slider_value)
        self.rod_GCP_slider.blockSignals(False)
        
        # Update the model via the controller
        params = self.controller.update_rod_group_GCP_position(value)
        
        # Update the interface
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()
    
    def adjust_rod_GCP(self, step):
        """Adjust GCP group position by step amount"""
        current_value = self.rod_GCP_spinbox.value()
        new_value = max(0, min(228, current_value + step))
        self.rod_GCP_spinbox.setValue(new_value)

    def on_boron_slider_changed(self, value):
        """Met à jour le spinbox depuis le slider."""
        self.boron_spinbox.blockSignals(True)
        self.boron_spinbox.setValue(float(value))
        self.boron_spinbox.blockSignals(False)
        
        # Update the model via the controller
        params = self.controller.update_boron_concentration(float(value))
        
        # Update the interface
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()
        
    def on_boron_spinbox_changed(self, value):
        """Met à jour le slider depuis le spinbox."""
        self.boron_slider.blockSignals(True)
        self.boron_slider.setValue(int(value))
        self.boron_slider.blockSignals(False)

        # Update the model via the controller
        params = self.controller.update_boron_concentration(float(value))
        
        # Update the interface
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()

    def adjust_boron(self, step):
        """Adjust boron concentration by step amount"""
        current_value = self.boron_spinbox.value()
        new_value = max(0, min(2000, current_value + step))
        self.boron_spinbox.setValue(new_value)


    def on_moderator_temp_slider_changed(self, value):
        """Handle moderator temperature slider change"""
        self.moderator_temp_spinbox.blockSignals(True)
        self.moderator_temp_spinbox.setValue(float(value))
        self.moderator_temp_spinbox.blockSignals(False)
        
        # Update the model via the controller
        params = self.controller.update_average_temperature(float(value))
        
        # Update the interface
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()
        
    def on_moderator_temp_spinbox_changed(self, value):
        """Handle moderator temperature spinbox change"""
        self.moderator_temp_slider.blockSignals(True)
        self.moderator_temp_slider.setValue(int(value))
        self.moderator_temp_slider.blockSignals(False)
        
        # Update the model via the controller
        params = self.controller.update_average_temperature(float(value))
        
        # Update the interface
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()

    def adjust_moderator_temp(self, step):
        """Adjust moderator temperature by step amount"""
        current_value = self.moderator_temp_spinbox.value()
        new_value = max(280, min(350, current_value + step))
        self.moderator_temp_spinbox.setValue(new_value)

    def on_fuel_enrichment_slider_changed(self, value):
        """Handle fuel enrichment slider change"""
        enrichment = value / 10.0
        self.fuel_enrichment_spinbox.blockSignals(True)
        self.fuel_enrichment_spinbox.setValue(enrichment)
        self.fuel_enrichment_spinbox.blockSignals(False)
        
        # Update the model via the controller
        params = self.controller.update_fuel_enrichment(enrichment)
        
        # Update the interface
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()
        
    def on_fuel_enrichment_spinbox_changed(self, value):
        """Handle fuel enrichment spinbox change"""
        slider_value = int(value * 10)
        self.fuel_enrichment_slider.blockSignals(True)
        self.fuel_enrichment_slider.setValue(slider_value)
        self.fuel_enrichment_slider.blockSignals(False)
        
        # Update the model via the controller
        params = self.controller.update_fuel_enrichment(value)
        
        # Update the interface
        self.update_reactor_params(params)
        self.update_visualizations()
        self.check_for_custom_preset()

    def adjust_fuel_enrichment(self, step):
        """Adjust fuel enrichment by step amount"""
        current_value = self.fuel_enrichment_spinbox.value()
        new_value = max(1.0, min(5.0, current_value + step))
        self.fuel_enrichment_spinbox.setValue(new_value)

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
        # Clear xenon plot history
        self.visualization_panel.xenon_widget.clear_history()
        self.check_for_custom_preset()
    


    def update_reactor_params(self, params):
        """Update the display of reactor parameters"""
        k_eff = params["k_effective"]
        reactivity_pcm = params["reactivity"] * 100000
        doubling_time = params["doubling_time"]
        
        self.k_effective_label.setText(f"k-eff: {k_eff:.2f}")
        self.reactivity_label.setText(f"Réactivité (pcm): {reactivity_pcm:.1f}")
        
        if doubling_time == float('inf'):
            self.doubling_time_label.setText("Temps de doublement: ∞")
        else:
            self.doubling_time_label.setText(f"Temps de doublement: {doubling_time:.1f} s")
            
    def update_visualizations(self):
        """Update all plots with the latest data from the model"""
        # Axial Flux - utiliser la position équivalente calculée par le modèle
        height, flux = self.controller.get_axial_flux_distribution()
        # La position équivalente est déjà calculée par le modèle
        equivalent_position = self.controller.model._get_equivalent_rod_position_percent()
        self.visualization_panel.update_flux_plot(height, flux, equivalent_position)
        
        # Four Factors
        factors_data = self.controller.get_four_factors_data()
        self.visualization_panel.update_factors_plot(factors_data)
        
        # Neutron Balance
        balance_data = self.controller.get_neutron_balance_data()
        self.visualization_panel.update_neutron_balance_plot(balance_data)
        
        # Neutron Cycle
        cycle_data = self.controller.get_neutron_cycle_data()
        self.visualization_panel.update_neutron_cycle_plot(cycle_data)
        
        # Xenon Dynamics
        xenon_data = self.controller.get_xenon_dynamics_data()
        self.visualization_panel.update_xenon_plot(xenon_data)

    def keyPressEvent(self, event):
        """Handle key press events for the main window"""
        if event.key() == Qt.Key.Key_I:
            self._show_info_dialog()
        
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Ensure proper cleanup on close"""
        # Unregister all widgets to prevent issues on shutdown
        if self.info_manager:
            widgets_to_unregister = list(self.info_manager.get_registered_widgets().keys())
            for widget in widgets_to_unregister:
                self.info_manager.unregister_widget(widget)
        
        super().closeEvent(event) 