FROM python:3.11-slim

RUN useradd --uid 1000 --create-home --shell /bin/bash app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY --chown=app:app . .

ARG PORT=4011
ENV PORT=$PORT
EXPOSE $PORT

# dossier où gunicorn pourra écrire
ENV GUNICORN_TMPDIR=/tmp
RUN mkdir -p /tmp && chown app:app /tmp

USER app

CMD ["gunicorn","main:app","--bind","0.0.0.0:4011","--workers","4","--threads","1","--worker-tmp-dir","/tmp","--access-logfile","-","--error-logfile","-"]