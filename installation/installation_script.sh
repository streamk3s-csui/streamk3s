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
docker run -it -p 1880:1880 -d --restart unless-stopped --name mynodered nodered/node-red
echo "--------------------------------------------"
echo "KEDA"
echo "--------------------------------------------"
# Without admission webhooks
kubectl apply --server-side -f https://github.com/kedacore/keda/releases/download/v2.12.0/keda-2.12.0-core.yaml