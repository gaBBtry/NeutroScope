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
from .widgets.pilotage_diagram_plot import PilotageDiagramPlot
from .widgets.info_panel import InfoPanel
from .widgets.info_button import InfoButton
from .widgets.neutron_cycle_plot import NeutronCyclePlot


class VisualizationPanel(QWidget):
    """
    Main panel for data visualization, containing multiple plots in a tabbed view.
    """
    def __init__(self, use_info_panel=True, parent=None):
        super().__init__(parent)
        self.use_info_panel = use_info_panel
        self.external_info_callback = None
        self.setup_ui()

    def set_external_info_callback(self, info_manager):
        """Set the callback for sending info updates to an external manager."""
        self.external_info_callback = info_manager
        
        # Pass the callback to child widgets that need it
        self.flux_plot.info_manager = info_manager
        self.factors_plot.info_manager = info_manager
        self.neutron_balance_plot.info_manager = info_manager
        self.pilotage_diagram.info_manager = info_manager

    def setup_ui(self):
        """Create and arrange widgets for the visualization panel."""
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        # Create plot widgets
        self.neutron_cycle_plot = NeutronCyclePlot()
        self.flux_plot = FluxDistributionPlot()
        self.factors_plot = FourFactorsPlot()
        self.neutron_balance_plot = NeutronBalancePlot()
        self.pilotage_diagram = PilotageDiagramPlot()
        
        # Add plots to tabs
        self.tabs.addTab(self.neutron_cycle_plot, "Cycle Neutronique")
        self.tabs.addTab(self.flux_plot, "Flux Axial")
        self.tabs.addTab(self.factors_plot, "Quatre Facteurs")
        self.tabs.addTab(self.neutron_balance_plot, "Bilan Neutronique")
        self.tabs.addTab(self.pilotage_diagram, "Diagramme de Pilotage")
        
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
        
    def update_pilotage_diagram_plot(self, data):
        """Update the pilotage diagram plot."""
        self.pilotage_diagram.update_plot(data)

    def update_neutron_cycle_plot(self, data):
        """Update the neutron cycle plot."""
        self.neutron_cycle_plot.update_data(data)

    # --- Info Panel Methods ---
    def update_info_panel(self, text, detailed_text=None):
        """Update the info panel with new text"""
        if hasattr(self, 'external_info_callback') and self.external_info_callback:
            # Use external info manager - this is a more complex integration
            # For now, we'll implement a simple approach
            if text:
                self.external_info_callback.info_requested.emit(text)
            else:
                self.external_info_callback.info_cleared.emit()
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

    def get_info_manager(self):
        return self.external_info_callback 