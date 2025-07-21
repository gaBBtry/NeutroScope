"""
Xenon Dynamics Visualization Widget

This widget displays the evolution of Iodine-135 and Xenon-135 concentrations over time,
along with their effect on reactor reactivity.
"""
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
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


class XenonControlWidget(QWidget):
    """Widget de contrôle pour la simulation temporelle automatique du Xénon"""
    
    time_advance_requested = pyqtSignal(float)  # Signal émis pour avancer le temps
    reset_requested = pyqtSignal()  # Signal pour remettre à l'équilibre
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self._advance_simulation_step)
        self.is_running = False
        self._setup_ui()
        
    def _setup_ui(self):
        """Configure l'interface utilisateur des contrôles"""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("Simulation Temporelle Xénon")
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Contrôles de simulation
        control_layout = QHBoxLayout()
        
        # Boutons Play/Pause/Stop
        self.play_button = QPushButton("▶ Play")
        self.play_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.play_button.clicked.connect(self._toggle_simulation)
        control_layout.addWidget(self.play_button)
        
        self.stop_button = QPushButton("⏹ Stop & Reset")
        self.stop_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.stop_button.clicked.connect(self._stop_and_reset)
        control_layout.addWidget(self.stop_button)
        
        layout.addLayout(control_layout)
        
        # Paramètres de simulation
        params_layout = QVBoxLayout()
        
        # Pas de temps de simulation (modifiable en temps réel)
        step_layout = QHBoxLayout()
        step_layout.addWidget(QLabel("Pas de temps:"))
        self.time_step_spinbox = QSpinBox()
        self.time_step_spinbox.setMinimum(1)
        self.time_step_spinbox.setMaximum(24)
        self.time_step_spinbox.setValue(1)
        self.time_step_spinbox.setSuffix(" h")
        self.time_step_spinbox.valueChanged.connect(self._update_simulation_params)
        step_layout.addWidget(self.time_step_spinbox)
        
        # Vitesse de simulation (intervalle entre pas)
        step_layout.addWidget(QLabel("Vitesse:"))
        self.speed_spinbox = QSpinBox()
        self.speed_spinbox.setMinimum(100)
        self.speed_spinbox.setMaximum(5000)
        self.speed_spinbox.setValue(1000)
        self.speed_spinbox.setSuffix(" ms")
        self.speed_spinbox.valueChanged.connect(self._update_simulation_params)
        step_layout.addWidget(self.speed_spinbox)
        
        params_layout.addLayout(step_layout)
        layout.addLayout(params_layout)
        
        # Info sur l'état actuel
        self.status_label = QLabel("État: Prêt - Appuyez sur Play pour démarrer")
        self.status_label.setStyleSheet("color: #2E8B57; font-style: italic; margin-top: 10px;")
        layout.addWidget(self.status_label)
        
    def _toggle_simulation(self):
        """Démarre ou met en pause la simulation"""
        if not self.is_running:
            self._start_simulation()
        else:
            self._pause_simulation()
    
    def _start_simulation(self):
        """Démarre la simulation automatique"""
        self.is_running = True
        self.play_button.setText("⏸ Pause")
        self.play_button.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        
        # Configurer le timer avec la vitesse actuelle
        interval_ms = self.speed_spinbox.value()
        self.simulation_timer.start(interval_ms)
        
        self.status_label.setText("État: Simulation en cours...")
        self.status_label.setStyleSheet("color: #4CAF50; font-style: italic; margin-top: 10px;")
    
    def _pause_simulation(self):
        """Met en pause la simulation"""
        self.is_running = False
        self.play_button.setText("▶ Play")
        self.play_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        self.simulation_timer.stop()
        
        self.status_label.setText("État: Simulation en pause")
        self.status_label.setStyleSheet("color: #FF9800; font-style: italic; margin-top: 10px;")
    
    def _stop_and_reset(self):
        """Arrête la simulation et remet à l'équilibre"""
        # Arrêter le timer d'abord
        if self.simulation_timer.isActive():
            self.simulation_timer.stop()
        
        # S'assurer que l'état est cohérent
        self.is_running = False
        self.play_button.setText("▶ Play")
        self.play_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        # Émettre le signal de reset
        self.reset_requested.emit()
        
        self.status_label.setText("État: Arrêté et remis à l'équilibre")
        self.status_label.setStyleSheet("color: #2E8B57; font-style: italic; margin-top: 10px;")
    
    
    def _advance_simulation_step(self):
        """Avance la simulation d'un pas (appelée par le timer)"""
        # Vérifier que la simulation est toujours active et que le timer tourne
        if self.is_running and self.simulation_timer.isActive():
            try:
                hours = self.time_step_spinbox.value()
                self.time_advance_requested.emit(hours)
            except Exception as e:
                # En cas d'erreur, arrêter la simulation pour éviter les plantages
                print(f"Erreur lors de l'avancement temporel: {e}")
                self._stop_and_reset()
    
    def _update_simulation_params(self):
        """Met à jour les paramètres de simulation en temps réel"""
        if self.is_running:
            # Redémarrer le timer avec le nouveau délai
            interval_ms = self.speed_spinbox.value()
            self.simulation_timer.start(interval_ms)
    
    def reset_status(self):
        """Remet à zéro le statut (compatibilité)"""
        self._stop_and_reset()
    
    def closeEvent(self, event):
        """Nettoyage lors de la fermeture du widget"""
        if hasattr(self, 'simulation_timer') and self.simulation_timer.isActive():
            self.simulation_timer.stop()
        super().closeEvent(event)
    
    def __del__(self):
        """Destructeur pour s'assurer que le timer est arrêté"""
        try:
            if hasattr(self, 'simulation_timer') and self.simulation_timer and self.simulation_timer.isActive():
                self.simulation_timer.stop()
        except (RuntimeError, AttributeError):
            # Objet Qt déjà détruit, ignorer l'erreur
            pass


class XenonVisualizationWidget(QWidget):
    """Widget principal combinant le graphique Xénon et ses contrôles"""
    
    def __init__(self, parent=None, info_manager: Optional[InfoManager] = None):
        super().__init__(parent)
        self.info_manager = info_manager
        self._setup_ui()
        
    def _setup_ui(self):
        """Configure l'interface utilisateur du widget complet"""
        layout = QVBoxLayout(self)
        
        # Graphique principal
        self.xenon_plot = XenonPlot(self, info_manager=self.info_manager)
        layout.addWidget(self.xenon_plot, stretch=3)
        
        # Contrôles
        self.controls = XenonControlWidget(self)
        layout.addWidget(self.controls, stretch=1)
        
    def update_data(self, data):
        """Met à jour les données du graphique"""
        self.xenon_plot.update_data(data)
        
    def clear_history(self):
        """Efface l'historique"""
        self.xenon_plot.clear_history()
        self.controls.reset_status()