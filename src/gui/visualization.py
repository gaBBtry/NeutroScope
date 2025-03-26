"""
Visualization components for the reactor simulation
"""
import matplotlib
matplotlib.use('QtAgg')  # Use QtAgg backend for PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, 
    QPushButton, QToolButton, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

class FluxDistributionPlot(FigureCanvasQTAgg):
    """Matplotlib canvas for plotting axial flux distribution"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Initial empty plot - Vertical orientation
        self.line, = self.axes.plot([], [])
        self.axes.set_ylabel('Hauteur relative du cœur')
        self.axes.set_xlabel('Flux neutronique relatif')
        self.axes.set_title('Distribution Axiale du Flux')
        self.axes.grid(True)
        self.axes.set_ylim(0, 1)  # Height from bottom to top
        self.axes.set_xlim(0, 1.1)  # Flux magnitude
        
        # Mark control rod positions - now horizontal line
        self.rod_line = self.axes.axhline(y=1, color='r', linestyle='--', alpha=0.5)
        
        # Store information for tooltip
        self.tooltip_text = ""
        
        # Connect mouse events
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('axes_leave_event', self.on_axes_leave)
        
        self.fig.tight_layout()
    
    def update_plot(self, height, flux, rod_position):
        """Update the flux distribution plot with new data"""
        # Plot with vertical orientation (flux on x-axis, height on y-axis)
        self.line.set_data(flux, height)
        
        # Update rod position line - rod comes from the top
        rod_height = 1.0 - (rod_position / 100.0)
        self.rod_line.set_ydata(rod_height)
        
        self.draw()
    
    def on_mouse_move(self, event):
        """Handle mouse movement to update tooltip info"""
        if event.inaxes != self.axes:
            return
        
        # Generate information about the current mouse position
        if 0 <= event.ydata <= 1 and 0 <= event.xdata <= 1.1:
            height = f"{event.ydata:.2f}"
            flux = f"{event.xdata:.2f}"
            
            self.tooltip_text = (
                "Distribution du flux neutronique\n\n"
                f"Hauteur relative: {height}\n"
                f"Flux relatif: {flux}"
            )
            
            # Emit a signal to update the info panel
            if hasattr(self.parent(), 'update_info_panel'):
                self.parent().update_info_panel(self.tooltip_text)
    
    def on_axes_leave(self, event):
        """Handle mouse leaving the axes"""
        self.tooltip_text = ""
        if hasattr(self.parent(), 'update_info_panel'):
            self.parent().update_info_panel("")


class FourFactorsPlot(FigureCanvasQTAgg):
    """Matplotlib canvas for plotting the four factors"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Initial empty plot
        self.bars = None
        self.tooltips = {}
        
        # References to plot elements that need to be cleaned up
        self.critical_line = None
        self.value_annotations = []
        
        self.axes.set_xlabel('Facteur')
        self.axes.set_ylabel('Valeur')
        self.axes.set_title('Facteurs du Cycle Neutronique')
        self.axes.grid(True, axis='y')
        
        # Connect mouse motion event
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('axes_leave_event', self.on_axes_leave)
        
        self.fig.tight_layout()
    
    def update_plot(self, factors_data):
        """Update the four factors plot with new data"""
        # Clean up previous elements first
        if self.bars is not None:
            for bar in self.bars:
                bar.remove()
        
        # Clear old value annotations
        for annotation in self.value_annotations:
            annotation.remove()
        self.value_annotations = []
        
        # Clean up old critical line
        if self.critical_line:
            self.critical_line.remove()
            self.critical_line = None
        
        # Extract data
        labels = ['η', 'ε', 'p', 'f', 'k∞', 'LT', 'LF', 'keff']
        values = [
            factors_data['eta'], 
            factors_data['epsilon'], 
            factors_data['p'], 
            factors_data['f'],
            factors_data['k_infinite'],
            factors_data['thermal_leakage'],
            factors_data['fast_leakage'],
            factors_data['k_effective']
        ]
        
        # Create French tooltips to describe each factor
        self.tooltips = {
            0: ('η', 'Facteur de reproduction', 'Neutrons produits par neutron absorbé', values[0]),
            1: ('ε', 'Facteur de fission rapide', 'Rapport des fissions totales sur les fissions thermiques', values[1]),
            2: ('p', 'Facteur antitrappe', 'Probabilité d\'échappement aux résonances', values[2]),
            3: ('f', 'Facteur d\'utilisation thermique', 'Rapport des neutrons absorbés dans le combustible aux neutrons absorbés partout', values[3]),
            4: ('k∞', 'Facteur de multiplication infini', 'Produit des quatre facteurs (η × ε × p × f)', values[4]),
            5: ('LT', 'Fuites thermiques', 'Probabilité de non-fuite pour les neutrons thermiques', values[5]),
            6: ('LF', 'Fuites rapides', 'Probabilité de non-fuite pour les neutrons rapides', values[6]),
            7: ('keff', 'Facteur de multiplication effectif', 'k∞ × LT × LF (prend en compte les fuites)', values[7])
        }
        
        # Create color map - first 4 are four factors, then k_inf, then leakage, then k_eff
        colors = ['#3498db', '#2ecc71', '#f1c40f', '#e74c3c', '#9b59b6', '#1abc9c', '#d35400', '#2c3e50']
        
        # Create bars
        self.bars = self.axes.bar(labels, values, color=colors)
        
        # Update axis limits
        self.axes.set_ylim(0, max(values) * 1.1)
        
        # Add annotations for important values
        for i, bar in enumerate(self.bars):
            if labels[i] in ['k∞', 'keff']:
                annotation = self.axes.text(i, values[i] + 0.02, f'{values[i]:.3f}', 
                               ha='center', va='bottom', fontsize=9)
                self.value_annotations.append(annotation)
        
        self.draw()
    
    def on_mouse_move(self, event):
        """Handle mouse movement over the bars to update info panel"""
        if event.inaxes != self.axes:
            return
        
        # Check if mouse is over a bar
        for i, bar in enumerate(self.bars):
            contains, _ = bar.contains(event)
            if contains:
                # Mouse is over this bar
                self.show_tooltip_in_panel(i)
                return
        
        # If not over any bar, clear the info panel
        if hasattr(self.parent(), 'update_info_panel'):
            self.parent().update_info_panel("")
    
    def on_axes_leave(self, event):
        """Handle mouse leaving the axes"""
        if hasattr(self.parent(), 'update_info_panel'):
            self.parent().update_info_panel("")
    
    def show_tooltip_in_panel(self, index):
        """Show tooltip for the bar at index in the info panel"""
        if index not in self.tooltips:
            return
        
        symbol, name, description, value = self.tooltips[index]
        
        tooltip_text = (
            f"{symbol} - {name}\n\n"
            f"{description}\n\n"
            f"Valeur: {value:.4f}"
        )
        
        # Send the text to the info panel
        if hasattr(self.parent(), 'update_info_panel'):
            self.parent().update_info_panel(tooltip_text)


