@echo off
echo --------------------------------------
echo INSTALLATION DES DEPENDANCES PYTHON
echo --------------------------------------

pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✔ Installation terminée.
pause