FROM python:3.11-slim

WORKDIR /app

# Installer dépendances système (PostgreSQL + MySQL + utils)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . .

# Lancer Flask avec Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:flask_app", "--chdir", "/app"]
