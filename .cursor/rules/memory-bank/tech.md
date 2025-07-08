# Technologies et Environnement de Développement

Ce document décrit les technologies, outils et pratiques utilisés dans le projet NeutroScope.

## Technologies Clés

-   **Langage** : **Python 3.12+**
    -   Choisi pour son écosystème scientifique (NumPy, Matplotlib), sa lisibilité et sa rapidité de développement.
-   **Interface Utilisateur (UI)** : **PyQt6**
    -   Framework GUI robuste et multi-plateforme offrant une apparence native.

## Librairies Principales

-   **Calculs Numériques** : **NumPy**
    -   Utilisé pour toutes les opérations numériques, notamment les calculs sur les tableaux dans le modèle du réacteur.
-   **Visualisation de Données** : **Matplotlib**
    -   Intégré à PyQt6 pour générer tous les graphiques (distribution de flux, quatre facteurs, etc.).
-   **Utilitaires Scientifiques** : **SciPy**
    -   Utilisé pour des fonctions scientifiques spécifiques si nécessaire.

## Outillage et Développement

-   **Gestion d'Environnement** : **venv**
    -   Outil standard de Python pour créer des environnements virtuels isolés.
-   **Gestion des Dépendances** : `requirements.txt`
    -   Fichier standard listant tous les paquets Python requis.
-   **Tests** : **Pytest**
    -   Framework utilisé pour les tests unitaires et d'intégration.
    -   **Plugins** : `pytest-qt` (test des composants PyQt6), `pytest-cov` (mesure de la couverture de test).
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

## Structure du Projet

-   Le projet suit une architecture MVC claire :
    -   `src/model/` : Logique de simulation.
    -   `src/gui/` : Composants de l'interface.
    -   `src/controller/` : Pont entre le modèle et l'interface.
    -   `tests/` : Tous les fichiers de test.
    -   `docs/` : Documentation du projet.
    -   `config.json` : **Source unique de vérité** pour toutes les constantes physiques et les préréglages. 