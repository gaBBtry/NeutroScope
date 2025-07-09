# Documented Tasks and Workflows

Ce fichier documente les tâches répétitives et leurs workflows pour faciliter les futures implémentations.

---

## Implémentation Système de Grappes R et GCP avec Granularité Fine

**Dernière exécution :** Janvier 2025  
**Contexte :** Transformation complète du système de contrôle des barres pour distinguer les groupes R (Régulation) et GCP (Compensation de Puissance)

### Type de tâche :
Extension majeure d'architecture avec nouveaux paramètres physiques, interface utilisateur sophistiquée et granularité industrielle

### Problème identifié :
- **Simplification excessive** : Système unique de barres ne reflétait pas la réalité industrielle des REP
- **Granularité limitée** : Échelle 0-100% insuffisante pour précision opérationnelle
- **Absence de distinction fonctionnelle** : Pas de différenciation entre rôles de régulation et compensation
- **Écart formation-industrie** : Interface non représentative des systèmes de contrôle professionnels

### Solution implémentée :
- **Distinction physique authentique** : Groupes R et GCP séparés avec rôles industriels spécifiques
- **Granularité professionnelle** : 228 pas par groupe selon standards REP
- **Worth pondéré réaliste** : R=30%, GCP=70% selon pratiques industrielles
- **Interface intuitive dédiée** : Contrôles séparés avec granularité adaptée aux rôles

### Fichiers principaux modifiés :
- `config.json` - **NOUVEAU** : Section `control_rod_groups` complète
- `src/model/reactor_model.py` - **ÉTENDU** : Paramètres R/GCP + calculs pondérés
- `src/model/preset_model.py` - **ADAPTÉ** : Support positions R/GCP dans presets
- `src/controller/reactor_controller.py` - **NOUVEAU** : Méthodes dédiées R/GCP
- `src/gui/main_window.py` - **NOUVEAU** : Interface grappes séparées
- `src/gui/widgets/flux_plot.py` - **ADAPTÉ** : Position équivalente pour visualisation

### Workflow d'Implémentation Complète :

**Étape 1 : Configuration et Modèle de Données**
1. **Définition paramètres** : Création section `control_rod_groups` dans `config.json`
   - Groupe R : worth_fraction (0.3), plages (0-228), granularité (1-10 pas)
   - Groupe GCP : worth_fraction (0.7), plages (0-228), granularité (5-50 pas)
   - Conversion : Équivalence 228 pas, worth de référence
2. **Extension modèle physique** : Ajout attributs `rod_group_R_position` et `rod_group_GCP_position`
3. **Calculs pondérés** : Implémentation `_get_total_rod_worth_fraction()` et `_get_equivalent_rod_position_percent()`
4. **Rétrocompatibilité** : Méthode conversion pour visualisations existantes

**Étape 2 : Logique Physique et Calculs**
1. **Intégration calculs neutroniques** : Adaptation facteur `f` pour worth pondéré
2. **Méthodes de mise à jour** : `update_rod_group_R_position()` et `update_rod_group_GCP_position()`
3. **Validation plages** : Vérification 0-228 pas pour chaque groupe
4. **Tests cohérence physique** : Validation k_eff avec nouvelles grappes

**Étape 3 : Extension Contrôleur**
1. **Nouvelles méthodes dédiées** :
   - `update_rod_group_R_position(position)` : Mise à jour groupe R
   - `update_rod_group_GCP_position(position)` : Mise à jour groupe GCP
   - `get_rod_group_positions()` : Récupération positions actuelles
   - `get_rod_groups_info()` : Informations configuration complète
2. **Rétrocompatibilité** : `update_control_rod_position()` convertit % en positions équivalentes
3. **Validation paramètres** : Vérification plages et retour paramètres réacteur

**Étape 4 : Interface Utilisateur Sophistiquée**
1. **Groupes séparés** :
   - **Groupe R** : Slider (0-228) + SpinBox + boutons ±1 pas
   - **Groupe GCP** : Slider (0-228) + SpinBox + boutons ±5 pas
