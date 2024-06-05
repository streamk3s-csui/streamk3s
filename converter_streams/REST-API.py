from systemd.journal import JournalHandler
import logging
import os
import shutil
import tempfile
import KEDA
import yaml
from flask import Flask, request

import Converter
import Kubernetes
import Parser
import sommelier

app = Flask(__name__)
log = logging.getLogger('Converter')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)


@app.route('/submit', methods=['POST'])
def validate():
    content = request.json
    dirpath = tempfile.mkdtemp(dir=os.getcwd())
    ff = open(dirpath + '/application_model.yaml', 'w+')
    yaml.dump(content, ff, allow_unicode=True, sort_keys=False)
    ff.close()
    if os.path.exists(dirpath + '/application_model.yaml'):
        with open(dirpath + '/application_model.yaml', 'r') as file:
             tosca_yaml = yaml.safe_load(file)
        current_imports = tosca_yaml.get('imports')
        new_imports = ["/opt/Stream-Processing/converter_streams/"+current_imports[0]]
        tosca_yaml['imports'] = new_imports
        with open(dirpath + '/application_model.yaml', 'w+') as file:
             yaml.dump(tosca_yaml, file, sort_keys=False)
        message, isCorrect = sommelier.validation(dirpath + '/application_model.yaml')
        shutil.rmtree(dirpath)
        if isCorrect:
            logging.info("application model is correct")
            operator_list, host_list, namespace = Parser.ReadFile(content)
            namespace_file = Converter.namespace(namespace)
            deployment_files, confimap_files = Converter.tosca_to_k8s(
                operator_list, host_list,
                namespace)
            Kubernetes.apply(namespace_file)
            for configmap in confimap_files:
                Kubernetes.apply(configmap)
            for deploy in deployment_files:
                Kubernetes.apply(deploy)
                os.system("kubectl wait --for condition=ready pods --all -n " + namespace + " --timeout=30s")
            KEDA.write_rules_config(operator_list)
            Converter.configure_instancemanager({"queue": "termination-queue", "namespace": namespace})
        else:
            logging.info("application model is not correct")
    return message


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='9001', debug=True)
