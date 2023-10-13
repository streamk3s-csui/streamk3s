## Description

It configures and installs RabbitMQ as a monitoring target for Prometheus. It also installs and configures Prometheus.

## Run

1. sudo python3 preparation.py
2. kubectl apply -f OperatorConfigMap.yaml
3. kubectl apply -f PublishConfigMap.yaml
4. kubectl apply -f deployment_operator_pub.yaml

