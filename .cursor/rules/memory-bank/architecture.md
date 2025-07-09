# Architecture de NeutroScope

Ce document décrit l'architecture logicielle finale de l'application NeutroScope, en se concentrant sur la séparation des responsabilités et le flux de données dans sa forme complète et opérationnelle.

## Vue d'ensemble : Modèle-Vue-Contrôleur (MVC) Avancé

Le projet est structuré selon une variante sophistiquée du design pattern **Modèle-Vue-Contrôleur (MVC)** pour garantir une séparation claire entre la logique métier (la physique du réacteur), l'interface utilisateur et la gestion des entrées, même avec les extensions temporelles, de gestion de presets et **du système de grappes R/GCP professionnel**.

**ARCHITECTURE FINALE** : L'architecture a été étendue pour supporter la **simulation temporelle complète** avec la dynamique Xénon-135, un **système de presets avancé** avec métadonnées et persistance, des **outils pédagogiques sophistiqués**, et maintenant un **système de contrôle des grappes R et GCP de niveau industriel** avec granularité fine de 228 pas, transformant NeutroScope d'un simulateur statique en un **simulateur pédagogique professionnel authentique**.

-   **Modèle (`src/model/`)**: Contient la logique de simulation pure avec dimension temporelle, système de presets avancé, **système de grappes R/GCP sophistiqué** et validation physique. Il ne connaît rien de l'interface utilisateur et est entièrement piloté par `config.json`.
-   **Vue (`src/gui/`)**: Responsable de l'affichage de l'information et de la capture des interactions de l'utilisateur, avec visualisations temporelles, interface de gestion de presets, **contrôles grappes R/GCP séparés** et système d'information contextuel.
-   **Contrôleur (`src/controller/`)**: Sert de pont sophistiqué entre le Modèle et la Vue, étendu pour les contrôles temporels, gestion de presets, **méthodes dédiées aux grappes R/GCP** et orchestration complète.

## Structure du Projet et Relations des Composants

```
NeutroScope/ (Architecture Finale Complète avec Grappes R/GCP)
├── src/
│   ├── model/                      # MODÈLE (Logique métier complète + grappes)
│   │   ├── reactor_model.py        # Simulation physique + Xénon + Presets + Grappes R/GCP
│   │   ├── preset_model.py         # Système de presets avancé avec positions R/GCP
│   │   ├── config.py               # Chargeur configuration étendue + grappes
│   │   └── calculators/            # Modules de calcul spécialisés
│   │
│   ├── controller/                 # CONTRÔLEUR (Orchestration complète + grappes)
│   │   └── reactor_controller.py   # Contrôleur unifié + temporel + presets + R/GCP
│   │
│   └── gui/                        # VUE (Interface professionnelle + grappes)
│       ├── main_window.py          # Fenêtre principale + onglets + presets + contrôles R/GCP
│       ├── visualization.py        # Gestionnaire visualisations étendues
│       └── widgets/                # Écosystème de widgets complets
│           ├── [preset_manager_dialog.py]    # SUPPRIMÉ - Interface simplifiée
│           ├── xenon_plot.py                 # Visualisation temporelle Xénon
│           ├── neutron_cycle_plot.py         # Cycle neutronique interactif
│           ├── flux_plot.py                  # Distribution axiale du flux (adapté grappes)
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
├── config.json                     # Configuration complète + grappes R/GCP + constantes physiques
├── user_presets.json               # Presets utilisateur (généré automatiquement)
├── requirements.txt                # Dépendances Python
├── build_windows.py                # Script de build PyInstaller optimisé
├── build_windows.bat               # Script batch automatisé pour Windows
└── main.py                         # Point d'entrée de l'application
```

---
## 1. Le Modèle (`src/model/`) - Simulation Complète avec Grappes R/GCP

Le cœur de la simulation, maintenant avec toutes les capacités temporelles, de gestion avancée et **système de grappes professionnel**.

### **`reactor_model.py`** - Simulation Physique Complète avec Grappes R/GCP
-   **Classe principale** : `ReactorModel` - Implémentation complète de la physique des réacteurs **avec système de grappes industriel**
-   **Nouveaux paramètres de base** :
    - `rod_group_R_position` : Position groupe Régulation (0-228 pas)
    - `rod_group_GCP_position` : Position groupe Compensation de Puissance (0-228 pas)
    - Abandon de `control_rod_position` unique au profit de la distinction R/GCP
-   **Physique de base** : Calculs basés sur la **formule des six facteurs** et la théorie de la diffusion neutronique **avec calculs pondérés pour grappes R/GCP**
-   **Extensions temporelles** : 
    - Modélisation temporelle avec équations différentielles de Bateman (Iode-135 → Xénon-135)
    - Calculs d'équilibre et évolution temporelle avec solutions analytiques exactes
    - Gestion de l'historique temporel pour visualisations continues
