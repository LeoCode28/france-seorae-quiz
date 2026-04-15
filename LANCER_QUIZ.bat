@echo off
chcp 65001 >nul
title France Seorae - Quiz App
cls

echo.
echo  ============================================
echo   FRANCE SEORAE - QUIZ APP
echo  ============================================
echo.

:: Cherche Python dans les emplacements habituels sur Windows
set PYTHON_CMD=

:: Test 1 : commande "python" standard
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :python_found
)

:: Test 2 : commande "py" (launcher Windows)
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto :python_found
)

:: Test 3 : chemins courants d'installation Windows
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "%PROGRAMFILES%\Python312\python.exe"
    "%PROGRAMFILES%\Python311\python.exe"
) do (
    if exist %%P (
        set PYTHON_CMD=%%P
        goto :python_found
    )
)

:: Python introuvable
echo  ERREUR : Python n'est pas installe.
echo.
echo  Telecharge Python sur : https://python.org/downloads
echo  IMPORTANT : Coche "Add Python to PATH" pendant l'installation !
echo.
echo  Appuie sur une touche pour ouvrir le site de telechargement...
pause >nul
start https://python.org/downloads
exit /b

:python_found
echo  Python detecte : %PYTHON_CMD%
echo.

:: Va dans le dossier du script
cd /d "%~dp0"

:: Verifie que run.py existe
if not exist "run.py" (
    echo  ERREUR : run.py introuvable dans ce dossier.
    echo  Place LANCER_QUIZ.bat dans le meme dossier que run.py
    echo.
    pause
    exit /b
)

:: Installe les dependances
echo  Installation des dependances Flask...
%PYTHON_CMD% -m pip install flask flask-sqlalchemy python-dotenv --quiet --disable-pip-version-check 2>nul
if errorlevel 1 (
    echo  Nouvelle tentative avec --user...
    %PYTHON_CMD% -m pip install flask flask-sqlalchemy python-dotenv --user --quiet 2>nul
)
echo  Dependances OK
echo.

:: Ouvre le navigateur apres 3 secondes
start "" cmd /c "ping -n 4 127.0.0.1 >nul && start http://localhost:5000"

echo  ============================================
echo   Serveur demarre !
echo   Adresse : http://localhost:5000
echo   Admin   : http://localhost:5000/admin
echo   Mot de passe admin : (voir le fichier .env)
echo  ============================================
echo.
echo  Pour arreter : ferme cette fenetre ou Ctrl+C
echo.

:: Lance Flask
%PYTHON_CMD% run.py

echo.
echo  Serveur arrete.
pause
