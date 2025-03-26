"""
Visualization components for the reactor simulation
"""
import matplotlib
matplotlib.use('QtAgg')  # Use QtAgg backend for PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

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
        if self.bars is not None:
            for bar in self.bars:
                bar.remove()
        
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
        
        # Draw critical line at 1.0 for k values
        self.axes.axhline(y=1.0, color='black', linestyle='--', alpha=0.7)
        
        # Update axis limits
        self.axes.set_ylim(0, max(values) * 1.1)
        
        # Add annotations for important values
        for i, bar in enumerate(self.bars):
            if labels[i] in ['k∞', 'keff']:
                self.axes.text(i, values[i] + 0.02, f'{values[i]:.3f}', 
                               ha='center', va='bottom', fontsize=9)
        
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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setMinimumHeight(150)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Title label
        self.title_label = QLabel("Informations")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Info content label
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.info_label.setWordWrap(True)
        self.info_label.setTextFormat(Qt.TextFormat.RichText)
        self.info_label.setMinimumHeight(100)
        
        # Add to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.info_label)
    
    def update_info(self, text):
        """Update the information displayed in the panel"""
        if not text:
            self.info_label.setText("<i>Passez votre souris sur un élément pour afficher des informations...</i>")
        else:
            self.info_label.setText(text.replace("\n", "<br>"))


class VisualizationPanel(QWidget):
    """Panel containing all visualizations for the reactor simulation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create main layout
        self.layout = QVBoxLayout(self)
        
        # Create plots
        self.flux_plot = FluxDistributionPlot(self)
        self.factors_plot = FourFactorsPlot(self)
        
        # Create info panel
        self.info_panel = InfoPanel(self)
        
        # Add plots to layout
        self.layout.addWidget(self.flux_plot, 3)  # 3/8 of space
        self.layout.addWidget(self.factors_plot, 3)  # 3/8 of space
        self.layout.addWidget(self.info_panel, 2)  # 2/8 of space
        
        # Initialize info panel with default text
        self.update_info_panel("")
    
    def update_flux_plot(self, height, flux, rod_position):
        """Update the flux distribution plot"""
        self.flux_plot.update_plot(height, flux, rod_position)
    
    def update_factors_plot(self, factors_data):
        """Update the four factors plot"""
        self.factors_plot.update_plot(factors_data)
    
    def update_info_panel(self, text):
        """Update the info panel with the provided text"""
        self.info_panel.update_info(text) 