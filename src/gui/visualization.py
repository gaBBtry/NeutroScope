"""
Visualization components for the reactor simulation
"""
import matplotlib
matplotlib.use('QtAgg')  # Use QtAgg backend for PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, 
    QPushButton, QToolButton, QSizePolicy, QSpacerItem,
    QDialog, QScrollArea
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
            self.parent().update_info_panel("", "")  # Réinitialiser également les infos détaillées
    
    def show_tooltip_in_panel(self, index):
        """Show tooltip for the bar at index in the info panel"""
        if index not in self.tooltips:
            return
        
        symbol, name, description, value = self.tooltips[index]
        
        # Créer des explications détaillées et contextuelles en fonction du facteur
        detailed_explanation = ""
        impact_explanation = ""
        recommendations = ""
        
        if symbol == 'η':  # Eta - facteur de reproduction
            detailed_explanation = (
                "Le facteur de reproduction η (eta) représente le nombre moyen de neutrons produits par neutron absorbé "
                "dans le combustible. C'est une mesure fondamentale de l'efficacité du combustible à générer de nouveaux neutrons.\n\n"
                "η dépend principalement de la composition du combustible :\n"
                "- Pour l'uranium-235 : η ≈ 2.07\n"
                "- Pour le plutonium-239 : η ≈ 2.15\n\n"
                "Plus la valeur de η est élevée, plus le combustible a le potentiel de maintenir une réaction en chaîne efficace."
            )
            
            # Évaluation contextuelle basée sur la valeur
            if value < 1.9:
                impact_explanation = "La valeur actuelle est faible, ce qui limite le potentiel de réactivité du cœur."
            elif value > 2.1:
                impact_explanation = "La valeur actuelle est élevée, ce qui favorise un bon bilan neutronique."
            
            # Recommandation
            if value < 1.9:
                recommendations = "Une augmentation de l'enrichissement en uranium-235 pourrait améliorer ce facteur."
            
        elif symbol == 'ε':  # Epsilon - facteur de fission rapide
            detailed_explanation = (
                "Le facteur de fission rapide ε (epsilon) représente le rapport entre le nombre total de fissions "
                "(rapides et thermiques) et le nombre de fissions thermiques uniquement.\n\n"
                "Il prend en compte les fissions supplémentaires causées par les neutrons rapides, principalement "
                "dans l'uranium-238. Dans un REP typique, ε est généralement compris entre 1.02 et 1.07, ce qui signifie "
                "que les fissions rapides contribuent à environ 2-7% des fissions totales.\n\n"
                "Ce facteur dépend principalement de la géométrie du combustible et du rapport entre l'uranium-238 et l'uranium-235."
            )
            
            # Évaluation contextuelle basée sur la valeur
            if value < 1.02:
                impact_explanation = "La valeur actuelle est faible, indiquant une contribution limitée des fissions rapides."
            elif value > 1.05:
                impact_explanation = "La valeur actuelle est élevée, indiquant une bonne contribution des fissions rapides au bilan neutronique."
            
        elif symbol == 'p':  # Facteur antitrappe / Probabilité d'échappement aux résonances
            detailed_explanation = (
                "Le facteur antitrappe p représente la probabilité qu'un neutron ralenti échappe à la capture par résonance, "
                "principalement par l'uranium-238, pendant sa modération.\n\n"
                "Il s'agit d'un facteur crucial qui reflète la compétition entre la modération et l'absorption des neutrons "
                "pendant qu'ils sont ralentis jusqu'aux énergies thermiques. Dans un REP, p est typiquement entre 0.7 et 0.8.\n\n"
                "Ce facteur est sensible à :\n"
                "- La température du combustible (effet Doppler)\n"
                "- La géométrie et l'arrangement du combustible\n"
                "- Le rapport modérateur/combustible"
            )
            
            # Évaluation contextuelle basée sur la valeur
            if value < 0.7:
                impact_explanation = "La valeur actuelle est faible, indiquant des pertes importantes par capture résonante."
                recommendations = "Une augmentation du rapport modérateur/combustible pourrait améliorer ce facteur."
            elif value > 0.8:
                impact_explanation = "La valeur actuelle est élevée, indiquant un excellent échappement aux captures résonantes."
            
        elif symbol == 'f':  # Facteur d'utilisation thermique
            detailed_explanation = (
                "Le facteur d'utilisation thermique f représente la fraction des neutrons thermiques absorbés dans le combustible "
                "par rapport à tous les neutrons thermiques absorbés dans le réacteur.\n\n"
                "Il mesure l'efficacité avec laquelle les neutrons thermiques sont utilisés pour produire des fissions plutôt "
                "que d'être absorbés par le modérateur, les poisons, les structures ou les barres de contrôle.\n\n"
                "Ce facteur est influencé par :\n"
                "- La concentration de bore dans le modérateur\n"
                "- La position des barres de contrôle\n"
                "- La présence de poisons neutroniques (xénon, samarium)\n"
                "- Les matériaux de structure du cœur"
            )
            
            # Évaluation contextuelle basée sur la valeur
            if value < 0.7:
                impact_explanation = "La valeur actuelle est faible, indiquant des absorptions importantes en dehors du combustible."
                recommendations = "Une réduction de la concentration en bore ou un retrait partiel des barres de contrôle pourrait améliorer ce facteur."
            elif value > 0.8:
                impact_explanation = "La valeur actuelle est élevée, indiquant une excellente utilisation des neutrons thermiques."
            
        elif symbol == 'k∞':  # Facteur de multiplication infini
            detailed_explanation = (
                "Le facteur de multiplication infini k∞ représente le rapport entre le nombre de neutrons produits et le nombre "
                "de neutrons absorbés dans un milieu infini (sans fuites).\n\n"
                "Il est calculé comme le produit des quatre facteurs : k∞ = η × ε × p × f\n\n"
                "Dans un réacteur réel (de taille finie), k∞ doit être supérieur à 1 pour compenser les fuites de neutrons "
                "et maintenir la criticité (keff = 1)."
            )
            
            # Évaluation contextuelle basée sur la valeur
            if value < 1.0:
                impact_explanation = "La valeur actuelle est inférieure à 1, ce qui signifie que même sans fuites, le réacteur ne pourrait pas maintenir une réaction en chaîne."
                recommendations = "Une augmentation de l'enrichissement ou une réduction des absorptions parasites est nécessaire."
            elif value > 1.3:
                impact_explanation = "La valeur actuelle est très élevée, indiquant un excès significatif de réactivité disponible."
            elif 1.0 <= value <= 1.05:
                impact_explanation = "La valeur actuelle est proche de 1, ce qui pourrait être insuffisant pour compenser les fuites neutroniques."
            
        elif symbol == 'LT':  # Probabilité de non-fuite thermique
            detailed_explanation = (
                "La probabilité de non-fuite thermique LT représente la fraction des neutrons thermiques qui ne s'échappent pas du cœur.\n\n"
                "Elle dépend de :\n"
                "- La taille et la géométrie du cœur (plus le cœur est grand, plus LT est proche de 1)\n"
                "- La présence de réflecteurs en périphérie du cœur\n"
                "- La distribution de puissance dans le cœur\n\n"
                "Dans les grands réacteurs de puissance, cette valeur est typiquement supérieure à 0.95."
            )
            
            # Évaluation contextuelle basée sur la valeur
            if value < 0.95:
                impact_explanation = "La valeur actuelle est faible, indiquant des fuites thermiques significatives."
                recommendations = "Une optimisation de la distribution de puissance pourrait réduire ces fuites."
            
        elif symbol == 'LF':  # Probabilité de non-fuite rapide
            detailed_explanation = (
                "La probabilité de non-fuite rapide LF représente la fraction des neutrons rapides qui ne s'échappent pas du cœur "
                "pendant leur ralentissement.\n\n"
                "Cette probabilité est généralement plus faible que LT car les neutrons rapides ont un libre parcours moyen plus "
                "grand que les neutrons thermiques.\n\n"
                "LF dépend de :\n"
                "- La taille et la géométrie du cœur\n"
                "- La densité du modérateur\n"
                "- L'efficacité des réflecteurs pour les neutrons rapides"
            )
            
            # Évaluation contextuelle basée sur la valeur
            if value < 0.95:
                impact_explanation = "La valeur actuelle est faible, indiquant des fuites rapides significatives."
            
        elif symbol == 'keff':  # Facteur de multiplication effectif
            detailed_explanation = (
                "Le facteur de multiplication effectif keff représente le rapport entre le nombre de neutrons dans une génération "
                "et le nombre de neutrons dans la génération précédente, en tenant compte des fuites.\n\n"
                "Il est calculé comme : keff = k∞ × LT × LF\n\n"
                "Cette valeur détermine l'état du réacteur :\n"
                "- keff < 1 : Réacteur sous-critique, la réaction en chaîne décroît\n"
                "- keff = 1 : Réacteur critique, la réaction en chaîne est stable\n"
                "- keff > 1 : Réacteur surcritique, la réaction en chaîne s'amplifie"
            )
            
            # Évaluation contextuelle basée sur la valeur
            if value < 0.98:
                impact_explanation = "Le réacteur est significativement sous-critique."
                recommendations = "Une réduction de la concentration en bore ou un retrait des barres de contrôle serait nécessaire pour atteindre la criticité."
            elif 0.98 <= value < 0.999:
                impact_explanation = "Le réacteur est légèrement sous-critique, proche de la criticité."
            elif 0.999 <= value <= 1.001:
                impact_explanation = "Le réacteur est critique, la réaction en chaîne est stable."
            elif 1.001 < value <= 1.02:
                impact_explanation = "Le réacteur est légèrement surcritique."
                recommendations = "Un ajustement mineur des éléments de contrôle peut être nécessaire pour stabiliser la puissance."
            elif value > 1.02:
                impact_explanation = "Le réacteur est significativement surcritique."
                recommendations = "Une insertion des barres de contrôle ou une augmentation de la concentration en bore est nécessaire pour éviter une augmentation rapide de la puissance."
        
        # Informations concises pour le panneau d'information
        concise_info = (
            f"{symbol} - {name}\n\n"
            f"Valeur actuelle : {value:.4f}\n\n"
            f"Impact : {impact_explanation}"
        )
        
        # Informations détaillées pour l'affichage complet
        detailed_info = (
            f"{symbol} - {name}\n\n"
            f"{description}\n\n"
            f"Valeur actuelle : {value:.4f}\n\n"
            f"{detailed_explanation}\n\n"
            f"Impact sur le réacteur : {impact_explanation}\n"
            f"{recommendations}"
        )
        
        # Send the text to the info panel
        if hasattr(self.parent(), 'update_info_panel'):
            self.parent().update_info_panel(concise_info, detailed_info)