-   **Physique avancée** :
    - Effet Doppler du combustible (facteur `p`)
    - Effet de température du modérateur sur l'absorption et les fuites
    - Cinétique des poisons neutroniques avec constantes de désintégration réalistes
    - Calculs de réactivité incluant l'anti-réactivité Xénon
    - **Nouveau** : Calcul pondéré du worth des grappes R (30%) et GCP (70%)
-   **Méthodes clés étendues** :
    - `update_rod_group_R_position(position)` : Mise à jour position groupe R
    - `update_rod_group_GCP_position(position)` : Mise à jour position groupe GCP
    - `_get_total_rod_worth_fraction()` : Calcul worth total pondéré
    - `_get_equivalent_rod_position_percent()` : Position équivalente pour rétrocompatibilité
    - `calculate_all()` : Calcul complet de tous les paramètres neutroniques
    - `calculate_xenon_equilibrium()` : Calcul de l'état d'équilibre Xénon
    - `update_xenon_dynamics(dt)` : Évolution temporelle selon Bateman
    - `advance_time(hours)` : Avancement temporel avec mise à jour complète
    - `get_xenon_dynamics_data()` : Données pour visualisation temporelle
-   **Intégration presets** : Support complet du nouveau système de presets avec **positions R/GCP** et état temporel
-   **Découplage total** : Aucune valeur "magique" - tous les coefficients depuis `config.py`

### **`preset_model.py`** - Système de Presets Professionnel avec Grappes R/GCP
-   **Architecture de données étendue** :
    - `PresetData` : Dataclass complète avec **positions R/GCP séparées**, validation, métadonnées et sérialisation
    - Nouveaux champs : `rod_group_R_position` et `rod_group_GCP_position` (0-228 pas)
    - `PresetCategory` : Enum pour catégorisation (BASE, TEMPOREL, AVANCÉ, PERSONNALISÉ)
    - `PresetType` : Enum pour type (SYSTÈME, UTILISATEUR)
-   **`PresetManager`** : Gestionnaire sophistiqué avec :
    - CRUD complet (Create, Read, Update, Delete) avec **validation grappes R/GCP**
    - Chargement automatique depuis `config.json` et `user_presets.json`
    - Import/Export JSON pour partage entre utilisateurs
    - Recherche, filtrage et organisation par catégories
    - Persistance automatique et gestion des versions
-   **Validation robuste étendue** : Vérification automatique des plages physiques (0-228 pas) et cohérence
-   **Métadonnées complètes** : ID unique, dates, auteur, descriptions, tags, notes
-   **État temporel** : Support complet des concentrations I-135/Xe-135 et temps simulation

### **`config.py`** - Configuration Étendue avec Grappes R/GCP
-   **Chargement unifié** : Exposition des paramètres de `config.json` vers le modèle
-   **Sections étendues** :
    - `physical_constants` : Constantes physiques fondamentales
    - `four_factors` : Coefficients pour calculs neutroniques avec effets température
    - `neutron_leakage` : Paramètres de géométrie et diffusion
    - `thermal_hydraulics` : Couplages thermiques
    - `xenon_dynamics` : Constantes pour dynamique temporelle Xénon-135
    - **`control_rod_groups`** : **NOUVEAU** - Configuration complète grappes R et GCP
    - `presets` : Configurations prédéfinies système **avec positions R/GCP**
-   **Nouvelle section `control_rod_groups`** :
    - Configuration R : Description, worth_fraction (0.3), plages pas, granularité
    - Configuration GCP : Description, worth_fraction (0.7), plages pas, granularité
    - Paramètres conversion : Équivalence 228 pas, worth de référence
-   **Aucune logique** : Uniquement accès aux données de configuration

## 2. Le Contrôleur (`src/controller/`) - Orchestration Complète avec Grappes R/GCP

L'orchestrateur sophistiqué de l'application, gérant toutes les interactions **y compris les nouvelles grappes R/GCP**.

### **`reactor_controller.py`** - Contrôleur Unifié Étendu
-   **Classe principale** : `ReactorController` - Façade complète pour le modèle **avec méthodes grappes R/GCP**
-   **Nouvelles méthodes grappes** :
    - `update_rod_group_R_position(position)` : Mise à jour groupe R avec validation
    - `update_rod_group_GCP_position(position)` : Mise à jour groupe GCP avec validation
    - `get_rod_group_positions()` : Récupération positions actuelles R et GCP
    - `get_rod_groups_info()` : Informations complètes configuration grappes
