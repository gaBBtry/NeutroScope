# Architecture de NeutroScope

Ce document décrit l'architecture logicielle de l'application NeutroScope, en se concentrant sur la séparation des responsabilités et le flux de données.

## Vue d'ensemble : Modèle-Vue-Contrôleur (MVC) avec Extensions Temporelles

Le projet est structuré selon une variante du design pattern **Modèle-Vue-Contrôleur (MVC)** pour garantir une séparation claire entre la logique métier (la physique du réacteur), l'interface utilisateur et la gestion des entrées.

**ÉVOLUTION MAJEURE** : L'architecture a été étendue pour supporter la **simulation temporelle** avec la dynamique Xénon-135, transformant NeutroScope d'un simulateur statique en un simulateur dynamique avancé.

-   **Modèle (`src/model/`)**: Contient la logique de simulation pure, maintenant avec dimension temporelle. Il ne connaît rien de l'interface utilisateur et est entièrement piloté par `config.json`.
-   **Vue (`src/gui/`)**: Responsable de l'affichage de l'information et de la capture des interactions de l'utilisateur, maintenant avec visualisations temporelles.
-   **Contrôleur (`src/controller/`)**: Sert de pont simple et direct entre le Modèle et la Vue, étendu pour les contrôles temporels.

## Structure du Projet et Relations des Composants

```
NeutroScope/
├── src/
│   ├── model/                      # MODÈLE (Logique métier + temporel)
│   │   ├── reactor_model.py        # Cœur de la simulation physique + Xénon
│   │   └── config.py               # Chargeur pour config.json
│   │
│   ├── controller/                 # CONTRÔLEUR (Orchestration + temporel)
│   │   └── reactor_controller.py   # Pont entre Modèle et Vue + contrôles temps
│   │
│   └── gui/                        # VUE (Interface + visualisations temporelles)
│       ├── main_window.py          # Fenêtre principale + onglet Xénon
│       ├── visualization.py        # Gestionnaire des visualisations
│       └── widgets/                # Composants d'interface réutilisables
│           ├── xenon_plot.py       # NOUVEAU: Visualisation temporelle Xénon
│           └── [autres widgets]
│
├── tests/                          # Tests unitaires et d'intégration
├── docs/                           # Documentation
│   ├── adr/                        # Architecture Decision Records
│   └── architecture.md             # Ce fichier
├── config.json                     # TOUTES les constantes + paramètres Xénon
├── requirements.txt                # Dépendances Python
├── build_windows.py                # Script de build PyInstaller optimisé
└── build_windows.bat               # Script batch automatisé pour Windows
```

---
## 1. Le Modèle (`src/model/`) - Extensions Temporelles

Le cœur de la simulation, maintenant avec capacités temporelles.

-   **`reactor_model.py`**:
    -   Classe principale : `ReactorModel`.
    -   Implémente les calculs physiques basés sur la **formule des six facteurs** et la théorie de la diffusion.
    -   **NOUVEAU** : Modélisation temporelle avec équations différentielles de Bateman (Iode-135 → Xénon-135).
    -   **Physique Avancée** :
        - Effet de température du modérateur sur le facteur `p`
        - Cinétique des poisons neutroniques avec constantes de désintégration
        - Calcul d'équilibre Xénon et évolution temporelle
    -   Contient l'état interne du réacteur ET l'historique temporel, mis à jour via une méthode `_update_parameter` générique.
    -   **Nouvelles méthodes clés** :
        - `calculate_xenon_equilibrium()` : Calcul de l'état d'équilibre
        - `update_xenon_dynamics()` : Évolution temporelle selon Bateman
        - `advance_time()` : Avancement temporel avec mise à jour complète
    -   **Totalement découplé** : Ne contient aucune valeur "magique". Tous les coefficients, constantes physiques et paramètres de simulation sont chargés depuis le module `config`.

