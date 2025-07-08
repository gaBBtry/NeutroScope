# Deployment Strategy - Windows Executable

Ce document détaille la stratégie de déploiement de NeutroScope via un exécutable Windows partagé sur OneDrive d'entreprise.

## Vue d'ensemble

NeutroScope utilise PyInstaller pour créer un exécutable Windows autonome qui peut être distribué via OneDrive d'entreprise sans nécessiter d'installation Python sur les machines cibles.

## Architecture de Build

### Scripts de Build
- **`build_windows.bat`** : Script batch principal pour utilisateurs finaux
  - Validation automatique de l'environnement (Python, répertoire)
  - Activation automatique de l'environnement virtuel si présent
  - Installation automatique des dépendances et PyInstaller
  - Lancement du build et validation du résultat
  - Interface utilisateur claire avec messages en français

- **`build_windows.py`** : Script Python avec contrôle avancé
  - Nettoyage automatique des builds précédents
  - Configuration optimisée PyInstaller avec gestion d'erreurs
  - Validation post-build et statistiques de taille
  - Copie automatique des fichiers additionnels

### Configuration PyInstaller

```python
# Options critiques pour résoudre les problèmes de modules
"--collect-submodules=src",     # Inclusion récursive tous modules src
"--paths=src",                  # Ajout src au chemin de recherche
"--hidden-import=src.controller.reactor_controller",
"--hidden-import=src.model.reactor_model",
"--hidden-import=src.gui.main_window",

# Optimisations de taille
"--exclude-module=tkinter",
"--exclude-module=unittest", 
"--exclude-module=test",

# Ressources
"--add-data=config.json;.",     # Inclusion fichier configuration
```

## Problèmes Résolus

### ModuleNotFoundError
**Problème** : `ModuleNotFoundError: No module named 'src.controller'`
**Cause** : PyInstaller n'incluait pas automatiquement les modules du package `src`
**Solution** : 
- `--collect-submodules=src` pour inclusion récursive
- `--paths=src` pour chemin de recherche
- Imports cachés explicites pour modules critiques

### Optimisation Taille
**Objectif** : Réduire la taille de l'exécutable (target ~50-80 MB)
**Méthodes** :
- Exclusion de modules inutiles (tkinter, unittest, test)
- Imports cachés ciblés uniquement pour les dépendances nécessaires
- Configuration matplotlib optimisée

## Processus de Déploiement

### 1. Création de l'Exécutable
```bash
# Méthode simple
build_windows.bat

# Méthode avancée
python build_windows.py
```

### 2. Validation
- Vérification automatique de la création de `releases/NeutroScope.exe`
- Test de lancement sur machine de développement
- Validation de la taille finale (~50-80 MB attendu)

### 3. Partage OneDrive
1. Copie du dossier `releases/` complet sur OneDrive d'entreprise
2. Attente de la synchronisation
3. Génération du lien de partage vers `NeutroScope.exe`
4. Distribution du lien aux utilisateurs cibles

### 4. Utilisation Finale
- Téléchargement direct de `NeutroScope.exe` depuis OneDrive
- Double-clic pour lancement (aucune installation requise)
- Tous les fichiers de configuration inclus dans l'exécutable

## Compatibilité

### Systèmes Supportés
- ✅ **Windows 10/11** : Compatibilité totale
- ✅ **Windows 8.1** : Compatible
- ⚠️ **Windows 7** : Peut nécessiter des mises à jour

### Dépendances Intégrées
- Python runtime complet
- PyQt6 avec tous les modules GUI
- NumPy et SciPy pour calculs scientifiques
- Matplotlib pour visualisations
- Toutes les dépendances système nécessaires

## Maintenance et Évolution

### Workflow de Release
1. Développement et tests en mode source
2. Mise à jour du numéro de version dans `main.py`
3. Exécution du build avec `build_windows.bat`
4. Test sur machine "propre" (sans Python)
5. Upload sur OneDrive et mise à jour du lien de partage

### Monitoring
- Surveillance de la taille de l'exécutable (augmentation significative = problème)
- Feedback utilisateurs sur compatibilité et performance
- Logs d'erreur Windows pour diagnostic de problèmes de lancement

### Évolutions Possibles
- **Signature numérique** : Éviter les avertissements antivirus
- **Auto-updater** : Mécanisme de mise à jour automatique
- **Compression UPX** : Réduction supplémentaire de la taille
- **Installeur MSI** : Alternative pour déploiement en entreprise 