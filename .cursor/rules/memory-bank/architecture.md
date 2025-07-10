# Architecture de NeutroScope

Ce document décrit l'architecture logicielle finale de l'application NeutroScope, en se concentrant sur la séparation des responsabilités et le flux de données dans sa forme complète et opérationnelle.

## Vue d'ensemble : Modèle-Vue-Contrôleur (MVC) Dirigé par la Configuration

Le projet est structuré selon une variante sophistiquée du design pattern **Modèle-Vue-Contrôleur (MVC)**. L'architecture a été refactorisée pour être **entièrement pilotée par la configuration**, où le fichier `config.json` agit comme la source unique de vérité pour tous les paramètres, y compris la physique du réacteur, les limites opérationnelles et la configuration de l'interface utilisateur.

**ARCHITECTURE FINALE** :
- **Modèle (`src/model/`)**: Contient la logique de simulation pure. Il est complètement découplé de l'interface et ses paramètres initiaux, ainsi que ses constantes physiques, sont exclusivement chargés depuis `config.json`.
- **Vue (`src/gui/`)**: Responsable de l'affichage. Sa construction (libellés, plages de valeurs, textes d'aide) est **dynamiquement générée** à partir de la configuration fournie par le contrôleur. **Aucune valeur n'est codée en dur**.
- **Contrôleur (`src/controller/`)**: Sert de pont robuste, exposant non seulement les données du modèle, mais aussi la configuration de l'interface (`get_gui_settings`, `get_parameter_config`) à la Vue.

## Structure du Projet et Relations des Composants

```
NeutroScope/ (Architecture Finale pilotée par config.json)
├── src/
│   ├── model/                      # MODÈLE (Logique métier pure)
│   │   ├── reactor_model.py        # Simulation physique, utilise config.py
│   │   ├── preset_model.py         # Logique des presets
│   │   └── config.py               # Chargeur et adaptateur pour config.json
│   │
│   ├── controller/                 # CONTRÔLEUR (Orchestration et pont de config)
│   │   └── reactor_controller.py   # Expose les données et la configuration à la Vue
│   │
│   └── gui/                        # VUE (Interface dynamique, sans valeurs codées en dur)
│       ├── main_window.py          # Se construit dynamiquement via le contrôleur
│       ├── visualization.py        # Gestionnaire de visualisations
│       └── widgets/                # Widgets configurables
│
├── config.json                     # SOURCE UNIQUE DE VÉRITÉ
│   ├── gui_settings                # Configuration de la fenêtre et des widgets
│   ├── physical_constants          # Constantes physiques
│   ├── parameters_config           # Configuration de TOUS les paramètres (plages, pas, textes)
│   ├── four_factors                # ... etc ...
│   └── presets                     # Scénarios prédéfinis
│
├── user_presets.json               # Presets utilisateur (généré automatiquement)
└── ...
```

---
## 1. Le Modèle (`src/model/`) - Initialisation par Configuration

Le cœur de la simulation, dont l'état initial est entièrement défini par `config.json`.

### **`reactor_model.py`**
- **Initialisation (`__init__`)**: Les valeurs par défaut de tous les paramètres (positions des barres, bore, température, etc.) sont chargées depuis la section `default_state` de `config.json`.
- **Découplage total**: Aucune valeur "magique" ou constante n'est définie dans le code du modèle ; tout est lu via le module `config`.
- **Logique de calcul**: Utilise les constantes physiques et les coefficients des autres sections de `config.json`.

### **`config.py`**
- **Rôle central**: Charge le fichier `config.json` au démarrage.
- **Accès structuré**: Expose les différentes sections de la configuration (`gui_settings`, `parameters_config`, etc.) au reste de l'application.

## 2. Le Contrôleur (`src/controller/`) - Pont de Configuration

L'orchestrateur qui fournit à la Vue les données *et* la configuration pour se construire.

### **`reactor_controller.py`**
- **Nouvelles méthodes de configuration**:
  - `get_gui_settings()`: Fournit les paramètres généraux de l'interface (titre, dimensions).
  - `get_parameter_config(param_name)`: Fournit la configuration complète pour un contrôle d'interface spécifique (ex: 'boron', 'rod_group_R').
