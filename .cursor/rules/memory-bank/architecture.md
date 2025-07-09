# Architecture de NeutroScope

Ce document décrit l'architecture logicielle finale de l'application NeutroScope, en se concentrant sur la séparation des responsabilités et le flux de données dans sa forme complète et opérationnelle.

## Vue d'ensemble : Modèle-Vue-Contrôleur (MVC) Avancé

Le projet est structuré selon une variante sophistiquée du design pattern **Modèle-Vue-Contrôleur (MVC)** pour garantir une séparation claire entre la logique métier (la physique du réacteur), l'interface utilisateur et la gestion des entrées, même avec les extensions temporelles et de gestion de presets.

**ARCHITECTURE FINALE** : L'architecture a été étendue pour supporter la **simulation temporelle complète** avec la dynamique Xénon-135, un **système de presets avancé** avec métadonnées et persistance, et des **outils pédagogiques sophistiqués**, transformant NeutroScope d'un simulateur statique en un **simulateur pédagogique professionnel**.

-   **Modèle (`src/model/`)**: Contient la logique de simulation pure avec dimension temporelle, système de presets avancé et validation physique. Il ne connaît rien de l'interface utilisateur et est entièrement piloté par `config.json`.
-   **Vue (`src/gui/`)**: Responsable de l'affichage de l'information et de la capture des interactions de l'utilisateur, avec visualisations temporelles, interface de gestion de presets et système d'information contextuel.
-   **Contrôleur (`src/controller/`)**: Sert de pont sophistiqué entre le Modèle et la Vue, étendu pour les contrôles temporels, gestion de presets et orchestration complète.

## Structure du Projet et Relations des Composants

```
NeutroScope/ (Architecture Finale Complète)
├── src/
│   ├── model/                      # MODÈLE (Logique métier complète)
│   │   ├── reactor_model.py        # Simulation physique + Xénon + Presets
│   │   ├── preset_model.py         # Système de presets avancé complet
│   │   ├── config.py               # Chargeur configuration étendue
│   │   └── calculators/            # Modules de calcul spécialisés
│   │
│   ├── controller/                 # CONTRÔLEUR (Orchestration complète)
│   │   └── reactor_controller.py   # Contrôleur unifié + temporel + presets
│   │
│   └── gui/                        # VUE (Interface professionnelle)
│       ├── main_window.py          # Fenêtre principale + onglets + presets
│       ├── visualization.py        # Gestionnaire visualisations étendues
│       └── widgets/                # Écosystème de widgets complets
│           ├── [preset_manager_dialog.py]    # SUPPRIMÉ - Interface simplifiée
│           ├── xenon_plot.py                 # Visualisation temporelle Xénon
│           ├── neutron_cycle_plot.py         # Cycle neutronique interactif
│           ├── flux_plot.py                  # Distribution axiale du flux
│           ├── four_factors_plot.py          # Facteurs neutroniques
│           ├── neutron_balance_plot.py       # Bilan neutronique
│           ├── enhanced_widgets.py           # Widgets avec info contextuelle
│           ├── info_manager.py               # Système d'information unifié
│           ├── info_panel.py                 # Panneau d'affichage info
│           ├── info_dialog.py                # Dialog information détaillée
│           ├── info_button.py                # Bouton d'information
│           └── credits_button.py             # Bouton crédits
│
├── tests/                          # Tests unitaires et d'intégration
├── docs/                           # Documentation et décisions architecture
│   ├── adr/                        # Architecture Decision Records
│   ├── architecture.md             # Ce fichier
│   └── BUILD_WINDOWS.md             # Documentation déploiement
├── config.json                     # Configuration complète et constantes physiques
├── user_presets.json               # Presets utilisateur (généré automatiquement)
├── requirements.txt                # Dépendances Python
├── build_windows.py                # Script de build PyInstaller optimisé
├── build_windows.bat               # Script batch automatisé pour Windows
└── main.py                         # Point d'entrée de l'application
```

---
## 1. Le Modèle (`src/model/`) - Simulation Complète

Le cœur de la simulation, maintenant avec toutes les capacités temporelles et de gestion avancée.

### **`reactor_model.py`** - Simulation Physique Complète
-   **Classe principale** : `ReactorModel` - Implémentation complète de la physique des réacteurs
-   **Physique de base** : Calculs basés sur la **formule des six facteurs** et la théorie de la diffusion neutronique
-   **Extensions temporelles** : 
    - Modélisation temporelle avec équations différentielles de Bateman (Iode-135 → Xénon-135)
    - Calculs d'équilibre et évolution temporelle avec solutions analytiques exactes
    - Gestion de l'historique temporel pour visualisations continues
-   **Physique avancée** :
    - Effet Doppler du combustible (facteur `p`)
    - Effet de température du modérateur sur l'absorption et les fuites
    - Cinétique des poisons neutroniques avec constantes de désintégration réalistes
    - Calculs de réactivité incluant l'anti-réactivité Xénon
