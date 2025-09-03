FROM python:3.11-slim

WORKDIR /app

# Copier uniquement les fichiers nécessaires (utiliser .dockerignore pour exclure les fichiers inutiles)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source de l'application
COPY . .

# Définir une valeur par défaut pour le port
ARG PORT=4011
ENV PORT=${PORT}

# Exposer le port utilisé par l'application
EXPOSE ${PORT}

# Utiliser un utilisateur non-root pour la sécurité
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Commande de démarrage avec gestion du port dynamique
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "main:app"]