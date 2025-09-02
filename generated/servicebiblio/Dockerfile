FROM node:20-slim

WORKDIR /app

COPY package*.json ./

# Installation des dépendances
RUN npm install --legacy-peer-deps

# Copie du reste du code source
COPY . .

ARG DB_HOST
ARG DB_PORT
ARG DB_USERNAME
ARG DB_PASSWORD
ARG DB_DATABASE
ARG UPLOAD_URL

ARG PORT

# Build du projet NestJS
RUN npm run build

ENV DB_HOST=${DB_HOST} \
    DB_PORT=${DB_PORT} \
    DB_USERNAME=${DB_USERNAME} \
    DB_PASSWORD=${DB_PASSWORD} \
    DB_DATABASE=${DB_DATABASE} \
    UPLOAD_URL=${UPLOAD_URL} \
    PORT=${PORT}

EXPOSE 5032

USER node

CMD ["node", "dist/main.js", "--port", "${PORT}"]
