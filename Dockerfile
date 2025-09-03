FROM python:3.11-slim

# Définir le dossier de travail
WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copier le code
COPY . .

# Définir une variable de port (par défaut 4001)
ARG PORT=4011
ENV PORT=$PORT

# Exposer le port (fixe pour Docker)
EXPOSE 4011

# Commande de démarrage avec Gunicorn (4 workers, 1 thread chacun)
CMD ["gunicorn", "--bind", "0.0.0.0:4011", "--workers", "4", "--threads", "1", "main:app"]
