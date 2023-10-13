apt update
apt install snapd
snap install helm --classic
helm repo add stable https://charts.helm.sh/stable
kubectl config view --raw > ~/.kube/config
kubectl create namespace rabbit
helm install mu-rabbit stable/rabbitmq --namespace rabbit --set rabbitmqVhost=streams
kubectl wait --namespace rabbit --for condition=ready pod/mu-rabbit-rabbitmq-0 --timeout=30s
kubectl expose -n rabbit pod mu-rabbit-rabbitmq-0 --port=15672 --target-port=15672 --name=loadbalancer --type=LoadBalancer