2. **Convention intuitive** : Slider droite = insertion, suffixe " pas"
3. **Synchronisation parfaite** : Sliders et SpinBoxes liés avec conversion automatique
4. **Information contextuelle** : Tooltips expliquant rôles R vs GCP
5. **Signaux dédiés** : Connexions séparées pour chaque groupe

**Étape 5 : Adaptation Système Presets**
1. **Extension PresetData** : Ajout champs `rod_group_R_position` et `rod_group_GCP_position`
2. **Validation étendue** : Plages 0-228 pas pour chaque groupe
3. **Conversion presets existants** : Migration des valeurs % vers positions R/GCP
4. **Cohérence presets système** : Adaptation tous scénarios dans config.json

**Étape 6 : Adaptation Visualisations**
1. **Position équivalente** : Utilisation `_get_equivalent_rod_position_percent()` dans flux_plot
2. **Rétrocompatibilité visualisations** : Maintien fonctionnement existant
3. **Information enrichie** : Tooltips incluant info grappes R/GCP

### Bonnes pratiques identifiées :

#### **Extension Majeure d'Architecture**
- **Planification globale** : Identifier TOUS les points d'impact avant démarrage
- **Rétrocompatibilité prioritaire** : Maintenir fonctionnement existant pendant transition
- **Validation continue** : Tests à chaque étape pour éviter régressions
- **Documentation synchronisée** : Mise à jour parallèle de tous textes d'aide

#### **Système Multi-Paramètres**
- **Distinction claire** : Séparation physique et fonctionnelle des paramètres
- **Calculs pondérés** : Méthodes centralisées pour combinaison de paramètres
- **Interface adaptée** : Granularité et contrôles adaptés aux rôles spécifiques
- **Configuration externalisée** : Tous paramètres modifiables sans recompilation

#### **Granularité Industrielle**
- **Standards authentiques** : Adoption granularité REP réelle (228 pas)
- **Interface progressive** : Granularité adaptée aux niveaux d'usage
- **Conversion automatique** : Équivalences pour compatibilité systèmes existants
- **Validation experte** : Confirmation conformité avec pratiques industrielles

### Code type pour système multi-grappes :

```python
# Configuration (config.json)
"control_rod_groups": {
    "R": {
        "description": "Groupe de Régulation",
        "worth_fraction": 0.3,
        "min_step": 1,
        "max_step": 10,
        "normal_step": 5,
        "position_range": [0, 228]
    },
    "GCP": {
        "description": "Groupe de Compensation de Puissance", 
        "worth_fraction": 0.7,
        "min_step": 5,
        "max_step": 50,
        "normal_step": 20,
        "position_range": [0, 228]
    }
}

# Modèle - Calculs pondérés
def _get_total_rod_worth_fraction(self):
    steps_max = config.control_rod_groups['conversion']['steps_to_percent']
    
    r_insertion_fraction = (steps_max - self.rod_group_R_position) / steps_max
    gcp_insertion_fraction = (steps_max - self.rod_group_GCP_position) / steps_max
    
    r_worth = config.control_rod_groups['R']['worth_fraction']
    gcp_worth = config.control_rod_groups['GCP']['worth_fraction']
    
    total_worth_fraction = (r_insertion_fraction * r_worth + 
                           gcp_insertion_fraction * gcp_worth)
    return total_worth_fraction

# Interface - Contrôles séparés
def create_rod_groups_controls(self):
    # Groupe R
    self.rod_R_slider = QSlider(Qt.Orientation.Horizontal)
    self.rod_R_slider.setRange(0, 228)
    self.rod_R_spinbox = QDoubleSpinBox()
    self.rod_R_spinbox.setRange(0, 228)
    self.rod_R_plus_btn = QPushButton("+1")
    self.rod_R_minus_btn = QPushButton("-1")
    
    # Groupe GCP 
    self.rod_GCP_slider = QSlider(Qt.Orientation.Horizontal)
    self.rod_GCP_slider.setRange(0, 228)
    self.rod_GCP_spinbox = QDoubleSpinBox()
    self.rod_GCP_spinbox.setRange(0, 228)
    self.rod_GCP_plus_btn = QPushButton("+5")
    self.rod_GCP_minus_btn = QPushButton("-5")
```

