# Architecture de NeutroScope

Ce document décrit l'architecture logicielle de l'application NeutroScope, en se concentrant sur la séparation des responsabilités et le flux de données.

## Vue d'ensemble : Modèle-Vue-Contrôleur (MVC)

Le projet est structuré selon une variante du design pattern **Modèle-Vue-Contrôleur (MVC)** pour garantir une séparation claire entre la logique métier (la physique du réacteur), l'interface utilisateur et la gestion des entrées.

-   **Modèle (`src/model/`)**: Contient la logique de simulation pure. Il ne connaît rien de l'interface utilisateur.
-   **Vue (`src/gui/`)**: Responsable de l'affichage de l'information et de la capture des interactions de l'utilisateur.
-   **Contrôleur (`src/controller/`)**: Sert de pont entre le Modèle et la Vue.

---

## 1. Le Modèle (`src/model/`)

Le cœur de la simulation.

-   **`reactor_model.py`**:
    -   Classe principale : `ReactorModel`.
    -   Implémente les calculs physiques basés sur la **formule des six facteurs** et la théorie de la diffusion à deux groupes pour les fuites.
    -   Contient l'état interne du réacteur : position des barres, concentration en bore, températures, etc.
    -   Expose des méthodes pour mettre à jour ces paramètres et recalculer l'état du réacteur (`k_eff`, réactivité, etc.).
    -   Gère la logique des presets (chargement, sauvegarde).

-   **`config.py`**:
    -   Charge les paramètres de configuration depuis `config.json` (constantes physiques, coefficients du modèle, presets par défaut).
    -   Ne contient aucune logique de simulation, seulement des données.

## 2. Le Contrôleur (`src/controller/`)

L'orchestrateur de l'application.

-   **`reactor_controller.py`**:
    -   Classe principale : `ReactorController`.
    -   Instancie le `ReactorModel`.
    -   Expose des méthodes que la Vue peut appeler en réponse aux actions de l'utilisateur (ex: `update_control_rod_position`).
    -   Traduit les actions de la Vue en appels au Modèle.
    -   Formate les données du Modèle pour qu'elles soient facilement consommables par la Vue.

## 3. La Vue (`src/gui/`)

L'interface utilisateur et l'expérience utilisateur.

-   **`main_window.py`**:
    -   Classe principale : `MainWindow`.
    -   Construit la fenêtre principale et assemble tous les widgets.
    -   Instancie le `ReactorController`.
    -   Connecte les signaux des widgets (ex: `slider.valueChanged`) aux slots (méthodes) correspondants qui appellent le contrôleur.

-   **`widgets/`**:
    -   Contient des composants d'interface réutilisables (graphiques, panneaux d'information, boutons personnalisés).
    -   Chaque widget est conçu pour être aussi autonome que possible.

-   **`visualization.py`**:
    -   Gère la mise en page et l'orchestration des différents graphiques (flux, facteurs, etc.).

## Flux de Données (Exemple : Mouvement d'un slider)

1.  **Utilisateur** : Déplace le slider de la position des barres de contrôle.
2.  **Vue (`MainWindow`)**: Le signal `valueChanged` du `QSlider` est émis.
3.  **Vue (`MainWindow`)**: Le slot connecté (`on_rod_position_changed`) est appelé.
4.  **Vue (`MainWindow`)**: Appelle `self.controller.update_control_rod_position(new_value)`.
5.  **Contrôleur (`ReactorController`)**: Appelle `self.model.update_control_rod_position(new_value)`.
6.  **Modèle (`ReactorModel`)**: Met à jour son état interne (`self.control_rod_position`).
7.  **Modèle (`ReactorModel`)**: Lance un recalcul complet (`calculate_all()`).
8.  **Contrôleur (`ReactorController`)**: Récupère les nouvelles données du modèle (`get_reactor_parameters`, `get_four_factors_data`, etc.).
9.  **Vue (`MainWindow`)**: Met à jour les labels (`k_effective_label`, etc.) et les graphiques avec les nouvelles données.

Cette architecture garantit que la logique de simulation peut être testée indépendamment de l'interface, et que l'interface peut être modifiée sans impacter la physique du modèle.

-   **`widgets/`**:
    -   Contient des composants d'interface réutilisables (graphiques, panneaux d'information, boutons personnalisés).
    -   Le widget le plus important est `NeutronCyclePlot`, qui dessine le diagramme du cycle neutronique.
    -   Chaque widget est conçu pour être aussi autonome que possible.

-   **`visualization.py`**:
    -   Gère la mise en page des différents graphiques dans un `QTabWidget`.
    -   Le premier onglet est le nouveau `NeutronCyclePlot`.

## Flux de Données (Exemple : Mouvement d'un slider)

1.  **Utilisateur** : Déplace le slider de la position des barres de contrôle.
2.  **Vue (`MainWindow`)**: Le signal `valueChanged` du `QSlider` est émis.
3.  **Vue (`MainWindow`)**: Le slot connecté (`on_rod_position_changed`) est appelé.
4.  **Vue (`MainWindow`)**: Appelle `self.controller.update_control_rod_position(new_value)`.
5.  **Contrôleur (`ReactorController`)**: Appelle `self.model.update_control_rod_position(new_value)`.
6.  **Modèle (`ReactorModel`)**: Met à jour son état interne (`self.control_rod_position`).
7.  **Modèle (`ReactorModel`)**: Lance un recalcul complet (`calculate_all()`).
8.  **Contrôleur (`ReactorController`)**: Récupère les nouvelles données du modèle (`get_reactor_parameters`, `get_neutron_cycle_data`, etc.).
9.  **Vue (`MainWindow`)**: Appelle les méthodes de mise à jour de `VisualizationPanel`, qui à son tour met à jour tous les graphiques, y compris le `NeutronCyclePlot`.

Cette architecture garantit que la logique de simulation peut être testée indépendamment de l'interface, et que l'interface peut être modifiée sans impacter la physique du modèle. 