class InfoPanel(QFrame):
    """Panel for displaying information about visualizations"""
    
    # Signal emitted when panel is closed
    closed = pyqtSignal()
    # Signal to request detailed info display
    show_details = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setMinimumHeight(100)  # Réduire la hauteur minimale
        self.setMaximumHeight(250)  # Limiter la hauteur maximale
        
        # Create layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create header with title only
        header_layout = QHBoxLayout()
        
        # Title label
        self.title_label = QLabel("Informations")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        self.title_label.setFont(title_font)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)
        
        # Info content label
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.info_label.setWordWrap(True)
        self.info_label.setTextFormat(Qt.TextFormat.RichText)
        
        # Indication pour la touche 'i'
        self.key_hint_label = QLabel("<i>Appuyez sur la touche 'i' pour plus d'informations</i>")
        self.key_hint_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.key_hint_label.setTextFormat(Qt.TextFormat.RichText)
        self.key_hint_label.setStyleSheet("color: #666; font-size: 10px;")
        
        # Add to layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.info_label)
        main_layout.addWidget(self.key_hint_label)
    
    def update_info(self, text):
        """Update the information displayed in the panel"""
        if not text:
            self.info_label.setText("")
            self.key_hint_label.setVisible(False)
        else:
            self.info_label.setText(text.replace("\n", "<br>"))
            self.key_hint_label.setVisible(True)
    
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
        
    def update_tooltip(self, is_panel_visible):
        """Update tooltip based on panel visibility"""
        if is_panel_visible:
            self.setToolTip("Fermer le panneau d'information")
        else:
            self.setToolTip("Afficher le panneau d'information")


