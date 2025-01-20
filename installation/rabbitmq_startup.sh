#!/bin/bash

echo "Starting RabbitMQ configuration update..."

# Ensure we have kubectl access
if ! kubectl get nodes > /dev/null 2>&1; then
    echo "Error: Cannot access kubernetes cluster"
    exit 1
fi

RABBITMQ_USERNAME="user"
RABBITMQ_PASSWORD=$(kubectl get secret mu-rabbit-rabbitmq --namespace rabbit -o jsonpath='{.data.rabbitmq-password}' | base64 --decode)

max_attempts=5
attempt=1
while [ $attempt -le $max_attempts ]; do
    pod_ip=$(kubectl get pod mu-rabbit-rabbitmq-0 -n rabbit -o jsonpath='{.status.podIP}')
    if [ -n "$pod_ip" ]; then
        echo "Found RabbitMQ Pod IP: $pod_ip"
        break
    fi
    echo "Attempt $attempt: Waiting for Pod IP... (will retry in 10 seconds)"
    sleep 10
    attempt=$((attempt + 1))
done

if [ -z "$pod_ip" ]; then
    echo "Error: Could not get Pod IP after $max_attempts attempts!"
    exit 1
fi

echo "Stopping services..."
systemctl stop instancemanager.service
systemctl stop converter.service

for DIR in "/opt/Stream-Processing/instancemanager" "/opt/Stream-Processing/converter_streams"; do
    echo "Updating configuration in $DIR"
    
    cat > "$DIR/.env" << EOF
RABBITMQ_USERNAME=$RABBITMQ_USERNAME
RABBITMQ_PASSWORD=$RABBITMQ_PASSWORD
POD_IP=$pod_ip
EOF

    chmod 644 "$DIR/.env"
done

echo "Starting services..."
systemctl start instancemanager.service
systemctl start converter.service

echo "Checking service status..."
systemctl status instancemanager.service --no-pager
systemctl status converter.service --no-pager

echo "Configuration update complete!"