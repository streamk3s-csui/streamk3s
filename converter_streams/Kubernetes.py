import json
import os
import shutil
import subprocess
import tempfile

import yaml
import socket


def apply(data):
    dirpath = tempfile.mkdtemp(dir=os.getcwd())
    ff = open(dirpath + "/temp.yaml", "w+")
    yaml.dump(data, ff, allow_unicode=True, sort_keys=False)
    ff.close()
    os.system("kubectl apply -f " + dirpath)
    os.system("rm -r " + dirpath)


def apply(data, dirpath):
    kind = data["kind"]
    name = data["metadata"]["name"]
    filename = f"{kind}_{name}.yaml".lower().replace(" ", "_")
    filepath = os.path.join(dirpath, filename)
    with open(filepath, "w+") as ff:
        yaml.dump(data, ff, allow_unicode=True, sort_keys=False)
    os.system(f"kubectl apply -f {filepath}")
