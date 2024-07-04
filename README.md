## StreamK3s: A stream-processing Function as a Service (FaaS) solution

StreamK3s, operating as a Function as a Service (FaaS) solution, empowers developers to integrate their own containerized streaming modules into our K3s cluster. This is accomplished by defining communication patterns within NodeRED. NodeRED has the ability to extract fields and create a TOSCA extension in JSON format, outlining the communication structure and scaling behavior of these modules. The TOSCA description is then processed by the Converter component. This component validates the TOSCA using the <a href=https://github.com/di-unipi-socc/Sommelier>TOSCA Sommelier validator</a>. If the TOSCA is found to be valid, the Converter generates corresponding Kubernetes files. It also configures RabbitMQ to facilitate communication between components via streams and sets up <a href=https://keda.sh/>KEDA</a> to implement scaling rules linked to RabbitMQ for each component. Additionally, the Instance Manager is configured by Converter, to terminate a scaled pod instance once it has completed its task.


## Architecture
![alt text](Stream%20Processing%20v4.drawio.png)

## Agnostic to Programming Languages

StreamK3s solution is language-agnostic, capable of hosting microservices written in any programming language, thanks to its utilization of Kubernetes for deployment. Developers are relieved from the need to understand RabbitMQ communication intricacies. Each microservice is deployed alongside a <a href=https://github.com/f-coda/Stream-Processing/tree/main/companion>companion container</a> that manages communication with RabbitMQ. Developers only need to interact with the endpoints of this companion container to publish or receive messages, simplifying their workflow.

## Main components of this repository

* <a href="https://github.com/f-coda/Stream-Processing/tree/main/companion"> Companion Container</a>
* <a href="https://github.com/f-coda/Stream-Processing/tree/main/converter_streams"> Converter Service</a>
* <a href="https://github.com/f-coda/Stream-Processing/tree/main/instancemanager"> Instance Manager Service</a> 
* <a href="https://github.com/f-coda/Stream-Processing/tree/main/operator"> Operator Container</a> 
## Installation

The platform's unified installation script is accessible <a href="https://github.com/f-coda/Stream-Processing/tree/main/installation">here</a>. RabbiMQ, KEDA, and NodeRED are installed as pods, while Instance Manager and Converter are deployed as Services on Linux. Prior to platform installation, a Kubernetes Cluster must be in place. The script manages all other necessary requirements automatically.

## Cite Us

If you use the above code for your research, please cite our paper:

- [StreamK3s: A K3s-Based Data Stream Processing Platform for Simplifying Pipeline Creation, Deployment, and Scaling](https://www.sciencedirect.com/science/article/pii/S2352711024001572)

      @article{KORONTANIS2024101786,
      title = {StreamK3s: A K3s-Based Data Stream Processing Platform for Simplifying Pipeline Creation, Deployment, and Scaling},
      journal = {SoftwareX},
      volume = {27},
      pages = {101786},
      year = {2024},
      issn = {2352-7110},
      doi = {https://doi.org/10.1016/j.softx.2024.101786},
      url = {https://www.sciencedirect.com/science/article/pii/S2352711024001572},
      author = {Ioannis Korontanis and Antonios Makris and Alexandros Kontogiannis and Iraklis Varlamis and Konstantinos Tserpes},
      keywords = {Cloud, Edge, FaaS platform, K3s cluster},
      abstract = {In today’s technology-driven era, applications focused on data stream processing are increasingly in need of user-friendly platforms, especially with the growing popularity of serverless computing solutions. Developers seek   features such as straightforward pipeline definition, component reusability, throughput-based automatic scaling, and efficient resource utilization, highlighting the demand for such capabilities. This paper introduces a platform that addresses these requirements, leveraging technologies like K3s, RabbitMQ, and KEDA. In contrast to conventional platforms, the presented solution excels through its seamless integration of adaptability and user-friendliness, surpassing fundamental capabilities. The platform’s simple self-configuration streamlines the deployment of developer-created functions, improving efficiency and guaranteeing a seamless experience. This allows developers to focus on creating functions without the burden of managing complex configurations.}
      }
