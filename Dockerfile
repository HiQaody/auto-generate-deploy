FROM python:3.11-slim

RUN useradd --uid 1000 --create-home --shell /bin/bash app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# copier tout le dossier local (main.py inclus)
COPY --chown=app:app . .

ARG PORT=4011
ENV PORT=$PORT
EXPOSE $PORT

USER app
# on lance le bon module
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:4011", "--workers", "4", "--threads", "1"]