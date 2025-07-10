"""
Xenon Dynamics Visualization Widget

This widget displays the evolution of Iodine-135 and Xenon-135 concentrations over time,
along with their effect on reactor reactivity.
"""
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal
from typing import Optional
from ..widgets.info_manager import InfoManager

class XenonPlot(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=8, height=6, dpi=100, info_manager: Optional[InfoManager] = None):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.info_manager = info_manager
        self.data_history = []  # Stockage de l'historique des données
        
        # Configuration des sous-graphiques
        self.ax1 = self.fig.add_subplot(211)  # Concentrations
        self.ax2 = self.fig.add_subplot(212)  # Effet sur la réactivité
        
        self.fig.suptitle('Dynamique Xénon-135', fontsize=14, fontweight='bold')
        self.fig.tight_layout()
        
        # Configuration de l'affichage
        self._setup_plots()
        
        # Connexion des événements de survol
        if self.info_manager:
            self.mpl_connect('motion_notify_event', self.on_mouse_move)
            self.mpl_connect('axes_leave_event', self.on_axes_leave)

    def _setup_plots(self):
        """Configure l'apparence des graphiques"""
        # Graphique des concentrations
        self.ax1.set_ylabel('Concentration\n(atomes/cm³)', fontsize=12)
        self.ax1.set_title('Concentrations I-135 et Xe-135', fontsize=12)
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_yscale('log')  # Échelle logarithmique pour les concentrations
        
        # Graphique de la réactivité
        self.ax2.set_xlabel('Temps (heures)', fontsize=12)
        self.ax2.set_ylabel('Anti-réactivité\nXénon (pcm)', fontsize=12)
        self.ax2.set_title('Effet du Xénon sur la Réactivité', fontsize=12)
        self.ax2.grid(True, alpha=0.3)
        
        # Couleurs cohérentes
        self.iodine_color = '#FF6B35'  # Orange pour l'iode
        self.xenon_color = '#4ECDC4'   # Turquoise pour le xénon
        self.reactivity_color = '#E74C3C'  # Rouge pour l'anti-réactivité

    def update_data(self, data):
        """Ajoute un nouveau point de données à l'historique et met à jour l'affichage"""
        # Ajouter le nouveau point à l'historique
        self.data_history.append({
            'time_hours': data['time_hours'],
            'iodine_concentration': data['iodine_concentration'],
            'xenon_concentration': data['xenon_concentration'],
            'xenon_reactivity_pcm': data['xenon_reactivity_pcm'],
            'power_level': data['power_level']
        })
        
        # Limiter l'historique à 100 points pour la performance
        if len(self.data_history) > 100:
            self.data_history = self.data_history[-100:]
        
        self._plot_data()

    def _plot_data(self):
        """Redessine les graphiques avec l'historique complet des données"""
        if not self.data_history:
            return
            
        # Extraction des données pour le plotting
        times = [d['time_hours'] for d in self.data_history]
        iodine_conc = [d['iodine_concentration'] for d in self.data_history]
        xenon_conc = [d['xenon_concentration'] for d in self.data_history]
        reactivity = [d['xenon_reactivity_pcm'] for d in self.data_history]
        
        # Nettoyage des axes
        self.ax1.clear()
        self.ax2.clear()
        
        # Reconfiguration après nettoyage
        self._setup_plots()
        
        # Graphique des concentrations
        if iodine_conc and max(iodine_conc) > 0:
            self.ax1.plot(times, iodine_conc, color=self.iodine_color, linewidth=2, 
                         label='Iode-135', marker='o', markersize=4)
        if xenon_conc and max(xenon_conc) > 0:
            self.ax1.plot(times, xenon_conc, color=self.xenon_color, linewidth=2, 
                         label='Xénon-135', marker='s', markersize=4)
        
        self.ax1.legend(loc='upper right')
        
        # Graphique de l'anti-réactivité
        if reactivity:
            self.ax2.plot(times, reactivity, color=self.reactivity_color, linewidth=2, 
                         label='Anti-réactivité Xe-135', marker='^', markersize=4)
            self.ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        self.ax2.legend(loc='upper right')
        
        # Ajustement automatique des échelles
        if times:
            for ax in [self.ax1, self.ax2]:
                ax.set_xlim(min(times), max(times) if max(times) > min(times) else min(times) + 1)
        
        self.fig.tight_layout()
        self.draw()

    def clear_history(self):
        """Efface l'historique des données et remet à zéro les graphiques"""
        self.data_history.clear()
        self.ax1.clear()
        self.ax2.clear()
        self._setup_plots()
        self.draw()

    def on_mouse_move(self, event):
        """Gestion du survol de la souris pour afficher des informations"""
        if not self.info_manager:
            return
            
        if event.inaxes == self.ax1:
            info_text = ("Concentrations Iode-135 et Xénon-135\n\n"
                        "L'Iode-135 est un produit de fission qui se désintègre "
                        "en Xénon-135 avec une période de 6,6 heures.\n\n"
                        "Le Xénon-135 est un poison neutronique très efficace "
                        "qui affecte significativement la réactivité du réacteur.")
            self.info_manager.info_requested.emit(info_text)
            
        elif event.inaxes == self.ax2:
            info_text = ("Anti-réactivité due au Xénon-135\n\n"
                        "Le Xénon-135 absorbe fortement les neutrons thermiques, "
                        "créant une anti-réactivité qui peut atteindre plusieurs "
                        "milliers de pcm.\n\n"
                        "Après un arrêt de réacteur, le 'pic Xénon' peut empêcher "
                        "le redémarrage pendant plusieurs heures.")
            self.info_manager.info_requested.emit(info_text)

    def on_axes_leave(self, event):
        """Efface les informations quand la souris quitte les graphiques"""
        if self.info_manager:
            self.info_manager.info_cleared.emit()


class XenonVisualizationWidget(QWidget):
    """Widget principal pour la visualisation Xénon avec bouton Reset intégré"""
    
    # Signal pour communiquer la demande de reset Xénon
    xenon_reset_requested = pyqtSignal()
    
    def __init__(self, parent=None, info_manager: Optional[InfoManager] = None):
        super().__init__(parent)
        self.info_manager = info_manager
        self._setup_ui()
        
    def _setup_ui(self):
        """Configure l'interface utilisateur du widget avec graphique et bouton reset"""
        layout = QVBoxLayout(self)
        
        # Graphique principal
        self.xenon_plot = XenonPlot(self, info_manager=self.info_manager)
        layout.addWidget(self.xenon_plot)
        
        # Layout horizontal pour le bouton centré
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Espace à gauche
        
        # Bouton Reset Xénon
        self.reset_button = QPushButton("Reset Xénon")
        self.reset_button.setMaximumWidth(120)
        self.reset_button.setToolTip("Remettre le Xénon à l'équilibre et effacer les courbes")
        self.reset_button.clicked.connect(self.xenon_reset_requested.emit)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()  # Espace à droite
        layout.addLayout(button_layout)
        
    def update_data(self, data):
        """Met à jour les données du graphique"""
        self.xenon_plot.update_data(data)
        
    def clear_history(self):
        """Efface l'historique"""
        self.xenon_plot.clear_history() 