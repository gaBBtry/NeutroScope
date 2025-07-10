"""
Matplotlib canvas for plotting neutron balance
"""
import matplotlib.pyplot as plt
from typing import Optional
from .base_matplotlib_widget import BaseMatplotlibWidget
from .info_manager import InfoManager


class NeutronBalancePlot(BaseMatplotlibWidget):
    """Matplotlib canvas for plotting the neutron balance as a pie chart"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100, info_manager: Optional[InfoManager] = None):
        super().__init__(parent, width, height, dpi, info_manager)
        
        # Store tooltips
        self.tooltips = []
    
    def _setup_plot(self):
        """Initialise le contenu spécifique du plot de bilan neutronique."""
        self.axes.set_title('Bilan Neutronique (Destin des Neutrons)')

    def update_plot(self, balance_data):
        """Update the neutron balance pie chart with new data"""
        self.axes.clear()
        
        # Extract data from the dictionary
        labels = [item['name'] for item in balance_data['sections']]
        sizes = [item['value'] for item in balance_data['sections']]
        colors = [item['color'] for item in balance_data['sections']]
        self.tooltips = [item['tooltip'] for item in balance_data['sections']]
        
        # Create pie chart
        wedges, texts, autotexts = self.axes.pie(
            sizes, 
            labels=labels, 
            colors=colors, 
            autopct='%1.1f%%', 
            startangle=140,
            pctdistance=0.85,
            labeldistance=1.05
        )
        
        # Style the plot
        self.axes.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.setp(autotexts, size=8, weight="bold", color="white")
        plt.setp(texts, size=10)
        self.axes.set_title('Bilan Neutronique (Destin des Neutrons)')
        
        self.draw()

    def on_mouse_move(self, event):
        """Handle mouse movement to show tooltips"""
        if event.inaxes != self.axes:
            return
        
        # Check if mouse is over a wedge
        for i, wedge in enumerate(self.axes.patches):
            if wedge.contains_point([event.x, event.y]):
                self.show_tooltip_in_panel(i)
                return
        
        self.on_axes_leave(event) # Clear panel if not over any wedge
        
    def on_axes_leave(self, event):
        """Handle mouse leaving the axes"""
        super().on_axes_leave(event)  # Utilise l'implémentation de la classe de base

    def show_tooltip_in_panel(self, index):
        """Show tooltip information in the info panel"""
        if 0 <= index < len(self.tooltips):
            info_text = self.tooltips[index]
            
            # General explanation for context
            general_explanation = (
                "Le bilan neutronique montre ce qu'il advient des neutrons dans le cœur du réacteur. "
                "Pour maintenir une réaction en chaîne stable (criticité), chaque neutron de fission doit, en moyenne, "
                "provoquer exactement une nouvelle fission.\n\n"
                "Les neutrons peuvent :\n"
                "- Prolonger la réaction en chaîne (Fissions)\n"
                "- Être absorbés par des matériaux non-fissiles (Captures)\n"
                "- S'échapper du cœur (Fuites)\n\n"
                "Le contrôle de cet équilibre est la clé du pilotage d'un réacteur."
            )
            
            full_info = f"Destin des Neutrons\n\n{info_text}\n\n{general_explanation}"
            
            if self.info_manager:
                self.info_manager.info_requested.emit(full_info) 