- **Rôle étendu**: Ne se contente pas de passer les données du modèle, mais fournit aussi les méta-données nécessaires à la Vue pour s'auto-configurer.

## 3. La Vue (`src/gui/`) - Construction Dynamique

L'interface utilisateur, qui est maintenant un simple "moteur de rendu" des informations et de la configuration qu'elle reçoit.

### **`main_window.py`**
- **Suppression des valeurs codées en dur**: Le dictionnaire `info_texts` et toutes les valeurs de plages, pas, et libellés ont été supprimés.
- **Construction dynamique (`create_control_panel`)**:
  - La méthode a été refactorisée pour utiliser une fonction d'aide (`_create_parameter_control`).
  - Cette fonction boucle sur les paramètres requis et appelle `controller.get_parameter_config()` pour chaque paramètre.
  - Les widgets (sliders, spinboxes) sont créés et configurés dynamiquement avec les informations récupérées (plage, pas, suffixe, texte d'info).
- **Principe de "Configuration over Code"**: Le comportement et l'apparence de l'interface sont définis dans `config.json`, pas dans le code de la Vue.

## Flux de Données - Piloté par la Configuration

1.  **Démarrage**: `config.py` charge `config.json`.
2.  **Initialisation du Modèle**: `ReactorModel` lit ses valeurs par défaut depuis `config.default_state`.
3.  **Initialisation de la Vue**:
    - `MainWindow` demande au `ReactorController` les `gui_settings` et la configuration de chaque paramètre.
    - `MainWindow` construit dynamiquement ses widgets en fonction de la configuration reçue.
4.  **Interaction Utilisateur**:
    - L'utilisateur interagit avec un widget (ex: slider du bore).
    - L'action est transmise au `ReactorController`, qui met à jour le `ReactorModel`.
    - Le `ReactorModel` recalcule ses paramètres.
    - Le `ReactorController` récupère les nouvelles données et les renvoie à la `MainWindow`, qui met à jour les affichages.

## Principes de Conception Finaux

1.  **Source Unique de Vérité (`Single Source of Truth`)**: `config.json` est le seul endroit où la configuration est définie. Toute modification de paramètre se fait dans ce fichier, sans toucher au code.
2.  **Configuration over Code**: La structure et le comportement de l'application sont définis par des données de configuration, pas par du code impératif.
3.  **Découplage Poussé**:
    - Le Modèle ne connaît rien de la Vue.
    - La Vue ne contient aucune logique métier ni de configuration en dur ; elle est entièrement dépendante de ce que le Contrôleur lui fournit.
4.  **Don't Repeat Yourself (DRY)**: La création de widgets dans la Vue a été factorisée pour éliminer la duplication de code.

## Impact Architectural Final

Cette architecture entièrement pilotée par la configuration transforme NeutroScope en une application extrêmement flexible et maintenable.
- **Clarté architecturale**: Les responsabilités sont plus claires que jamais. Le Modèle calcule, le Contrôleur orchestre, la Vue affiche ce qu'on lui dit d'afficher.
- **Maintenabilité**: Pour changer une plage de valeurs, un libellé, ou un texte d'aide, il suffit de modifier une ligne dans `config.json`. Aucune recompilation n'est nécessaire.
- **Extensibilité**: Ajouter un nouveau paramètre contrôlable à l'interface devient trivial : il suffit de l'ajouter à `config.json` et d'appeler la fonction de création de widget dans `main_window.py`.
- **Qualité Éducative**: Les textes d'aide et les scénarios sont centralisés et facilement modifiables par des non-développeurs.

## Conclusion Architecturale

L'architecture finale de NeutroScope représente un exemple abouti du principe de **séparation des préoccupations**, renforcé par un pilotage par la configuration. Elle constitue une base solide et évolutive, optimisant la flexibilité et la facilité de maintenance pour un outil éducatif de niveau professionnel. 