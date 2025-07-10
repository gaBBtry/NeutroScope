"""
Classe de base pour tous les widgets matplotlib dans NeutroScope.
Élimine les redondances de code entre FluxDistributionPlot, FourFactorsPlot, 
NeutronBalancePlot et XenonPlot.
"""
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from typing import Optional
from .info_manager import InfoManager


class BaseMatplotlibWidget(FigureCanvasQTAgg):
    """
    Classe de base abstraite pour tous les widgets matplotlib de NeutroScope.
    
    Fournit les fonctionnalités communes :
    - Initialisation figure matplotlib
    - Gestion des événements souris
    - Intégration InfoManager
    - Layout automatique
    """
    
    def __init__(self, parent=None, width=5, height=4, dpi=100, info_manager: Optional[InfoManager] = None):
        """
        Initialise le widget matplotlib de base.
        
        Args:
            parent: Widget parent Qt
            width: Largeur de la figure en pouces
            height: Hauteur de la figure en pouces  
            dpi: Résolution en points par pouce
            info_manager: Gestionnaire d'informations contextuelles
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.info_manager = info_manager
        
        self._setup_mouse_events()
        self.fig.tight_layout()
        
        # Permettre aux sous-classes d'initialiser leur contenu spécifique
        self._setup_plot()
    
    def _setup_mouse_events(self):
        """Configure les événements souris standard pour tous les widgets matplotlib."""
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('axes_leave_event', self.on_axes_leave)
    
    def on_axes_leave(self, event):
        """
        Gère la sortie de la souris des axes.
        Implémentation commune pour tous les widgets.
        """
        if self.info_manager:
            self.info_manager.info_cleared.emit()
    
    def _setup_plot(self):
        """
        Initialise le contenu spécifique du plot.
        À implémenter par chaque sous-classe.
        """
        raise NotImplementedError("Les sous-classes doivent implémenter _setup_plot()")
    
    def on_mouse_move(self, event):
        """
        Gère le mouvement de la souris sur le plot.
        À implémenter par chaque sous-classe selon ses besoins.
        """
        raise NotImplementedError("Les sous-classes doivent implémenter on_mouse_move()")
    
    def update_plot(self, *args, **kwargs):
        """
        Met à jour le contenu du plot avec de nouvelles données.
        À implémenter par chaque sous-classe selon ses besoins.
        """
        raise NotImplementedError("Les sous-classes doivent implémenter update_plot()") 