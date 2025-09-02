import os


def write_secret_yaml(app_name, envs, output_dir):
    k8s_dir = os.path.join(output_dir, "k8s")
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
            # Value: if present use it, else use Jenkins placeholder for envsubst
            value = e['value'] if e['value'] else f"${{{e['name']}}}"
            f.write(f"  {e['name']}: \"{value}\"\n")

