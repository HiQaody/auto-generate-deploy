import os

def write_jenkinsfile(app_name, port, node_port, envs, output_dir):
    jenkinsfile_path = os.path.join(output_dir, "Jenkinsfile")
    # Credentials uniquement pour ceux ayant un secret_id
    creds = []
    for e in envs:
        if 'secret_id' in e and e['secret_id']:
            creds.append((e['secret_id'], e['name']))

    with open(jenkinsfile_path, "w") as f:
        # Bloc environment
        f.write(f"""pipeline {{
    agent any
    environment {{
        REGISTRY         = 'harbor.tsirylab.com'
        HARBOR_PROJECT   = 'pnud-agvm'
        IMAGE_NAME       = '{app_name}'
        IMAGE_TAG        = "${{BUILD_NUMBER}}"
        FULL_IMAGE_NAME  = "${{REGISTRY}}/${{HARBOR_PROJECT}}/${{IMAGE_NAME}}:${{IMAGE_TAG}}"
        NAMESPACE        = 'pnud-agvm'
        K8S_DIR          = 'k8s'
        DEPLOYMENT_NAME  = '{app_name}'
        SERVICE_NAME     = '{app_name}-service'
        HPA_NAME         = '{app_name}-hpa'
        SECRET_NAME      = '{app_name}-secret'
        PORT             = '{port}'
        NODE_PORT        = '{node_port}'
""")
        f.write("    }\n")
        f.write("    stages {\n")

        # --- Build & Push ---
        f.write("        stage('Build & Push') {\n")
        f.write("            steps {\n")
        f.write("                withCredentials([\n")
        f.write("                    usernamePassword(credentialsId: 'harbor-credentials', usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS'),\n")
        for sid, name in creds:
            f.write(f"                    string(credentialsId: '{sid}', variable: '{name}'),\n")
        f.write("                ]) {\n")
        f.write("                    sh '''\n")
        f.write("                        set -e\n")
        f.write("                        docker logout $REGISTRY || true\n")
        f.write("                        docker build \\\n")
        f.write(f"                          --build-arg PORT={port} \\\n")
        f.write("                          -t $FULL_IMAGE_NAME .\n")
        f.write("                        echo $HARBOR_PASS | \\\n")
        f.write("                          docker login -u $HARBOR_USER --password-stdin $REGISTRY\n")
        f.write("                        docker push $FULL_IMAGE_NAME\n")
        f.write("                        docker logout $REGISTRY\n")
        f.write("                    '''\n")
        f.write("                }\n")
        f.write("            }\n")
        f.write("        }\n")

        # --- Deploy ---
        f.write("        stage('Deploy') {\n")
        f.write("            steps {\n")
        f.write("                withCredentials([\n")
        f.write("                    file(credentialsId: 'kubeconfig-jenkins', variable: 'KUBECONFIG'),\n")
        f.write("                    usernamePassword(credentialsId: 'harbor-credentials', usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS'),\n")
        for sid, name in creds:
            f.write(f"                    string(credentialsId: '{sid}', variable: '{name}'),\n")
        f.write("                ]) {\n")
        f.write("                    sh '''\n")
        f.write("                        set -e\n")
        f.write("                        export KUBECONFIG=$KUBECONFIG\n\n")
        f.write("                        kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -\n")
        f.write("                        kubectl delete secret harbor-registry-secret -n $NAMESPACE --ignore-not-found\n")
        f.write("                        kubectl create secret docker-registry harbor-registry-secret \\\n")
        f.write("                          --docker-server=$REGISTRY \\\n")
        f.write("                          --docker-username=\"$HARBOR_USER\" \\\n")
        f.write("                          --docker-password=\"$HARBOR_PASS\" \\\n")
        f.write("                          --namespace=$NAMESPACE\n\n")
        f.write("                        kubectl delete secret $SECRET_NAME -n $NAMESPACE --ignore-not-found\n")
        f.write("                        kubectl create secret generic $SECRET_NAME \\\n")
        for e in envs:
            if 'value' in e and e['value']:
                # Valeur statique
                f.write(f"                          --from-literal={e['name']}=\"{e['value']}\" \\\n")
            else:
                # Valeur dynamique (via credentials)
                f.write(f"                          --from-literal={e['name']}=\"$$${e['name']}\" \\\n")
        f.write("                          --namespace=$NAMESPACE\n\n")
        f.write("                        for res in deployment service hpa; do\n")
        f.write(f"                            envsubst < $K8S_DIR/{app_name}-$res.yaml > /tmp/{app_name}-$res.yaml\n")
        f.write(f"                            kubectl apply -f /tmp/{app_name}-$res.yaml\n")
        f.write("                        done\n\n")
        f.write(f"                        kubectl rollout status deployment/{app_name} -n $NAMESPACE --timeout=120s\n")
        f.write(f"                        kubectl get pods -n $NAMESPACE -l app={app_name}\n")
        f.write("                    '''\n")
        f.write("                }\n")
        f.write("            }\n")
        f.write("        }\n")
        f.write("    }\n")
        f.write("    post { always { cleanWs() } }\n")
        f.write("}\n")