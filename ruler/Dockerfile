FROM python:latest
RUN mkdir /Ruler
WORKDIR /Ruler
COPY ./main.py ./
COPY ./MongoDB.py ./

RUN pip3 install requests \
    flask \
    pymongo

ENV MONGO_IP="#pod_ip"
ENV MONGO_PORT = "#api_port"


CMD ["/usr/local/bin/python","./main.py"]
