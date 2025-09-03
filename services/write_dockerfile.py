import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Chemin absolu vers le dossier des templates (adapter si besoin)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'templates', 'dockerfile')

def write_dockerfile(app_name, port, envs, output_dir, project_type, backend_framework=None):
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape()
    )
    if project_type == 'backend':
        backend_framework = (backend_framework or 'nestjs').lower()
        if backend_framework not in ('nestjs', 'flask'):
            raise ValueError("backend_framework doit être 'nestjs' ou 'flask'")
        template_name = f"Dockerfile.backend.{backend_framework}.j2"
    elif project_type == 'frontend':
        template_name = "Dockerfile.frontend.j2"
    else:
        raise ValueError("project_type doit être 'backend' ou 'frontend'")

    try:
        template = env.get_template(template_name)
    except Exception as e:
        raise FileNotFoundError(f"Le template {template_name} est introuvable dans {TEMPLATE_DIR}: {e}")

    vite_port = next((e['value'] for e in envs if e['name'] == 'VITE_PORT'), port)
    dockerfile_content = template.render(
        app_name=app_name,
        port=port,
        envs=envs,
        vite_port=vite_port
    )

    os.makedirs(output_dir, exist_ok=True)
    dockerfile_path = os.path.join(output_dir, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content)