class InfoPanel(QFrame):
    """Panel for displaying information about visualizations"""
    
    # Signal emitted when panel is closed
    closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setMinimumHeight(120)
        
        # Create layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create header with title and close button
        header_layout = QHBoxLayout()
        
        # Title label
        self.title_label = QLabel("Informations")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        self.title_label.setFont(title_font)
        
        # Close button
        self.close_button = QToolButton()
        self.close_button.setText("×")  # Unicode × symbol
        self.close_button.setToolTip("Fermer le panneau d'information")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.close_button.setFont(font)
        self.close_button.setStyleSheet("""
            QToolButton { 
                border: none; 
                color: #999; 
                padding: 0 5px; 
            }
            QToolButton:hover { 
                color: #333; 
            }
        """)
        self.close_button.clicked.connect(self.close_panel)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.close_button)
        
        # Info content label
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.info_label.setWordWrap(True)
        self.info_label.setTextFormat(Qt.TextFormat.RichText)
        self.info_label.setMinimumHeight(80)
        
        # Add to layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.info_label)
    
    def update_info(self, text):
        """Update the information displayed in the panel"""
        if not text:
            self.info_label.setText("")
        else:
            self.info_label.setText(text.replace("\n", "<br>"))
    
    def close_panel(self):
        """Hide the panel and emit closed signal"""
        self.hide()
        self.closed.emit()


