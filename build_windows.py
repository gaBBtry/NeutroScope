#!/usr/bin/env python3
"""
Script de build pour créer l'exécutable Windows de NeutroScope
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """Script principal de build"""
    print("🔧 Création de l'exécutable Windows NeutroScope...")
    
    # Vérifier que nous sommes dans le bon répertoire
    if not Path("main.py").exists():
        print("❌ Erreur: main.py non trouvé. Exécutez ce script depuis la racine du projet.")
        sys.exit(1)
    
    # Nettoyer les builds précédents
    print("🧹 Nettoyage des builds précédents...")
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"   Supprimé: {dir_name}")
    
    # Supprimer les fichiers .spec existants
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"   Supprimé: {spec_file}")
    
    # Créer le répertoire de sortie
    output_dir = Path("releases")
    output_dir.mkdir(exist_ok=True)
    
    # Commande PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                    # Un seul fichier exécutable
        "--windowed",                   # Pas de console (interface graphique)
        "--name=NeutroScope",           # Nom de l'exécutable
        "--icon=docs/icon.ico" if Path("docs/icon.ico").exists() else "",  # Icône si disponible
        "--add-data=config.json;.",     # Inclure le fichier de config
        "--paths=src",                  # Ajouter src au path de recherche
        "--hidden-import=PyQt6.QtCore", # Imports cachés nécessaires pour PyQt6
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=matplotlib.backends.backend_qt5agg",
        "--hidden-import=matplotlib.backends.backend_agg",
        "--hidden-import=numpy",
        "--hidden-import=scipy",
        "--collect-submodules=src",     # Inclure récursivement tous les modules src
        "--exclude-module=tkinter",     # Exclure tkinter pour réduire la taille
        "--exclude-module=unittest",    # Exclure unittest pour réduire la taille
        "--exclude-module=test",        # Exclure les modules de test
        "--distpath=releases",          # Répertoire de sortie
        "main.py"                       # Point d'entrée
    ]
    
    # Filtrer les arguments vides
    cmd = [arg for arg in cmd if arg]
    
    print("🚀 Lancement de PyInstaller...")
    print(f"Commande: {' '.join(cmd)}")
    
    try:
        # Exécuter PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build réussi!")
        
        # Vérifier que l'exécutable a été créé
        exe_path = output_dir / "NeutroScope.exe"
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # Taille en MB
            print(f"📦 Exécutable créé: {exe_path}")
            print(f"📊 Taille: {file_size:.1f} MB")
            
            # Copier les fichiers additionnels si nécessaire
            additional_files = ["README.md", "config.json"]
            for file_name in additional_files:
                if Path(file_name).exists():
                    shutil.copy(file_name, output_dir)
                    print(f"📄 Copié: {file_name}")
            
            print("\n🎉 Build terminé avec succès!")
            print(f"🎯 L'exécutable est disponible dans: {output_dir.absolute()}")
            print("\n📋 Instructions pour le partage:")
            print("1. Copiez le dossier 'releases' sur votre OneDrive")
            print("2. Partagez le lien vers NeutroScope.exe")
            print("3. Les utilisateurs peuvent lancer directement l'exécutable")
            
        else:
            print("❌ Erreur: L'exécutable n'a pas été créé")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du build: {e}")
        if e.stdout:
            print("📤 Sortie standard:")
            print(e.stdout)
        if e.stderr:
            print("📤 Erreur standard:")
            print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Erreur: PyInstaller n'est pas installé.")
        print("💡 Installez-le avec: pip install pyinstaller")
        sys.exit(1)

if __name__ == "__main__":
    main() 