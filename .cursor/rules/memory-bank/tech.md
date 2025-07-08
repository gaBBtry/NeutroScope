# Technologies et Environnement de Développement

Ce document décrit les technologies, outils et pratiques utilisés dans le projet NeutroScope dans sa version finale complète.

## Technologies Clés

-   **Langage** : **Python 3.12+**
    -   Choisi pour son écosystème scientifique (NumPy, Matplotlib), sa lisibilité et sa rapidité de développement.
    -   **Fonctionnalités avancées** : Capacités étendues pour la résolution d'équations différentielles, simulation temps réel, et gestion de données complexes.
    -   **Support moderne** : Dataclasses, type hints, énumérations, et fonctionnalités Python récentes
-   **Interface Utilisateur (UI)** : **PyQt6**
    -   Framework GUI robuste et multi-plateforme offrant une apparence native.
    -   **Extensions complètes** : Widgets temporels, graphiques temps réel, dialogs avancés, système de signaux sophistiqué.
    -   **Composants utilisés** : QMainWindow, QTabWidget, QTreeWidget, QDoubleSpinBox, QSlider, signaux/slots

## Librairies Principales

-   **Calculs Numériques** : **NumPy**
    -   Utilisé pour toutes les opérations numériques, notamment les calculs sur les tableaux dans le modèle du réacteur.
    -   **Applications avancées** : Calculs matriciels pour l'évolution temporelle (équations de Bateman), gestion des historiques temporels.
-   **Visualisation de Données** : **Matplotlib**
    -   Intégré à PyQt6 pour générer tous les graphiques (distribution de flux, quatre facteurs, etc.).
    -   **Fonctionnalités étendues** : Graphiques temporels animés, axes jumeaux pour visualisations multiples, interaction souris avancée.
    -   **Intégration Qt** : FigureCanvasQTAgg pour embedding seamless dans l'interface
-   **Utilitaires Scientifiques** : **SciPy**
    -   Utilisé pour des fonctions scientifiques spécifiques et validation des calculs physiques.
    -   **Applications** : Validation de solutions analytiques, comparaisons numériques, fonctions mathématiques avancées.

## Architecture de Données Avancée

### **Gestion de Configuration Externalisée**
-   **`config.json`** : Source unique de vérité pour toutes les constantes physiques
-   **Sections organisées** :
    - `physical_constants` : Constantes fondamentales de physique nucléaire
    - `four_factors` : Coefficients pour calculs neutroniques avec effets de température
    - `neutron_leakage` : Paramètres de géométrie et diffusion neutronique
    - `xenon_dynamics` : Constantes spécialisées pour dynamique temporelle
    - `presets` : Configurations prédéfinies du système
-   **Validation** : Vérification automatique de cohérence et plages physiques

### **Système de Presets Professionnel**
-   **Architecture de données** : Dataclasses Python avec validation intégrée
-   **Persistance** : JSON structuré avec versioning et métadonnées
-   **Types** : `PresetData`, `PresetCategory`, `PresetType`, `PresetManager`
-   **Fonctionnalités** : CRUD complet, import/export, filtrage, recherche
-   **Validation** : Plages physiques, cohérence temporelle, intégrité des données

## Modélisation Physique Complète

### **Simulation Temporelle Avancée**
-   **Équations Différentielles** : Implémentation directe des équations de Bateman pour la chaîne I-135 → Xe-135
-   **Méthodes Numériques** : Solutions analytiques exactes pour stabilité et performance optimales
-   **Gestion du Temps** : Avancement temporel contrôlé avec historique complet pour visualisations continues
-   **Performance** : Calculs optimisés permettant simulation fluide (<100ms par étape)

### **Physique des Réacteurs Étendue**
-   **Modèle Six Facteurs Complet** : Implémentation rigoureuse avec tous les contre-effets de température
-   **Effet Doppler** : Modélisation sophistiquée de l'élargissement des résonances avec la température du combustible
-   **Effet Modérateur** : Impact de la température du modérateur sur l'absorption neutronique et les fuites
-   **Poisons Neutroniques** : Cinétique complète I-135/Xe-135 avec constantes réalistes de REP
-   **Calculs de Réactivité** : Intégration de tous les effets incluant anti-réactivité Xénon

## Architecture Logicielle Professionnelle

### **Pattern MVC Avancé**
-   **Modèle** : Logique de simulation pure avec état temporel et validation physique
-   **Vue** : Interface sophistiquée avec widgets spécialisés et système d'information contextuel
-   **Contrôleur** : Orchestration complète des interactions avec gestion d'état cohérente
-   **Séparation claire** : Aucun couplage direct entre couches, communication par interfaces définies

