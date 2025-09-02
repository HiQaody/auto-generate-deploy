import os

def write_secret_yaml(app_name, envs, output_dir):
    k8s_dir = os.path.join(output_dir, "k8s")
    os.makedirs(k8s_dir, exist_ok=True)
    secret_path = os.path.join(k8s_dir, f"{app_name}-secret.yaml")
    with open(secret_path, "w") as f:
        f.write(f"""apiVersion: v1
kind: Secret
metadata:
  name: {app_name}-secret
  namespace: ${{NAMESPACE}}
type: Opaque
stringData:
""")
        for e in envs:
            if 'value' in e and e['value']:
                # valeur statique pour le secret
                f.write(f"  {e['name']}: \"{e['value']}\"\n")
            else:
                # placeholder pour envsubst
                f.write(f"  {e['name']}: \"${{{e['name']}}}\"\n")