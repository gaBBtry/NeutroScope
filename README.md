# NeutroScope

**Simulateur pédagogique avancé du cycle neutronique – Production Ready**

NeutroScope est un simulateur interactif de physique des réacteurs nucléaires, conçu pour l'enseignement et la formation professionnelle. Il permet de visualiser, manipuler et comprendre en profondeur le cycle de vie des neutrons, la criticité, la réactivité et les phénomènes temporels complexes (dynamique xénon, effets de température, scénarios transitoires). L'interface est 100% en français, moderne, épurée et adaptée à tous les niveaux.

## Fonctionnalités principales

- **Visualisation du cycle neutronique** : Diagramme interactif à six facteurs, flux de neutrons, pertes, fissions, etc.
- **Simulation temporelle automatisée** : Contrôles Play/Pause/Stop, évolution continue des concentrations d'isotopes (I-135, Xe-135), graphiques dynamiques.
- **Contrôles physiques réalistes** : Barres de contrôle (groupes R/GCP), bore, température, puissance, tous configurables en temps réel.
- **Scénarios prédéfinis (presets)** : Début/fin de cycle, fonctionnement en puissance, transitoires xénon, etc. – extensibles via `config.json`.
- **Audit physique intégré** : Validation automatique de la cohérence physique (standards PWR, calibration industrielle).
- **Info-bulles universelles** : Explications pédagogiques sur chaque élément, aide contextuelle détaillée (touche "i").
- **Interface épurée et robuste** : Protection anti-plantage, synchronisation sécurisée, architecture modulaire.

## Installation rapide (Windows)

1. **Téléchargez ou clonez** le projet NeutroScope sur votre PC Windows.
2. **Double-cliquez** sur le fichier `build_windows.bat` à la racine du projet.
3. Laissez le script s’exécuter (quelques minutes).  
   Il installe les dépendances, prépare l’environnement et crée l’exécutable.
4. À la fin, l’exécutable `NeutroScope.exe` sera disponible dans le dossier `releases/`.

**Prérequis** :
- Windows avec Python 3.8+ et pip installés (voir [python.org](https://python.org) si besoin).
- Connexion internet pour la première installation.

**Dépannage** :
- Si une erreur indique que Python ou pip est manquant, installez-les puis relancez le script.
- Si le build échoue, consultez les messages affichés dans la console pour identifier le problème.

**Partage** :
- Vous pouvez copier le dossier `releases/` (et son contenu) sur une clé USB ou un service cloud (ex : OneDrive) pour distribuer l’exécutable.

**Pour plus de détails, de dépannage ou d’options avancées, consultez le guide complet dans `docs/BUILD_WINDOWS.md`.**

## Architecture du projet

- `main.py` : Point d'entrée de l'application.
- `config.json` : **Source unique de vérité** – tous les paramètres physiques, UI, presets, textes d'aide.
- `src/` : Code source principal.
    - `model/` : Logique physique, simulation, gestion des presets.
    - `controller/` : Orchestration, pont entre modèle et interface, expose la configuration à la vue.
    - `gui/` : Interface utilisateur dynamique, widgets, visualisations, info-bulles.

## Extension et personnalisation

- **Ajout de paramètres ou scénarios** : Modifiez simplement `config.json` (voir documentation et workflows dans `.cursor/rules/memory-bank/tasks.md`).
- **Architecture modulaire** : Ajoutez de nouveaux widgets, visualisations ou modèles physiques sans modifier l’interface existante.
- **Internationalisation** : Toute l’interface est en français, mais la structure permet une adaptation future.
