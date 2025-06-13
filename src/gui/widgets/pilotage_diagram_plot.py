"""
Matplotlib canvas for plotting the pilotage diagram
"""
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class PilotageDiagramPlot(FigureCanvasQTAgg):
    """Matplotlib canvas for plotting the pilotage diagram"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.axes.set_xlabel('Axial Offset (%)')
        self.axes.set_ylabel('Puissance du réacteur (%)')
        self.axes.set_title('Diagramme de Pilotage')
        self.axes.grid(True)
        self.axes.set_xlim(-50, 50)
        self.axes.set_ylim(0, 110)
        
        # Plot operating point
        self.op_point, = self.axes.plot([], [], 'ro', markersize=10, label='Point de fonctionnement')
        
        # Connect mouse motion event
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('axes_leave_event', self.on_axes_leave)
        
        self.fig.tight_layout()
        
    def update_plot(self, ao_data):
        """Update the plot with new data"""
        axial_offset = ao_data['axial_offset']
        power = ao_data['power_percentage']
        
        self.op_point.set_data([axial_offset], [power])
        
        self.draw()
        
    def on_mouse_move(self, event):
        """Handle mouse movement to show tooltips"""
        if event.inaxes != self.axes:
            return
            
        # Get current data from plot
        x_data, y_data = self.op_point.get_data()
        if not x_data or not y_data:
            return
            
        axial_offset = x_data[0]
        power = y_data[0]

        # General explanation of the diagram
        general_explanation = (
            "Le diagramme de pilotage permet de visualiser l'état du réacteur en fonction de deux paramètres clés :\n"
            "- La puissance (généralement en % de la puissance nominale)\n"
            "- L'Axial Offset (AO), qui mesure le déséquilibre de puissance entre le haut et le bas du cœur.\n\n"
            "Un AO de 0% indique une distribution de puissance parfaitement symétrique. Un AO positif signifie que le haut du cœur produit plus de puissance, et un AO négatif que le bas du cœur est plus puissant.\n\n"
            "Les opérateurs doivent maintenir le point de fonctionnement à l'intérieur d'une zone autorisée pour garantir la sécurité et l'efficacité de l'exploitation."
        )

        # Analysis of the current point
        ao_analysis = ""
        if axial_offset > 10:
            ao_analysis = "Le flux est fortement décalé vers le haut du cœur. Cela peut être causé par des barres de contrôle trop insérées."
        elif axial_offset < -10:
            ao_analysis = "Le flux est fortement décalé vers le bas du cœur. Cela peut se produire en fin de cycle de combustible."
        else:
            ao_analysis = "La distribution axiale de puissance est bien équilibrée."

        power_analysis = ""
        if power > 100:
            power_analysis = "Le réacteur fonctionne en surpuissance, ce qui n'est autorisé que pour de courtes périodes."
        elif power > 50:
            power_analysis = "Le réacteur est dans un régime de puissance élevée."
        elif power > 1:
            power_analysis = "Le réacteur est en régime de faible puissance."
        else:
            power_analysis = "Le réacteur est à l'arrêt ou très proche de la criticité minimale."

        # Construct the info text
        info_text = (
            "Diagramme de Pilotage\n\n"
            f"Point de fonctionnement actuel :\n"
            f"- Puissance : {power:.1f} %\n"
            f"- Axial Offset : {axial_offset:.1f} %\n\n"
            f"Analyse :\n"
            f"- {ao_analysis}\n"
            f"- {power_analysis}\n\n"
            f"Description : {general_explanation}"
        )
        
        if hasattr(self.parent(), 'update_info_panel'):
            self.parent().update_info_panel(info_text)

    def on_axes_leave(self, event):
        """Handle mouse leaving the axes"""
        if hasattr(self.parent(), 'update_info_panel'):
            self.parent().update_info_panel("") 