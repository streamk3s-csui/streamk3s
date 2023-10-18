import json
import os

import Host
import Kubernetes
from hurry.filesize import size, iec
import subprocess
import requests

def convert_bytes(bytes):
    output = 0
    if 'MB' in bytes:
        number = bytes.replace('MB', '')
        output = int(number) * 1024 * 1024
    if 'GB' in bytes:
        number = bytes.replace('GB', '')
        output = int(number) * 1024 * 1024 * 1024
    return output


def tosca_to_k8s(operator_list, host_list, namespace_pack):
    output_topic_list = []
    images = []
    deployment = {}
    edge_os = ''
    edge_disk = ''
    edge_cpu = ''
    edge_mem = ''
    vm_os = ''
    persistent_files = []
    deployment_files = []
    resource_list = []
    configmap_list = []
    resources = []
    value = 7000
    for x in host_list:
        for y in operator_list:
            port_yaml = []
            if y.get_host() == x.get_name():
                mem_size = convert_bytes(x.get_ram())
                kube_ram = size(mem_size, system=iec)
                disk_size = convert_bytes(x.get_disk())
                kube_disk = size(disk_size, system=iec)
                if x.get_arch() == 'x86_64':
                    node_arch = 'amd64'
                resource_yaml = {
                    'limits': {'cpu': x.get_cpu(),
                               'memory': kube_ram,
                               'ephemeral-storage': kube_disk}}

                operator_type = y.get_operator_type()
                ip = os.getenv("POD_IP", "ip")
                password = os.getenv("RABBITMQ_PASSWORD", "password")
                topics = y.get_topics()
                properties = topics.get("properties")
                input_topic = properties.get("input_topic")
                output_topic = properties.get("output_topic")
                if input_topic is not None and output_topic is not None:
                    operator_configmap = {
                        "kind": "ConfigMap",
                        "apiVersion": "v1",
                        "metadata": {
                            "name": "appconfig-" + str(y.get_order()),
                            "namespace": namespace_pack
                        },
                        "data": {
                            "API_PORT": "4321",
                            "PUBLISH_PATH": "/post_message",
                            "CONSUME_PATH": "/get_message",
                        }
                    }
                    publish_configmap = {
                        "kind": "ConfigMap",
                        "apiVersion": "v1",
                        "metadata": {
                            "name": "publishconfig-" + str(y.get_order()),
                            "namespace": namespace_pack
                        },
                        "data": {
                            "OPERATOR_PORT": "4322",
                            "OPERATOR_PATH": "/post_message",
                            "RABBIT_IP": ip,
                            "RABBITMQ_PASSWORD": password,
                            "INPUT_TOPIC": input_topic,
                            "OUTPUT_TOPIC": output_topic,
                            "APPLICATION": namespace_pack
                        }
                    }
                    generate_topic(input_topic, namespace_pack, output_topic_list)
                    generate_topic(output_topic, namespace_pack, output_topic_list, "output", y.get_order())
                if input_topic is not None and output_topic is None:
                    operator_configmap = {
                        "kind": "ConfigMap",
                        "apiVersion": "v1",
                        "metadata": {
                            "name": "appconfig-" + str(y.get_order()),
                            "namespace": namespace_pack
                        },
                        "data": {
                            "API_PORT": "4321",
                            "CONSUME_PATH": "/get_message",

                        }
                    }
                    publish_configmap = {
                        "kind": "ConfigMap",
                        "apiVersion": "v1",
                        "metadata": {
                            "name": "publishconfig-" + str(y.get_order()),
                            "namespace": namespace_pack
                        },
                        "data": {
                            "OPERATOR_PORT": "4322",
                            "OPERATOR_PATH": "/post_message",
                            "RABBIT_IP": ip,
                            "RABBITMQ_PASSWORD": password,
                            "INPUT_TOPIC": input_topic,
                            "APPLICATION": namespace_pack
                        }
                    }
                    generate_topic(input_topic, namespace_pack, output_topic_list)
                if output_topic is not None and input_topic is None:
                    operator_configmap = {
                        "kind": "ConfigMap",
                        "apiVersion": "v1",
                        "metadata": {
                            "name": "appconfig-" + str(y.get_order()),
                            "namespace": namespace_pack
                        },
                        "data": {
                            "API_PORT": "4321",
                            "PUBLISH_PATH": "/post_message",
                        }
                    }
                    publish_configmap = {
                        "kind": "ConfigMap",
                        "apiVersion": "v1",
                        "metadata": {
                            "name": "publishconfig-" + str(y.get_order()),
                            "namespace": namespace_pack
                        },
                        "data": {
                            "OPERATOR_PORT": "4322",
                            "OPERATOR_PATH": "/post_message",
                            "RABBIT_IP": ip,
                            "RABBITMQ_PASSWORD": password,
                            "OUTPUT_TOPIC": output_topic,
                            "APPLICATION": namespace_pack
                        }
                    }
                    generate_topic(output_topic, namespace_pack, output_topic_list, "output", y.get_order())

                configmap_list.append(publish_configmap)
                configmap_list.append(operator_configmap)

                ports = y.get_port()
                if isinstance(ports, str):
                    content = {'containerPort': int(ports), 'name': y.get_name()}
                    port_yaml.append(content)
                if isinstance(ports, list):
                    i = 0
                    for port in ports:
                        i = i + 1
                        content = {'containerPort': int(port), 'name': y.get_name() + str(i)}
                        port_yaml.append(content)

                    deployment = {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "metadata": {
                            "name": y.get_name(),
                            "namespace": namespace_pack,
                            "labels": {"app": y.get_application()}
                        },
                        'spec': {
                            'selector': {
                                'matchLabels': {
                                    'app': y.get_application()}},
                            'strategy': {
                                'type': 'Recreate'},
                            'template': {
                                'metadata': {
                                    'labels': {
                                        'app': y.get_application()}},
                                "spec": {
                                    "containers": [
                                        {
                                            "name": "companion-container",
                                            "image": "gkorod/companion:v2.4",
                                            "imagePullPolicy": "Always",
                                            "env": [
                                                {
                                                    "name": "MY_POD_IP",
                                                    "valueFrom": {
                                                        "fieldRef": {
                                                            "fieldPath": "status.podIP"
                                                        }
                                                    }
                                                },
                                                {"name": "MY_POD_NAME",
                                                 "valueFrom": {"fieldRef": {"fieldPath": "metadata.name"}}},
                                            ],
                                            "ports": [
                                                {
                                                    "containerPort": 4321,
                                                    "name": "publishport"
                                                }
                                            ],
                                            'volumeMounts': [
                                                {
                                                    'name': 'cache-volume',
                                                    'mountPath': 'volume' + str(y.get_order())}],
                                            "envFrom": [
                                                {
                                                    "configMapRef": {
                                                        "name": "publishconfig-" + str(y.get_order())
                                                    }
                                                }
                                            ]
                                        },
                                        {
                                            "name": y.get_name(),
                                            'resources': resource_yaml,
                                            "image": y.get_image(),
                                            "imagePullPolicy": "Always",
                                            "env": [
                                                {
                                                    "name": "MY_POD_IP",
                                                    "valueFrom": {
                                                        "fieldRef": {
                                                            "fieldPath": "status.podIP"
                                                        }
                                                    }
                                                },
                                                {"name": "MY_POD_NAME",
                                                 "valueFrom": {"fieldRef": {"fieldPath": "metadata.name"}}},
                                                {"name": "MY_POD_NAMESPACE",
                                                 "valueFrom": {"fieldRef": {"fieldPath": "metadata.namespace"}}}
                                            ],
                                            "ports": [
                                                {
                                                    "containerPort": 4322,
                                                    "name": "operatorport"
                                                }
                                            ],
                                            "envFrom": [
                                                {
                                                    "configMapRef": {
                                                        "name": "appconfig-" + str(y.get_order())
                                                    }
                                                }
                                            ]
                                        }

                                    ],
                                    'volumes': [{
                                        'name': 'cache-volume',
                                        'emptyDir': {'sizeLimit': kube_disk}}],
                                    'nodeSelector': {
                                        'beta.kubernetes.io/os': x.get_os(),
                                        'beta.kubernetes.io/arch': node_arch},
                                }
                            }}}

                    deployment_files.append(deployment)
    return deployment_files, configmap_list, output_topic_list


