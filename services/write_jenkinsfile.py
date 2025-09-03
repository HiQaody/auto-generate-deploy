import os
from jinja2 import Environment, FileSystemLoader


def write_jenkinsfile(app_name, port, envs, output_dir, project_type, node_port=None, simple=False):
    """
    Génère un Jenkinsfile pour un projet frontend ou backend, selon le type.
    Pour frontend, utilise le template Jinja2 Jenkinsfile.frontend.j2.
    """
    jenkinsfile_path = os.path.join(output_dir, "Jenkinsfile")

    # Chemin du dossier où se trouve le template
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))

    if simple:
        # Ici, on pourrait ajouter un template "Jenkinsfile.simple.j2" si besoin
        raise NotImplementedError("Le mode simple n'est pas géré par ce template Jinja2.")

    if project_type == "frontend":
        template = env.get_template("Jenkinsfile.frontend.j2")
        jenkinsfile_content = template.render(
            app_name=app_name,
            port=port,
            envs=envs
        )
        with open(jenkinsfile_path, "w") as f:
            f.write(jenkinsfile_content)
    else:
        template = env.get_template("Jenkinsfile.backend.j2")
        jenkinsfile_content = template.render(
            app_name=app_name,
            port=port,
            envs=envs,
            node_port=node_port)
        with open(jenkinsfile_path, "w") as f:
            f.write(jenkinsfile_content)
