import os


def write_service_yaml(app_name, port, node_port, output_dir):
    k8s_dir = os.path.join(output_dir, "k8s")
    service_path = os.path.join(k8s_dir, f"{app_name}-service.yaml")
    with open(service_path, "w") as f:
        f.write(f"""apiVersion: v1
kind: Service
metadata:
  name: {app_name}-service
  namespace: pnud-agvm
spec:
  type: NodePort
  selector:
    app: {app_name}
  ports:
    - protocol: TCP
      port: {port}
      targetPort: {port}
      nodePort: {node_port}
""")