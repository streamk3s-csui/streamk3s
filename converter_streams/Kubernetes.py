import json
import os
import shutil
import subprocess
import tempfile

import yaml
import socket


def apply(data):
    dirpath = tempfile.mkdtemp(dir=os.getcwd())
    ff = open(dirpath + '/temp.yaml', 'w+')
    yaml.dump(data, ff, allow_unicode=True, sort_keys=False)
    ff.close()
    os.system("kubectl apply -f " + dirpath)
    os.system("rm -r " + dirpath)


def find_ip():
    k3s = os.popen("kubectl get -n rabbit service mu-rabbit-rabbitmq -o json").read()
    json_file = json.loads(k3s)
    spec = json_file.get('spec')
    ip = spec.get('clusterIP')
    print(ip)
    return ip


def find_password():
    k3s = os.popen(
        "kubectl get secret mu-rabbit-rabbitmq --namespace rabbit -o jsonpath='{.data.rabbitmq-password}' | base64 --decode").read()
    return k3s