### **Gestion d'État Robuste**
-   **État du Réacteur** : Paramètres physiques + concentrations isotopiques + historique temporel
-   **Synchronisation UI** : `blockSignals` pour éviter boucles infinies lors de mises à jour
-   **Persistance** : Sauvegarde automatique des presets utilisateur avec gestion des versions
-   **Validation** : Vérification systématique à tous les niveaux (UI, modèle, persistance)

## Interface Utilisateur Avancée

### **Widgets Spécialisés**
-   **Graphiques Matplotlib** : `FigureCanvasQTAgg` avec interaction souris et tooltips contextuels
-   **Visualisations Temporelles** : Graphiques jumeaux avec échelles logarithmiques et historique
-   **Contrôles Synchronisés** : Sliders et SpinBoxes liés avec validation en temps réel
-   **Dialogs Avancés** : Gestionnaire de presets avec onglets, filtrage, et vue hiérarchique

### **Système d'Information Unifié**
-   **InfoManager** : Gestionnaire centralisé pour tooltips et informations contextuelles
-   **Tooltips Universels** : Chaque élément d'interface fournit des explications physiques
-   **Dialog d'Information** : Appui sur 'i' pour informations détaillées sur l'élément survolé
-   **Cohérence Linguistique** : Interface entièrement en français avec terminologie technique appropriée

## Outils de Développement et Qualité

### **Tests et Validation**
-   **Framework** : `pytest` avec `pytest-qt` pour tests d'interface graphique
-   **Couverture** : Tests unitaires (modèle), tests d'intégration (contrôleur), tests GUI (interface)
-   **Validation Physique** : Comparaison avec valeurs théoriques et validation par experts
-   **Tests de Performance** : Vérification temps de réponse pour simulation temps réel

### **Build et Déploiement**
-   **PyInstaller** : Création d'exécutables Windows autonomes avec configuration optimisée
-   **Scripts Automatisés** : `build_windows.bat` et `build_windows.py` pour compilation simplifiée
-   **Optimisations** : Exclusion de modules inutiles, imports cachés, compression
-   **Distribution** : Partage via OneDrive d'entreprise avec instructions utilisateur

## Configuration de Développement

### **Environnement Recommandé**
-   **Python** : 3.12+ dans environnement virtuel (.venv)
-   **IDE** : Support PyQt6 avec debugging graphique
-   **Outils** : pytest, pytest-qt, pytest-cov pour tests et couverture
-   **Plateforme** : Développement cross-platform (Windows/macOS/Linux)

### **Dépendances Critiques** (requirements.txt)
```
PyQt6          # Interface graphique
numpy          # Calculs numériques
matplotlib     # Visualisations
scipy          # Fonctions scientifiques
pytest         # Tests unitaires
pytest-qt      # Tests interface graphique
pytest-cov     # Couverture de tests
pyinstaller    # Build exécutables
```

## Performance et Optimisations

### **Calculs Temps Réel**
-   **Solutions Analytiques** : Éviter calculs numériques itératifs pour performance
-   **Mise à jour Sélective** : Recalcul uniquement des paramètres impactés
-   **Gestion Mémoire** : Limitation historique temporel pour éviter croissance mémoire
-   **Responsivité UI** : Calculs non-bloquants avec mise à jour asynchrone des graphiques

### **Optimisations Architecturales**
-   **Configuration Cache** : Chargement unique du config.json au démarrage
-   **Widgets Réutilisables** : Composants modulaires pour réduction code dupliqué
-   **Signaux Optimisés** : Connexions directes sans overhead de dispatching
-   **Validation Efficace** : Vérifications rapides avec messages d'erreur clairs

## Principes Techniques Appliqués

### **Qualité du Code**
1. **Séparation des responsabilités** : Chaque module a une fonction claire et délimitée
2. **Configuration externalisée** : Aucune constante "magique" dans le code
3. **Validation systématique** : Vérification à tous les points d'entrée de données
4. **Documentation intégrée** : Docstrings et commentaires explicatifs en français
5. **Gestion d'erreurs robuste** : Exceptions gérées avec messages utilisateur appropriés

### **Extensibilité Future**
-   **Architecture modulaire** : Ajout facile de nouveaux isotopes ou phénomènes physiques
-   **Interface plugin** : Possibilité d'extensions via système de widgets
-   **Configuration flexible** : Support de nouveaux paramètres sans modification code
-   **Base de données** : Architecture prête pour migration vers base de données si nécessaire

## Conclusion Technique

L'implémentation technique finale de NeutroScope représente un **équilibre optimal** entre :
- **Sophistication scientifique** : Modèles physiques rigoureux et validation experte
- **Performance d'usage** : Réactivité temps réel pour expérience utilisateur fluide
- **Maintenabilité** : Architecture claire facilitant évolutions et corrections
- **Extensibilité** : Base solide pour fonctionnalités futures sans refactoring majeur

Cette base technique constitue une **fondation professionnelle robuste** pour un outil éducatif de niveau industriel dans le domaine de la physique des réacteurs nucléaires. 