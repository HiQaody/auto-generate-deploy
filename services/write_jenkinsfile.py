import os

def write_jenkinsfile(app_name, port, envs, output_dir, project_type, node_port=None):
    jenkinsfile_path = os.path.join(output_dir, "Jenkinsfile")

    if project_type == "frontend":
        # Préparation des variables d'environnement pour le front-end
        env_lines = []
        build_args = []
        secret_lines = []
        for e in envs:
            env_lines.append(f"        {e['name']} = '{e['value']}'")
            build_args.append(f"                          --build-arg {e['name']}=${{{e['name']}}} \\")
            secret_lines.append(f"                          --from-literal={e['name']}=\"${{{e['name']}}}\" \\")

        with open(jenkinsfile_path, "w") as f:
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
{chr(10).join(env_lines)}
        VITE_PORT        = '{port}'
    }}

    stages {{
        stage('Build & Push') {{
            steps {{
                withCredentials([
                    usernamePassword(credentialsId: 'harbor-credentials',
                                     usernameVariable: 'HARBOR_USER',
                                     passwordVariable: 'HARBOR_PASS')
                ]) {{
                    sh '''
                        set -e
                        docker logout ${{REGISTRY}} || true

                        docker build \\
{chr(10).join(build_args)}
                          -t ${{FULL_IMAGE_NAME}} .

                        echo ${{HARBOR_PASS}} | \\
                          docker login -u ${{HARBOR_USER}} --password-stdin ${{REGISTRY}}

                        docker push ${{FULL_IMAGE_NAME}}
                        docker logout ${{REGISTRY}}
                    '''
                }}
            }}
        }}

        stage('Deploy to K3s') {{
            steps {{
                withCredentials([
                    file(credentialsId: 'kubeconfig-jenkins', variable: 'KUBECONFIG'),
                    usernamePassword(credentialsId: 'harbor-credentials',
                                     usernameVariable: 'HARBOR_USER',
                                     passwordVariable: 'HARBOR_PASS')
                ]) {{
                    sh '''
                        set -e
                        export KUBECONFIG=${{KUBECONFIG}}

                        kubectl create namespace ${{NAMESPACE}} --dry-run=client -o yaml | kubectl apply -f -

                        kubectl delete secret harbor-registry-secret -n ${{NAMESPACE}} --ignore-not-found
                        kubectl create secret docker-registry harbor-registry-secret \\
                          --docker-server=${{REGISTRY}} \\
                          --docker-username="${{HARBOR_USER}}" \\
                          --docker-password="${{HARBOR_PASS}}" \\
                          --namespace=${{NAMESPACE}}

                        kubectl delete secret ${{SECRET_NAME}} -n ${{NAMESPACE}} --ignore-not-found
                        kubectl create secret generic ${{SECRET_NAME}} \\
{chr(10).join(secret_lines)}
                          --namespace=${{NAMESPACE}}

                        # template toutes les ressources
                        for res in deployment service hpa secret; do
                            envsubst < ${{K8S_DIR}}/${{DEPLOYMENT_NAME}}.$res.yaml > /tmp/${{DEPLOYMENT_NAME}}.$res.yaml
                            kubectl apply -f /tmp/${{DEPLOYMENT_NAME}}.$res.yaml
                        done

                        kubectl rollout status deployment/${{DEPLOYMENT_NAME}} -n ${{NAMESPACE}} --timeout=600s
                        kubectl get pods -n ${{NAMESPACE}} -l app=${{DEPLOYMENT_NAME}}
                    '''
                }}
            }}
        }}
    }}

    post {{ always {{ cleanWs() }} }}
}}
""")
    else:  # backend
        # Credentials uniquement pour ceux ayant un secret_id
        creds = []
        for e in envs:
            if 'secret_id' in e and e['secret_id']:
                creds.append((e['secret_id'], e['name']))
        with open(jenkinsfile_path, "w") as f:
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
    }}

    stages {{
        stage('Build & Push') {{
            steps {{
                withCredentials([
                    usernamePassword(credentialsId: 'harbor-credentials', usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS'),
{chr(10).join([f"                    string(credentialsId: '{sid}', variable: '{name}')," for sid, name in creds])}
                ]) {{
                    sh '''
                        set -e
                        docker logout $REGISTRY || true
                        docker build \\
                          --build-arg PORT={port} \\
                          -t $FULL_IMAGE_NAME .
                        echo $HARBOR_PASS | \\
                          docker login -u $HARBOR_USER --password-stdin $REGISTRY
                        docker push $FULL_IMAGE_NAME
                        docker logout $REGISTRY
                    '''
                }}
            }}
        }}

        stage('Deploy') {{
            steps {{
                withCredentials([
                    file(credentialsId: 'kubeconfig-jenkins', variable: 'KUBECONFIG'),
                    usernamePassword(credentialsId: 'harbor-credentials', usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS'),
{chr(10).join([f"                    string(credentialsId: '{sid}', variable: '{name}')," for sid, name in creds])}
                ]) {{
                    sh '''
                        set -e
                        export KUBECONFIG=$KUBECONFIG

                        kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
                        kubectl delete secret harbor-registry-secret -n $NAMESPACE --ignore-not-found
                        kubectl create secret docker-registry harbor-registry-secret \\
                          --docker-server=$REGISTRY \\
                          --docker-username="$HARBOR_USER" \\
                          --docker-password="$HARBOR_PASS" \\
                          --namespace=$NAMESPACE

                        kubectl delete secret $SECRET_NAME -n $NAMESPACE --ignore-not-found
                        kubectl create secret generic $SECRET_NAME \\
{chr(10).join([f"                          --from-literal={e['name']}=\"{e['value']}\" \\" if 'value' in e and e['value'] else f"                          --from-literal={e['name']}=\"$$${e['name']}\" \\" for e in envs])}
                          --namespace=$NAMESPACE

                        for res in deployment service hpa; do
                            envsubst < $K8S_DIR/{app_name}-$res.yaml > /tmp/{app_name}-$res.yaml
                            kubectl apply -f /tmp/{app_name}-$res.yaml
                        done

                        kubectl rollout status deployment/{app_name} -n $NAMESPACE --timeout=120s
                        kubectl get pods -n $NAMESPACE -l app={app_name}
                    '''
                }}
            }}
        }}
    }}

    post {{ always {{ cleanWs() }} }}
}}
""")