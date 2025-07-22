@echo off

REM Forcer l'encodage UTF-8
chcp 65001 >nul

echo ==================================================
echo           NEUTROSCOPE - BUILD WINDOWS
echo ==================================================
echo.
echo Programme de build pour NeutroScope. Peut prendre quelques minutes.
echo.

REM Vérifier que Python est installé
echo.
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] PYTHON N'EST PAS INSTALLÉ OU PAS DANS LE PATH.
    echo Veuillez installer Python depuis https://python.org
    pause
    exit /b 1
) else (
    echo [INFO] PYTHON DÉTECTÉ :
    python --version
)
echo.

REM Vérifier que pip est installé
echo.
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] PIP N'EST PAS INSTALLÉ.
    pause
    exit /b 1
) else (
    echo [INFO] PIP DÉTECTÉ :
    pip --version
)
echo.

REM Vérifier que nous sommes dans le bon répertoire
echo.
if not exist "main.py" (
    echo [ERREUR] main.py NON TROUVÉ.
    echo Veuillez exécuter ce script depuis la racine du projet NeutroScope
    pause
    exit /b 1
) else (
    echo [INFO] RÉPERTOIRE DE PROJET VALIDE.
)
echo.

REM Activer l'environnement virtuel s'il existe
echo.
set VENV_ACTIVATOR=
if exist ".venv\Scripts\activate.bat" set VENV_ACTIVATOR=.venv\Scripts\activate.bat
if not defined VENV_ACTIVATOR if exist "venv\Scripts\activate.bat" set VENV_ACTIVATOR=venv\Scripts\activate.bat
if not defined VENV_ACTIVATOR if exist "env\Scripts\activate.bat" set VENV_ACTIVATOR=env\Scripts\activate.bat

if defined VENV_ACTIVATOR (
    echo [INFO] ACTIVATION DE L'ENVIRONNEMENT VIRTUEL...
    call "%VENV_ACTIVATOR%"
    echo [INFO] ENVIRONNEMENT VIRTUEL ACTIVÉ.
) else (
    echo [INFO] AUCUN ENVIRONNEMENT VIRTUEL TROUVÉ.
    echo [INFO] CRÉATION DE L'ENVIRONNEMENT VIRTUEL...
    python -m venv .venv
    echo [INFO] ENVIRONNEMENT VIRTUEL CRÉÉ.
    echo [INFO] ACTIVATION DE L'ENVIRONNEMENT VIRTUEL...
    call .venv\Scripts\activate.bat
    echo [INFO] ENVIRONNEMENT VIRTUEL ACTIVÉ.
)
echo.

REM Installer/Mettre à jour les dépendances
echo.
echo [INFO] INSTALLATION DES DÉPENDANCES...
echo ==================================================
pip install -r requirements.txt
echo ==================================================
echo [INFO] DÉPENDANCES INSTALLÉES.
echo.

REM Lancer le script de build Python
echo.
echo [INFO] LANCEMENT DU BUILD...
echo ==================================================
python build_windows.py
echo ==================================================

REM Vérifier le résultat
echo.
if exist "releases\NeutroScope.exe" (
    echo ==================================================
    echo             *** BUILD RÉUSSI ! ***
    echo ==================================================
    echo.
    echo L'exécutable a été créé dans le dossier "releases".
) else (
    echo ==================================================
    echo             *** ÉCHEC DU BUILD ***
    echo ==================================================
    echo.
    echo L'exécutable n'a pas pu être créé.
    echo Vérifiez les messages d'erreur ci-dessus.
)
echo.

echo.
echo Appuyez sur une touche pour fermer.
pause >nul