-   **Méthodes de base étendues** : Gestion des paramètres physiques (barres, bore, température, etc.)
-   **Extensions temporelles** :
    - `advance_time_hours(hours)` : Avancement temporel avec validation
    - `reset_xenon_to_equilibrium()` : Remise à l'équilibre
    - `get_xenon_dynamics_data()` : Récupération données temporelles
-   **Gestion presets avancée** :
    - `get_preset_manager()` : Accès au gestionnaire de presets
    - `create_preset_from_current_state()` : Création depuis état actuel **avec positions R/GCP**
    - `export_presets()` / `import_presets()` : Fonctions import/export
    - `get_current_state_as_preset_data()` : Conversion état → preset **avec R/GCP**
-   **Rétrocompatibilité** : `update_control_rod_position()` convertit % en positions équivalentes R/GCP
-   **Méthodes de récupération** : Toutes les données nécessaires pour la vue
-   **Aucune logique métier** : Translation pure des actions Vue → Modèle

## 3. La Vue (`src/gui/`) - Interface Professionnelle avec Grappes R/GCP

L'interface et l'expérience utilisateur complète avec tous les outils pédagogiques **et contrôles grappes sophistiqués**.

### **`main_window.py`** - Interface Principale avec Grappes R/GCP
-   **Classe principale** : `MainWindow` - Assemblage de l'interface complète **avec contrôles grappes séparés**
-   **Nouvelle structure grappes** :
    - **Groupe R (Régulation)** : Slider + SpinBox + boutons ±1 pas pour contrôle fin
    - **Groupe GCP (Compensation)** : Slider + SpinBox + boutons ±5 pas pour contrôle global
    - **Convention intuitive** : Slider droite = insertion, suffixe " pas" pour clarté
    - **Ticks visuels** : Graduation 50 pas sur sliders pour référence
-   **Structure simplifiée existante** :
    - Panneau de contrôle avec sliders et spinboxes synchronisés
    - Système de presets avec QComboBox + bouton "Reset" uniquement
    - Interface streamline sans complexité de gestion avancée
-   **Méthodes clés étendues** :
    - `on_rod_R_slider_changed()` / `on_rod_R_spinbox_changed()` : Gestion groupe R
    - `on_rod_GCP_slider_changed()` / `on_rod_GCP_spinbox_changed()` : Gestion groupe GCP
    - `adjust_rod_R(step)` / `adjust_rod_GCP(step)` : Ajustements par boutons
    - `on_preset_changed()` : Gestion sélection preset via dropdown **avec R/GCP**
    - `reset_to_selected_preset()` : Reset aux paramètres du preset sélectionné
    - `update_reset_button_state()` : Gestion état bouton Reset
    - `connect_signals()` : Connexion des signaux UI simplifiés **+ signaux grappes**
-   **Textes d'information enrichis** : Explications détaillées rôles R vs GCP dans `info_texts`
-   **Gestion temporelle** : Connexion des contrôles Xénon avec signaux appropriés
-   **Architecture info** : Intégration système d'information contextuel

### **`visualization.py`** - Gestionnaire de Visualisations Adapté
-   **Organisation en onglets** : QTabWidget avec tous les graphiques
-   **Onglets disponibles** :
    - "Neutronique" : Cycle neutronique, facteurs, flux, bilan
    - "Dynamique Xénon" : Visualisations temporelles et contrôles temps
-   **Méthode d'update** : `update_all_plots(data)` pour synchronisation générale **avec nouvelles grappes**
-   **Gestion info** : Distribution du `InfoManager` vers tous les widgets

### Widgets de Visualisation - Écosystème Complet Adapté

#### **Widgets de Simulation Physique**
-   **`neutron_cycle_plot.py`** : 
    - Visualisation du cycle neutronique avec populations détaillées
    - Info-bulles enrichies avec explications physiques complètes **incluant grappes R/GCP**
    - Animations et feedback visuel pour concepts pédagogiques
-   **`four_factors_plot.py`** : 
    - Graphique des quatre facteurs avec k_inf et k_eff
    - Ligne critique et annotations automatiques
    - Tooltips détaillés pour chaque facteur
-   **`flux_plot.py`** : 
    - Distribution axiale du flux avec effet des barres de contrôle
    - **Adapté** : Utilise position équivalente calculée depuis grappes R/GCP
    - Interaction souris avec informations contextuelles
    - Visualisation impact géométrique
-   **`neutron_balance_plot.py`** : Bilan neutronique en secteurs

#### **Widgets Temporels**
-   **`xenon_plot.py`** :
    - Classe `XenonPlot` : Graphiques jumeaux concentrations + réactivité
    - Classe `XenonControlWidget` : Contrôles temporels intégrés
    - Classe `XenonVisualizationWidget` : Widget complet avec historique
    - Architecture modulaire compatible MVC
    - Gestion échelles logarithmiques et mise à jour temps réel

