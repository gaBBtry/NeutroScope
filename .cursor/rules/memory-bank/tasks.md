# Documented Tasks and Workflows

Ce fichier documente les tâches répétitives et leurs workflows pour faciliter les futures implémentations.

---

## Suppression d'Interface Complexe (Simplification UX)

**Dernière exécution :** Janvier 2025  
**Contexte :** Suppression du gestionnaire de presets avancé pour simplifier l'expérience utilisateur

### Type de tâche :
Simplification d'interface avec préservation des fonctionnalités backend essentielles

### Fichiers modifiés :
- `src/gui/main_window.py` - Suppression bouton "Gérer..." et méthodes associées
- `src/gui/widgets/preset_manager_dialog.py` - **SUPPRIMÉ** complètement
- Documentation mise à jour (memory bank, tooltips)

### Workflow de Suppression Propre :

**Étapes :**
1. **Analyse des dépendances** :
   - Identifier tous les usages du composant à supprimer
   - Cartographier les imports et références
   - Vérifier les signals/slots connectés

2. **Suppression progressive** :
   - Supprimer l'import en premier
   - Supprimer les références dans l'interface (boutons, connexions)
   - Supprimer les méthodes appelantes
   - Supprimer le fichier en dernier

3. **Mise à jour documentation** :
   - Textes d'aide et tooltips
   - Documentation memory bank
   - Tests si nécessaire

### Bonnes pratiques identifiées :

#### **Ordre de suppression critique**
1. **Imports** - Supprimer en premier pour détecter les erreurs de compilation
2. **Éléments UI** - Boutons, widgets, connexions
3. **Méthodes** - Méthodes qui utilisaient le composant supprimé
4. **Fichier** - Supprimer le fichier source en dernier
5. **Documentation** - Mise à jour cohérente de tous les textes

#### **Validation post-suppression**
- Test de compilation Python (`python -m py_compile`)
- Test d'import du module principal
- Vérification fonctionnement des fonctionnalités conservées
- Mise à jour memory bank et documentation

### Points critiques :
1. **Backend préservé** : Garder les fonctionnalités utiles en arrière-plan
2. **UX cohérente** : S'assurer que l'interface reste logique après suppression
3. **Documentation synchronisée** : Mettre à jour tous les textes d'aide
4. **Tests complets** : Vérifier que l'application reste stable

### Code type pour suppression propre :

```python
# AVANT - Interface complexe
def create_control_panel(self):
    # ...
    self.manage_presets_button = QPushButton("Gérer...")
    self.manage_presets_button.clicked.connect(self.open_preset_manager)
    # ...

def open_preset_manager(self):
    dialog = PresetManagerDialog(...)
    dialog.preset_applied.connect(self.on_preset_applied_from_manager)
    # ...

# APRÈS - Interface simplifiée
def create_control_panel(self):
    # Bouton "Gérer..." supprimé
    # Seuls dropdown + bouton Reset conservés
    # ...

# Méthodes open_preset_manager(), on_preset_applied_from_manager() 
# et refresh_preset_combo() complètement supprimées
```

---

## Refactor Complet d'un Système de Gestion (Presets Avancés) - OBSOLÈTE

**Dernière exécution :** Janvier 2025  
**Contexte :** Transformation du système de presets simple vers un système professionnel complet

### Type de tâche :
Refactor majeur avec nouveau modèle de données, interface GUI sophistiquée, et intégration complète

### Fichiers principaux créés/modifiés :
- **NOUVEAU** `src/model/preset_model.py` - Système de données avancé complet
- **NOUVEAU** `src/gui/widgets/preset_manager_dialog.py` - Interface GUI sophistiquée
- **NOUVEAU** `user_presets.json` - Fichier de persistance utilisateur
- `src/model/reactor_model.py` - Extensions pour intégration presets avancés
- `src/controller/reactor_controller.py` - Méthodes de gestion presets
- `src/gui/main_window.py` - Bouton d'accès et synchronisation

### Workflow Phase 1 : Architecture de Données

**Étapes :**
1. **Analyse des besoins** :
   - Identifier limitations du système existant (pas de métadonnées, validation, organisation)
   - Définir exigences nouvelles (catégorisation, temporel, import/export, validation)
   - Concevoir structure de données extensible

2. **Création du modèle de données** :
   - Implémenter `PresetData` comme dataclass avec validation intégrée
   - Créer enums `PresetCategory` et `PresetType` pour organisation
   - Ajouter métadonnées complètes (ID, dates, auteur, descriptions, tags)
   - Support état temporel (concentrations I-135/Xe-135, temps simulation)

3. **Gestionnaire sophistiqué** :
   - Classe `PresetManager` avec CRUD complet
   - Chargement automatique depuis `config.json` (système) et `user_presets.json` (utilisateur)
   - Validation robuste avec vérification plages physiques
   - Persistance automatique avec gestion versions

### Workflow Phase 2 : Interface Graphique Avancée

**Étapes :**
1. **Dialog principal** :
   - Créer `PresetManagerDialog` avec architecture en onglets
   - Onglet "Parcourir" : Vue hiérarchique par catégories avec filtrage
   - Onglet "Créer/Modifier" : Formulaires avec validation temps réel
   - Onglet "Import/Export" : Fonctions partage avec gestion erreurs

2. **Widgets spécialisés** :
   - Vue arborescente avec icônes par catégorie
   - Formulaires adaptatifs selon type de preset
   - Prévisualisation et comparaison de presets
   - Gestion des métadonnées avec interfaces intuitives

3. **Gestion des signaux** :
   - Signal `preset_applied` pour communication avec interface principale
   - Validation en temps réel avec feedback visuel
   - Synchronisation bidirectionnelle avec système existant

