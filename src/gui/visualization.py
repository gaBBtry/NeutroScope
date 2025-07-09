"""
Visualization components for the reactor simulation
"""
import matplotlib
matplotlib.use('QtAgg')  # Use QtAgg backend for PyQt6
import numpy as np
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, 
    QPushButton, QToolButton, QSizePolicy, QSpacerItem,
    QDialog, QScrollArea, QGridLayout, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from .widgets.flux_plot import FluxDistributionPlot
from .widgets.four_factors_plot import FourFactorsPlot
from .widgets.neutron_balance_plot import NeutronBalancePlot
from .widgets.info_panel import InfoPanel

from .widgets.neutron_cycle_plot import NeutronCyclePlot
from .widgets.xenon_plot import XenonVisualizationWidget
from .widgets.info_manager import InfoManager


class VisualizationPanel(QWidget):
    """
    Main panel for data visualization, containing multiple plots in a tabbed view.
    """
    def __init__(self, info_manager: InfoManager, parent=None):
        super().__init__(parent)
        self.info_manager = info_manager
        self.setup_ui()

    def setup_ui(self):
        """Create and arrange widgets for the visualization panel."""
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        # Create plot widgets, passing the info_manager instance
        self.neutron_cycle_plot = NeutronCyclePlot(info_manager=self.info_manager)
        self.flux_plot = FluxDistributionPlot(info_manager=self.info_manager)
        self.factors_plot = FourFactorsPlot(info_manager=self.info_manager)
        self.neutron_balance_plot = NeutronBalancePlot(info_manager=self.info_manager)
        self.xenon_widget = XenonVisualizationWidget(info_manager=self.info_manager)
        
        # Create a container widget for factors and balance plots
        analysis_tab = QWidget()
        analysis_layout = QHBoxLayout(analysis_tab)
        analysis_layout.addWidget(self.factors_plot)
        analysis_layout.addWidget(self.neutron_balance_plot)

        # Add plots to tabs
        self.tabs.addTab(self.neutron_cycle_plot, "Cycle Neutronique")
        self.tabs.addTab(self.flux_plot, "Flux Axial")
        self.tabs.addTab(analysis_tab, "Analyse Neutronique")
        self.tabs.addTab(self.xenon_widget, "Dynamique Xénon")
        
        layout.addWidget(self.tabs)

    def resizeEvent(self, event):
        """Handle resize event to adjust layout"""
        # This can be used to switch to a different layout on smaller screens
        super().resizeEvent(event)
        
    # --- Plot Update Methods ---
    def update_flux_plot(self, height, flux, rod_pos):
        """Update the axial flux distribution plot."""
        self.flux_plot.update_plot(height, flux, rod_pos)

    def update_factors_plot(self, data):
        """Update the four factors plot."""
        self.factors_plot.update_plot(data)

    def update_neutron_balance_plot(self, data):
        """Update the neutron balance plot."""
        self.neutron_balance_plot.update_plot(data)
        


    def update_neutron_cycle_plot(self, data):
        """Update the neutron cycle plot."""
        self.neutron_cycle_plot.update_data(data)

    def update_xenon_plot(self, data):
        """Update the xenon dynamics plot."""
        self.xenon_widget.update_data(data)

    def get_xenon_controls(self):
        """Get reference to xenon control widget for signal connections."""
        return self.xenon_widget.controls

    # --- Info Panel Methods ---
    def get_info_manager(self):
        return self.info_manager 