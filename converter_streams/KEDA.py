import re
import Kubernetes
import os
import logging
import base64

logging.basicConfig(
    filename="std.log", filemode="w", format="%(name)s - %(levelname)s - %(message)s"
)
logging.getLogger().setLevel(logging.INFO)


def write_rules_config(operatorlist, dirpath):
    for operator in operatorlist:
        deployment = operator.get_name()
        namespace = operator.get_application()
        rule_list = operator.get_scale()
        if rule_list is not None:
            scale_object = {
                "apiVersion": "keda.sh/v1alpha1",
                "kind": "ScaledObject",
                "metadata": {"name": f"{deployment}-scale", "namespace": namespace},
                "spec": {
                    "scaleTargetRef": {"name": deployment},
                    "pollingInterval": 5,
                    "cooldownPeriod": 10,
                    "minReplicaCount": 1,
                    "maxReplicaCount": 1,
                    "triggers": [],
                },
            }
            max_replicas = 1

            for rule in rule_list:
                condition = rule.get("condition")
                scale_up = rule.get("scale")
                queue = rule.get("output_queue") or rule.get("input_queue")
                if not queue:
                    continue

                # Update maxReplicaCount
                if scale_up and scale_up > max_replicas:
                    max_replicas = scale_up

                value = int(re.search(r"\d+", condition).group())

                if "QueueLength" in condition:
                    scale_object["spec"]["triggers"].append(
                        {
                            "type": "rabbitmq",
                            "metadata": {
                                "protocol": "http",
                                "queueName": queue,
                                "mode": "QueueLength",
                                "value": str(value),
                            },
                            "authenticationRef": {
                                "name": "keda-trigger-auth-rabbitmq-conn"
                            },
                        }
                    )

                if "MessageRate" in condition:
                    scale_object["spec"]["triggers"].append(
                        {
                            "type": "rabbitmq",
                            "metadata": {
                                "protocol": "http",
                                "queueName": queue,
                                "mode": "MessageRate",
                                "value": str(value),
                            },
                            "authenticationRef": {
                                "name": "keda-trigger-auth-rabbitmq-conn"
                            },
                        }
                    )

            # Set the maxReplicaCount to the highest value found
            scale_object["spec"]["maxReplicaCount"] = max_replicas

            logging.info(scale_object)
            Kubernetes.apply(scale_object, dirpath)

        password = os.getenv("RABBITMQ_PASSWORD", "password")
        ip = os.getenv("POD_IP", "ip")
        username = "user"
        uri = f"http://{username}:{password}@{ip}:15672/{namespace}"

        uri_bytes = uri.encode("ascii")
        base64_uri = base64.b64encode(uri_bytes)
        credentials = base64_uri.decode("ascii")

        secret_config = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {"name": "keda-rabbitmq-secret", "namespace": namespace},
            "data": {"host": credentials},
        }
        Kubernetes.apply(secret_config, dirpath)

        trigger_auth = {
            "apiVersion": "keda.sh/v1alpha1",
            "kind": "TriggerAuthentication",
            "metadata": {
                "name": "keda-trigger-auth-rabbitmq-conn",
                "namespace": namespace,
            },
            "spec": {
                "secretTargetRef": [
                    {"parameter": "host", "name": "keda-rabbitmq-secret", "key": "host"}
                ]
            },
        }
        Kubernetes.apply(trigger_auth, dirpath)
