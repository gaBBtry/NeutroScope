# Technologies et Environnement de Développement

Ce document décrit les technologies, outils et pratiques utilisés dans le projet NeutroScope.

## Technologies Clés

-   **Langage** : **Python 3.12+**
    -   Choisi pour son écosystème scientifique, sa lisibilité et sa rapidité de développement.
-   **Interface Utilisateur (UI)** : **PyQt6**
    -   Framework GUI robuste et multi-plateforme.

## Librairies Principales

-   **Calculs Numériques** : **NumPy**
    -   Utilisé pour les opérations sur les tableaux dans le modèle du réacteur.
-   **Visualisation de Données** : **Matplotlib**
    -   Intégré à PyQt6 pour générer les graphiques.
-   **Utilitaires Scientifiques** : **SciPy**
    -   Utilisé pour des fonctions scientifiques spécifiques.

## Architecture de Données : `config.json` comme Source Unique de Vérité

L'application est entièrement pilotée par un fichier de configuration central.

-   **`config.json`** : Source unique de vérité pour tous les paramètres.
-   **Sections organisées** :
    - `gui_settings`: Configure l'apparence de la fenêtre (titre, taille) et les dimensions des widgets.
    - `physical_constants`: Constantes physiques fondamentales.
    - `parameters_config`: **Définit TOUS les paramètres de l'interface utilisateur**. Chaque paramètre (ex: `boron`, `rod_group_R`) a son propre objet contenant son libellé, sa plage de valeurs, son pas d'incrémentation, son suffixe et son texte d'information.
    - `four_factors`, `neutron_leakage`, etc. : Coefficients pour la simulation physique.
    - `presets`: Scénarios prédéfinis.
    - `default_state`: Valeurs d'initialisation du modèle de réacteur.

-   **Validation** : La cohérence des paramètres est implicitement gérée par la structure de `config.json`.

## Modélisation Physique

-   **Modèle Six Facteurs Complet** : Implémentation rigoureuse avec tous les contre-effets de température et grappes pondérées.
-   **Initialisation par Configuration**: Le `ReactorModel` est initialisé avec les valeurs de la section `default_state` de `config.json`.
-   **Simulation Temporelle Avancée**: Implémentation des équations de Bateman pour la cinétique Xénon-135.

## Architecture Logicielle : MVC Dirigé par la Configuration

-   **Modèle (`src/model/`)**: Logique de simulation pure, initialisée par `config.json`.
-   **Vue (`src/gui/`)**: Interface entièrement dynamique. Elle se construit en demandant la configuration au Contrôleur. **Aucune valeur (plage, libellé, texte) n'est codée en dur.**
-   **Contrôleur (`src/controller/`)**: Sert de pont et expose les données du modèle ainsi que la configuration de l'interface (`get_gui_settings`, `get_parameter_config`) à la Vue.

## Interface Utilisateur Dynamique

-   **Construction par Configuration**: Les widgets de contrôle (`QSlider`, `QDoubleSpinBox`) sont créés et entièrement configurés (plages, pas, suffixes) à partir des données de `parameters_config` lues dans `config.json`.
-   **Système d'Information Unifié**: Les textes d'aide sont également chargés depuis `config.json`.

## Outils de Développement et Qualité

-   **Build et Déploiement** : **PyInstaller** avec des scripts de build automatisés.
-   **Note** : Il n'existe plus de validation automatique par tests (unitaires, d'intégration ou de validation physique) dans le projet. Toute vérification doit être réalisée manuellement.

## Optimisations et Améliorations Récentes

### **Précision Numérique Avancée**
-   **Algorithme Runge-Kutta 4** : Remplacement de l'intégration d'Euler pour la simulation temporelle des isotopes Xénon-135
-   **Précision améliorée** : Réduction significative des erreurs numériques pour les pas de temps longs (>1 heure)
-   **Stabilité temporelle** : Conservation des équations de Bateman sur de longues périodes de simulation

### **Architecture de Code Optimisée**
-   **Refactorisation Modulaire** : Décomposition des méthodes monolithiques
    - `calculate_four_factors()` → méthodes privées spécialisées (`_calculate_eta()`, `_calculate_p()`, etc.)
    - Code plus maintenable et testable individuellement
    - Séparation claire des responsabilités physiques
-   **Élimination Constantes Magiques** : Centralisation complète dans `config.json`
    - Section `unit_conversions` pour toutes les constantes de conversion
    - Aucune valeur codée en dur dans le code source
    - Configuration 100% externalisée

## Dépendances Critiques (`requirements.txt`)
```
PyQt6
numpy
matplotlib
scipy
pyinstaller
```

## Principes Techniques Appliqués

1.  **Source Unique de Vérité**: `config.json` est le seul point de modification pour tout paramètre, qu'il soit physique ou visuel.
2.  **Configuration over Code**: L'apparence et les limites de l'interface sont définies par des données, non par du code.
3.  **Séparation Stricte des Responsabilités**: Le Modèle calcule, le Contrôleur orchestre et configure, la Vue affiche.
4.  **Don't Repeat Yourself (DRY)**: La création des widgets de l'interface est factorisée dans une méthode unique qui lit la configuration.
5.  **Numerical Accuracy**: Utilisation d'algorithmes numériquement stables pour les simulations temporelles.

## Conclusion Technique

L'implémentation technique de NeutroScope représente un équilibre optimal entre la rigueur scientifique et la flexibilité de la configuration. L'architecture est maintenant plus simple, plus maintenable et plus facilement extensible, constituant une base professionnelle et robuste. Les récentes optimisations transforment le projet d'un simulateur éducatif vers un outil pédagogique de niveau professionnel avec une précision numérique industrielle et une robustesse logicielle exemplaire. 