"""
Matplotlib canvas for plotting the four factors
"""
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


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
                                           ha='center', va='bottom', fontsize=9, 
                                           bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.5))
                self.value_annotations.append(annotation)

        # Add line for critical (k_effective = 1)
        self.critical_line = self.axes.axhline(y=1, color='r', linestyle='--', linewidth=1.5, label='Criticité (k=1)')

        self.draw()

    def on_mouse_move(self, event):
        """Handle mouse movement to show tooltips"""
        if event.inaxes != self.axes:
            return
        
        # Check if mouse is over a bar
        for i, bar in enumerate(self.bars):
            if bar.contains(event)[0]:
                self.show_tooltip_in_panel(i)
                return

        self.on_axes_leave(event)  # Clear panel if not over any bar
        
    def on_axes_leave(self, event):
        """Handle mouse leaving the axes area"""
        if hasattr(self.parent(), 'update_info_panel'):
            self.parent().update_info_panel("")

    def show_tooltip_in_panel(self, index):
        """Show tooltip information in the info panel"""
        if index in self.tooltips:
            symbol, name, description, value = self.tooltips[index]
            
            # Additional context based on factor
            context = ""
            if symbol == 'η':
                context = "Dépend principalement de l'enrichissement du combustible."
            elif symbol == 'ε':
                context = "Considéré constant pour une géométrie de réacteur donnée."
            elif symbol == 'p':
                context = "Affecté par la température du combustible (effet Doppler)."
            elif symbol == 'f':
                context = "Affecté par les poisons (bore, barres de contrôle)."
            elif symbol == 'k∞':
                context = "Représente la performance du réacteur dans un milieu infini (sans fuites)."
            elif symbol == 'LT' or symbol == 'LF':
                context = "Dépend de la taille et de la géométrie du cœur."
            elif symbol == 'keff':
                context = "La valeur clé qui détermine le comportement du réacteur :\n" \
                          "keff > 1 : sur-critique (puissance augmente)\n" \
                          "keff = 1 : critique (puissance stable)\n" \
                          "keff < 1 : sous-critique (puissance diminue)"

            info_text = (
                f"{name} ({symbol})\n\n"
                f"Valeur : {value:.4f}\n\n"
                f"Description : {description}\n\n"
                f"Contexte : {context}"
            )
            
            if hasattr(self.parent(), 'update_info_panel'):
                self.parent().update_info_panel(info_text) 