-   **Méthodes clés** :
    - `calculate_all()` : Calcul complet de tous les paramètres neutroniques
    - `calculate_xenon_equilibrium()` : Calcul de l'état d'équilibre Xénon
    - `update_xenon_dynamics(dt)` : Évolution temporelle selon Bateman
    - `advance_time(hours)` : Avancement temporel avec mise à jour complète
    - `get_xenon_dynamics_data()` : Données pour visualisation temporelle
-   **Intégration presets** : Support complet du nouveau système de presets avec état temporel
-   **Découplage total** : Aucune valeur "magique" - tous les coefficients depuis `config.py`

### **`preset_model.py`** - Système de Presets Professionnel
-   **Architecture de données** :
    - `PresetData` : Dataclass complète avec validation, métadonnées et sérialisation
    - `PresetCategory` : Enum pour catégorisation (BASE, TEMPOREL, AVANCÉ, PERSONNALISÉ)
    - `PresetType` : Enum pour type (SYSTÈME, UTILISATEUR)
-   **`PresetManager`** : Gestionnaire sophistiqué avec :
    - CRUD complet (Create, Read, Update, Delete) avec validation
    - Chargement automatique depuis `config.json` et `user_presets.json`
    - Import/Export JSON pour partage entre utilisateurs
    - Recherche, filtrage et organisation par catégories
    - Persistance automatique et gestion des versions
-   **Validation robuste** : Vérification automatique des plages physiques et cohérence
-   **Métadonnées complètes** : ID unique, dates, auteur, descriptions, tags, notes
-   **État temporel** : Support complet des concentrations I-135/Xe-135 et temps simulation

### **`config.py`** - Configuration Étendue
-   **Chargement unifié** : Exposition des paramètres de `config.json` vers le modèle
-   **Sections étendues** :
    - `physical_constants` : Constantes physiques fondamentales
    - `four_factors` : Coefficients pour calculs neutroniques avec effets température
    - `neutron_leakage` : Paramètres de géométrie et diffusion
    - `thermal_hydraulics` : Couplages thermiques
    - `xenon_dynamics` : Constantes pour dynamique temporelle Xénon-135
    - `presets` : Configurations prédéfinies système
-   **Aucune logique** : Uniquement accès aux données de configuration

## 2. Le Contrôleur (`src/controller/`) - Orchestration Complète

L'orchestrateur sophistiqué de l'application, gérant toutes les interactions.

### **`reactor_controller.py`** - Contrôleur Unifié
-   **Classe principale** : `ReactorController` - Façade complète pour le modèle
-   **Méthodes de base** : Gestion des paramètres physiques (barres, bore, température, etc.)
-   **Extensions temporelles** :
    - `advance_time_hours(hours)` : Avancement temporel avec validation
    - `reset_xenon_to_equilibrium()` : Remise à l'équilibre
    - `get_xenon_dynamics_data()` : Récupération données temporelles
-   **Gestion presets avancée** :
    - `get_preset_manager()` : Accès au gestionnaire de presets
    - `create_preset_from_current_state()` : Création depuis état actuel
    - `export_presets()` / `import_presets()` : Fonctions import/export
    - `get_current_state_as_preset_data()` : Conversion état → preset
-   **Méthodes de récupération** : Toutes les données nécessaires pour la vue
-   **Aucune logique métier** : Translation pure des actions Vue → Modèle

## 3. La Vue (`src/gui/`) - Interface Professionnelle

L'interface et l'expérience utilisateur complète avec tous les outils pédagogiques.

### **`main_window.py`** - Interface Principale
-   **Classe principale** : `MainWindow` - Assemblage de l'interface complète
-   **Structure simplifiée** :
    - Panneau de contrôle avec sliders et spinboxes synchronisés
    - Système de presets avec QComboBox + bouton "Reset" uniquement
    - Interface streamline sans complexité de gestion avancée
-   **Méthodes clés** :
    - `on_preset_changed()` : Gestion sélection preset via dropdown
    - `reset_to_selected_preset()` : Reset aux paramètres du preset sélectionné
    - `update_reset_button_state()` : Gestion état bouton Reset
    - `connect_signals()` : Connexion des signaux UI simplifiés
-   **Gestion temporelle** : Connexion des contrôles Xénon avec signaux appropriés
-   **Architecture info** : Intégration système d'information contextuel

### **`visualization.py`** - Gestionnaire de Visualisations
-   **Organisation en onglets** : QTabWidget avec tous les graphiques
-   **Onglets disponibles** :
    - "Neutronique" : Cycle neutronique, facteurs, flux, bilan
    - "Dynamique Xénon" : Visualisations temporelles et contrôles temps
-   **Méthode d'update** : `update_all_plots(data)` pour synchronisation générale
-   **Gestion info** : Distribution du `InfoManager` vers tous les widgets

### Widgets de Visualisation - Écosystème Complet

