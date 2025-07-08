# Architecture de NeutroScope

Ce document décrit l'architecture logicielle de l'application NeutroScope, en se concentrant sur la séparation des responsabilités et le flux de données.

## Vue d'ensemble : Modèle-Vue-Contrôleur (MVC)

Le projet est structuré selon une variante du design pattern **Modèle-Vue-Contrôleur (MVC)** pour garantir une séparation claire entre la logique métier (la physique du réacteur), l'interface utilisateur et la gestion des entrées.

-   **Modèle (`src/model/`)**: Contient la logique de simulation pure. Il ne connaît rien de l'interface utilisateur et est entièrement piloté par `config.json`.
-   **Vue (`src/gui/`)**: Responsable de l'affichage de l'information et de la capture des interactions de l'utilisateur.
-   **Contrôleur (`src/controller/`)**: Sert de pont simple et direct entre le Modèle et la Vue.

## Structure du Projet et Relations des Composants

```
NeutroScope/
├── src/
│   ├── model/                      # MODÈLE (Logique métier)
│   │   ├── reactor_model.py        # Cœur de la simulation physique
│   │   └── config.py               # Chargeur pour config.json
│   │
│   ├── controller/                 # CONTRÔLEUR (Orchestration)
│   │   └── reactor_controller.py   # Pont entre Modèle et Vue
│   │
│   └── gui/                        # VUE (Interface utilisateur)
│       ├── main_window.py          # Fenêtre principale et logique UI
│       ├── visualization.py        # Gestionnaire des visualisations
│       └── widgets/                # Composants d'interface réutilisables
│
├── tests/                          # Tests unitaires et d'intégration
├── docs/                           # Documentation
│   ├── adr/                        # Architecture Decision Records
│   └── architecture.md             # Ce fichier
├── config.json                     # TOUTES les constantes et presets
├── requirements.txt                # Dépendances Python
├── build_windows.py                # Script de build PyInstaller optimisé
└── build_windows.bat               # Script batch automatisé pour Windows
```

---
## 1. Le Modèle (`src/model/`)

Le cœur de la simulation.

-   **`reactor_model.py`**:
    -   Classe principale : `ReactorModel`.
    -   Implémente les calculs physiques basés sur la **formule des six facteurs** et la théorie de la diffusion.
    -   Contient l'état interne du réacteur, mis à jour via une méthode `_update_parameter` générique.
    -   **Totalement découplé** : Ne contient aucune valeur "magique". Tous les coefficients, constantes physiques et paramètres de simulation sont chargés depuis le module `config`.

-   **`config.py`**:
    -   Charge et expose les paramètres de `config.json`.
    -   Ne contient aucune logique, uniquement des données de configuration.

## 2. Le Contrôleur (`src/controller/`)

L'orchestrateur de l'application.

-   **`reactor_controller.py`**:
    -   Classe principale : `ReactorController`.
    -   Agit comme une simple **façade** pour le modèle.
    -   Traduit les actions de la Vue en appels au Modèle sans ajouter de logique.

## 3. La Vue (`src/gui/`)

L'interface et l'expérience utilisateur.

-   **`main_window.py`**:
    -   Classe principale : `MainWindow`.
    -   Construit l'interface et assemble les widgets.
    -   Instancie le `ReactorController`.
    -   Connecte les signaux des widgets à des slots qui appellent le contrôleur via une méthode générique `_update_parameter_and_ui`.
    -   Utilise `blockSignals` pour une synchronisation claire et robuste entre les widgets (ex: slider et spinbox).

### Widgets de Visualisation

-   **`widgets/`**: Contient tous les composants graphiques, y compris les graphiques Matplotlib et les widgets QPainter.
-   **`visualization.py`**: Gère la disposition des graphiques dans un `QTabWidget`.

## Principes de Conception après Refactorisation

1.  **Séparation Stricte des Responsabilités** : MVC clairement implémenté.
2.  **Configuration Externalisée** : `config.json` est la source unique de vérité pour toutes les constantes.
3.  **Don't Repeat Yourself (DRY)** : Logique dupliquée éliminée dans le modèle (`_update_parameter`) et la vue (`_update_parameter_and_ui`).
4.  **Cohérence Linguistique** : Interface, commentaires et documentation principalement en français.
5.  **Build Optimisé** : Le script `build_windows.py` a été nettoyé des options redondantes. 