class CreditsButton(QToolButton):
    """Button to show the credits dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("©")  # Unicode copyright symbol
        self.setToolTip("Afficher les crédits")
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)
        self.setStyleSheet("""
            QToolButton { 
                border: 1px solid #ddd; 
                border-radius: 4px;
                padding: 5px; 
                background-color: #f8f8f8;
                color: #888;
            }
            QToolButton:hover { 
                background-color: #e6e6e6; 
                color: #444;
            }
        """)
        self.setFixedSize(30, 30)
        self.clicked.connect(self.show_credits)
        
    def show_credits(self):
        """Show the credits dialog"""
        dialog = QDialog(self.parent())
        dialog.setWindowTitle("Crédits")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel("Simulation Neutronique des REP")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        credits = QLabel(
            "© 2023-2024 EDF UFPI\n\n"
            "Développé pour la formation et l'apprentissage\n"
            "des principes de la neutronique des réacteurs.\n\n"
            "Version: alpha 0.1"
        )
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits.setWordWrap(True)
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(dialog.accept)
        
        layout.addWidget(title)
        layout.addWidget(credits)
        layout.addWidget(close_button)
        
        dialog.exec()


class NeutronBalancePlot(FigureCanvasQTAgg):
    """Matplotlib canvas for plotting the neutron balance pie chart"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Set up initial empty pie chart
        self.wedges = None
        self.tooltips = {}
        self.annotations = []
        
        self.axes.set_title('Bilan des Neutrons')
        self.axes.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Connect mouse events
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('axes_leave_event', self.on_axes_leave)
        
        self.fig.tight_layout()
    
    def update_plot(self, balance_data):
        """Update the neutron balance plot with new data"""
        # Clear previous plot elements
        if self.wedges is not None:
            for wedge in self.wedges:
                wedge.remove()
        
        for annotation in self.annotations:
            annotation.remove()
        self.annotations = []
        
        # Extract data
        sections = balance_data["sections"]
        values = [section["value"] for section in sections]
        labels = [section["name"] for section in sections]
        colors = [section["color"] for section in sections]
        
        # Create tooltips dictionary
        self.tooltips = {}
        for i, section in enumerate(sections):
            self.tooltips[i] = section["tooltip"]
        
        # Create pie chart
        self.wedges, texts = self.axes.pie(
            values,
            colors=colors,
            wedgeprops=dict(width=0.5),  # Make it a donut chart
            startangle=90  # Start from the top
        )
        
        # Add a white circle at the center to make it a donut
        centre_circle = plt.Circle((0, 0), 0.25, fc='white')
        self.axes.add_patch(centre_circle)
        
        # Add labels
        for i, (wedge, label) in enumerate(zip(self.wedges, labels)):
            # Get wedge center
            theta = np.pi/2 - (wedge.theta1 + wedge.theta2)/2
            radius = 0.7  # Just outside the pie
            x = radius * np.cos(np.deg2rad(wedge.theta1 + wedge.theta2) / 2)
            y = radius * np.sin(np.deg2rad(wedge.theta1 + wedge.theta2) / 2)
            
            # Add label and value
            text = f"{label}\n{values[i]}%"
            annotation = self.axes.text(
                x, y, text,
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=8
            )
            self.annotations.append(annotation)
        
        self.draw()
    
    def on_mouse_move(self, event):
        """Handle mouse movement over the pie chart to update info panel"""
        if event.inaxes != self.axes:
            return
        
        # Check if mouse is over a wedge
        for i, wedge in enumerate(self.wedges):
            contains, _ = wedge.contains(event)
            if contains:
                # Mouse is over this wedge
                self.show_tooltip_in_panel(i)
                return
        
        # If not over any wedge, clear the info panel
        if hasattr(self.parent(), 'update_info_panel'):
            self.parent().update_info_panel("")
    
    def on_axes_leave(self, event):
        """Handle mouse leaving the axes"""
        if hasattr(self.parent(), 'update_info_panel'):
            self.parent().update_info_panel("", "")  # Réinitialiser également les infos détaillées
    
    def show_tooltip_in_panel(self, index):
        """Show tooltip for the wedge at index in the info panel"""
        if index not in self.tooltips:
            return
        
        base_tooltip = self.tooltips[index]
        
        # Récupérer la valeur directement à partir des données originales
        # Au lieu d'utiliser get_width() qui n'existe pas pour les objets Wedge
        section_value = 0
        if hasattr(self, 'wedges') and index < len(self.wedges):
            # On récupère le pourcentage directement
            section_name = base_tooltip.split(':')[0] if ':' in base_tooltip else ""
            # Extrait le pourcentage qui est dans le tooltip de base
            try:
                section_parts = base_tooltip.split()
                for i, part in enumerate(section_parts):
                    if '%' in part:
                        # Extraire la valeur numérique
                        section_value = float(part.replace('%', '').replace(',', '.'))
                        break
            except (ValueError, IndexError):
                # En cas d'erreur, utiliser 0
                section_value = 0
        
        # Créer des explications détaillées et contextuelles en fonction de la section
        detailed_explanation = ""
        recommendations = ""
        
        if "Fissions" in base_tooltip:
            detailed_explanation = (
                "Les fissions sont les réactions qui produisent de l'énergie dans le réacteur. "
                "Lorsqu'un noyau d'uranium-235 ou de plutonium-239 capture un neutron, il peut se diviser "
                "en deux fragments plus légers, libérant de l'énergie et des neutrons supplémentaires.\n\n"
                "Ces neutrons émis peuvent être :\n"
                "- Lents (thermiques) : Principaux responsables des nouvelles fissions\n"
                "- Rapides : Issus directement de la fission, ils peuvent provoquer des fissions dans l'uranium-238"
            )
            
            # Ajouter des observations contextuelles
            if "lents" in base_tooltip:
                slow_pct = float(base_tooltip.split("lents ")[1].split("%")[0])
                if slow_pct < 35:
                    recommendations = "\n\nLe taux de fission est bas, ce qui indique une réactivité réduite. "
                    recommendations += "Cela peut être dû à une insertion importante des barres de contrôle ou une concentration élevée de bore."
                elif slow_pct > 40:
                    recommendations = "\n\nLe taux de fission est élevé, indiquant une bonne réactivité du cœur."
            
        elif "Captures fertiles" in base_tooltip:
            detailed_explanation = (
                "Les captures fertiles sont des réactions où un neutron est absorbé par un noyau non-fissile "
                "pour produire un noyau fissile. Dans un REP, l'uranium-238 (non-fissile) capture un neutron "
                "pour devenir du plutonium-239 (fissile) après deux désintégrations bêta successives.\n\n"
                "Ce phénomène, appelé conversion, permet de 'régénérer' partiellement le combustible "
                "pendant le fonctionnement du réacteur et contribue significativement à la production d'énergie "
                "en fin de cycle."
            )
            
            # Explications contextuelles
            if section_value > 20:
                recommendations = "\n\nLe taux de captures fertiles est élevé, ce qui est favorable pour la durée de vie du combustible."
            
        elif "Captures stériles" in base_tooltip:
            detailed_explanation = (
                "Les captures stériles sont des réactions où un neutron est absorbé sans produire ni fission "
                "ni noyau fissile. Ces captures sont 'improductives' du point de vue de la réaction en chaîne.\n\n"
                "Les captures stériles se produisent :\n"
                "- Dans les produits de fission qui s'accumulent (xénon, samarium...)\n"
                "- Dans des isotopes non-fertiles du combustible\n"
                "- Dans les matériaux de structure (acier...)"
            )
            
            # Explications contextuelles
            if section_value > 15:
                recommendations = "\n\nLe taux de captures stériles est élevé, ce qui peut indiquer une accumulation de produits de fission ou une concentration importante de bore."
        
        elif "Fuites" in base_tooltip:
            detailed_explanation = (
                "Les fuites représentent les neutrons qui s'échappent du cœur sans interagir avec le combustible. "
                "Ces neutrons sont perdus pour la réaction en chaîne.\n\n"
                "Les fuites se divisent en :\n"
                "- Fuites de neutrons rapides : Principalement en périphérie du cœur\n"
                "- Fuites de neutrons thermiques : Plus importantes dans les petits réacteurs"
                "\n\nUn taux de fuite élevé diminue l'efficacité du réacteur mais contribue à la "
                "protection radiologique en périphérie du cœur."
            )
            
            # Explications contextuelles
            if "rapides" in base_tooltip:
                fast_pct = float(base_tooltip.split("rapides ")[1].split("%")[0])
                if fast_pct > 12:
                    recommendations = "\n\nLe taux de fuites de neutrons rapides est élevé. Dans un réacteur de puissance, cela pourrait indiquer un problème avec le réflecteur en périphérie du cœur."
        
        elif "Modérateur" in base_tooltip:
            detailed_explanation = (
                "Les captures dans le modérateur représentent les neutrons absorbés par l'eau qui ralentit les neutrons. "
                "L'hydrogène de l'eau capture parfois un neutron pour former du deutérium.\n\n"
                "Ces captures sont inévitables et représentent une perte neutronique inhérente au fonctionnement "
                "d'un réacteur à eau. Elles augmentent avec la température car la densité de l'eau diminue, "
                "réduisant l'efficacité de la modération."
            )
            
        elif "Combustible" in base_tooltip:
            detailed_explanation = (
                "Les captures dans le combustible (hors fissions et captures fertiles) sont des réactions "
                "où le combustible absorbe un neutron sans produire de fission ni de noyau fissile. "
                "Ces captures comprennent les réactions avec :\n"
                "- L'oxygène dans l'UO₂\n"
                "- Certains isotopes peu abondants de l'uranium\n"
                "- D'autres actinides présents dans le combustible\n\n"
                "Ces captures sont considérées comme des pertes neutroniques car elles ne contribuent pas "
                "directement à la réaction en chaîne."
            )
            
        elif "Poisons/Barres" in base_tooltip:
            detailed_explanation = (
                "Cette catégorie comprend les neutrons absorbés par les éléments de contrôle de la réactivité :\n"
                "- Barres de contrôle : Éléments absorbants mobiles (généralement en carbure de bore ou alliage argent-indium-cadmium)\n"
                "- Bore dissous : Élément absorbant homogène ajouté à l'eau du circuit primaire\n"
                "- Poisons consommables : Absorbants intégrés à certains assemblages\n\n"
                "Ces absorbants sont utilisés pour contrôler la réactivité du cœur et garantir sa stabilité."
            )
            
            # Explications contextuelles
            if section_value > 8:
                recommendations = "\n\nLe taux d'absorption par les poisons et barres est élevé, indiquant un contrôle significatif de la réactivité. Cela peut être nécessaire en début de cycle ou pour compenser un excès de réactivité."
        
        # Information concise pour le panneau d'information
        concise_info = base_tooltip
        
        # Information détaillée pour l'affichage complet
        detailed_info = f"{base_tooltip}\n\n{detailed_explanation}{recommendations}"
        
        # Send the text to the info panel
        if hasattr(self.parent(), 'update_info_panel'):
            self.parent().update_info_panel(concise_info, detailed_info)