-   **`config.py`**:
    -   Charge et expose les paramètres de `config.json`.
    -   **ÉTENDU** : Gestion des nouvelles sections de configuration (xenon_dynamics, températures).
    -   Ne contient aucune logique, uniquement des données de configuration.

## 2. Le Contrôleur (`src/controller/`) - Extensions Temporelles

L'orchestrateur de l'application, étendu pour les simulations temporelles.

-   **`reactor_controller.py`**:
    -   Classe principale : `ReactorController`.
    -   Agit comme une simple **façade** pour le modèle.
    -   **ÉTENDU** : Nouvelles méthodes pour contrôles temporels :
        - `advance_time_hours()` : Avancement temporel avec validation
        - `reset_xenon_to_equilibrium()` : Remise à l'équilibre
    -   Traduit les actions de la Vue en appels au Modèle sans ajouter de logique.

## 3. La Vue (`src/gui/`) - Visualisations Temporelles

L'interface et l'expérience utilisateur, enrichie des visualisations temporelles.

-   **`main_window.py`**:
    -   Classe principale : `MainWindow`.
    -   Construit l'interface et assemble les widgets.
    -   **ÉTENDU** : Nouvel onglet "Dynamique Xénon" avec contrôles temporels.
    -   Instancie le `ReactorController`.
    -   Connecte les signaux des widgets à des slots qui appellent le contrôleur via une méthode générique `_update_parameter_and_ui`.
    -   **NOUVEAU** : Gestion des contrôles temporels (boutons avancement temps, reset).
    -   Utilise `blockSignals` pour une synchronisation claire et robuste entre les widgets (ex: slider et spinbox).

### Widgets de Visualisation - Extensions Temporelles

-   **`widgets/`**: Contient tous les composants graphiques, y compris les graphiques Matplotlib et les widgets QPainter.
-   **`widgets/xenon_plot.py`** (**NOUVEAU**) :
    -   Widget spécialisé pour la visualisation temporelle Xénon-135
    -   Graphiques jumeaux : concentrations I-135/Xe-135 et effet sur réactivité
    -   Contrôles intégrés : avancement temps (1-24h), reset équilibre
    -   Architecture modulaire compatible MVC
-   **`visualization.py`**: Gère la disposition des graphiques dans un `QTabWidget`, étendu pour l'onglet Xénon.

## Flux de Données Temporelles

### Simulation Statique (existante)
1. Interface → Contrôleur → Modèle → Calcul instantané → Contrôleur → Interface

### Simulation Temporelle (nouvelle)
1. Interface (contrôle temporel) → Contrôleur → Modèle
2. Modèle : Résolution équations différentielles + mise à jour état
3. Modèle → Contrôleur → Interface (mise à jour graphiques temporels)
4. Historique sauvegardé pour visualisation continue

## Principes de Conception après Extensions Temporelles

1.  **Séparation Stricte des Responsabilités** : MVC clairement implémenté, même avec extensions temporelles.
2.  **Configuration Externalisée** : `config.json` est la source unique de vérité pour toutes les constantes, y compris Xénon.
3.  **Don't Repeat Yourself (DRY)** : Logique dupliquée éliminée dans le modèle (`_update_parameter`) et la vue (`_update_parameter_and_ui`).
4.  **Cohérence Linguistique** : Interface, commentaires et documentation principalement en français.
5.  **Build Optimisé** : Le script `build_windows.py` a été nettoyé des options redondantes.
6.  **NOUVEAU** : **Extensibilité Temporelle** : Architecture conçue pour supporter facilement d'autres phénomènes temporels (autres isotopes, transitoires).
7.  **NOUVEAU** : **Performance Temps Réel** : Calculs optimisés pour simulation fluide avec visualisation continue.

## Impact Architectural

Cette extension transforme NeutroScope d'une **calculatrice physique statique** en un **simulateur dynamique avancé** tout en préservant :
- La clarté de l'architecture MVC
- La séparation des responsabilités
- La configurabilité externalisée
- La facilité de maintenance et d'extension 