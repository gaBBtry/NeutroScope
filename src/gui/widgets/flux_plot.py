"""
Matplotlib canvas for plotting axial flux distribution
"""
from typing import Optional
from .base_matplotlib_widget import BaseMatplotlibWidget
from .info_manager import InfoManager


class FluxDistributionPlot(BaseMatplotlibWidget):
    """Matplotlib canvas for plotting axial flux distribution"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100, info_manager: Optional[InfoManager] = None):
        super().__init__(parent, width, height, dpi, info_manager)
        
        # Store information for tooltip
        self.tooltip_text = ""
    
    def _setup_plot(self):
        """Initialise le contenu spécifique du plot de flux axial."""
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
    
    def update_plot(self, height, flux, rod_position):
        """Update the flux distribution plot with new data"""
        # Plot with vertical orientation (flux on x-axis, height on y-axis)
        self.line.set_data(flux, height)
        
        # Update rod position line - rod comes from the top
        # Nouvelle convention: rod_position est le % de retrait (0% = insérées, 100% = retirées)
        rod_insertion_fraction = (100.0 - rod_position) / 100.0  # Fraction d'insertion réelle
        rod_tip_height = 1.0 - rod_insertion_fraction  # Position des pointes des barres
        self.rod_line.set_ydata([rod_tip_height, rod_tip_height])
        
        self.draw()
    
    def on_mouse_move(self, event):
        """Handle mouse movement to update tooltip info"""
        if event.inaxes != self.axes:
            return
        
        # Generate information about the current mouse position
        if 0 <= event.ydata <= 1 and 0 <= event.xdata <= 1.1:
            height = event.ydata
            flux = event.xdata
            rod_tip_height = self.rod_line.get_ydata()[0]  # Position des pointes (0-1 scale)
            rod_insertion_fraction = 1.0 - rod_tip_height  # Fraction d'insertion réelle
            rod_position = 100.0 - (rod_insertion_fraction * 100.0)  # % de retrait pour affichage
            
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
            if rod_insertion_fraction > 0:  # Si les barres sont partiellement insérées
                if height > rod_tip_height:
                    insertion_percentage = rod_insertion_fraction * 100.0
                    barres_description = f" Cette région est affectée par les barres de contrôle (insérées à {insertion_percentage:.0f}%)."
                else:
                    distance_to_rods = rod_tip_height - height
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
            if rod_insertion_fraction > 0:
                insertion_percentage = rod_insertion_fraction * 100.0
                impact_barres = (
                    f"\n\nImpact des barres de contrôle : Les barres sont actuellement insérées à {insertion_percentage:.0f}% depuis le haut du cœur. "
                    f"Elles créent une dépression du flux dans la partie supérieure, ce qui modifie la distribution de puissance "
                    f"et peut affecter les marges thermiques."
                )
            
            # Recommandations éventuelles
            recommandations = ""
            if rod_insertion_fraction > 0.5 and flux < 0.5 and height > 0.8:
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
            
            if self.info_manager:
                self.info_manager.info_requested.emit(concise_info)
    
    def on_axes_leave(self, event):
        """Handle mouse leaving the axes"""
        self.tooltip_text = ""
        super().on_axes_leave(event)  # Utilise l'implémentation de la classe de base