#### **Système d'Information Unifié**
-   **`info_manager.py`** : Gestionnaire centralisé des informations contextuelles
-   **`info_panel.py`** : Panneau d'affichage des informations
-   **`info_dialog.py`** : Dialog pour informations détaillées
-   **`enhanced_widgets.py`** : Widgets avec support info intégré

## Flux de Données - Architecture Complète avec Grappes R/GCP

### **Simulation Statique** (étendue)
1. Interface (grappes R/GCP) → Contrôleur → Modèle → Calcul pondéré instantané → Contrôleur → Interface

### **Simulation Temporelle** (maintenue)
1. Interface (contrôle temporel) → Contrôleur → Modèle
2. Modèle : Résolution équations différentielles + mise à jour état + historique
3. Modèle → Contrôleur → Interface (mise à jour graphiques temporels)

### **Gestion de Presets avec Grappes** (adaptée)
1. Interface (dropdown) → Contrôleur → PresetManager → Application preset **avec positions R/GCP**
2. PresetManager → Contrôleur → Interface (mise à jour paramètres **incluant grappes**)
3. Backend complet préservé mais non exposé en GUI pour simplification UX

### **Système d'Information** (enrichi)
1. Survol souris → Widget → InfoManager → InfoPanel **avec info grappes R/GCP**
2. Appui touche 'i' → InfoManager → InfoDialog → Affichage détaillé **incluant rôles grappes**

## Principes de Conception Finaux avec Grappes R/GCP

1.  **Séparation Stricte des Responsabilités** : MVC rigoureusement implémenté, même avec toutes les extensions **et les grappes R/GCP**
2.  **Configuration Externalisée Complète** : `config.json` source unique de vérité pour toutes les constantes **y compris grappes**
3.  **Don't Repeat Yourself (DRY)** : Élimination de toute duplication avec méthodes génériques **et calculs pondérés**
4.  **Cohérence Linguistique** : Interface, commentaires et documentation en français
5.  **Build Optimisé** : Scripts de compilation streamlinés et performants
6.  **Extensibilité Architecturale** : Support facile d'autres groupes de grappes et fonctionnalités
7.  **Performance Temps Réel** : Calculs optimisés pour simulation fluide avec visualisation continue
8.  **Validation Systématique** : Vérification automatique à tous les niveaux (physique, UI, persistance) **incluant grappes**
9.  **Modularité Complète** : Chaque composant indépendant et testable
10. **Évolutivité Éducative** : Architecture préparée pour extensions pédagogiques futures
11. **Authenticité Industrielle** : **NOUVEAU** - Système grappes R/GCP conforme aux standards REP

## Impact Architectural Final avec Grappes R/GCP

Cette architecture finale avec système de grappes R/GCP transforme NeutroScope d'une **calculatrice physique statique** en un **simulateur pédagogique professionnel de niveau industriel** tout en préservant et renforçant :

- **Clarté architecturale** : MVC encore plus évident avec responsabilités étendues **et grappes séparées**
- **Séparation des responsabilités** : Chaque couche a un rôle précis et bien défini **y compris gestion grappes**
- **Configurabilité** : Tout paramètre externalisé et modifiable **incluant paramètres grappes**
- **Maintenabilité** : Code modulaire facilitant évolutions et corrections **avec grappes extensibles**
- **Extensibilité** : Ajout facile de nouvelles fonctionnalités sans impact architecture **nouveaux groupes**
- **Testabilité** : Chaque composant indépendamment testable **validation grappes incluse**
- **Performance** : Optimisations permettant usage temps réel fluide **calculs pondérés efficaces**
- **Qualité éducative** : Support architectural pour outils pédagogiques sophistiqués **avec authenticity industrielle**
- **Authenticité professionnelle** : **NOUVEAU** - Fidélité aux pratiques industrielles REP réelles

## Conclusion Architecturale

L'architecture finale de NeutroScope avec système de grappes R/GCP représente un **équilibre optimal** entre :
- **Sophistication technique** : Capacités avancées de simulation et gestion **avec grappes professionnelles**
- **Simplicité conceptuelle** : MVC clair et compréhensible **même avec extensions grappes**
- **Flexibilité éducative** : Support de multiples approches pédagogiques **du conceptuel au professionnel**
- **Robustesse opérationnelle** : Fiabilité pour usage en production éducative **avec standards industriels**
- **Authenticité industrielle** : **NOUVEAU** - Fidélité aux systèmes de contrôle REP réels

Cette architecture constitue une **base solide et évolutive** pour un outil éducatif de niveau professionnel dans le domaine de la physique des réacteurs nucléaires, permettant une transition naturelle de l'apprentissage théorique vers la pratique industrielle. 