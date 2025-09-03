pipeline {
    agent any
    environment {
        REGISTRY         = 'harbor.tsirylab.com'
        HARBOR_PROJECT   = 'pnud-agvm'
        IMAGE_NAME       = 'jacquinot-devops'
        IMAGE_TAG        = "${BUILD_NUMBER}"
        FULL_IMAGE_NAME  = "${REGISTRY}/${HARBOR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}"
        NAMESPACE        = 'pnud-agvm'
        K8S_DIR          = 'k8s'
        DEPLOYMENT_NAME  = 'jacquinot-devops'
        SERVICE_NAME     = 'jacquinot-devops-service'
        HPA_NAME         = 'jacquinot-devops-hpa'
        SECRET_NAME      = 'jacquinot-devops-secret'
        PORT             = '4011'
        NODE_PORT        = '30045'
    }

    stages {
        stage('Build & Push') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'harbor-credentials', usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS'),

                ]) {
                    sh '''
                        set -e
                        docker logout $REGISTRY || true
                        docker build \
                          --build-arg PORT=4011 \
                          -t $FULL_IMAGE_NAME .
                        echo $HARBOR_PASS | \
                          docker login -u $HARBOR_USER --password-stdin $REGISTRY
                        docker push $FULL_IMAGE_NAME
                        docker logout $REGISTRY
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([
                    file(credentialsId: 'kubeconfig-jenkins', variable: 'KUBECONFIG'),
                    usernamePassword(credentialsId: 'harbor-credentials', usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS'),

                ]) {
                    sh '''
                        set -e
                        export KUBECONFIG=$KUBECONFIG

                        kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
                        kubectl delete secret harbor-registry-secret -n $NAMESPACE --ignore-not-found
                        kubectl create secret docker-registry harbor-registry-secret \
                          --docker-server=$REGISTRY \
                          --docker-username="$HARBOR_USER" \
                          --docker-password="$HARBOR_PASS" \
                          --namespace=$NAMESPACE

                        kubectl delete secret $SECRET_NAME -n $NAMESPACE --ignore-not-found
                        kubectl create secret generic $SECRET_NAME \

                          --namespace=$NAMESPACE

                        for res in deployment service hpa; do
                            envsubst < $K8S_DIR/jacquinot-devops-$res.yaml > /tmp/jacquinot-devops-$res.yaml
                            kubectl apply -f /tmp/jacquinot-devops-$res.yaml
                        done

                        kubectl rollout status deployment/jacquinot-devops -n $NAMESPACE --timeout=120s
                        kubectl get pods -n $NAMESPACE -l app=jacquinot-devops
                    '''
                }
            }
        }
    }

    post { always { cleanWs() } }
}
