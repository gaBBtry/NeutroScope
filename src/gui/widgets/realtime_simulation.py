"""
Moteur de simulation temps réel pour NeutroScope

Ce module gère la simulation dynamique continue du réacteur avec contrôles
de type lecteur multimédia (play/pause/stop) et vitesse variable.
"""
import math
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QLabel, QGroupBox
from PyQt6.QtCore import Qt
from typing import Optional

from .info_manager import InfoManager


class RealtimeSimulationEngine(QObject):
    """
    Moteur de simulation temps réel gérant l'avancement automatique du temps
    à 1Hz avec vitesse configurable de 1s/s à 1h/s.
    """
    
    # Signaux émis par le moteur
    time_advanced = pyqtSignal(float)  # Émis à chaque pas de temps (heures avancées)
    simulation_state_changed = pyqtSignal(str)  # État: "playing", "paused", "stopped"
    time_scale_changed = pyqtSignal(float)  # Échelle temporelle en s/s
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Timer principal à 1Hz
        self.timer = QTimer()
        self.timer.timeout.connect(self._advance_simulation_step)
        
        # État de simulation
        self.is_running = False
        self.current_state = "stopped"
        self.time_scale = 1.0  # secondes simulées par seconde réelle (défaut: 1s/s)
        
        # Statistiques
        self.total_sim_time = 0.0  # temps total simulé en heures
        
    def set_time_scale(self, scale_seconds_per_second):
        """
        Définit l'échelle temporelle de la simulation.
        
        Args:
            scale_seconds_per_second: Vitesse en secondes simulées par seconde réelle
                                    (1.0 = temps réel, 3600.0 = 1 heure sim/seconde)
        """
        # Limiter entre 1s/s et 1h/s
        self.time_scale = max(1.0, min(3600.0, scale_seconds_per_second))
        self.time_scale_changed.emit(self.time_scale)
        
    def play(self):
        """Démarre la simulation temps réel"""
        if not self.is_running:
            self.timer.start(1000)  # 1Hz = 1000ms
            self.is_running = True
            self.current_state = "playing"
            self.simulation_state_changed.emit(self.current_state)
            
    def pause(self):
        """Met en pause la simulation"""
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.current_state = "paused"
            self.simulation_state_changed.emit(self.current_state)
            
    def stop(self):
        """Arrête la simulation et remet à zéro le temps"""
        self.timer.stop()
        self.is_running = False
        self.current_state = "stopped"
        
        # Remettre le temps de simulation à zéro
        self.controller.model.simulation_time = 0.0
        # Remettre les concentrations Xénon à l'équilibre
        self.controller.reset_xenon_to_equilibrium()
        
        self.total_sim_time = 0.0
        self.simulation_state_changed.emit(self.current_state)
        
    def get_state(self):
        """Retourne l'état actuel de la simulation"""
        return {
            "state": self.current_state,
            "time_scale": self.time_scale,
            "is_running": self.is_running,
            "total_sim_time": self.total_sim_time
        }
        
    def _advance_simulation_step(self):
        """
        Avance la simulation d'un pas de temps.
        Appelé automatiquement par le timer à 1Hz.
        """
        # Calculer le nombre d'heures à avancer basé sur l'échelle temporelle
        # 1 seconde réelle = time_scale secondes simulées
        hours_to_advance = self.time_scale / 3600.0
        
        # Avancer la simulation via le contrôleur
        self.controller.advance_time(hours_to_advance)
        
        # Mettre à jour les statistiques
        self.total_sim_time += hours_to_advance
        
        # Émettre le signal pour mise à jour UI
        self.time_advanced.emit(hours_to_advance)


