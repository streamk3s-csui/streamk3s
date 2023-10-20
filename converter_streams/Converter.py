import json
import os

import Host
import Kubernetes
from hurry.filesize import size, iec
import subprocess
import requests
from systemd.journal import JournalHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


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
    output_queue_list = []
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
                queues = y.get_queues()
                properties = queues.get("properties")
                input_queue = properties.get("input_queue")
                output_queue = properties.get("output_queue")
                if input_queue is not None and output_queue is not None:
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
                            "INPUT_QUEUE": input_queue,
                            "OUTPUT_QUEUE": output_queue,
                            "APPLICATION": namespace_pack
                        }
                    }
                    generate_queue(input_queue, namespace_pack, output_queue_list)
                    generate_queue(output_queue, namespace_pack, output_queue_list, "output", y.get_order(),
                                   y.get_name())
                if input_queue is not None and output_queue is None:
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
                            "INPUT_QUEUE": input_queue,
                            "APPLICATION": namespace_pack
                        }
                    }
                    generate_queue(input_queue, namespace_pack, output_queue_list)
                if output_queue is not None and input_queue is None:
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
                            "OUTPUT_QUEUE": output_queue,
                            "APPLICATION": namespace_pack
                        }
                    }
                    generate_queue(output_queue, namespace_pack, output_queue_list, "output", y.get_order(),
                                   y.get_name())

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
    return deployment_files, configmap_list, output_queue_list


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


def generate_queue(queue, application, output_queue_list, type="None", order=0, operator="None"):
    password = os.getenv("RABBITMQ_PASSWORD", "password")
    parameters = {"durable": True}
    ip = os.getenv("POD_IP", "ip")
    command = "curl -u user:" + password + " -X PUT http://" + ip + ":15672/api/queues/" + application + "/" + queue + " --data " + "'" + json.dumps(
        parameters) + "'"
    if type is not "None" and order is not 0 and operator is not "None":
        output_queue_list.append({"queue": queue, "order": order, "namespace": application, "operator":operator})
    print(str(command))
    subprocess.call([str(command)], shell=True)


def configure_instancemanager(list):
    sorted_list = sorted(list, key=lambda x: x["order"])
    for json_item in sorted_list:
        if json_item.get("scale"):
            response = requests.post("0.0.0.0:4004/init", json=json_item)
            if response.status_code == 200:
                print("Instancemanager is configured successfully!")
            else:
                print("Instancemanager is not configured, status code:", response.status_code)
