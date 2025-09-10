# Utiliser Python 3.13 slim
FROM python:3.13-slim

# Dossier de travail
WORKDIR /app

# Installer dépendances système
RUN apt-get update && apt-get install -y \
    gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Copier requirements.txt et installer dépendances
COPY ../../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source de l’app Flask
COPY ../../ .

# Exposer le port Flask
EXPOSE 5000

# Lancer Flask via Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
