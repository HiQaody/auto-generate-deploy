import os

def write_jenkinsfile(app_name, port, node_port, envs, output_dir):
    jenkinsfile_path = os.path.join(output_dir, "Jenkinsfile")
    with open(jenkinsfile_path, "w") as f:
        f.write(f"""pipeline {{
    agent any
    environment {{
        REGISTRY         = 'harbor.tsirylab.com'
        HARBOR_PROJECT   = 'pnud-agvm'
        IMAGE_NAME       = '{app_name}'
        IMAGE_TAG        = "\\${{BUILD_NUMBER}}"
        FULL_IMAGE_NAME  = "\\${{REGISTRY}}/\\${{HARBOR_PROJECT}}/\\${{IMAGE_NAME}}:\\${{IMAGE_TAG}}"
        NAMESPACE        = 'pnud-agvm'
        K8S_DIR          = 'k8s'
        DEPLOYMENT_NAME  = '{app_name}'
        SERVICE_NAME     = '{app_name}-service'
        HPA_NAME         = '{app_name}-hpa'
        SECRET_NAME      = '{app_name}-secret'
        PORT             = '{port}'
        NODE_PORT        = '{node_port}'
{"".join([f"        {e['name']} = ''\n" for e in envs])}
    }}
    stages {{
        stage('Build & Push') {{
            steps {{
                withCredentials([
                    usernamePassword(credentialsId: 'harbor-credentials',
                                     usernameVariable: 'HARBOR_USER',
                                     passwordVariable: 'HARBOR_PASS'),\n""")
        for e in envs:
            if e.get('secret_id'):
                f.write(f"                    string(credentialsId: '{e['secret_id']}', variable: '{e['name']}'),\n")
        f.write(f"""                ]) {{
                    sh '''
                        set -e
                        docker logout \\${{REGISTRY}} || true
                        docker build \\
""")
        for e in envs:
            f.write(f"                          --build-arg {e['name']}=\"\\${{{e['name']}}}\" \\\n")
        f.write(
            f"""                          --build-arg PORT={port} \\
                          -t \\${{FULL_IMAGE_NAME}} .
                        echo \\${{HARBOR_PASS}} | \\
                          docker login -u \\${{HARBOR_USER}} --password-stdin \\${{REGISTRY}}
                        docker push \\${{FULL_IMAGE_NAME}}
                        docker logout \\${{REGISTRY}}
                    '''
                }}
            }}
        }}
        stage('Deploy') {{
            steps {{
                withCredentials([
                    file(credentialsId: 'kubeconfig-jenkins', variable: 'KUBECONFIG'),
                    usernamePassword(credentialsId: 'harbor-credentials',
                                     usernameVariable: 'HARBOR_USER',
                                     passwordVariable: 'HARBOR_PASS'),\n""")
        for e in envs:
            if e.get('secret_id'):
                f.write(f"                    string(credentialsId: '{e['secret_id']}', variable: '{e['name']}'),\n")
        f.write(f"""                ]) {{
                    sh '''
                        set -e
                        export KUBECONFIG=\\${{KUBECONFIG}}

                        kubectl create namespace \\${{NAMESPACE}} --dry-run=client -o yaml | kubectl apply -f -
                        kubectl delete secret harbor-registry-secret -n \\${{NAMESPACE}} --ignore-not-found
                        kubectl create secret docker-registry harbor-registry-secret \\
                          --docker-server=\\${{REGISTRY}} \\
                          --docker-username="\\${{HARBOR_USER}}" \\
                          --docker-password="\\${{HARBOR_PASS}}" \\
                          --namespace=\\${{NAMESPACE}}

                        kubectl delete secret \\${{SECRET_NAME}} -n \\${{NAMESPACE}} --ignore-not-found
                        kubectl create secret generic \\${{SECRET_NAME}} \\
""")
        for e in envs:
            f.write(f"                          --from-literal={e['name']}=\"\\${{{e['name']}}}\" \\\n")
        f.write("""                          --namespace=\\${NAMESPACE}

                        for res in deployment service hpa; do
                            envsubst < \\${K8S_DIR}/""" + f"{app_name}" + """-${res}.yaml > /tmp/""" + f"{app_name}" + """-${res}.yaml
                            kubectl apply -f /tmp/""" + f"{app_name}" + """-${res}.yaml
                        done

                        kubectl rollout status deployment/""" + f"{app_name}" + """ -n \\${NAMESPACE} --timeout=120s
                        kubectl get pods -n \\${NAMESPACE} -l app=""" + f"{app_name}" + """
                    '''
                }}
            }}
        }
    post {{ always {{ cleanWs() }} }}
""")