### Points critiques :

1. **Cohérence globale** : Tous les usages des paramètres grappes doivent être cohérents
2. **Rétrocompatibilité** : Les visualisations existantes doivent continuer à fonctionner
3. **Validation physique** : Les calculs pondérés doivent être physiquement sensés
4. **Interface intuitive** : Les contrôles doivent refléter les rôles industriels réels
5. **Performance** : Les calculs pondérés ne doivent pas impacter la fluidité
6. **Documentation** : Tous les textes d'aide doivent expliquer les nouveaux concepts

### Extensions futures possibles :
- **Groupes additionnels** : M1/M2 ou autres selon type de réacteur
- **Courbes de worth non-linéaires** : Fonction position pour worth variable
- **Interlocks et séquences** : Simulation verrouillages opérationnels
- **Vitesses de déplacement** : Temps réalistes de mouvement des grappes
- **Historique opérationnel** : Log actions avec analyse rétroactive

---

## Inversion Complète de Convention d'Interface (Barres de Contrôle)

**Dernière exécution :** Janvier 2025  
**Contexte :** Inversion de la convention des barres de contrôle pour adopter un standard industriel plus intuitif

### Type de tâche :
Changement majeur d'interface et de logique nécessitant une modification cohérente dans toutes les couches de l'architecture

### Problème identifié :
- **Convention non-standard** : L'ancienne convention (0% = retirées, 100% = insérées) était contraire aux standards industriels
- **Confusion pédagogique** : Interface non cohérente avec les outils professionnels utilisés dans l'industrie
- **Besoin de standardisation** : Faciliter la transition des étudiants vers les environnements professionnels

