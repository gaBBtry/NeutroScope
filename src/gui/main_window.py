"""
Main window implementation for the Neutro_EDF application
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QSlider, QComboBox, QGroupBox, QDoubleSpinBox,
    QToolButton, QDialog, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QEnterEvent, QFont

from src.controller.reactor_controller import ReactorController
from src.gui.visualization import (
    VisualizationPanel, InfoPanel, InfoButton
)


class InfoItem(QWidget):
    """
    Mixin class to add hover information capability to any widget
    """
    # Signal to send info to the info panel
    info_signal = pyqtSignal(str)
    
    def __init__(self, parent=None, info_text=""):
        super().__init__(parent)
        self.info_text = info_text
        self.setMouseTracking(True)
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Filter events to detect mouse hover"""
        if event.type() == QEvent.Type.Enter:
            # Mouse entered widget
            self.send_info()
        elif event.type() == QEvent.Type.Leave:
            # Mouse left widget
            self.clear_info()
        return super().eventFilter(obj, event)
    
    def send_info(self):
        """Send info text to the panel"""
        self.info_signal.emit(self.info_text)
    
    def clear_info(self):
        """Clear info panel"""
        self.info_signal.emit("")
    
    def set_info_text(self, text):
        """Set the information text for this widget"""
        self.info_text = text