### Workflow Phase 3 : Intégration Système

**Étapes :**
1. **Extension du modèle** :
   - Intégrer `PresetManager` dans `ReactorModel`
   - Adapter méthodes `apply_preset()` et `save_preset()` pour nouveau système
   - Support des états temporels dans les presets
   - Maintenir rétrocompatibilité avec presets existants

2. **Extension du contrôleur** :
   - Nouvelles méthodes dans `ReactorController`
   - `get_preset_manager()`, `create_preset_from_current_state()`
   - `export_presets()`, `import_presets()`
   - `get_current_state_as_preset_data()`

3. **Interface principale** :
   - Ajouter bouton "Gérer..." à côté du QComboBox existant
   - Méthode `open_preset_manager()` avec gestion signaux
   - Synchronisation `update_preset_combo()` pour actualisation
   - Préservation expérience utilisateur existante

### Bonnes pratiques identifiées :

#### **Architecture de Données**
- **Validation intégrée** : Dataclass avec méthodes `validate()` automatiques
- **Sérialisation robuste** : `to_dict()` et `from_dict()` avec gestion types Python
- **Extensibilité** : Structure prête pour ajout futurs champs sans breaking changes
- **Versioning** : Support versions de format pour migrations futures

#### **Interface Utilisateur**
- **Progressive disclosure** : Interface adaptée niveau utilisateur (débutant → expert)
- **Feedback immédiat** : Validation temps réel avec messages clairs
- **Cohérence visuelle** : Respect guidelines Qt avec icônes et couleurs cohérentes
- **Accessibilité** : Raccourcis clavier et navigation au clavier

#### **Intégration Système**
- **Rétrocompatibilité** : Ancien système continue de fonctionner pendant transition
- **Migration douce** : Presets existants automatiquement convertis au nouveau format
- **Synchronisation** : État cohérent entre ancien et nouveau système
- **Fallback gracieux** : Gestion élégante des erreurs de chargement/sauvegarde

### Points critiques :

1. **Gestion des versions** : Format de fichier évolutif sans perte de données
2. **Performance** : Chargement rapide même avec nombreux presets
3. **Validation** : Vérification cohérence sans bloquer interface
4. **Import/Export** : Gestion robuste erreurs avec feedback utilisateur
5. **Tests** : Validation complète fonctionnalités CRUD et intégration

### Code type pour extension système gestion :

```python
# Modèle de données avec validation
@dataclass
class PresetData:
    # Champs requis
    name: str
    description: str
    category: PresetCategory
    # Paramètres physiques
    control_rod_position: float
    # ... autres paramètres
    # Métadonnées
    created_date: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def validate(self) -> List[str]:
        """Validation avec retour d'erreurs explicites"""
        errors = []
        if not (0 <= self.control_rod_position <= 100):
            errors.append("Position barres doit être 0-100%")
        return errors

# Gestionnaire avec CRUD complet
class PresetManager:
    def __init__(self):
        self._presets = {}
        self._load_system_presets()
        self._load_user_presets()
    
    def create_preset(self, name: str, **params) -> Optional[PresetData]:
        """Création avec validation automatique"""
        preset = PresetData(name=name, **params)
        errors = preset.validate()
        if errors:
            raise ValueError(f"Validation échouée: {', '.join(errors)}")
        
        self._presets[preset.id] = preset
        self._save_user_presets()
        return preset

# Interface avec validation temps réel
class PresetManagerDialog(QDialog):
    preset_applied = pyqtSignal(str)  # Signal pour communication
    
    def setup_validation(self):
        """Connexion validation temps réel"""
        self.name_edit.textChanged.connect(self.validate_form)
        self.description_edit.textChanged.connect(self.validate_form)
        # ... autres connexions
    
    def validate_form(self):
        """Validation avec feedback visuel immédiat"""
        errors = []
        if not self.name_edit.text().strip():
            errors.append("Nom requis")
        
        if errors:
            self.create_button.setEnabled(False)
            self.error_label.setText("; ".join(errors))
        else:
            self.create_button.setEnabled(True)
            self.error_label.clear()
```

### Extensions futures possibles :
- Presets avec dépendances temporelles (séquences)
- Sharing cloud avec authentification
- Templates de presets pour créations rapides
- Historique des modifications avec rollback
- Export formats multiples (PDF, PowerPoint pour cours)

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
3. **Méthodes d'événements :** Implémenter ou modifier `mouseMoveEvent` et `leaveEvent`
4. **Gestion des zones :** Utiliser des rectangles ou régions pour détecter le survol

### Workflow général :

1. **Modification du constructeur du widget**
2. **Implémentation/modification des gestionnaires d'événements souris**
3. **Mise à jour de la création du widget dans la classe parent** pour passer `info_manager`
4. **Test du système de survol** avec différents éléments du widget

### Exemple de code :

```python
# Pour Matplotlib
def __init__(self, parent=None, info_manager: Optional[InfoManager] = None):
    super().__init__(parent)
    self.info_manager = info_manager
    if self.info_manager:
        self.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.mpl_connect('axes_leave_event', self.on_axes_leave)

def on_mouse_move(self, event):
    if self.info_manager and event.inaxes:
        info_text = "Information contextuelle appropriée..."
        self.info_manager.info_requested.emit(info_text)

# Pour QPainter  
def mouseMoveEvent(self, event):
    if self.info_manager:
        # Logique pour déterminer la zone survolée
        zone_info = self._get_zone_info(event.pos())
        if zone_info:
            self.info_manager.info_requested.emit(zone_info)
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