# Guide Express : Création d'un Exécutable Windows pour NeutroScope

## ⚡ Mode d'emploi rapide

 Lancer le script `build_windows.bat` à la racine du projet.

Le script va :
- Vérifier Python et pip
- Créer/activer un environnement virtuel
- Installer les dépendances
- Lancer le build
- Placer l'exécutable dans le dossier `releases/`

## 📁 Après le build

- L'exécutable `NeutroScope.exe` se trouve dans `releases/`
- **Le fichier `config.json` doit impérativement être placé dans le même dossier que l'exécutable lors du partage.**
- Copiez ce dossier sur OneDrive pour le partager

## ⚠️ ATTENTION : Problème fréquent de fin de lignes (CRLF)

> **Si le script `build_windows.bat` affiche des erreurs étranges ou ne fonctionne pas** :
> - Vérifiez que le fichier utilise bien les fins de ligne **CRLF** (standard Windows), pas LF (Unix).
> - Ouvrez-le dans VS Code ou Notepad++ et convertissez si besoin (voir l'icône en bas à droite).
> - Un script batch avec de mauvaises fins de ligne ne sera pas compris par Windows !

## 🛠️ En cas de problème

- **Erreur "n’est pas reconnu en tant que commande"** :
  - Presque toujours un problème de fins de ligne (voir ci-dessus)
- **Erreur Python/pip non trouvé** :
  - Installez Python 3.8+ depuis https://python.org
- **L'exécutable ne se lance pas** :
  - Vérifiez que tous les fichiers sont dans `releases/`
  - Testez sur une machine Windows récente

## 📝 Notes

- Pour un build manuel :
  1. `pip install -r requirements.txt`
  2. `python build_windows.py`
- Pour personnaliser l'icône, placez `icon.ico` dans `docs/`
- Pour réduire la taille, voir la doc avancée

---

Pour toute question, contactez le responsable du projet ou consultez la documentation complète. 