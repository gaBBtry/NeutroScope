# Documented Tasks and Workflows

Ce fichier documente les tâches répétitives et leurs workflows pour faciliter les futures implémentations.

---

## Implémentation d'Optimisations Physiques Majeures

**Dernière exécution :** Janvier 2025  
**Contexte :** Transformation de NeutroScope d'un simulateur statique vers un simulateur dynamique avancé

### Type de tâche :
Extension majeure avec nouveaux modèles physiques et capacités temporelles

### Fichiers principaux modifiés :
- `config.json` - Nouveaux paramètres physiques et section xenon_dynamics
- `src/model/config.py` - Extensions pour nouveaux paramètres  
- `src/model/reactor_model.py` - Modèles physiques et équations temporelles
- `src/controller/reactor_controller.py` - Nouvelles méthodes de contrôle temporel
- `src/gui/widgets/xenon_plot.py` - **NOUVEAU** widget de visualisation temporelle
- `src/gui/widgets/neutron_cycle_plot.py` - Info-bulles enrichies pour nouveaux effets
- `src/gui/visualization.py` - Nouvel onglet et intégration
- `src/gui/main_window.py` - Contrôles temporels et nouveaux presets

### Workflow Phase 1 : Affinement Physique (Température Modérateur)

**Étapes :**
1. **Configuration** : Ajouter paramètres `P_MOD_TEMP_COEFF` et `P_REF_MOD_TEMP_C` dans `config.json`
2. **Modèle** : Étendre `calculate_four_factors()` pour intégrer l'effet modérateur sur facteur `p`
3. **Validation** : Vérifier cohérence physique (effet opposé à l'effet Doppler)
4. **Interface** : Enrichir tooltips du widget `NeutronCyclePlot` avec explications du double effet
5. **Tests** : Valider que les valeurs par défaut donnent des résultats physiquement sensés

### Workflow Phase 2 : Dynamique Temporelle (Xénon-135)

**Étapes :**
1. **Configuration étendue** :
   - Section `xenon_dynamics` avec constantes de désintégration, rendements, sections efficaces
   - Paramètres physiques basés sur données REP réelles

2. **Modèle physique** :
   - Implémentation équations de Bateman (I-135 → Xe-135)
   - Méthodes `calculate_xenon_equilibrium()` et `update_xenon_dynamics()`
   - Intégration dans le facteur `f` (utilisation thermique)
   - Gestion de l'historique temporel

3. **Nouveau widget de visualisation** :
   - Création `XenonVisualizationWidget` avec architecture MVC complète
   - Graphiques jumeaux : concentrations + réactivité
   - Contrôles intégrés : avancement temps, reset équilibre
   - Gestion des échelles et légendes dynamiques

4. **Extensions de l'architecture** :
   - Nouvelles méthodes dans `ReactorController` pour contrôles temporels
   - Nouvel onglet "Dynamique Xénon" dans l'interface principale
   - Connexion des signaux et slots pour contrôles temps réel

5. **Presets enrichis** :
   - "Fonctionnement Xénon équilibre" : État stable puissance nominale
   - "Post-arrêt pic Xénon" : Simulation phénomène transitoire

### Bonnes pratiques identifiées :

#### Architecture
- **Respect MVC strict** : Même avec complexité temporelle, maintenir séparation claire
- **Configuration externalisée** : Tous nouveaux paramètres dans `config.json`
- **Performance** : Solutions analytiques plutôt que numériques pour stabilité

#### Interface temporelle
- **Contrôles intuitifs** : Boutons pour avancement par heures (1h, 6h, 12h, 24h)
- **Visualisation continue** : Graphiques mis à jour en temps réel avec historique
- **Reset intelligent** : Retour à l'équilibre avec recalcul complet de l'état

#### Physique
- **Constantes réalistes** : Utiliser données de réacteurs REP pour crédibilité
- **Validation croisée** : Vérifier cohérence entre modèles statique et temporel
- **Pédagogie** : Maintenir explications physiques dans tous les nouveaux éléments

### Points critiques :

1. **Gestion du temps** : Architecture pour historique sans fuite mémoire
2. **Performance temps réel** : Calculs optimisés (<100ms par step)
3. **Interface réactive** : Mise à jour asynchrone des graphiques
4. **Cohérence des unités** : Vérification systématique (concentrations, temps, réactivité)
5. **Tests de validation** : Comparaison avec valeurs théoriques connues

### Code type pour extension temporelle :

```python
# Dans ReactorModel - équations de Bateman
def update_xenon_dynamics(self, dt_hours: float):
    # Solution analytique exacte
    lambda_i = self.config.xenon_dynamics['I135_DECAY_CONSTANT']
    lambda_xe = self.config.xenon_dynamics['XE135_DECAY_CONSTANT']
    # ... équations de Bateman ...

# Dans le widget - contrôles temporels
def setup_time_controls(self):
    time_layout = QHBoxLayout()
    for hours in [1, 6, 12, 24]:
        btn = QPushButton(f"+{hours}h")
        btn.clicked.connect(lambda checked, h=hours: self.advance_time(h))
        time_layout.addWidget(btn)
```

### Extensions possibles futures :
- Autres isotopes (Samarium-149, etc.)
- Couplages thermohydrauliques
- Cinétique point avec précurseurs retardés
- Contrôle automatique/pilotage

---

## Intégrer InfoManager avec un Widget de Visualisation

**Dernière exécution :** 07/07/2025  
**Contexte :** Correction du système de survol d'informations après refactoring

### Fichiers à modifier selon le type de widget :

#### Pour un widget Matplotlib (`FigureCanvasQTAgg`)
**Exemples :** `flux_plot.py`, `four_factors_plot.py`, `neutron_balance_plot.py`, `pilotage_diagram_plot.py`

**Modifications requises :**
1. **Constructeur :** Ajouter `info_manager: Optional[InfoManager] = None` 
2. **Stockage :** `self.info_manager = info_manager`
3. **Connexions :** Garder les `mpl_connect` existants pour `motion_notify_event` et `axes_leave_event`
4. **Méthodes de callback :** Modifier pour utiliser `self.info_manager.info_requested.emit()` et `self.info_manager.info_cleared.emit()`

#### Pour un widget QPainter (`QWidget`)
**Exemples :** `neutron_cycle_plot.py`

**Modifications requises :**
1. **Constructeur :** Ajouter `info_manager: Optional[InfoManager] = None`
2. **Stockage :** `self.info_manager = info_manager`
3. **Mouse tracking :** `self.setMouseTracking(True)` (déjà présent généralement)
4. **Événements :** Implémenter `mouseMoveEvent` et `leaveEvent`
5. **Hit testing :** Logique pour détecter sur quoi survole l'utilisateur
6. **Émission :** Utiliser `self.info_manager.info_requested.emit()` et `self.info_manager.info_cleared.emit()`

### Modifications dans les classes parentes :

#### VisualizationPanel
**Fichier :** `src/gui/visualization.py`

1. **Constructeur :** Ajouter `info_manager: InfoManager` comme paramètre requis
2. **Stockage :** `self.info_manager = info_manager`
3. **Initialisation des widgets :** Passer `info_manager=self.info_manager` à tous les widgets de visualisation
4. **Nettoyage :** Supprimer les méthodes obsolètes comme `set_external_info_callback`

#### MainWindow
**Fichier :** `src/gui/main_window.py`

1. **Création :** Passer l'InfoManager lors de la création du VisualizationPanel :
   ```python
   self.visualization_panel = VisualizationPanel(self, info_manager=self.info_manager)
   ```

### Workflow étape par étape :

1. **Identifier le type de widget** (Matplotlib vs QPainter)
2. **Modifier le constructeur** pour accepter InfoManager
3. **Adapter les événements de souris** selon le type
4. **Remplacer les anciens callbacks** par les émissions de signaux InfoManager
5. **Supprimer le code de fallback** (ex: `elif hasattr(self.parent(), 'update_info_panel')`)
6. **Mettre à jour la chaîne d'initialisation** depuis MainWindow → VisualizationPanel → Widgets
7. **Tester** le survol et la fonctionnalité de la touche 'i'

### Points critiques à retenir :

- **Types cohérents :** Attention aux `QPointF` vs `QPoint` dans les widgets QPainter
- **Nettoyage automatique :** L'InfoManager gère automatiquement l'enregistrement/désenregistrement
- **Pas de fallback :** Supprimer complètement les anciens mécanismes de callback
- **Tests :** Vérifier que les informations s'affichent correctement et que la touche 'i' fonctionne
- **Performance :** Les émissions de signaux sont légères et n'impactent pas les performances

### Exemple de code type :

```python
# Dans le constructeur
def __init__(self, parent=None, width=5, height=4, dpi=100, info_manager: Optional[InfoManager] = None):
    # ... init existant ...
    self.info_manager = info_manager

# Dans les callbacks de souris
def on_mouse_move(self, event):
    # ... logique de détection ...
    if self.info_manager:
        self.info_manager.info_requested.emit(info_text)

def on_axes_leave(self, event):
    if self.info_manager:
        self.info_manager.info_cleared.emit()
```

---

## Améliorer la Lisibilité d'un Widget de Visualisation

**Dernière exécution :** Décembre 2024  
**Contexte :** Amélioration du widget NeutronCyclePlot pour une meilleure expérience éducative

### Améliorations typiques :

#### Tailles de Police
- **Titres des boîtes :** 9pt → 14pt
- **Valeurs principales :** 12pt → 18pt  
- **Labels des facteurs :** 10pt → 14pt
- **Valeur centrale (k_eff) :** 16pt → 24pt
- **Texte de statut :** 12pt → 16pt

#### Tailles des Éléments
- **Boîtes :** 160×70 → 200×90 pixels
- **Marges :** 50px → 70px
- **Espace central :** Augmenté proportionnellement

#### Localisation et Contenu
- **Traduction complète** en français des termes techniques
- **Informations enrichies** avec contexte physique et valeurs d'énergie
- **Descriptions détaillées** pour les tooltips éducatifs
- **Ajout de formules** comme la formule des six facteurs

#### Visuels
- **Couleurs d'état :** Rouge (critique), vert (surcritique), bleu (sous-critique)
- **Épaisseur des traits :** Augmentée pour une meilleure visibilité
- **Contraste :** Amélioré pour la lisibilité

### Workflow :
1. **Augmenter toutes les tailles de police** d'au moins 30-50%
2. **Agrandir les éléments graphiques** proportionnellement
3. **Traduire tout le contenu** en français technique approprié
4. **Enrichir les informations** avec du contexte éducatif
5. **Tester la lisibilité** sur différentes tailles d'écran
6. **Ajuster l'espacement** pour éviter les chevauchements 