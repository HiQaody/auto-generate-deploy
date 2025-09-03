FROM python:3.11-slim

# Créer et sécuriser le dossier temporaire pour Python/Gunicorn
RUN mkdir -p /tmp && chmod 1777 /tmp

# Créer un utilisateur non-root (optionnel mais recommandé)
RUN useradd --create-home --shell /bin/bash app

# Définir le dossier de travail
WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copier le code source (avec permissions pour l'utilisateur non-root)
COPY --chown=app:app . .

# Définir la variable de port (modifiable à l'exécution)
ARG PORT=4011
ENV PORT=$PORT

# Exposer le port indiquant l'app, par défaut 4011 (ajuster si besoin)
EXPOSE $PORT

# Utiliser l'utilisateur non-root
USER app

# Commande de démarrage avec Gunicorn (4 workers, 1 thread chacun)
# Utilise la variable d'environnement PORT pour la flexibilité
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "--workers", "4", "--threads", "1", "app:app"]