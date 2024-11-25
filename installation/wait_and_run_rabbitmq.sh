#!/bin/bash


# Wait for k8s to be readt
while ! sudo kubectl get nodes > /dev/null 2>&1; do
    echo "Waiting for kubernetes to be ready..."
    sleep 10
done

# Waitt againn
wait 30 

sudo /usr/local/bin/rabbitmq_startup.sh