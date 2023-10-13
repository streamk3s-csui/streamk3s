import os
import subprocess
import threading
import oyaml as yaml


def find_ip():
    rabbit_mq_exporter = os.popen(
        "kubectl get -n rabbit service monitorable-rabbit-mq --template '{{.spec.clusterIP}}'").read()

    master_ip = "0.0.0.0"
    return rabbit_mq_exporter, master_ip


def write_targets_json(rabbit_mq_exporter, prometheus_ip):
    list_exporters = []
    list_prometheus = []
    rabbit_mq_exporter = rabbit_mq_exporter + ':15692'
    list_exporters.append(rabbit_mq_exporter)
    prometheus_ip = prometheus_ip + ":9090"
    list_prometheus.append(prometheus_ip)
    scrape = {"scrape_configs": [
        {"job_name": 'prometheus',
         "static_configs": [{"targets": list_prometheus}]},
        {"job_name": "rabbit-exporter",
         "static_configs": [{"targets": list_exporters}]}]}
    with open('prometheus.yml', 'w') as outfile:
        yaml.dump(scrape, outfile, default_flow_style=False)


def init_mongodb():
    subprocess.call(["kubectl apply -f mongo.yaml"], shell=True)


def init_rabbimq():
    subprocess.call(["sudo ./requirements.sh"], shell=True)
    subprocess.call(["kubectl apply -f rabbitmq_metrics_service.yaml"], shell=True)


def init_prometheus():
    rabbit_mq_exporter, prometheus_ip = find_ip()
    write_targets_json(rabbit_mq_exporter, prometheus_ip)
    subprocess.call([
        'docker run -d -p 9090:9090 -v /home/giannis/monitoring_rabbitmq/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus'],
        shell=True)


def port_forwarding():
    subprocess.call(['nohup ./port-forwarding.sh &'], shell=True)


def find_password():
    k3s = os.popen(
        "kubectl get secret mu-rabbit-rabbitmq --namespace rabbit -o jsonpath='{.data.rabbitmq-password}' | base64 --decode").read()
    return k3s


thread_rabbitmq = threading.Thread(target=init_rabbimq)
thread_rabbitmq.start()


