import json
import os
import shutil
import subprocess
import tempfile

import yaml
import socket


def apply(data):
    dirpath = tempfile.mkdtemp(dir=os.getcwd())
    ff = open(dirpath + '/temp.yaml', 'w+')
    yaml.dump(data, ff, allow_unicode=True, sort_keys=False)
    ff.close()
    os.system("kubectl apply -f " + dirpath)
    os.system("rm -r " + dirpath)






