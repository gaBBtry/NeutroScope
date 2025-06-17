"""
Visualization components for the reactor simulation
"""
import matplotlib
matplotlib.use('QtAgg')  # Use QtAgg backend for PyQt6
import numpy as np
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, 
    QPushButton, QToolButton, QSizePolicy, QSpacerItem,
    QDialog, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from .widgets.flux_plot import FluxDistributionPlot
from .widgets.four_factors_plot import FourFactorsPlot
from .widgets.neutron_balance_plot import NeutronBalancePlot
from .widgets.pilotage_diagram_plot import PilotageDiagramPlot
from .widgets.info_panel import InfoPanel
from .widgets.info_button import InfoButton


class VisualizationPanel(QWidget):
    """
    Main panel that holds all the visualization plots and info panel
    """
    
    def __init__(self, parent=None, use_info_panel=True):
        super().__init__(parent)
        
        self.use_info_panel = use_info_panel
        self.external_info_manager = None
        
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Create a grid for the plots
        plot_grid = QGridLayout()
        
        # Create plot widgets
        self.flux_plot = FluxDistributionPlot()
        self.factors_plot = FourFactorsPlot()
        self.balance_plot = NeutronBalancePlot()
        self.pilotage_plot = PilotageDiagramPlot()
        
        # Add plots to the grid
        plot_grid.addWidget(self.flux_plot, 0, 0)
        plot_grid.addWidget(self.factors_plot, 0, 1)
        plot_grid.addWidget(self.balance_plot, 1, 0)
        plot_grid.addWidget(self.pilotage_plot, 1, 1)

        main_layout.addLayout(plot_grid)
        
        # Information Panel (optional, can be controlled externally)
        if self.use_info_panel:
            info_container = QWidget()
            info_layout = QVBoxLayout(info_container)
            
            self.info_panel = InfoPanel()
            self.info_button = InfoButton()
            
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(self.info_button)
            
            info_layout.addLayout(button_layout)
            info_layout.addWidget(self.info_panel)
            
            main_layout.addWidget(info_container)
            
            # Connect signals
            self.info_button.clicked.connect(self.toggle_info_panel)
            self.info_panel.closed.connect(self.on_info_panel_closed)
            
            # Detailed info functionality
            self.detailed_info_text = ""
            self.info_panel.show_details.connect(self.show_detailed_info)
    
    def set_external_info_callback(self, info_manager):
        """Set an external InfoManager to use for updating info"""
        self.external_info_manager = info_manager
    
    def resizeEvent(self, event):
        """Handle resize event to adjust layout"""
        # This can be used to switch to a different layout on smaller screens
        super().resizeEvent(event)
        
    # --- Plot Update Methods ---
    def update_flux_plot(self, height, flux, rod_position):
        """Update the flux distribution plot"""
        self.flux_plot.update_plot(height, flux, rod_position)
        
    def update_factors_plot(self, factors_data):
        """Update the four factors plot"""
        self.factors_plot.update_plot(factors_data)

    def update_neutron_balance_plot(self, balance_data):
        """Update the neutron balance plot"""
        self.balance_plot.update_plot(balance_data)

    def update_pilotage_diagram_plot(self, ao_data):
        """Update the pilotage diagram plot"""
        self.pilotage_plot.update_plot(ao_data)

    # --- Info Panel Methods ---
    def update_info_panel(self, text, detailed_text=None):
        """Update the info panel with new text"""
        if hasattr(self, 'external_info_manager') and self.external_info_manager:
            # Use external info manager - this is a more complex integration
            # For now, we'll implement a simple approach
            if text:
                self.external_info_manager.info_requested.emit(text)
            else:
                self.external_info_manager.info_cleared.emit()
        elif self.use_info_panel:
            self.info_panel.update_info(text)
            if detailed_text:
                self.detailed_info_text = detailed_text

    def toggle_info_panel(self):
        """Toggle the visibility of the info panel"""
        if not self.use_info_panel: return
        
        is_visible = not self.info_panel.isVisible()
        self.info_panel.setVisible(is_visible)
        self.info_button.setChecked(is_visible)
        self.info_button.update_tooltip(is_visible)

    def on_info_panel_closed(self):
        """Handle the info panel being closed by its own button"""
        if not self.use_info_panel: return
        
        self.info_button.setChecked(False)
        self.info_button.update_tooltip(False)

    def show_detailed_info(self):
        """Show a dialog with detailed information"""
        if not self.detailed_info_text:
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Information Détaillée")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        label = QLabel(self.detailed_info_text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        scroll_area.setWidget(label)
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(dialog.accept)
        
        layout.addWidget(scroll_area)
        layout.addWidget(close_button)
        
        dialog.exec()
        
    def showEvent(self, event):
        """Focus this widget when it is shown"""
        super().showEvent(event)
        self.setFocus()

    def keyPressEvent(self, event):
        """Handle key presses for shortcuts"""
        # Toggle info panel with 'i' key
        if event.key() == Qt.Key.Key_I:
            if self.use_info_panel:
                self.toggle_info_panel()
        
        # Show detailed info with 'd' key
        if event.key() == Qt.Key.Key_D:
            self.show_detailed_info()
            
        super().keyPressEvent(event) 