class InfoButton(QToolButton):
    """Button to toggle the info panel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("ℹ️")  # Unicode info symbol
        self.setToolTip("Afficher le panneau d'information")
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)
        self.setStyleSheet("""
            QToolButton { 
                border: 1px solid #ddd; 
                border-radius: 4px;
                padding: 5px; 
                background-color: #f8f8f8;
            }
            QToolButton:hover { 
                background-color: #e6e6e6; 
            }
        """)
        self.setFixedSize(30, 30)


class VisualizationPanel(QWidget):
    """Panel containing all visualizations for the reactor simulation"""
    
    def __init__(self, parent=None, use_info_panel=True):
        super().__init__(parent)
        
        # Create main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create plots
        self.flux_plot = FluxDistributionPlot(self)
        self.factors_plot = FourFactorsPlot(self)
        
        # Flag to determine if we should use an internal info panel or an external one
        self.use_info_panel = use_info_panel
        
        if use_info_panel:
            # Create info panel and info button
            self.info_panel = InfoPanel(self)
            self.info_button = InfoButton(self)
            self.info_button.clicked.connect(self.toggle_info_panel)
            
            # Connect info panel closed signal
            self.info_panel.closed.connect(self.on_info_panel_closed)
            
            # Flag to control automatic showing of info panel
            self.auto_show_info = False
            
            # Create a container for plots and info button
            plots_container = QWidget()
            plots_layout = QVBoxLayout(plots_container)
            plots_layout.setContentsMargins(0, 0, 0, 0)
            
            # Add plots to plots container
            plots_layout.addWidget(self.flux_plot, 1)
            plots_layout.addWidget(self.factors_plot, 1)
            
            # Create container for info button (bottom right corner)
            btn_container = QWidget(plots_container)
            btn_container.setGeometry(0, 0, 40, 40)  # Will be repositioned in resizeEvent
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 5, 5)
            btn_layout.addStretch(1)
            btn_layout.addWidget(self.info_button)
            
            # Add plots container and info panel to main layout
            self.layout.addWidget(plots_container, 1)
            self.layout.addWidget(self.info_panel)
            
            # Hide info panel by default
            self.info_panel.hide()
        else:
            # Simpler layout without info panel
            self.layout.addWidget(self.flux_plot, 1)
            self.layout.addWidget(self.factors_plot, 1)
        
        # External callback for info events when not using internal panel
        self.external_info_callback = None
    
    def set_external_info_callback(self, callback):
        """Set an external callback for info events when not using internal panel"""
        self.external_info_callback = callback
    
    def resizeEvent(self, event):
        """Handle resize event to reposition the info button"""
        if self.use_info_panel:
            btn_container = self.info_button.parent()
            if btn_container:
                # Position in bottom right corner of plots container
                plots_container = self.layout.itemAt(0).widget()
                w, h = btn_container.width(), btn_container.height()
                btn_container.setGeometry(
                    plots_container.width() - w - 5,  # 5px margin right
                    plots_container.height() - h - 5,  # 5px margin bottom
                    w, h
                )
        super().resizeEvent(event)
    
    def update_flux_plot(self, height, flux, rod_position):
        """Update the flux distribution plot"""
        self.flux_plot.update_plot(height, flux, rod_position)
    
    def update_factors_plot(self, factors_data):
        """Update the four factors plot"""
        self.factors_plot.update_plot(factors_data)
    
    def update_info_panel(self, text):
        """Update the info panel with the provided text"""
        if self.use_info_panel:
            self.info_panel.update_info(text)
            # Only show the panel if auto_show is enabled
            if text and not self.info_panel.isVisible() and self.auto_show_info:
                self.info_panel.show()
        elif self.external_info_callback:
            # Use external callback if available
            self.external_info_callback(text)
    
    def toggle_info_panel(self):
        """Toggle visibility of info panel"""
        if not self.use_info_panel:
            return
            
        if self.info_panel.isVisible():
            self.info_panel.hide()
            self.auto_show_info = False
        else:
            self.info_panel.show()
            self.auto_show_info = True
    
    def on_info_panel_closed(self):
        """Handle info panel being closed"""
        self.auto_show_info = False 