class PilotageDiagramPlot(FigureCanvasQTAgg):
    """Matplotlib canvas for plotting the pilotage diagram (AO vs Power)"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Current state point
        self.state_point = None
        
        # Initial setup
        self.axes.set_xlabel('Axial Offset (%)')
        self.axes.set_ylabel('Puissance nucléaire (%)')
        self.axes.set_title('Diagramme de Pilotage')
        self.axes.set_xlim(-30, 30)  # Typical AO range
        self.axes.set_ylim(0, 110)   # Power percentage range
        self.axes.grid(True)
        
        # Connect mouse events
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('axes_leave_event', self.on_axes_leave)
        
        self.fig.tight_layout()
    
    def update_plot(self, ao_data):
        """Update the pilotage diagram with new data"""
        axial_offset = ao_data["axial_offset"]
        power_percentage = ao_data["power_percentage"]
        
        # Remove previous state point if it exists
        if self.state_point:
            self.state_point.remove()
        
        # Plot new state point
        self.state_point = self.axes.scatter(
            axial_offset, power_percentage, 
            color='red', s=100, marker='o', 
            edgecolor='black', linewidth=1.5,
            zorder=5
        )
        
        self.draw()
    
    def on_mouse_move(self, event):
        """Handle mouse movement to update tooltip info"""
        if event.inaxes != self.axes:
            return
        
        # Generate information about the current mouse position
        if -30 <= event.xdata <= 30 and 0 <= event.ydata <= 110:
            ao = event.xdata
            power = event.ydata
            
            # Get current state point position
            current_ao = None
            current_power = None
            if self.state_point:
                current_ao = self.state_point.get_offsets()[0, 0]
                current_power = self.state_point.get_offsets()[0, 1]
            
            # Description of axial offset
            ao_description = ""
            if ao < -15:
                ao_description = "fort déséquilibre vers le bas"
            elif ao < -5:
                ao_description = "déséquilibre vers le bas"
            elif ao < 5:
                ao_description = "équilibre"
            elif ao < 15:
                ao_description = "déséquilibre vers le haut"
            else:
                ao_description = "fort déséquilibre vers le haut"
            
            # Build tooltip text
            tooltip_text = (
                "Diagramme de Pilotage\n\n"
                f"Position actuelle :\n"
                f"Axial Offset : {current_ao:.1f}%\n"
                f"Puissance : {current_power:.1f}%\n\n"
                f"Position pointée :\n"
                f"Axial Offset : {ao:.1f}% ({ao_description})\n"
                f"Puissance : {power:.1f}%\n\n"
                "Le diagramme de pilotage permet de visualiser l'état du réacteur\n"
                "en termes de déséquilibre axial de puissance (AO) et de niveau de puissance.\n\n"
                "L'Axial Offset représente la différence relative de puissance entre\n"
                "les moitiés supérieure et inférieure du cœur."
            )
            
            # Update info panel
            if hasattr(self.parent(), 'update_info_panel'):
                self.parent().update_info_panel(tooltip_text)
    
    def on_axes_leave(self, event):
        """Handle mouse leaving the axes"""
        if hasattr(self.parent(), 'update_info_panel'):
            self.parent().update_info_panel("", "")  # Réinitialiser également les infos détaillées


class VisualizationPanel(QWidget):
    """Panel containing all visualizations for the reactor simulation"""
    
    def __init__(self, parent=None, use_info_panel=True):
        super().__init__(parent)
        
        # Activer le focus clavier avec acceptation automatique
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()  # Prendre le focus dès l'initialisation
        
        # Create main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create plots
        self.flux_plot = FluxDistributionPlot(self)
        self.factors_plot = FourFactorsPlot(self)
        self.neutron_balance_plot = NeutronBalancePlot(self)
        self.pilotage_diagram_plot = PilotageDiagramPlot(self)
        
        # Stockage des informations détaillées pour affichage complet
        self.detail_info = ""
        
        # Flag to determine if we should use an internal info panel or an external one
        self.use_info_panel = use_info_panel
        
        if use_info_panel:
            # Create info panel and info button
            self.info_panel = InfoPanel(self)
            self.info_button = InfoButton(self)
            self.credits_button = CreditsButton(self)
            self.info_button.clicked.connect(self.toggle_info_panel)
            
            # Connect info panel closed signal
            self.info_panel.closed.connect(self.on_info_panel_closed)
            
            # Connect details button signal
            self.info_panel.show_details.connect(self.show_detailed_info)
            
            # Flag to control automatic showing of info panel
            self.auto_show_info = False
            
            # Create a container for plots and info button
            plots_container = QWidget()
            plots_layout = QVBoxLayout(plots_container)
            plots_layout.setContentsMargins(0, 0, 0, 0)
            
            # Create horizontal layout for flux and pilotage diagram
            flux_pilotage_layout = QHBoxLayout()
            flux_pilotage_layout.addWidget(self.flux_plot, 1)
            flux_pilotage_layout.addWidget(self.pilotage_diagram_plot, 1)
            
            # Create horizontal layout for factors and neutron balance
            factors_balance_layout = QHBoxLayout()
            factors_balance_layout.addWidget(self.factors_plot, 1)
            factors_balance_layout.addWidget(self.neutron_balance_plot, 1)
            
            # Add plots to plots container
            plots_layout.addLayout(flux_pilotage_layout, 1)
            plots_layout.addLayout(factors_balance_layout, 1)
            
            # Create container for buttons (bottom right corner)
            btn_container = QWidget(plots_container)
            btn_container.setGeometry(0, 0, 80, 40)  # Will be repositioned in resizeEvent
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 5, 5)
            btn_layout.setSpacing(10)
            btn_layout.addStretch(1)
            btn_layout.addWidget(self.credits_button)
            btn_layout.addWidget(self.info_button)
            
            # Add plots container and info panel to main layout
            self.layout.addWidget(plots_container, 1)
            self.layout.addWidget(self.info_panel)
            
            # Hide info panel by default
            self.info_panel.hide()
        else:
            # Simpler layout without info panel
            
            # Create horizontal layout for flux and pilotage diagram
            flux_pilotage_layout = QHBoxLayout()
            flux_pilotage_layout.addWidget(self.flux_plot, 1)
            flux_pilotage_layout.addWidget(self.pilotage_diagram_plot, 1)
            
            # Add top row
            self.layout.addLayout(flux_pilotage_layout, 1)
            
            # Create horizontal layout for factors and neutron balance
            factors_balance_layout = QHBoxLayout()
            factors_balance_layout.addWidget(self.factors_plot, 1)
            factors_balance_layout.addWidget(self.neutron_balance_plot, 1)
            
            # Add lower row
            self.layout.addLayout(factors_balance_layout, 1)
        
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
    
    def update_neutron_balance_plot(self, balance_data):
        """Update the neutron balance plot"""
        self.neutron_balance_plot.update_plot(balance_data)
    
    def update_pilotage_diagram_plot(self, ao_data):
        """Update the pilotage diagram"""
        self.pilotage_diagram_plot.update_plot(ao_data)
    
    def update_info_panel(self, text, detailed_text=None):
        """
        Update the info panel with the provided text
        
        Parameters:
        - text: Basic information to show in the panel
        - detailed_text: Detailed information to store for "i" key press
        """
        # Store detailed information for key press - effacer si text est vide
        if not text:
            self.detail_info = ""  # Effacer les informations détaillées quand on quitte une zone
        elif detailed_text is not None:
            self.detail_info = detailed_text
        else:
            self.detail_info = text  # Si pas de texte détaillé fourni, utiliser le texte de base
            
        if self.use_info_panel:
            self.info_panel.update_info(text)
            # Only show the panel if auto_show is enabled
            if text and not self.info_panel.isVisible() and self.auto_show_info:
                self.info_panel.show()
                self.info_button.update_tooltip(True)
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
            self.info_button.update_tooltip(False)
        else:
            self.info_panel.show()
            self.auto_show_info = True
            self.info_button.update_tooltip(True)
    
    def on_info_panel_closed(self):
        """Handle info panel being closed"""
        self.auto_show_info = False
        self.info_button.update_tooltip(False)
    
    def show_detailed_info(self):
        """Show detailed information in a dialog when 'i' key is pressed"""
        if not self.detail_info:
            print("Aucune information détaillée disponible")  # Debug
            return
            
        print("Affichage des informations détaillées")  # Debug
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Informations détaillées")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)
        dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(dialog)
        
        # Créer un QTextEdit pour afficher le texte avec défilement
        text_display = QLabel()
        text_display.setWordWrap(True)
        text_display.setTextFormat(Qt.TextFormat.RichText)
        text_display.setText(self.detail_info.replace("\n", "<br>"))
        
        # Ajouter un scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(text_display)
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(dialog.accept)
        
        layout.addWidget(scroll_area)
        layout.addWidget(close_button)
        
        dialog.exec()
    
    def showEvent(self, event):
        """Override showEvent to take focus when shown"""
        super().showEvent(event)
        self.setFocus()  # Prendre le focus quand le widget devient visible
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_I:
            # N'ouvrir la fenêtre que s'il y a des informations détaillées
            if self.detail_info:
                self.show_detailed_info()
                event.accept()
                return
        super().keyPressEvent(event) 