#### **Widgets de Simulation Physique**
-   **`neutron_cycle_plot.py`** : 
    - Visualisation du cycle neutronique avec populations détaillées
    - Info-bulles enrichies avec explications physiques complètes
    - Animations et feedback visuel pour concepts pédagogiques
-   **`four_factors_plot.py`** : 
    - Graphique des quatre facteurs avec k_inf et k_eff
    - Ligne critique et annotations automatiques
    - Tooltips détaillés pour chaque facteur
-   **`flux_plot.py`** : 
    - Distribution axiale du flux avec effet des barres de contrôle
    - Interaction souris avec informations contextuelles
    - Visualisation impact géométrique
-   **`neutron_balance_plot.py`** : Bilan neutronique en secteurs

#### **Widgets Temporels**
-   **`xenon_plot.py`** (**NOUVEAU**) :
    - Classe `XenonPlot` : Graphiques jumeaux concentrations + réactivité
    - Classe `XenonControlWidget` : Contrôles temporels intégrés
    - Classe `XenonVisualizationWidget` : Widget complet avec historique
    - Architecture modulaire compatible MVC
    - Gestion échelles logarithmiques et mise à jour temps réel

#### **Widgets de Gestion**
-   **`preset_manager_dialog.py`** (**SUPPRIMÉ**) :
    - Interface complexe de gestion supprimée pour simplification UX
    - Fonctionnalités backend PresetManager conservées
    - Focus sur interface streamline pour usage éducatif
    - Gestion avancée disponible par modification de fichiers de configuration

#### **Système d'Information Unifié**
-   **`info_manager.py`** : Gestionnaire centralisé des informations contextuelles
-   **`info_panel.py`** : Panneau d'affichage des informations
-   **`info_dialog.py`** : Dialog pour informations détaillées
-   **`enhanced_widgets.py`** : Widgets avec support info intégré

## Flux de Données - Architecture Complète

### **Simulation Statique** (existante)
1. Interface → Contrôleur → Modèle → Calcul instantané → Contrôleur → Interface

### **Simulation Temporelle** (nouvelle)
1. Interface (contrôle temporel) → Contrôleur → Modèle
2. Modèle : Résolution équations différentielles + mise à jour état + historique
3. Modèle → Contrôleur → Interface (mise à jour graphiques temporels)

### **Gestion de Presets** (simplifiée)
1. Interface (dropdown) → Contrôleur → PresetManager → Application preset
2. PresetManager → Contrôleur → Interface (mise à jour paramètres)
3. Backend complet préservé mais non exposé en GUI pour simplification UX

### **Système d'Information** (nouveau)
1. Survol souris → Widget → InfoManager → InfoPanel
2. Appui touche 'i' → InfoManager → InfoDialog → Affichage détaillé

## Principes de Conception Finaux

1.  **Séparation Stricte des Responsabilités** : MVC rigoureusement implémenté, même avec toutes les extensions
2.  **Configuration Externalisée Complète** : `config.json` source unique de vérité pour toutes les constantes
3.  **Don't Repeat Yourself (DRY)** : Élimination de toute duplication avec méthodes génériques
4.  **Cohérence Linguistique** : Interface, commentaires et documentation en français
5.  **Build Optimisé** : Scripts de compilation streamlinés et performants
6.  **Extensibilité Architecturale** : Support facile d'autres phénomènes temporels et fonctionnalités
7.  **Performance Temps Réel** : Calculs optimisés pour simulation fluide avec visualisation continue
8.  **Validation Systématique** : Vérification automatique à tous les niveaux (physique, UI, persistance)
9.  **Modularité Complète** : Chaque composant indépendant et testable
10. **Évolutivité Éducative** : Architecture préparée pour extensions pédagogiques futures

## Impact Architectural Final

Cette architecture finale transforme NeutroScope d'une **calculatrice physique statique** en un **simulateur pédagogique professionnel complet** tout en préservant et renforçant :

- **Clarté architecturale** : MVC encore plus évident avec responsabilités étendues
- **Séparation des responsabilités** : Chaque couche a un rôle précis et bien défini
- **Configurabilité** : Tout paramètre externalisé et modifiable
- **Maintenabilité** : Code modulaire facilitant évolutions et corrections
- **Extensibilité** : Ajout facile de nouvelles fonctionnalités sans impact architecture
- **Testabilité** : Chaque composant indépendamment testable
- **Performance** : Optimisations permettant usage temps réel fluide
- **Qualité éducative** : Support architectural pour outils pédagogiques sophistiqués

## Conclusion Architecturale

L'architecture finale de NeutroScope représente un **équilibre optimal** entre :
- **Sophistication technique** : Capacités avancées de simulation et gestion
- **Simplicité conceptuelle** : MVC clair et compréhensible
- **Flexibilité éducative** : Support de multiples approches pédagogiques
- **Robustesse opérationnelle** : Fiabilité pour usage en production éducative

Cette architecture constitue une **base solide et évolutive** pour un outil éducatif de niveau professionnel dans le domaine de la physique des réacteurs nucléaires. 