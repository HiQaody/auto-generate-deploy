import os

def write_deployment_yaml(app_name, port, output_dir):
    k8s_dir = os.path.join(output_dir, "k8s")
    deployment_path = os.path.join(k8s_dir, f"{app_name}.yaml")
    with open(deployment_path, "w") as f:
        f.write(f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  namespace: pnud-agvm
  labels:
    app: {app_name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
        - name: {app_name}
          image: ${{FULL_IMAGE_NAME}}
          imagePullPolicy: Always
          ports:
            - containerPort: {port}
              name: http
          envFrom:
            - secretRef:
                name: {app_name}-secret
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
          livenessProbe:
            httpGet:
              path: /{app_name}
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /{app_name}
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
      imagePullSecrets:
        - name: harbor-registry-secret
""")
