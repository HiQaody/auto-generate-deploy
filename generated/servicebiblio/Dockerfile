FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci --ignore-scripts && npm cache clean --force
COPY . .

ARG DB_HOST
ARG DB_PORT
ARG DB_USERNAME
ARG DB_PASSWORD
ARG DB_DATABASE
ARG UPLOAD_URL

ARG PORT

ENV DB_HOST=${DB_HOST} \
    DB_PORT=${DB_PORT} \
    DB_USERNAME=${DB_USERNAME} \
    DB_PASSWORD=${DB_PASSWORD} \
    DB_DATABASE=${DB_DATABASE} \
    UPLOAD_URL=${UPLOAD_URL} \
    PORT=${PORT}

EXPOSE ${PORT}

USER node
CMD ["node", "dist/main", "--port", "${PORT}"]
