# NeutroScope - Simulation Pédagogique du Cycle Neutronique

NeutroScope est un logiciel de simulation interactif conçu comme un outil pédagogique pour l'apprentissage des principes de la physique des réacteurs nucléaires. Il se concentre sur la visualisation du cycle de vie des neutrons et l'impact des paramètres de pilotage sur la réactivité du cœur.

## Fonctionnalités

-   **Visualisation du cycle neutronique** : Suivez une population de neutrons à travers les six facteurs du cycle pour comprendre comment la criticité est atteinte.
-   **Contrôles interactifs** : Manipulez les barres de contrôle, la concentration en bore et les températures pour voir leur effet en temps réel.
-   **Données en temps réel** : Observez `k_eff`, la réactivité (en pcm) et la valeur de chaque facteur du cycle.
-   **Presets de scénarios** : Chargez des configurations de réacteur prédéfinies (début/fin de cycle, etc.).
-   **Interface Pédagogique** : Des info-bulles détaillées expliquent chaque paramètre et concept physique.

## Installation et Lancement

### Prérequis

-   Python 3.8+
-   PyQt6

### Installation

1.  **Clonez le dépôt**

    ```bash
    git clone https://github.com/votre-utilisateur/NeutroScope.git
    cd NeutroScope
    ```

2.  **Créez un environnement virtuel**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Windows: venv\Scripts\activate
    ```

3.  **Installez les dépendances**

    ```bash
    pip install -r requirements.txt
    ```

### Lancement

```bash
python main.py
```

## Structure du Projet

-   `main.py` : Point d'entrée de l'application.
-   `config.json` : Fichier de configuration pour les paramètres physiques et les presets.
-   `src/` : Code source de l'application.
    -   `model/` : Logique de la simulation physique (`reactor_model.py`).
    -   `controller/` : Pont entre le modèle et l'interface (`reactor_controller.py`).
    -   `gui/` : Tous les composants de l'interface utilisateur (fenêtre principale, widgets, graphiques).
-   `tests/` : Tests unitaires et d'intégration.
-   `docs/` : Documentation du projet.
-   `data/` : Données (si nécessaire pour de futures extensions).

## Comment Contribuer

Les contributions sont les bienvenues ! Veuillez suivre les étapes suivantes :

1.  Forkez le projet.
2.  Créez une branche pour votre fonctionnalité (`git checkout -b feature/NouvelleFonctionnalite`).
3.  Commitez vos changements (`git commit -m 'Ajout de la fonctionnalité X'`).
4.  Poussez vers la branche (`git push origin feature/NouvelleFonctionnalite`).
5.  Ouvrez une Pull Request.
