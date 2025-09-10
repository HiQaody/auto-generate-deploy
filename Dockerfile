FROM python:3.11-slim

RUN useradd --uid 1000 --create-home --shell /bin/bash app

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY --chown=app:app . .

ARG PORT=4011
ENV PORT=$PORT
EXPOSE $PORT

USER app
CMD ["gunicorn", "--bind", "0.0.0.0:4011", "--workers", "4", "--threads", "1", "app:app"]