class RealtimeControlWidget(QWidget):
    """
    Widget de contrôle pour la simulation temps réel avec boutons play/pause/stop
    et curseur de vitesse temporelle.
    """
    
    # Signal xenon_reset_requested supprimé - maintenant dans le widget Xénon
    
    def __init__(self, engine: RealtimeSimulationEngine, info_manager: Optional[InfoManager] = None, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.info_manager = info_manager
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Configure l'interface utilisateur des contrôles"""
        # Layout principal horizontal pour tout mettre sur une ligne
        main_layout = QHBoxLayout(self)
        
        # Boutons de contrôle (style lecteur multimédia)
        self.play_button = QPushButton("▶")
        self.play_button.setMaximumWidth(40)
        self.play_button.setToolTip("Démarrer la simulation temps réel")
        self.play_button.clicked.connect(self.engine.play)
        
        self.pause_button = QPushButton("⏸⏸")
        self.pause_button.setMaximumWidth(40)
        self.pause_button.setToolTip("Mettre en pause la simulation")
        self.pause_button.clicked.connect(self.engine.pause)
        
        self.stop_button = QPushButton("⏹")
        self.stop_button.setMaximumWidth(40)
        self.stop_button.setToolTip("Arrêter et remettre à zéro la simulation")
        self.stop_button.clicked.connect(self.engine.stop)
        
        # Ajouter les boutons au layout principal
        main_layout.addWidget(self.play_button)
        main_layout.addWidget(self.pause_button)
        main_layout.addWidget(self.stop_button)
        
        # Séparateur supprimé - bouton Reset Xénon déplacé dans le widget Xénon
        
        # Espacement entre boutons et curseur
        main_layout.addSpacing(20)
        
        # Contrôles de vitesse à droite des boutons
        main_layout.addWidget(QLabel("1s/s"))
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(0, 100)  # 0-100 pour mapping logarithmique
        self.speed_slider.setValue(0)  # Défaut: 1s/s
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(25)
        self.speed_slider.valueChanged.connect(self._on_speed_slider_changed)
        self.speed_slider.setToolTip("Ajuster la vitesse de simulation de 1s/s à 1h/s")
        self.speed_slider.setMinimumWidth(200)  # Largeur minimum pour le curseur
        main_layout.addWidget(self.speed_slider)
        
        main_layout.addWidget(QLabel("1h/s"))
        
        # Label indicateur vitesse actuelle
        self.speed_label = QLabel("1 s/s")
        self.speed_label.setStyleSheet("font-weight: bold; color: #2E8B57; margin-left: 10px;")
        self.speed_label.setMinimumWidth(60)
        main_layout.addWidget(self.speed_label)
        
        # Affichage temps de simulation
        self.sim_time_label = QLabel("0.0 h")
        self.sim_time_label.setStyleSheet("color: #2E8B57; margin-left: 10px;")
        self.sim_time_label.setMinimumWidth(50)
        main_layout.addWidget(self.sim_time_label)
        
        # Stretch final pour pousser tout vers la gauche
        main_layout.addStretch()
        
    def _connect_signals(self):
        """Connecte les signaux du moteur de simulation"""
        self.engine.simulation_state_changed.connect(self._update_buttons_state)
        self.engine.time_scale_changed.connect(self._update_speed_display)
        self.engine.time_advanced.connect(self._update_sim_time)
        
    def _on_speed_slider_changed(self, value):
        """Gestion du changement de vitesse via slider"""
        # Mapping logarithmique: 0 → 1s/s, 100 → 3600s/s
        speed = 1.0 * (3600.0 ** (value / 100.0))
        self.engine.set_time_scale(speed)
        
    def _update_speed_display(self, speed):
        """Met à jour l'affichage de la vitesse"""
        if speed >= 3600:
            self.speed_label.setText("1 h/s")
        elif speed >= 60:
            minutes = speed / 60
            self.speed_label.setText(f"{minutes:.1f} min/s")
        else:
            self.speed_label.setText(f"{speed:.1f} s/s")
            
    def _update_buttons_state(self, state):
        """Met à jour l'état des boutons selon l'état de simulation"""
        # Activer/désactiver boutons selon l'état
        self.play_button.setEnabled(state != "playing")
        self.pause_button.setEnabled(state == "playing")
        self.stop_button.setEnabled(state != "stopped")
        
    def _update_sim_time(self, hours_advanced):
        """Met à jour l'affichage du temps de simulation"""
        total_hours = self.engine.total_sim_time
        if total_hours >= 24:
            days = total_hours / 24
            self.sim_time_label.setText(f"{days:.1f} j")
        else:
            self.sim_time_label.setText(f"{total_hours:.1f} h") 