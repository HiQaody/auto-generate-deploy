FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG PORT=4011
ENV PORT=${PORT}

EXPOSE ${PORT}

# Utiliser python -m gunicorn pour éviter les problèmes de PATH
CMD ["python", "main.py"]