### Nouvelle convention adoptée :
- **0%** = Barres complètement insérées (maximum d'absorption neutronique)
- **100%** = Barres extraites (minimum d'absorption neutronique)
- **Slider à gauche** = Barres insérées (réacteur sous-critique)
- **Slider à droite** = Barres retirées (réacteur critique/surcritique)

### Fichiers modifiés :
- `src/model/reactor_model.py` - Logique physique d'absorption
- `src/gui/main_window.py` - Interface slider et gestion des événements
- `src/gui/widgets/flux_plot.py` - Visualisation et calculs de position
- `src/model/preset_model.py` - Descriptions des presets
- `config.json` - Valeurs de tous les presets système

### Workflow d'Inversion Complète :

**Étape 1 : Analyse d'impact**
1. **Identification des usages** : Recherche exhaustive (`grep_search`) de tous les endroits utilisant le paramètre
2. **Cartographie des dépendances** : Identifier les couches affectées (physique, contrôleur, interface, presets, tests)
3. **Planification séquentielle** : Ordre optimal des modifications pour éviter les incohérences temporaires

**Étape 2 : Modifications de la logique physique**
1. **Calculs d'absorption** : Inverser la formule `rod_abs_ratio = config.F_CONTROL_ROD_WORTH * (self.control_rod_position / 100.0)`
   - Nouvelle logique : `rod_insertion_fraction = (100.0 - self.control_rod_position) / 100.0`
2. **Distribution de flux** : Adapter les calculs de position et d'effet des barres
   - Adapter `rod_depth` → `rod_insertion_depth` avec nouvelle correspondance
3. **Validation physique** : Tests pour s'assurer de la cohérence (0% → k_eff faible, 100% → k_eff élevé)

**Étape 3 : Modifications de l'interface utilisateur**
1. **Slider inversé** : Modifier la correspondance valeur slider ↔ valeur physique
   - `update_ui_from_preset()` : `inverted_slider_value = 100 - int(config["control_rod_position"])`
   - `on_rod_position_changed()` : `inverted_value = 100 - value`
2. **Cohérence des visualisations** : Adapter `update_visualizations()` pour utiliser la valeur correcte
3. **Textes d'aide** : Mettre à jour toutes les descriptions et tooltips

**Étape 4 : Adaptation des données de configuration**
1. **Presets système** : Inverser toutes les valeurs dans `config.json`
   - Exemple : 0.0 → 100.0, 80.0 → 20.0, 95.0 → 5.0
2. **Descriptions presets** : Adapter les textes descriptifs dans `preset_model.py`
3. **Validation cohérence** : Vérifier que tous les presets restent physiquement sensés

**Étape 5 : Validation et tests**
1. **Tests unitaires physiques** : Vérifier que la logique d'absorption est correcte
2. **Tests d'interface** : Vérifier que le slider se comporte comme attendu
3. **Tests d'intégration** : Vérifier que les presets chargent correctement
4. **Validation experte** : Confirmer que la convention adoptée est bien la norme industrielle

### Bonnes pratiques identifiées :

#### **Changements de Convention Majeurs**
- **Planification exhaustive** : Identifier TOUS les points d'impact avant de commencer
- **Ordre séquentiel optimal** : Physique → Interface → Configuration → Tests
- **Documentation temps réel** : Commenter CHAQUE changement avec la nouvelle convention
- **Validation continue** : Tester à chaque étape pour éviter les erreurs cumulatives

#### **Gestion des Données Inversées**
- **Variables explicites** : Utiliser des noms clairs (`rod_insertion_fraction` vs `rod_position`)
- **Commentaires détaillés** : Documenter la nouvelle convention à chaque utilisation
- **Validation aux extremes** : Tester les valeurs 0% et 100% pour confirmer le comportement
- **Cohérence visuelle** : S'assurer que l'interface reflète intuitivement la physique

#### **Tests de Régression**
- **Avant/après comparaison** : Documenter les valeurs de k_eff pour validation
- **Presets critiques** : Tester chaque preset pour cohérence physique
- **Interface utilisateur** : Vérifier que le comportement du slider est intuitif
- **Documentation** : Mettre à jour tous les textes d'aide et descriptions

### Code type pour inversion de convention :

```python
# AVANT - Convention originale
rod_abs_ratio = config.F_CONTROL_ROD_WORTH * (self.control_rod_position / 100.0)

# APRÈS - Convention inversée avec documentation
# Nouvelle convention: 0% = insérées, 100% = retirées
rod_insertion_fraction = (100.0 - self.control_rod_position) / 100.0
rod_abs_ratio = config.F_CONTROL_ROD_WORTH * rod_insertion_fraction
```

```python
# Interface - Slider inversé
def on_rod_position_changed(self, value):
    # Inverser la valeur du slider : slider=0 → 100% (retirées), slider=100 → 0% (insérées)
    inverted_value = 100 - value
    # Continuer avec inverted_value...
```

### Points critiques :

1. **Cohérence globale** : TOUS les usages du paramètre doivent être modifiés simultanément
2. **Validation physique** : La nouvelle convention doit être physiquement sensée
3. **Tests exhaustifs** : Validation à tous les niveaux (unitaire, intégration, interface)
4. **Documentation synchronisée** : Mettre à jour TOUS les textes explicatifs
5. **Standards industriels** : Vérifier que la nouvelle convention est bien la norme acceptée

### Extensions futures possibles :
- Application de la même méthodologie à d'autres paramètres (bore, température)
- Outils automatisés pour faciliter les inversions de convention
- Templates documentés pour autres types de changements majeurs
- Processus de validation standardisé pour changements d'interface

---

## Correction de Comportement Physique avec Fonction de Transition Fluide

**Dernière exécution :** Janvier 2025  
**Contexte :** Correction du flux axial pour un comportement physiquement correct aux fortes insertions de barres de contrôle

### Type de tâche :
Correction physique majeure avec optimisation de fluidité utilisant fonctions mathématiques avancées

### Fichiers modifiés :
- `src/model/reactor_model.py` - Méthode `get_axial_flux_distribution()` complètement refactorisée

### Problème identifié :
- **Incohérence physique** : Le flux s'écrasait correctement mais ne se restabilisait pas aux fortes insertions
- **Transition brusque** : Passage direct de l'écrasement à la symétrie sans progression naturelle
- **Point critique** : À 100% d'insertion, le flux doit être parfaitement symétrique (cosinus pur)

### Workflow de Correction Physique :

**Étapes :**
1. **Analyse du comportement requis** :
   - 0% insertion : Flux symétrique (cosinus pur)
   - 1-85% insertion : Écrasement gaussien normal
   - 85-99% insertion : Atténuation progressive et fluide
   - 100% insertion : Flux parfaitement symétrique (identique à 0%)

2. **Implémentation de la logique conditionnelle** :
   - Exclusion explicite de la position 100% du calcul d'effet
   - Zone de transition définie entre 85% et 100%
   - Application conditionnelle des coefficients d'atténuation

3. **Implémentation fonction sigmoïde** :
   - Choix de la fonction `1/(1 + e^(-12(x-0.5)))` pour courbe en S naturelle
   - Normalisation de la plage 85-100% vers 0-1 pour la fonction
   - Inversion pour obtenir atténuation (1 - sigmoid_factor)

4. **Optimisation des paramètres** :
   - Coefficient de raideur : 12 pour équilibre fluidité/réactivité
   - Point central : 0.5 pour symétrie parfaite de la transition
   - Validation du comportement aux points critiques

### Bonnes pratiques identifiées :

#### **Fonctions de Transition Fluides**
- **Sigmoïdes** : Excellentes pour transitions naturelles en forme de S
- **Paramètres critiques** : Coefficient de raideur détermine la douceur de transition
- **Normalisation** : Toujours mapper la plage d'entrée vers [0,1] pour la fonction mathématique
- **Points de contrôle** : Valider le comportement aux extremes (0%, 50%, 100%)

#### **Validation Physique**
- **Conditions limites** : Vérifier comportement aux cas extrêmes
- **Continuité** : Assurer absence de discontinuités dans les dérivées
- **Cohérence** : Le modèle doit refléter la physique réelle observée
- **Symétrie** : À insertion complète, les effets asymétriques doivent disparaître

#### **Performance et Fluidité**
- **Éviter les branches conditionnelles** excessives dans les calculs temps réel
- **Fonctions mathématiques optimisées** : NumPy pour vectorisation
- **Mise en cache** : Éviter recalculs de constantes à chaque appel
- **Tests de régression** : S'assurer que les corrections n'affectent pas les autres comportements

### Code type pour correction avec fonction sigmoïde :

```python
# AVANT - Transition brusque
if rod_depth > 0.8:
    attenuation_factor = 1.0 - 5.0 * ((rod_depth - 0.8) / 0.2)
    attenuation_factor = max(0.0, attenuation_factor)
    effect_coeff = config.CONTROL_ROD_EFFECT_COEFF * attenuation_factor

# APRÈS - Transition fluide avec sigmoïde
if rod_depth > 0.85:
    # Normalisation de la plage vers [0,1]
    relative_depth = (rod_depth - 0.85) / 0.15  # 0.85-1.0 → 0-1
    
    # Fonction sigmoïde pour transition en S
    sigmoid_factor = 1.0 / (1.0 + np.exp(-12 * (relative_depth - 0.5)))
    attenuation_factor = 1.0 - sigmoid_factor  # Inversion pour atténuation
    
    effect_coeff = config.CONTROL_ROD_EFFECT_COEFF * attenuation_factor

# Condition d'exclusion pour 100%
if self.control_rod_position > 0 and self.control_rod_position < 100:
    # Application de l'effet uniquement entre 0-99%
```

### Points critiques :

1. **Exclusion explicite des cas limites** : Éviter les calculs inutiles aux positions spéciales
2. **Choix de la fonction de transition** : Sigmoïde optimale pour fluidité naturelle
3. **Paramètres de transition** : Balance entre réactivité et douceur du comportement
4. **Validation continue** : Tests avec différentes valeurs d'insertion
5. **Performance** : Éviter overhead calculatoire pour gains de fluidité

### Extensions futures possibles :
- Application similaire à d'autres phénomènes physiques (température, concentration bore)
- Paramètres de transition configurables dans `config.json`
- Fonctions de transition alternatives (cosinus, polynomiales)
- Optimisation pour autres comportements asymptotiques

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

## Diagnostiquer et Corriger une Incohérence Physique

**Dernière exécution :** Juillet 2025
**Contexte :** Correction d'une incohérence fondamentale où `k_eff` n'était pas égal à 1.00 dans des conditions critiques stables.

### Type de tâche :
Investigation et correction de bugs dans le modèle physique fondamental.

### Workflow de Diagnostic et Correction :

**Étape 1 : Identification du Symptôme**
1.  **Observation** : Identifier un comportement du simulateur qui contredit directement les principes physiques attendus.
    - *Exemple* : Pour un preset de fonctionnement à puissance stabilisée (PMD), le `k_eff` est significativement différent de 1.00 et la réactivité n'est pas nulle.
2.  **Hypothèse Fondamentale** : Si les paramètres d'entrée (`config.json`) sont considérés comme corrects, l'erreur se situe dans les formules de calcul du modèle (`src/model/reactor_model.py`).

**Étape 2 : Analyse du Modèle Physique**
1.  **Traçage Inversé** : Partir de la valeur erronée (`k_eff`) et remonter la chaîne de dépendances de calcul.
    - `k_eff` dépend de `k_inf` et des probabilités de non-fuite.
    - `k_inf` dépend des quatre facteurs : `η`, `ε`, `p`, `f`.
2.  **Revue des Formules** : Examiner chaque formule de calcul des facteurs.
    - Se concentrer sur les changements récents ou les formules complexes.
    - **Vérifier la cohérence dimensionnelle** : S'assurer que les unités des termes additionnés ou comparés sont cohérentes. C'était la clé de la résolution du bug de `k_eff`.

**Étape 3 : Implémentation de la Correction**
1.  **Remplacement Ciblé** : Remplacer uniquement la ligne ou la section de code incorrecte par une formule physiquement juste.
2.  **Cohérence du Modèle** : S'assurer que la nouvelle formule utilise des constantes et des variables déjà définies dans le modèle pour maintenir une cohérence interne. Éviter d'introduire de nouvelles "valeurs magiques".
3.  **Documentation du Changement** : Ajouter des commentaires expliquant pourquoi l'ancienne formule était incorrecte et ce que la nouvelle accomplit.

**Étape 4 : Validation Post-Correction**
1.  **Test du Cas Problématique** : Recharger le preset ou recréer les conditions qui ont révélé le bug.
    - Vérifier que le `k_eff` est maintenant correct (≈ 1.00).
2.  **Tests de non-régression** :
    - Tester d'autres presets (démarrage, fin de cycle, etc.) pour s'assurer qu'ils se comportent toujours de manière logique.
    - Vérifier que la correction n'a pas introduit d'effets de bord inattendus.
3.  **Validation de l'Affichage** : S'assurer que l'interface utilisateur reflète correctement les nouvelles valeurs calculées avec le formatage attendu.

### Bonnes pratiques identifiées :
- **La cohérence dimensionnelle est un outil de débogage puissant** pour les modèles physiques. Une incohérence (ex: additionner des termes sans unité avec des termes en cm⁻¹) est un signal d'alarme.
- **Le traçage inversé** depuis le symptôme jusqu'à la cause racine est une méthode efficace.
- **La centralisation des calculs** (refactoring pour `k_infinite`) réduit la surface d'attaque des bugs et simplifie la maintenance.
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