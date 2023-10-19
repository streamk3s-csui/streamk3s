class Operator:

    def __init__(self, image, type, name, application, operator_type, port, arch, os, host, scale, queues, order):
        self.image = image
        self.type = type
        self.name = name
        self.application = application
        self.operator_type = operator_type
        self.port = port
        self.arch = arch
        self.os = os
        self.host = host
        self.scale = scale
        self.queues = queues
        self.order = order

    def get_host(self):
        return self.host

    def get_operator_type(self):
        return self.operator_type

    def get_port(self):
        return self.port

    def get_name(self):
        return self.name

    def get_application(self):
        return self.application

    def get_image(self):
        return self.image

    def get_order(self):
        return self.order

    def get_scale(self):
        return self.scale

    def get_queues(self):
        return self.queues