def secret_generation(json, application):
    secret = {'apiVersion': 'v1',
              'kind': 'Secret',
              'metadata': {
                  'name': application + '-registry-credentials',
                  'namespace': application},
              'type': 'kubernetes.io/dockerconfigjson',
              'data': {
                  '.dockerconfigjson': json}}
    return secret


def namespace(application):
    namespace = {'apiVersion': 'v1', 'kind': 'Namespace',
                 'metadata': {'name': application}}
    password = os.getenv("RABBITMQ_PASSWORD", "password")
    ip = os.getenv("POD_IP", "ip")
    command = 'curl -u user:' + password + ' -X PUT http://' + ip + ':15672/api/vhosts/' + application
    print(str(command))
    subprocess.call([str(command)], shell=True)

    return namespace


def generate_topic(topic, application, output_topic_list, type="None", order=0):
    password = os.getenv("RABBITMQ_PASSWORD", "password")
    parameters = {"durable": True}
    ip = os.getenv("POD_IP", "ip")
    command = "curl -u user:" + password + " -X PUT http://" + ip + ":15672/api/queues/" + application + "/" + topic + " --data " + "'" + json.dumps(
        parameters) + "'"
    if type is not "None" and order is not 0:
        output_topic_list.append({"topic": topic, "order": order})
    print(str(command))
    subprocess.call([str(command)], shell=True)


def configure_instancemanager(list):
    sorted_list = sorted(list, key=lambda x: x["order"])
    last_output_topic = sorted_list[-1]
    last_output_topic.pop('order', None)
    response = requests.post("0.0.0.0:4004/init", json=last_output_topic)
    if response.status_code == 200:
        print("Instancemanager is configured successfully!")
    else:
        print("Instancemanager is not configured, status code:", response.status_code)