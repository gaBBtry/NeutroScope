# Contexte : NeutroScope - Architecture pilotée par la configuration

## Focus Actuel
- **STATUT FINAL** : Le refactoring majeur est terminé. NeutroScope est maintenant entièrement piloté par son fichier de configuration `config.json`, ce qui en fait une application robuste, maintenable et flexible.
- **Dernière modification majeure** : Centralisation de tous les paramètres (physiques, UI, états initiaux) dans `config.json`.

## Accomplissement Majeur Récent : Centralisation Complète de la Configuration ✅

Le projet a été entièrement refactorisé pour éliminer toutes les valeurs codées en dur et faire de `config.json` la **source unique de vérité**.

- **Principe de conception** : "Configuration over Code".
- **Impact** : Simplification drastique de la maintenance et de l'évolution du projet. La modification d'un paramètre, d'un libellé ou d'une limite se fait désormais en un seul endroit.

### 1. Centralisation de la configuration de l'Interface (`gui_settings`)
- **Problème** : Titre de la fenêtre, dimensions, et largeurs de widgets étaient codés en dur dans `main_window.py`.
- **Solution** : Création de la section `gui_settings` dans `config.json` pour contenir tous ces paramètres. `MainWindow` les lit désormais au démarrage via le contrôleur.

### 2. Centralisation des paramètres des contrôles (`parameters_config`)
- **Problème** : Les plages de valeurs, les pas d'incrémentation, les suffixes et les textes d'aide des sliders et spinboxes étaient définis directement dans `main_window.py`.
- **Solution** : Création de la section `parameters_config` dans `config.json`. Chaque paramètre (ex: `boron`, `rod_group_R`) possède maintenant un objet de configuration complet. L'interface se construit dynamiquement à partir de cette section.

### 3. Centralisation de l'état initial (`default_state`)
- **Problème** : Les valeurs d'initialisation du modèle (`ReactorModel`) étaient codées en dur dans son constructeur `__init__`.
- **Solution** : Création de la section `default_state` dans `config.json` pour définir l'état de départ du réacteur.

### 4. Centralisation des constantes de calcul
- **Problème** : Des constantes "magiques" (facteurs de conversion, tolérances) étaient dispersées dans le code.
- **Solution** : Ajout de `XENON_REACTIVITY_CONVERSION_FACTOR` et des `preset_matching_tolerances` dans `config.json` pour une meilleure clarté.

## État Technique Actuel

### Architecture Logicielle Finalisée
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
│   ├── parameters_config           # Configuration de TOUS les paramètres
│   ├── ... (autres sections)
│   └── presets                     # Scénarios prédéfinis
│
└── ...
```

### Flux de Travail
1.  **Configuration** : Toute modification de paramètre se fait dans `config.json`.
2.  **Chargement** : `src/model/config.py` charge le JSON au démarrage.
3.  **Initialisation** : Le `ReactorModel` et la `MainWindow` sont initialisés avec les valeurs de la configuration via le `ReactorController`.
4.  **Exécution** : L'application s'exécute avec les paramètres définis.

## Prochaines Étapes
- **Validation** : Tester l'application de manière exhaustive pour s'assurer que le refactoring n'a introduit aucune régression.
- **Packaging** : Préparer une nouvelle version exécutable de l'application.
- **Documentation** : Mettre à jour la documentation utilisateur si nécessaire pour refléter la nouvelle flexibilité de l'application.

## Remarques Finales
Le projet a atteint une maturité technique significative. L'architecture est désormais non seulement robuste et fonctionnelle, mais aussi extrêmement flexible et facile à maintenir. La centralisation de la configuration est un investissement majeur qui portera ses fruits pour toute évolution future du projet. 