import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Chemin ABSOLU depuis la racine du projet
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'templates', 'dockerfile')

def write_dockerfile(app_name, port, envs, output_dir, project_type):
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape()
    )
    if project_type not in ('backend', 'frontend'):
        raise ValueError("project_type doit être 'backend' ou 'frontend'")

    template = env.get_template(f"Dockerfile.{project_type}.j2")
    vite_port = next((e['value'] for e in envs if e['name'] == 'VITE_PORT'), port)
    dockerfile_content = template.render(
        app_name=app_name,
        port=port,
        envs=envs,
        vite_port=vite_port
    )
    dockerfile_path = os.path.join(output_dir, "Dockerfile")
    print("generate dockerfile : ", dockerfile_path)
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content)