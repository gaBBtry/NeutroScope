# Architecture de NeutroScope

## Vue d'ensemble

NeutroScope est une application pédagogique de simulation neutronique pour les Réacteurs à Eau Pressurisée (REP). L'application suit une architecture Model-View-Controller (MVC) pour séparer la logique métier de l'interface utilisateur.

## Structure du projet

```
NeutroScope/
├── main.py                 # Point d'entrée de l'application
├── config.json            # Configuration et constantes physiques
├── requirements.txt       # Dépendances Python
├── build_windows.py       # Script de build pour Windows
├── build_windows.bat      # Script batch pour faciliter le build
└── src/
    ├── model/             # Couche Modèle
    │   ├── reactor_model.py    # Modèle physique du réacteur
    │   ├── config.py          # Chargeur de configuration
    │   └── calculators/       # Modules de calcul spécialisés
    ├── controller/        # Couche Contrôleur
    │   └── reactor_controller.py  # Contrôleur principal
    └── gui/              # Couche Vue
        ├── main_window.py     # Fenêtre principale
        ├── visualization.py   # Panneau de visualisation
        └── widgets/          # Widgets personnalisés

```

## Architecture MVC

### Modèle (`src/model/`)

Le modèle contient toute la logique de simulation neutronique :

- **`reactor_model.py`** : Classe principale qui implémente les calculs neutroniques
  - Calcul des quatre facteurs (η, ε, p, f)
  - Calcul du k-effectif et de la réactivité
  - Calcul du temps de doublement
  - Gestion des préréglages

- **`config.py`** : Module de configuration qui charge les constantes depuis `config.json`
  - Constantes physiques (β, temps de vie des neutrons prompts, etc.)
  - Coefficients des modèles
  - Paramètres de géométrie du cœur

### Vue (`src/gui/`)

L'interface utilisateur est construite avec PyQt6 :

- **`main_window.py`** : Fenêtre principale de l'application
  - Panneau de contrôle avec sliders pour les paramètres
  - Affichage des paramètres calculés
  - Gestion des préréglages

- **`visualization.py`** : Panneau contenant tous les graphiques
  - Distribution axiale du flux
  - Diagramme des quatre facteurs
  - Bilan neutronique
  - Diagramme de pilotage
  - Cycle neutronique

- **`widgets/`** : Widgets personnalisés réutilisables
  - Boutons d'information et de crédits
  - Panneaux d'information contextuels
  - Boîtes de dialogue personnalisées

### Contrôleur (`src/controller/`)

- **`reactor_controller.py`** : Fait le lien entre la vue et le modèle
  - Transmet les changements de paramètres au modèle
  - Récupère les résultats calculés pour la vue
  - Gère l'application des préréglages

## Flux de données

1. **Entrée utilisateur** : L'utilisateur modifie un paramètre via l'interface
2. **Signal Qt** : Un signal est émis vers le gestionnaire d'événements approprié
3. **Contrôleur** : Le gestionnaire appelle la méthode correspondante du contrôleur
4. **Modèle** : Le contrôleur met à jour le modèle et déclenche les calculs
5. **Résultats** : Les résultats sont renvoyés au contrôleur
6. **Mise à jour UI** : Le contrôleur met à jour l'interface avec les nouveaux résultats

## Configuration

Le fichier `config.json` centralise toutes les constantes du projet :

- **Constantes physiques** : β, temps de vie des neutrons, etc.
- **Coefficients des modèles** : Paramètres pour les calculs des quatre facteurs
- **Géométrie du cœur** : Dimensions pour les calculs de fuite
- **Préréglages** : Configurations prédéfinies du réacteur

## Build et distribution

L'application peut être compilée en exécutable Windows autonome :

- **`build_windows.py`** : Script Python utilisant PyInstaller
- **`build_windows.bat`** : Script batch pour automatiser le processus
- L'exécutable final est créé dans le dossier `releases/`

## Technologies utilisées

- **Python 3.x** : Langage principal
- **PyQt6** : Framework d'interface graphique
- **NumPy** : Calculs numériques
- **Matplotlib** : Graphiques scientifiques
- **SciPy** : Fonctions scientifiques avancées
- **PyInstaller** : Création d'exécutables

## Principes de conception

1. **Séparation des responsabilités** : Architecture MVC stricte
2. **Configuration centralisée** : Toutes les constantes dans `config.json`
3. **Code maintenable** : Méthodes courtes et focalisées
4. **Interface bilingue** : UI en français, code/commentaires techniques en français
5. **Approche pédagogique** : Modèles simplifiés mais physiquement cohérents 