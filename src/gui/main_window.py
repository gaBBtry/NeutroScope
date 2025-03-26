"""
Main window implementation for the Neutro_EDF application
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QSlider, QComboBox, QGroupBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt

from src.controller.reactor_controller import ReactorController
from src.gui.visualization import VisualizationPanel

class MainWindow(QMainWindow):
    """Main application window with control panel and visualization area"""
    
    def __init__(self):
        super().__init__()
        
        # Create controller
        self.controller = ReactorController()
        
        self.setWindowTitle("Simulation Neutronique des REP")
        self.setMinimumSize(1200, 800)
        
        # Create the central widget and main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        
        # Create control panel (left side)
        control_panel = self.create_control_panel()
        
        # Create visualization area (right side)
        self.visualization_panel = VisualizationPanel()
        visualization_container = self.create_visualization_area()
        
        # Add both panels to the main layout
        main_layout.addWidget(control_panel, 1)  # 1/3 of window width
        main_layout.addWidget(visualization_container, 2)  # 2/3 of window width
        
        self.setCentralWidget(central_widget)
        
        # Initialize visualizations with current data
        self.update_visualizations()
    
    def create_control_panel(self):
        """Create the left control panel with parameter controls"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Difficulty level selector
        difficulty_group = QGroupBox("Niveau de difficulté")
        difficulty_layout = QVBoxLayout(difficulty_group)
        
        self.difficulty_selector = QComboBox()
        self.difficulty_selector.addItems(["Débutant", "Intermédiaire", "Expert"])
        difficulty_layout.addWidget(self.difficulty_selector)
        
        layout.addWidget(difficulty_group)
        
        # Control parameters
        control_group = QGroupBox("Paramètres de contrôle")
        control_layout = QVBoxLayout(control_group)
        
        # Control rod position
        rod_layout = QVBoxLayout()
        rod_label = QLabel("Position des barres de contrôle:")
        self.rod_slider = QSlider(Qt.Orientation.Horizontal)
        self.rod_slider.setMinimum(0)
        self.rod_slider.setMaximum(100)
        self.rod_value = QLabel("0%")
        self.rod_slider.valueChanged.connect(self.on_rod_position_changed)
        
        rod_layout.addWidget(rod_label)
        rod_layout.addWidget(self.rod_slider)
        rod_layout.addWidget(self.rod_value)
        
        # Boron concentration
        boron_layout = QVBoxLayout()
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
        
        boron_layout.addWidget(boron_label)
        boron_layout.addWidget(self.boron_slider)
        boron_layout.addLayout(boron_value_layout)
        
        control_layout.addLayout(rod_layout)
        control_layout.addLayout(boron_layout)
        
        layout.addWidget(control_group)
        
        # Physical parameters
        physics_group = QGroupBox("Paramètres physiques")
        physics_layout = QVBoxLayout(physics_group)
        
        # Temperature
        temp_mod_layout = QVBoxLayout()
        temp_mod_label = QLabel("Température du modérateur (°C):")
        self.temp_mod_spin = QDoubleSpinBox()
        self.temp_mod_spin.setRange(280, 350)
        self.temp_mod_spin.setValue(310)
        self.temp_mod_spin.valueChanged.connect(self.on_moderator_temperature_changed)
        
        temp_mod_layout.addWidget(temp_mod_label)
        temp_mod_layout.addWidget(self.temp_mod_spin)
        
        # Fuel enrichment
        enrich_layout = QVBoxLayout()
        enrich_label = QLabel("Enrichissement du combustible (%):")
        self.enrich_spin = QDoubleSpinBox()
        self.enrich_spin.setRange(1.0, 5.0)
        self.enrich_spin.setValue(3.5)
        self.enrich_spin.setSingleStep(0.1)
        self.enrich_spin.valueChanged.connect(self.on_fuel_enrichment_changed)
        
        enrich_layout.addWidget(enrich_label)
        enrich_layout.addWidget(self.enrich_spin)
        
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
        self.params_group = QGroupBox("Paramètres du réacteur")
        params_layout = QVBoxLayout(self.params_group)
        
        self.neutron_rate = QLabel("Taux de neutrons retardés: 0.0065")
        self.doubling_time = QLabel("Temps de doublement: N/A")
        self.reactivity = QLabel("Réactivité (ρ): 0.000")
        self.k_effective = QLabel("k-effectif: 1.000")
        
        params_layout.addWidget(self.neutron_rate)
        params_layout.addWidget(self.doubling_time)
        params_layout.addWidget(self.reactivity)
        params_layout.addWidget(self.k_effective)
        
        layout.addWidget(self.params_group)
        
        # Add visualization panel
        layout.addWidget(self.visualization_panel)
        
        return panel
    
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