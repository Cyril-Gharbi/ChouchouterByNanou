#!/bin/bash
echo "--------------------------------------"
echo " INSTALLATION DES DÉPENDANCES PYTHON "
echo "--------------------------------------"

# Pip update
python3 -m pip install --upgrade pip

# Installation of prod dependencies
pip install -r requirements.txt

# Installation of dev dependencies if available
if [ -f requirements-dev.txt ]; then
    pip install -r requirements-dev.txt
    echo "✔ Dépendances de dev installées"
else
    echo "⚠ Aucun requirements-dev.txt trouvé, skip..."
fi

echo "✔ Installation terminée."
