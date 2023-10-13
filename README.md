## Stream-Processing

Stream-Processing, functioning as a Function as a Service (FaaS) solution, empowers developers to introduce their own containerized streaming modules into our K3s cluster. This is achieved by defining communication patterns within NodeRED. NodeRED is capable of extracting fields and generating a TOSCA extension in JSON format. This extension describes the communication structure and scaling behavior of these modules. The TOSCA description is then processed by the Converter component. This component validates the TOSCA using the <a href=https://github.com/di-unipi-socc/Sommelier>TOSCA Sommelier validator</a>. If the TOSCA is deemed valid, the Converter generates corresponding Kubernetes files. It also configures RabbitMQ to facilitate communication between components via streams and sets up <a href=https://keda.sh/>KEDA</a> to implement scaling rules linked to RabbitMQ for each component.

## Architecture
![alt text](Streaming%20Processing%20v2.drawio%20(6).png)

## Installation

The platform's unified installation script is accessible <a href="https://github.com/f-coda/Stream-Processing/tree/main/installation">here</a>. RabbiMQ, KEDA, and NodeRED are installed as pods, while Instance Manager and Converter are deployed as Services on Linux. Prior to platform installation, a Kubernetes Cluster must be in place. The script manages all other necessary requirements automatically.