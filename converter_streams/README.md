## Description
The Converter component functions as a reasoner tool capable of both reading and generating Kubernetes definition YAML files. It is seamlessly integrated with the Sommelier Validator. Initially, Sommelier Validator is employed to validate our TOSCA extension. Upon confirming the validity of the provided model, Converter is then able to generate the necessary files.

### Sommelier Validator

Sommelier is a tool capable of validating TOSCA application topologies. The introduction of Sommelier was initially documented in the following research paper:
 > _A. Brogi, A. Di Tommaso, J. Soldani. <br>
 > **Sommelier: A Tool for Validating TOSCA Application Topologies.** <br>
 > In: Pires L., Hammoudi S., Selic B. (eds) Model-Driven Engineering and Software Development. MODELSWARD 2017. Communications in Computer and Information Science, vol 880. Springer, Cham_


The code for Sommelier can be found in this <a href=https://github.com/di-unipi-socc/Sommelier>repository</a>.

### How Sommelier & Converter works in our Platform

1. An HTTP Post endpoint <mark>\submit</mark> within the <mark>validate()</mark> function is being provided by <a href=https://github.com/f-coda/Stream-Processing/blob/main/converter_streams/REST-API.py>REST-API.py</a>. This endpoint expects TOSCA data in JSON format from NodeRED. Upon receiving the TOSCA model, it is temporarily stored as a YAML file.
2. The temporary file is sent to Sommelier Validator through the <mark>validation(path)</mark> function in the <a href=https://github.com/f-coda/Stream-Processing/blob/main/converter_streams/sommelier.py>sommelier.py</a> script. This function validates TOSCA models in YAML format. Sommelier is capable of validating TOSCA models based on the definitions of the objects it recognizes. You can find the definitions of our custom extended language <a href=https://github.com/f-coda/Stream-Processing/tree/main/converter_streams/definitions>here</a>.
3. If the submitted model is valid, the <mark>ReadFile(content)</mark> function from the <a href=https://github.com/f-coda/Stream-Processing/blob/main/converter_streams/Parser.py>Parser.py</a> script is invoked by REST-API.py. This function parses the model and creates lists containing the corresponding semantics.
4. Following this, REST-API.py invokes two functions from <a href=https://github.com/f-coda/Stream-Processing/blob/main/converter_streams/Converter.py>Converter.py</a> to produce the relevant Kubernetes YAML files. The first function, <mark>namespace(namespace)</mark>, generates the namespace responsible for hosting the application and sets up the necessary vhost on RabbitMQ. The second function, called <mark>Converter.tosca_to_k8s(operator_list, host_list, namespace)</mark>, retrieves lists of semantics describing operators/applications and hosts, in addition to the generated namespace. These details are utilized to deploy applications along with companion containers on the platform.
5. Subsequently, REST-API.py repeatedly invokes the <mark>apply(data)</mark> function from <a href=https://github.com/f-coda/Stream-Processing/blob/main/converter_streams/Kubernetes.py>Kubernetes.py</a> to deploy the generated files onto the Kubernetes cluster. The same function is being utilized to create configmaps that will configure the deployed containers to communicate with their companion container pair.
6. In the final step, REST-API.py employs the <mark>write_rules_config(operator_list)</mark> function from the <a href=https://github.com/f-coda/Stream-Processing/blob/main/converter_streams/KEDA.py>KEDA.py</a> script. This function generates KEDA YAML files, encapsulating scale rules for the operators derived from the description provided in TOSCA models.