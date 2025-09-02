import os

def write_hpa_yaml(app_name, output_dir):
    k8s_dir = os.path.join(output_dir, "k8s")
    hpa_path = os.path.join(k8s_dir, f"{app_name}-hpa.yaml")
    with open(hpa_path, "w") as f:
        f.write(f"""apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {app_name}-hpa
  namespace: pnud-agvm
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {app_name}
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
""")
