"""
Matplotlib canvas for plotting neutron balance
"""
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from typing import Optional
from ..widgets.info_manager import InfoManager


class NeutronBalancePlot(FigureCanvasQTAgg):
    """Matplotlib canvas for plotting the neutron balance as a pie chart"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100, info_manager: Optional[InfoManager] = None):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.info_manager = info_manager
        
        self.axes.set_title('Bilan Neutronique (Destin des Neutrons)')
        
        # Store tooltips
        self.tooltips = []
        
        # Connect mouse motion event
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('axes_leave_event', self.on_axes_leave)

        self.fig.tight_layout()

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
        if self.info_manager:
            self.info_manager.info_cleared.emit()

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