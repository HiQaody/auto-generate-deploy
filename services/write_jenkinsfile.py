import os
from jinja2 import Environment, FileSystemLoader

def write_jenkinsfile(app_name, port, envs, output_dir, project_type, node_port=None, simple=False):
    """
    Génère un Jenkinsfile pour un projet frontend ou backend, selon le type.
    Pour frontend, utilise le template Jinja2 Jenkinsfile.frontend.j2.
    Pour backend, utilise Jenkinsfile.backend.j2.
    """
    if not app_name or not port or not envs or not output_dir or not project_type:
        raise ValueError("Tous les paramètres requis doivent être fournis.")

    jenkinsfile_path = os.path.join(output_dir, "Jenkinsfile")

    # Dossier contenant les templates Jinja2
    template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    env = Environment(loader=FileSystemLoader(template_dir))

    if simple:
        # Si tu veux gérer un template simple, ajoute-le ici.
        raise NotImplementedError("Le mode simple n'est pas géré par ce template Jinja2.")

    if project_type == "frontend":
        template = env.get_template("Jenkinsfile.frontend.j2")
        jenkinsfile_content = template.render(
            app_name=app_name,
            port=port,
            envs=envs
        )
    elif project_type == "backend":
        template = env.get_template("Jenkinsfile.backend.j2")
        jenkinsfile_content = template.render(
            app_name=app_name,
            port=port,
            envs=envs,
            node_port=node_port
        )
    else:
        raise ValueError("project_type doit être 'frontend' ou 'backend'.")

    # Écriture du Jenkinsfile généré
    with open(jenkinsfile_path, "w") as f:
        f.write(jenkinsfile_content)