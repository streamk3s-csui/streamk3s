import logging
import os
import shutil
import tempfile
import KEDA
import yaml
from flask import Flask, request
from systemd.journal import JournalHandler  # Import JournalHandler

import Converter
import Kubernetes
import Parser
import sommelier
import datetime

app = Flask(__name__)
# Configure logging
logging.basicConfig(level=logging.INFO)
# Configure logging to use JournalHandler
logger = logging.getLogger()
logger.setLevel(logging.INFO)
journal_handler = JournalHandler()
journal_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
journal_handler.setFormatter(formatter)
logger.addHandler(journal_handler)


@app.route("/submit", methods=["POST"])
def validate():
    content = request.json

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    static_dir = os.path.join(os.getcwd(), "manifests", timestamp)
    os.makedirs(static_dir, exist_ok=True)

    application_model_path = os.path.join(static_dir, "application_model.yaml")

    logging.info("application model path: %s", application_model_path)

    with open(application_model_path, "w+") as ff:
        yaml.dump(content, ff, allow_unicode=True, sort_keys=False)

    if os.path.exists(application_model_path):
        with open(application_model_path, "r") as file:
            tosca_yaml = yaml.safe_load(file)
        current_imports = tosca_yaml.get("imports")
        new_imports = ["/opt/Stream-Processing/converter_streams/" + current_imports[0]]
        tosca_yaml["imports"] = new_imports
        with open(application_model_path, "w+") as file:
            yaml.dump(tosca_yaml, file, sort_keys=False)

        message, isCorrect = sommelier.validation(application_model_path)

        if isCorrect:
            logger.info("Application model is correct")
            operator_list, host_list, namespace = Parser.ReadFile(content)
            namespace_file = Converter.namespace(namespace)
            persistent_volumes, deployment_files, confimap_files = (
                Converter.tosca_to_k8s(operator_list, host_list, namespace)
            )

            Kubernetes.apply(namespace_file, static_dir)
            if persistent_volumes:
                for pv in persistent_volumes:
                    Kubernetes.apply(pv, static_dir)
            for configmap in confimap_files:
                Kubernetes.apply(configmap, static_dir)
            for deploy in deployment_files:
                Kubernetes.apply(deploy, static_dir)
                os.system(
                    "kubectl wait --for condition=ready pods --all -n "
                    + namespace
                    + " --timeout=30s"
                )
            KEDA.write_rules_config(operator_list, static_dir)

            script_dir = os.path.dirname(os.path.abspath(__file__))
            producer_service_file_path = os.path.join(
                script_dir, "producer-service.yaml"
            )

            try:
                with open(producer_service_file_path, "r") as f:
                    producer_service_data = yaml.safe_load(f)
                if not producer_service_data:
                    logger.error("producer-service.yaml is empty or invalid.")
                else:
                    Kubernetes.apply(producer_service_data, static_dir)
            except FileNotFoundError:
                logger.error(
                    f"Error: producer-service.yaml not found at {producer_service_file_path}"
                )
            except yaml.YAMLError as e:
                logger.error(f"Error parsing producer-service.yaml: {e}")
            except Exception as e:
                logger.error(f"An error occurred applying producer-service.yaml: {e}")

            Converter.configure_instancemanager(
                {"queue": "termination-queue", "namespace": namespace}
            )
        else:
            logger.info("Application model is not correct")
    return message


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="9001", debug=True)
