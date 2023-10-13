echo "--------------------------------------------"
echo "Requirements"
echo "--------------------------------------------"
apt update
apt install snapd
snap install helm --classic
echo "--------------------------------------------"
echo "RabbitMQ"
echo "--------------------------------------------"
helm repo add stable https://charts.helm.sh/stable
kubectl config view --raw > ~/.kube/config
kubectl create namespace rabbit
helm install mu-rabbit stable/rabbitmq --namespace rabbit --set rabbitmqVhost=streams
kubectl wait --namespace rabbit --for condition=ready pod/mu-rabbit-rabbitmq-0 --timeout=30s
kubectl expose -n rabbit pod mu-rabbit-rabbitmq-0 --port=15672 --target-port=15672 --name=loadbalancer --type=LoadBalancer
echo "--------------------------------------------"
echo "NodeRED"
echo "--------------------------------------------"
kubectl apply -f nodered-namespace.yaml
kubectl apply -f nodered-deployment.yaml
echo "--------------------------------------------"
echo "KEDA"
echo "--------------------------------------------"
# Without admission webhooks
kubectl apply --server-side -f https://github.com/kedacore/keda/releases/download/v2.12.0/keda-2.12.0-core.yaml