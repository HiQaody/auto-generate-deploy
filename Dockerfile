FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY generated/jacquinot-devops .


ARG PORT

ENV \

  PORT=${PORT}

EXPOSE 4011

CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "main:app"]