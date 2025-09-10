@echo off
echo --------------------------------------
echo INSTALLATION DES DEPENDANCES PYTHON
echo --------------------------------------

REM Pip update
python -m pip install --upgrade pip

REM Installation of prod dependencies
pip install -r requirements.txt

REM Installation of dev dependencies if the file exists
if exist requirements-dev.txt (
    pip install -r requirements-dev.txt
    echo ✔ Dépendances de dev installées
) else (
    echo ⚠ Aucun requirements-dev.txt trouvé, skip...
)

echo.
echo ✔ Installation terminée.
pause
