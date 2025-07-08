# Guide de Création d'Exécutable Windows - NeutroScope

Ce guide explique comment créer un exécutable Windows autonome de NeutroScope pour le partage via OneDrive.

## 📋 Prérequis

1. **Python 3.8+** installé sur Windows
2. **Git** (optionnel, pour récupérer le code)
3. Une connexion internet pour télécharger les dépendances

## 🚀 Méthode Rapide (Recommandée)

### Étape 1: Préparer l'environnement
```bash
# Cloner le projet (si pas déjà fait)
git clone <url-du-repo> NeutroScope
cd NeutroScope

# Créer un environnement virtuel (recommandé)
python -m venv .venv
.venv\Scripts\activate
```

### Étape 2: Lancer le build automatique
Double-cliquez sur le fichier `build_windows.bat` ou exécutez-le depuis l'invite de commande :

```cmd
build_windows.bat
```

Ce script va automatiquement :
- ✅ Vérifier que Python est installé
- ✅ Installer toutes les dépendances nécessaires
- ✅ Installer PyInstaller si nécessaire
- ✅ Créer l'exécutable dans le dossier `releases/`
- ✅ Proposer d'ouvrir le dossier de sortie

## 🛠️ Méthode Manuelle

Si vous préférez contrôler chaque étape :

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Lancer le script de build
```bash
python build_windows.py
```

### 3. Vérifier la sortie
L'exécutable sera créé dans `releases/NeutroScope.exe`

## 📦 Résultat

Après un build réussi, vous trouverez dans le dossier `releases/` :
- `NeutroScope.exe` - L'exécutable principal (≈50-80 MB)
- `config.json` - Fichier de configuration (copié automatiquement)
- `README.md` - Documentation (si présente)

## 🌐 Partage via OneDrive

### Étape 1: Copier sur OneDrive
1. Copiez tout le dossier `releases/` dans votre OneDrive
2. Attendez la synchronisation

### Étape 2: Partager le lien
1. Clic droit sur `NeutroScope.exe` dans OneDrive
2. Sélectionnez "Partager" ou "Copier le lien"
3. Partagez le lien avec vos collègues

### Étape 3: Instructions pour les utilisateurs
Les utilisateurs peuvent :
1. Télécharger `NeutroScope.exe` depuis le lien OneDrive
2. Double-cliquer pour lancer l'application (aucune installation requise)

## 🔧 Configuration Avancée

### Optimisation de la taille
Si l'exécutable est trop volumineux, vous pouvez :

1. Modifier `build_windows.py` pour exclure certains modules :
```python
"--exclude-module=tkinter",
"--exclude-module=unittest",
```

2. Utiliser UPX pour compresser l'exécutable :
```bash
pip install upx-windows-binaries
# Ajouter --upx-dir à la commande PyInstaller
```

### Personnalisation de l'icône
1. Placez un fichier `icon.ico` dans le dossier `docs/`
2. Le script de build l'utilisera automatiquement

### Signature numérique (Entreprise)
Pour éviter les avertissements Windows Defender :
1. Obtenez un certificat de signature de code
2. Utilisez `signtool.exe` pour signer l'exécutable

## 🐛 Résolution de Problèmes

### Erreur "Module not found"
```bash
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Erreur "Permission denied"
- Fermez tous les antivirus temporairement
- Exécutez l'invite de commande en tant qu'administrateur

### L'exécutable ne se lance pas
1. Vérifiez que tous les fichiers sont présents dans `releases/`
2. Testez sur une machine Windows "propre" (sans Python installé)
3. Vérifiez les logs d'erreur Windows (Observateur d'événements)

### Antivirus bloque l'exécutable
C'est normal pour les exécutables PyInstaller. Solutions :
1. Ajouter une exception dans l'antivirus
2. Signer numériquement l'exécutable
3. Uploader sur VirusTotal pour analyse

## 📊 Informations Techniques

### Taille typique de l'exécutable
- **Base PyQt6 + NumPy + Matplotlib** : ≈50-80 MB
- **Avec toutes les dépendances** : ≈100-150 MB

### Temps de compilation
- **Machine moderne** : 2-5 minutes
- **Machine plus ancienne** : 5-15 minutes

### Compatibilité
- **Windows 10/11** : ✅ Totalement compatible
- **Windows 8.1** : ✅ Compatible
- **Windows 7** : ⚠️ Peut nécessiter des mises à jour

## 📝 Notes de Version

Lors de chaque release :
1. Mettre à jour le numéro de version dans `main.py`
2. Recréer l'exécutable avec ce guide
3. Tester sur une machine propre
4. Mettre à jour le lien OneDrive

## 🆘 Support

En cas de problème :
1. Vérifiez la section "Résolution de Problèmes" ci-dessus
2. Consultez les logs de build dans la console
3. Testez d'abord avec `python main.py` pour isoler le problème 