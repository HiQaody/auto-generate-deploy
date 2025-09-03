# �tape 1 : build des d�pendances
FROM python:3.10-slim AS build

# Installer d�pendances syst�me n�cessaires � psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# Cr�er un utilisateur non-root
RUN useradd --create-home --shell /bin/bash app

# Copier et installer les d�pendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY --chown=app:app . .


ARG PORT=4011

# �tape 2 : runner
FROM python:3.10-slim

# Installer d�pendances d'ex�cution
RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# Cr�er un utilisateur non-root
RUN useradd --create-home --shell /bin/bash app

# Copier les d�pendances depuis l'�tape build
COPY --from=build /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=build /usr/local/bin /usr/local/bin

# Copier le code source avec les permissions appropri�es
COPY --from=build --chown=app:app /app .

# Cr�er le r�pertoire uploads avec les permissions appropri�es
RUN mkdir -p uploads && chown app:app uploads

# Exposer le port Flask (adapt� dynamiquement)
EXPOSE 4011

# Variables d'environnement
ENV \

  PORT=${PORT}

# Changer d'utilisateur
USER app

# Lancer Flask (adapte la commande si tu utilises FastAPI/Uvicorn)
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:${PORT}"]