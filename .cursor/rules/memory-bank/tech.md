# Technologies et Environnement de Développement

Ce document décrit les technologies, outils et pratiques utilisés dans le projet NeutroScope.

## Technologies Clés

-   **Langage** : **Python 3.12+**
    -   Choisi pour son écosystème scientifique (NumPy, Matplotlib), sa lisibilité et sa rapidité de développement.
    -   **Extension temporelle** : Capacités avancées pour la résolution d'équations différentielles et la simulation temps réel.
-   **Interface Utilisateur (UI)** : **PyQt6**
    -   Framework GUI robuste et multi-plateforme offrant une apparence native.
    -   **Extensions** : Widgets temporels, graphiques temps réel, contrôles interactifs avancés.

## Librairies Principales

-   **Calculs Numériques** : **NumPy**
    -   Utilisé pour toutes les opérations numériques, notamment les calculs sur les tableaux dans le modèle du réacteur.
    -   **NOUVEAU** : Calculs matriciels pour l'évolution temporelle (équations de Bateman).
-   **Visualisation de Données** : **Matplotlib**
    -   Intégré à PyQt6 pour générer tous les graphiques (distribution de flux, quatre facteurs, etc.).
    -   **NOUVEAU** : Graphiques temporels animés, axes jumeaux pour visualisations multiples.
-   **Utilitaires Scientifiques** : **SciPy**
    -   Utilisé pour des fonctions scientifiques spécifiques si nécessaire.
    -   **NOUVEAU** : Potentiel pour méthodes d'intégration numérique avancées (future extension).

## Modélisation Physique Avancée

### Simulation Temporelle
-   **Équations Différentielles** : Implémentation directe des équations de Bateman pour la chaîne I-135 → Xe-135
-   **Méthodes Numériques** : Solutions analytiques exactes pour stabilité et performance optimales
-   **Gestion du Temps** : Avancement temporel contrôlé avec historique pour visualisations continues

### Physique des Réacteurs
-   **Modèle Six Facteurs** : Implémentation complète avec tous les contre-effets de température
-   **Théorie de la Diffusion** : Calculs de fuites neutroniques deux groupes
-   **Empoisonnement Neutronique** : Modélisation rigoureuse Xénon-135 avec constantes physiques réalistes
-   **Effets de Température** :
    - Effet Doppler sur le facteur de fission (η)
    - **NOUVEAU** : Effet de température du modérateur sur l'anti-résonance (p)

## Outillage et Développement

-   **Gestion d'Environnement** : **venv**
    -   Outil standard de Python pour créer des environnements virtuels isolés.
-   **Gestion des Dépendances** : `requirements.txt`
    -   Fichier standard listant tous les paquets Python requis.
-   **Tests** : **Pytest**
    -   Framework utilisé pour les tests unitaires et d'intégration.
    -   **Plugins** : `pytest-qt` (test des composants PyQt6), `pytest-cov` (mesure de la couverture de test).
    -   **NOUVEAU** : Tests de validation physique pour modèles temporels.
-   **Contrôle de Version** : **Git**
    -   Tout le code source est géré dans un dépôt Git.

## Build et Déploiement

-   **Outil de Build** : **PyInstaller**
    -   Crée des exécutables Windows autonomes avec toutes les dépendances incluses.
    -   La configuration est optimisée pour les applications PyQt6 avec Matplotlib, et les options redondantes ont été supprimées pour simplifier la maintenance.
-   **Scripts de Build** :
    -   `build_windows.bat` : Script batch automatisé pour une utilisation simple.
    -   `build_windows.py` : Script Python pour un contrôle avancé, le nettoyage et la validation.
-   **Déploiement** : Partage via **OneDrive** d'entreprise.

## Structure du Projet Étendue

-   Le projet suit une architecture MVC claire avec extensions temporelles :
    -   `src/model/` : Logique de simulation **+ modèles temporels**.
    -   `src/gui/` : Composants de l'interface **+ visualisations temporelles**.
    -   `src/controller/` : Pont entre le modèle et l'interface **+ contrôles temporels**.
    -   `tests/` : Tous les fichiers de test **+ validation physique**.
    -   `docs/` : Documentation du projet.
    -   `config.json` : **Source unique de vérité** pour toutes les constantes physiques, préréglages **+ paramètres temporels**.

## Performance et Optimisations

### Simulation Temps Réel
-   **Calculs Optimisés** : Solutions analytiques plutôt que numériques pour les équations de Bateman
-   **Gestion Mémoire** : Historique temporel avec limitation automatique pour éviter les fuites
-   **Interface Réactive** : Mise à jour asynchrone des graphiques pour fluidité maximale

### Scalabilité
-   **Architecture Modulaire** : Facilite l'ajout de nouveaux isotopes ou phénomènes temporels
-   **Configuration Externalisée** : Tous les paramètres physiques modifiables sans recompilation
-   **Design Patterns** : MVC strict maintenu même avec complexité temporelle accrue

## Contraintes Techniques

### Plateforme
-   **Windows** : Déploiement principal via PyInstaller
-   **Cross-platform** : Architecture PyQt6 compatible Linux/macOS (non testé)

### Performance
-   **Calculs** : Optimisés pour simulation temps réel (<100ms par step temporel)
-   **Mémoire** : Gestion efficace de l'historique temporel
-   **Interface** : Responsive même avec graphiques temps réel

### Pédagogie
-   **Simplicité** : Interface accessible aux débutants malgré la complexité physique
-   **Progressivité** : Fonctionnalités de base (statique) et avancées (temporelle) séparées
-   **Explicabilité** : Info-bulles et explications physiques intégrées 