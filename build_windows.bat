@echo off
echo ==================================================
echo        NEUTROSCOPE - BUILD WINDOWS
echo ==================================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installé ou pas dans le PATH
    echo Veuillez installer Python depuis https://python.org
    pause
    exit /b 1
)

echo [INFO] Python détecté
python --version

REM Vérifier que nous sommes dans le bon répertoire
if not exist "main.py" (
    echo [ERREUR] main.py non trouvé
    echo Veuillez exécuter ce script depuis la racine du projet NeutroScope
    pause
    exit /b 1
)

echo [INFO] Répertoire de projet validé

REM Activer l'environnement virtuel s'il existe
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activation de l'environnement virtuel...
    call .venv\Scripts\activate.bat
) else (
    echo [ATTENTION] Aucun environnement virtuel trouvé
    echo Il est recommandé d'utiliser un environnement virtuel
)

REM Installer/Mettre à jour les dépendances
echo [INFO] Installation des dépendances...
pip install -r requirements.txt

REM Vérifier que PyInstaller est installé
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] PyInstaller n'est pas installé
    echo Installation en cours...
    pip install pyinstaller
)

echo [INFO] PyInstaller détecté
pyinstaller --version

REM Lancer le script de build Python
echo [INFO] Lancement du build...
python build_windows.py

REM Vérifier le résultat
if exist "releases\NeutroScope.exe" (
    echo.
    echo ==================================================
    echo          BUILD RÉUSSI !
    echo ==================================================
    echo.
    echo L'exécutable a été créé dans le dossier "releases"
    echo Vous pouvez maintenant copier ce dossier sur votre OneDrive
    echo.
    echo Fichiers créés:
    dir /b releases\
    echo.
    echo Voulez-vous ouvrir le dossier releases ? (O/N)
    set /p OPEN_FOLDER=
    if /I "%OPEN_FOLDER%"=="O" (
        explorer releases
    )
) else (
    echo.
    echo ==================================================
    echo          ÉCHEC DU BUILD
    echo ==================================================
    echo.
    echo L'exécutable n'a pas pu être créé.
    echo Vérifiez les messages d'erreur ci-dessus.
)

echo.
echo Appuyez sur une touche pour fermer...
pause >nul 