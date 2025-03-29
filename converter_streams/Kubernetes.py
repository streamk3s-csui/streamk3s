import json
import os
import shutil
import subprocess
import tempfile

import yaml
import socket


def apply(data):
    dirpath = tempfile.mkdtemp(dir=os.getcwd())
    filename = dirpath + '/temp.yaml'
    ff = open(filename, 'w+')
    yaml.dump(data, ff, allow_unicode=True, sort_keys=False)
    ff.close()
    os.system("kubectl apply -f " + filename)
    os.system("rm -r " + filename)






