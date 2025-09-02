import glob
import os
import shutil
import zipfile
from datetime import datetime

import requests
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

# === Services ===
from services.write_dockerfile import write_dockerfile
from services.write_deployment_yaml import write_deployment_yaml
from services.write_service_yaml import write_service_yaml
from services.write_hpa_yaml import write_hpa_yaml
from services.write_secret_yaml import write_secret_yaml
from services.write_jenkinsfile import write_jenkinsfile
from services.write_nginx_conf import write_nginx_conf


# === Main Orchestration ===
def generate_files(app_name, port, node_port, envs, output_dir, project_type, simple):
    k8s_dir = os.path.join(output_dir, "k8s")
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(k8s_dir, exist_ok=True)
    # Simple mode : juste Dockerfile et Jenkinsfile
    write_dockerfile(app_name, port, envs, output_dir, project_type)
    write_jenkinsfile(app_name, port, envs, output_dir, project_type, node_port, simple)
    if project_type == "frontend" :
        write_nginx_conf(port, output_dir)
    if not simple:
        write_deployment_yaml(app_name, port, output_dir, project_type)
        write_service_yaml(app_name, port, node_port, output_dir)
        write_hpa_yaml(app_name, output_dir)
        write_secret_yaml(app_name, envs, output_dir)
        if project_type == "frontend":
            write_nginx_conf(port, output_dir)
    # En mode simple, pas de nginx.conf ni YAML

# === Flask Endpoints ===
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.json
        app_name = data.get("app_name")
        port = data.get("port")
        node_port = data.get("node_port")
        envs = data.get("envs", [])
        project_type = data.get("project_type", "backend")
        simple = data.get("simple", False)
        output_dir = os.path.join("generated", app_name)

        generate_files(app_name, port, node_port, envs, output_dir, project_type, simple)

        # Compresser le dossier
        zip_path = f"{app_name}.zip"
        with zipfile.ZipFile(zip_path, "w") as zip_file:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, output_dir)
                    zip_file.write(abs_path, rel_path)

        return send_file(zip_path, as_attachment=True, download_name=f"{app_name}.zip")

    except requests.exceptions.ConnectionError:
        return jsonify({"success": False, "message": "Erreur de connexion : Impossible de contacter le serveur"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    try:
        zip_path = filename
        if not os.path.exists(zip_path):
            return jsonify({"error": "Fichier non trouvé"}), 404
        return send_file(zip_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/list-files", methods=["GET"])
def list_generated_files():
    try:
        zip_files = glob.glob("*.zip")
        files_info = []
        for zip_file in zip_files:
            stat = os.stat(zip_file)
            files_info.append({
                "name": zip_file,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        files_info.sort(key=lambda x: x["created"], reverse=True)
        return jsonify({"files": files_info})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/cleanup", methods=["POST"])
def cleanup_files():
    try:
        zip_files = glob.glob("*.zip")
        for zip_file in zip_files:
            os.remove(zip_file)
        if os.path.exists("generated"):
            shutil.rmtree("generated")
        return jsonify({"success": True, "message": f"Supprimé {len(zip_files)} fichier(s)"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)