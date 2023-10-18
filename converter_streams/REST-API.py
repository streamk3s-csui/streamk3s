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

logging.basicConfig(filename='std.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)


@app.route('/submit', methods=['POST'])
def validate():
    content = request.json
    dirpath = tempfile.mkdtemp(dir=os.getcwd())
    ff = open(dirpath + '/application_model.yaml', 'w+')
    yaml.dump(content, ff, allow_unicode=True, sort_keys=False)
    ff.close()
    if os.path.exists(dirpath + '/application_model.yaml'):
        message, isCorrect = sommelier.validation(dirpath + '/application_model.yaml')
        shutil.rmtree(dirpath)
        if isCorrect:
            logging.info("application model is correct")
            operator_list, host_list, namespace = Parser.ReadFile(content)
            namespace_file = Converter.namespace(namespace)
            deployment_files, confimap_files, output_topic_list = Converter.tosca_to_k8s(operator_list, host_list,
                                                                                         namespace)
            Kubernetes.apply(namespace_file)
            for configmap in confimap_files:
                Kubernetes.apply(configmap)
            for deploy in deployment_files:
                Kubernetes.apply(deploy)
                os.system("kubectl wait --for condition=ready pods --all -n " + namespace + " --timeout=30s")
            KEDA.write_rules_config(operator_list)
        else:
            logging.info("application model is not correct")
    return message


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='9001', debug=True)
