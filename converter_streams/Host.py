





def sort_hosts(host_list, operator_list):
    size_list = len(host_list) - 1
    i = 0
    while i <= size_list:
        host_name = host_list[i].get_name()
        for operator in operator_list:
            operator_host = operator.get_host()
            if host_name == operator_host:
                order = operator.get_order()
                order = order - 1
                host_list[order], host_list[i] = host_list[i], host_list[order]
        i = i + 1


class Host:
    def __init__(self, type, name, cpu, ram, disk_size, arch, os):
        self.type = type
        self.name = name
        self.cpu = cpu
        self.ram = ram
        self.disk_size = disk_size
        self.arch = arch
        self.os = os

    def get_type(self):
        return self.type

    def get_name(self):
        return self.name

    def get_cpu(self):
        return self.cpu

    def get_ram(self):
        return self.ram

    def get_disk(self):
        return self.disk_size

    def get_arch(self):
        return self.arch

    def get_os(self):
        return self.os
