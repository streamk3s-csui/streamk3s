FROM python:latest
RUN mkdir /Operator
WORKDIR /Operator
COPY ./dummy_operator.py ./
COPY ./Interface.py ./

RUN pip3 install requests \
    flask

ENV MY_POD_IP="#pod_ip"
ENV API_PORT = "#api_port"
ENV MESSAGE="#message"
ENV PUBLISH_PATH="#publish_path"
ENV CONSUME_PATH="#consume_path"

CMD ["/usr/local/bin/python","./dummy_operator.py"]
