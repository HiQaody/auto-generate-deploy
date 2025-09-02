import os


def write_dockerfile(app_name, port, envs, output_dir):
    dockerfile_path = os.path.join(output_dir, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write(f"""FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci --ignore-scripts && npm cache clean --force
COPY . .

{"".join([f"ARG {e['name']}\n" for e in envs])}
ARG PORT

ENV {" \\\n    ".join([f"{e['name']}=${{{e['name']}}}" for e in envs])} \\
    PORT=${{PORT}}

EXPOSE ${{PORT}}

USER node
CMD ["node", "dist/main", "--port", "${{PORT}}"]
""")

