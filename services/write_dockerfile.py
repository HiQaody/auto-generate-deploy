import os

def write_dockerfile(app_name, port, envs, output_dir, project_type):
    dockerfile_path = os.path.join(output_dir, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        if project_type == "backend":
            # Dockerfile pour backend Node.js (ex: NestJS)
            f.write(f"""FROM node:20-slim

WORKDIR /app

COPY package*.json ./

RUN npm install --legacy-peer-deps

COPY . .

{"".join([f"ARG {e['name']}\n" for e in envs])}
ARG PORT

RUN npm run build

ENV {" \\\n    ".join([f"{e['name']}=${{{e['name']}}}" for e in envs])} \\
    PORT=${{PORT}}

EXPOSE {port}

USER node

CMD ["node", "dist/main.js", "--port", "${{PORT}}"]
""")
        elif project_type == "frontend":
            # Dockerfile pour frontend Vite + Nginx
            env_args = "".join([f"ARG {e['name']}\n" for e in envs])
            env_vars = " \\\n    ".join([f"{e['name']}=${{{e['name']}}}" for e in envs])
            vite_port = next((e['value'] for e in envs if e['name'] == 'VITE_PORT'), port)
            f.write(f"""###########################################################################
# ÉTAPE 1 – Build Vite
###########################################################################
FROM node:20-slim AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci --ignore-scripts && npm cache clean --force

COPY . .

{env_args}
ARG VITE_PORT={vite_port}

ENV {env_vars} \\
    VITE_PORT=${{VITE_PORT}}

RUN npm run build

###########################################################################
# ÉTAPE 2 – Image Nginx (non-root)
###########################################################################
FROM nginxinc/nginx-unprivileged:1.25-alpine AS runner
USER 101
WORKDIR /usr/share/nginx/html

COPY --from=builder --chown=101:101 /app/dist .

COPY nginx.conf /etc/nginx/conf.d/default.conf
ENV PORT=${{VITE_PORT}}
EXPOSE $vite_port

CMD ["nginx","-g","daemon off;"]
""")
        else:
            raise ValueError("project_type doit être 'backend' ou 'frontend'")
