import os

def write_dockerfile(app_name, port, envs, output_dir):
    dockerfile_path = os.path.join(output_dir, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write(f"""FROM node:20-slim

WORKDIR /app

COPY package*.json ./

# Installation des dépendances
RUN npm install --legacy-peer-deps

# Copie du reste du code source
COPY . .

{"".join([f"ARG {e['name']}\n" for e in envs])}
ARG PORT

# Build du projet NestJS
RUN npm run build

ENV {" \\\n    ".join([f"{e['name']}=${{{e['name']}}}" for e in envs])} \\
    PORT=${{PORT}}

EXPOSE {port}

USER node

CMD ["node", "dist/main.js", "--port", "${{PORT}}"]
""")