class InfoGroupBox(QGroupBox):
    """GroupBox with hover information capability"""
    
    info_signal = pyqtSignal(str)
    
    def __init__(self, title, info_text="", parent=None):
        super().__init__(title, parent)
        self.info_text = info_text
        self.setMouseTracking(True)
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Filter events to detect mouse hover"""
        if event.type() == QEvent.Type.Enter:
            # Mouse entered widget
            self.send_info()
        elif event.type() == QEvent.Type.Leave:
            # Mouse left widget
            self.clear_info()
        return super().eventFilter(obj, event)
    
    def send_info(self):
        """Send info text to the panel"""
        self.info_signal.emit(self.info_text)
    
    def clear_info(self):
        """Clear info panel"""
        self.info_signal.emit("")
    
    def set_info_text(self, text):
        """Set the information text for this widget"""
        self.info_text = text


class CreditsButton(QToolButton):
    """Button to show the credits dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("©")  # Unicode copyright symbol
        self.setToolTip("Afficher les crédits")
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)
        self.setStyleSheet("""
            QToolButton { 
                border: 1px solid #ddd; 
                border-radius: 4px;
                padding: 5px; 
                background-color: #f8f8f8;
                color: #888;
            }
            QToolButton:hover { 
                background-color: #e6e6e6; 
                color: #444;
            }
        """)
        self.setFixedSize(30, 30)
        self.clicked.connect(self.show_credits)
        
    def show_credits(self):
        """Show the credits dialog"""
        dialog = QDialog(self.parent())
        dialog.setWindowTitle("Crédits")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel("Simulation Neutronique des REP")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        credits = QLabel(
            "© 2023-2024 EDF UFPI\n\n"
            "Développé pour la formation et l'apprentissage\n"
            "des principes de la neutronique des réacteurs.\n\n"
            "Version: alpha 0.1"
        )
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits.setWordWrap(True)
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(dialog.accept)
        
        layout.addWidget(title)
        layout.addWidget(credits)
        layout.addWidget(close_button)
        
        dialog.exec()


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
        visualization_container = self.create_visualization_area()
        
        # Add both containers to the main layout
        main_layout.addWidget(left_container, 1)  # 1/3 of window width
        main_layout.addWidget(visualization_container, 2)  # 2/3 of window width
        
        self.setCentralWidget(central_widget)
        
        # Hide info panel by default
        self.info_panel.hide()
        
        # Initialize visualizations with current data
        self.update_visualizations()
    
    def create_control_panel(self):
        """Create the left control panel with parameter controls"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Control parameters
        control_group = QGroupBox("Paramètres de contrôle")
        control_layout = QVBoxLayout(control_group)
        
        # Control rod position
        rod_layout = QVBoxLayout()
        rod_container = self.create_info_widget(self.info_texts["rod_control"])
        rod_container_layout = QVBoxLayout(rod_container)
        
        rod_label = QLabel("Position des barres de contrôle:")
        self.rod_slider = QSlider(Qt.Orientation.Horizontal)
        self.rod_slider.setMinimum(0)
        self.rod_slider.setMaximum(100)
        self.rod_value = QLabel("0%")
        self.rod_slider.valueChanged.connect(self.on_rod_position_changed)
        
        rod_container_layout.addWidget(rod_label)
        rod_container_layout.addWidget(self.rod_slider)
        rod_container_layout.addWidget(self.rod_value)
        rod_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Connect info signal
        rod_container.info_signal.connect(self.show_info)
        
        rod_layout.addWidget(rod_container)
        
        # Boron concentration
        boron_layout = QVBoxLayout()
        boron_container = self.create_info_widget(self.info_texts["boron"])
        boron_container_layout = QVBoxLayout(boron_container)
        
        boron_label = QLabel("Concentration en bore (ppm):")
        
        # Add slider for boron
        self.boron_slider = QSlider(Qt.Orientation.Horizontal)
        self.boron_slider.setMinimum(0)
        self.boron_slider.setMaximum(2000)
        self.boron_slider.setValue(500)
        self.boron_slider.valueChanged.connect(self.on_boron_slider_changed)
        
        # Create horizontal layout for the boron value display and spinbox
        boron_value_layout = QHBoxLayout()
        self.boron_value = QLabel("500 ppm")
        
        # Keep the spinbox for precise control
        self.boron_spin = QDoubleSpinBox()
        self.boron_spin.setRange(0, 2000)
        self.boron_spin.setValue(500)
        self.boron_spin.valueChanged.connect(self.on_boron_spinbox_changed)
        
        boron_value_layout.addWidget(self.boron_value)
        boron_value_layout.addWidget(self.boron_spin)
        
        boron_container_layout.addWidget(boron_label)
        boron_container_layout.addWidget(self.boron_slider)
        boron_container_layout.addLayout(boron_value_layout)
        boron_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Connect info signal
        boron_container.info_signal.connect(self.show_info)
        
        boron_layout.addWidget(boron_container)
        
        control_layout.addLayout(rod_layout)
        control_layout.addLayout(boron_layout)
        
        layout.addWidget(control_group)
        
        # Physical parameters
        physics_group = QGroupBox("Paramètres physiques")
        physics_layout = QVBoxLayout(physics_group)
        
        # Temperature
        temp_mod_layout = QVBoxLayout()
        temp_container = self.create_info_widget(self.info_texts["moderator_temp"])
        temp_container_layout = QVBoxLayout(temp_container)
        
        temp_mod_label = QLabel("Température du modérateur (°C):")
        self.temp_mod_spin = QDoubleSpinBox()
        self.temp_mod_spin.setRange(280, 350)
        self.temp_mod_spin.setValue(310)
        self.temp_mod_spin.valueChanged.connect(self.on_moderator_temperature_changed)
        
        temp_container_layout.addWidget(temp_mod_label)
        temp_container_layout.addWidget(self.temp_mod_spin)
        temp_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Connect info signal
        temp_container.info_signal.connect(self.show_info)
        
        temp_mod_layout.addWidget(temp_container)
        
        # Fuel enrichment
        enrich_layout = QVBoxLayout()
        enrich_container = self.create_info_widget(self.info_texts["fuel_enrichment"])
        enrich_container_layout = QVBoxLayout(enrich_container)
        
        enrich_label = QLabel("Enrichissement du combustible (%):")
        self.enrich_spin = QDoubleSpinBox()
        self.enrich_spin.setRange(1.0, 5.0)
        self.enrich_spin.setValue(3.5)
        self.enrich_spin.setSingleStep(0.1)
        self.enrich_spin.valueChanged.connect(self.on_fuel_enrichment_changed)
        
        enrich_container_layout.addWidget(enrich_label)
        enrich_container_layout.addWidget(self.enrich_spin)
        enrich_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Connect info signal
        enrich_container.info_signal.connect(self.show_info)
        
        enrich_layout.addWidget(enrich_container)
        
        physics_layout.addLayout(temp_mod_layout)
        physics_layout.addLayout(enrich_layout)
        
        layout.addWidget(physics_group)
        
        # Add stretch to push controls to the top
        layout.addStretch(1)
        
        return panel
    
    def create_visualization_area(self):
        """Create the right visualization area"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Reactor parameters display
        self.params_group = self.create_info_groupbox("Paramètres du réacteur", 
                                                     self.info_texts["reactor_params"])
        params_layout = QVBoxLayout(self.params_group)
        
        self.neutron_rate = QLabel("Taux de neutrons retardés: 0.0065")
        self.doubling_time = QLabel("Temps de doublement: N/A")
        self.reactivity = QLabel("Réactivité (ρ): 0.000")
        self.k_effective = QLabel("k-effectif: 1.000")
        
        params_layout.addWidget(self.neutron_rate)
        params_layout.addWidget(self.doubling_time)
        params_layout.addWidget(self.reactivity)
        params_layout.addWidget(self.k_effective)
        
        # Connect info signal
        self.params_group.info_signal.connect(self.show_info)
        
        layout.addWidget(self.params_group)
        
        # Add visualization panel
        layout.addWidget(self.visualization_panel)
        
        return panel
    
    def create_info_widget(self, info_text):
        """Create a widget with info text capability"""
        widget = InfoItem(info_text=info_text)
        return widget
    
    def create_info_groupbox(self, title, info_text):
        """Create a groupbox with info text capability"""
        groupbox = InfoGroupBox(title, info_text)
        return groupbox
    
    def show_info(self, text):
        """Show information in the info panel"""
        self.info_panel.update_info(text)
        # Only show the panel if auto_show is enabled
        if text and not self.info_panel.isVisible() and self.auto_show_info:
            self.info_panel.show()
            self.info_button.update_tooltip(True)
    
    def toggle_info_panel(self):
        """Toggle visibility of info panel"""
        if self.info_panel.isVisible():
            self.info_panel.hide()
            self.auto_show_info = False
            self.info_button.update_tooltip(False)
        else:
            self.info_panel.show()
            self.auto_show_info = True
            self.info_button.update_tooltip(True)
    
    def on_info_panel_closed(self):
        """Handle info panel being closed"""
        self.auto_show_info = False
        self.info_button.update_tooltip(False)
    
    def on_rod_position_changed(self, value):
        """Handle changes to the control rod position slider"""
        self.rod_value.setText(f"{value}%")
        params = self.controller.update_control_rod_position(float(value))
        self.update_reactor_params(params)
        self.update_visualizations()
    
    def on_boron_slider_changed(self, value):
        """Handle changes to the boron concentration slider"""
        self.boron_value.setText(f"{value} ppm")
        self.boron_spin.setValue(value)
        params = self.controller.update_boron_concentration(float(value))
        self.update_reactor_params(params)
        self.update_visualizations()
    
    def on_boron_spinbox_changed(self, value):
        """Handle changes to the boron concentration spinbox"""
        self.boron_slider.setValue(int(value))
        # The slider's valueChanged signal will call on_boron_slider_changed
    
    def on_boron_concentration_changed(self, value):
        """Deprecated - replaced by the slider and spinbox specific handlers"""
        params = self.controller.update_boron_concentration(value)
        self.update_reactor_params(params)
        self.update_visualizations()
    
    def on_moderator_temperature_changed(self, value):
        """Handle changes to the moderator temperature spinbox"""
        params = self.controller.update_moderator_temperature(value)
        self.update_reactor_params(params)
        self.update_visualizations()
    
    def on_fuel_enrichment_changed(self, value):
        """Handle changes to the fuel enrichment spinbox"""
        params = self.controller.update_fuel_enrichment(value)
        self.update_reactor_params(params)
        self.update_visualizations()
    
    def update_reactor_params(self, params):
        """Update the reactor parameter display labels"""
        self.neutron_rate.setText(f"Taux de neutrons retardés: {params['delayed_neutron_fraction']:.6f}")
        
        if params['doubling_time'] == float('inf'):
            self.doubling_time.setText("Temps de doublement: N/A")
        else:
            self.doubling_time.setText(f"Temps de doublement: {params['doubling_time']:.1f} s")
        
        self.reactivity.setText(f"Réactivité (ρ): {params['reactivity']:.6f}")
        self.k_effective.setText(f"k-effectif: {params['k_effective']:.3f}")
    
    def update_visualizations(self):
        """Update all visualizations with current model data"""
        # Update flux plot
        height, flux = self.controller.get_axial_flux_distribution()
        self.visualization_panel.update_flux_plot(height, flux, self.rod_slider.value())
        
        # Update four factors plot
        factors_data = self.controller.get_four_factors_data()
        self.visualization_panel.update_factors_plot(factors_data)
        
        # Update neutron balance plot
        balance_data = self.controller.get_neutron_balance_data()
        self.visualization_panel.update_neutron_balance_plot(balance_data) 