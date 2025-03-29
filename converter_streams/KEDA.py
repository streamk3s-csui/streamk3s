import tempfile
import re
import Kubernetes
import oyaml as yaml
import os
import logging
import base64

logging.basicConfig(filename='std.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)


def write_rules_config(operatorlist):
    for operator in operatorlist:
        deployment = operator.get_name()
        namespace = operator.get_application()
        rule_list = operator.get_scale()
        if rule_list is not None:
            for rule in rule_list:
                rule['deployment'] = deployment
                logging.info(rule)
                name = rule.get('deployment')
                logging.info(name)
                condition = rule.get('condition')
                scale_up = rule.get('scale')
                if rule.get('output_queue'):
                    queue = rule.get('output_queue')
                if rule.get('input_queue'):
                    queue = rule.get('input_queue')
                scale_object = {
                    'apiVersion': 'keda.sh/v1alpha1',
                    'kind': 'ScaledObject',
                    'metadata': {
                        'name': name, 
                        'namespace': namespace
                    },
                    'spec': {
                        'scaleTargetRef': {'name': name}, 
                        'pollingInterval': 5, 
                        'cooldownPeriod': 10,
                        'minReplicaCount': 1, 
                        'maxReplicaCount': scale_up,
                        'triggers': []
                    }
                }
                if 'QueueLength' in condition:
                    condition_name = 'QueueLength'
                    value = int(re.search(r'\d+', condition).group())
                    scale_object['spec']['triggers'].append(
                        {
                            'type': 'rabbitmq',
                            'metadata': {
                                'protocol': 'http', 
                                'queueName': queue,
                                'mode': condition_name,
                                'value': str(value)},
                                'authenticationRef': {'name': 'keda-trigger-auth-rabbitmq-conn'}
                        }
                    )
                if 'MessageRate' in condition:
                    condition_name = 'MessageRate'
                    value = int(re.search(r'\d+', condition).group())
                    scale_object['spec']['triggers'].append(
                        {
                            'type': 'rabbitmq',
                            'metadata': {
                                'protocol': 'http', 
                                'queueName': queue,
                                'mode': condition_name,
                                'value': str(value)},
                                'authenticationRef': {'name': 'keda-trigger-auth-rabbitmq-conn'}
                        }
                    )
                value = int(re.search(r'\d+', condition).group())
                logging.info(scale_object)
                Kubernetes.apply(scale_object)
            password = os.getenv("RABBITMQ_PASSWORD", "password")
            ip = os.getenv("POD_IP", "ip")
            username = 'user'
            uri = 'http://' + username + ":" + password + "@"+ip+":15672/" + namespace

            uri_bytes = uri.encode('ascii')
            base64_uri = base64.b64encode(uri_bytes)
            credentials = base64_uri.decode('ascii')

            secret_config = {'apiVersion': 'v1',
                             'kind': 'Secret',
                             'metadata': {'name': 'keda-rabbitmq-secret', 'namespace': namespace},
                             'data': {'host': credentials}}
            Kubernetes.apply(secret_config)
            trigger_auth = {'apiVersion': 'keda.sh/v1alpha1',
                            'kind': 'TriggerAuthentication',
                            'metadata': {'name': 'keda-trigger-auth-rabbitmq-conn', 'namespace': namespace},
                            'spec': {
                                'secretTargetRef': [
                                    {'parameter': 'host', 'name': 'keda-rabbitmq-secret', 'key': 'host'}]}}
            Kubernetes.apply(trigger_auth)
