FROM node:20-slim

WORKDIR /app

COPY package*.json ./

RUN npm install --legacy-peer-deps

COPY . .

ARG POSTGRES_HOST

ARG PORT

RUN npm run build

ENV \
POSTGRES_HOST=$POSTGRES_HOST \

  PORT=${PORT}

EXPOSE 3000

USER node

CMD ["node", "dist/main.js", "--port", "${PORT}"]