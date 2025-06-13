"""
Matplotlib canvas for plotting axial flux distribution
"""
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


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
        self.rod_line.set_ydata([rod_height, rod_height])
        
        self.draw()
    
    def on_mouse_move(self, event):
        """Handle mouse movement to update tooltip info"""
        if event.inaxes != self.axes:
            return
        
        # Generate information about the current mouse position
        if 0 <= event.ydata <= 1 and 0 <= event.xdata <= 1.1:
            height = event.ydata
            flux = event.xdata
            rod_position = 1.0 - self.rod_line.get_ydata()[0]  # 0-1 scale
            
            # Position dans le cœur (convertir en description qualitative)
            position_description = ""
            if height < 0.2:
                position_description = "partie inférieure"
            elif height < 0.4:
                position_description = "partie basse"
            elif height < 0.6:
                position_description = "partie centrale"
            elif height < 0.8:
                position_description = "partie haute"
            else:
                position_description = "partie supérieure"
            
            # Analyser la position par rapport aux barres de contrôle
            barres_description = ""
            if rod_position > 0:  # Si les barres sont insérées
                rod_height = 1.0 - rod_position  # Position des barres (0-1)
                if height > rod_height:
                    barres_description = f" Cette région est affectée par les barres de contrôle (insérées à {rod_position*100:.0f}%)."
                else:
                    distance_to_rods = rod_height - height
                    if distance_to_rods < 0.2:
                        barres_description = f" Cette région est légèrement influencée par la proximité des barres de contrôle."
            
            # Évaluer l'intensité du flux à cet endroit
            flux_description = ""
            if flux < 0.3:
                flux_description = "très faible"
            elif flux < 0.6:
                flux_description = "modéré"
            elif flux < 0.8:
                flux_description = "important"
            elif flux < 0.95:
                flux_description = "très important"
            else:
                flux_description = "maximal"
            
            # Explication générale sur la distribution du flux
            general_explanation = (
                "La distribution axiale du flux neutronique montre comment l'intensité des réactions nucléaires "
                "varie le long de la hauteur du cœur du réacteur.\n\n"
                "Dans un REP, cette distribution est typiquement en forme de cosinus, mais elle est déformée par :\n"
                "- La position des barres de contrôle (qui absorbent les neutrons)\n"
                "- Les variations de densité du modérateur (plus faible en haut en raison de l'ébullition locale)\n"
                "- L'usure non uniforme du combustible\n\n"
                "Une distribution de flux équilibrée est importante pour :\n"
                "- Minimiser les points chauds dans le combustible\n"
                "- Optimiser l'utilisation du combustible\n"
                "- Maintenir les marges de sécurité thermique"
            )
            
            # Créer des observations spécifiques en fonction de la position et du flux
            specific_observation = f"À cette position ({position_description} du cœur), le flux neutronique est {flux_description} ({flux:.2f} relatif au maximum).{barres_description}"
            
            # Impact des barres de contrôle
            impact_barres = ""
            if rod_position > 0:
                impact_barres = (
                    f"\n\nImpact des barres de contrôle : Les barres sont actuellement insérées à {rod_position*100:.0f}% depuis le haut du cœur. "
                    f"Elles créent une dépression du flux dans la partie supérieure, ce qui modifie la distribution de puissance "
                    f"et peut affecter les marges thermiques."
                )
            
            # Recommandations éventuelles
            recommandations = ""
            if rod_position > 0.5 and flux < 0.5 and height > 0.8:
                recommandations = "\n\nDans un réacteur réel, une insertion aussi importante des barres de contrôle sur une longue période " \
                                  "pourrait créer un déséquilibre axial de puissance. Une combinaison de barres partiellement " \
                                  "insérées et d'ajustement de la concentration en bore serait généralement préférée pour le contrôle à long terme."
            
            # Informations essentielles pour le panneau d'information (concis)
            concise_info = (
                "Distribution Axiale du Flux Neutronique\n\n"
                f"Hauteur relative : {height:.2f}\n"
                f"Flux neutronique relatif : {flux:.2f}\n\n"
                f"Observation : {specific_observation}"
            )
            
            # Informations détaillées pour l'affichage avec la touche 'i' (complet)
            detailed_info = (
                "Distribution Axiale du Flux Neutronique\n\n"
                f"Hauteur relative : {height:.2f}\n"
                f"Flux neutronique relatif : {flux:.2f}\n\n"
                f"{general_explanation}\n\n"
                f"Observation : {specific_observation}{impact_barres}{recommandations}"
            )
            
            # Emit a signal to update the info panel
            if hasattr(self.parent(), 'update_info_panel'):
                self.parent().update_info_panel(concise_info, detailed_info)
    
    def on_axes_leave(self, event):
        """Handle mouse leaving the axes"""
        self.tooltip_text = ""
        if hasattr(self.parent(), 'update_info_panel'):
            self.parent().update_info_panel("", "")  # Réinitialiser également les infos détaillées 