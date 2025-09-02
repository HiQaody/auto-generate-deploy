FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci --ignore-scripts && npm cache clean --force
COPY . .

ARG DB_HOST
ARG DB_port

ARG PORT

ENV DB_HOST=${DB_HOST} \
    DB_port=${DB_port} \
    PORT=${PORT}

EXPOSE ${PORT}

USER node
CMD ["node", "dist/main", "--port", "${PORT}"]
