import logging
import os

import pymongo as pymongo

mongo_ip = os.getenv("MONGO_IP", "#ip")
mongo_port = os.getenv("MONGO_PORT", "#port")
myclient = pymongo.MongoClient(mongo_ip + ":" + mongo_port)
mydb = myclient["applications"]
mycol = mydb["rules"]
logging.getLogger().setLevel(logging.INFO)


def insert(record):
    x = mycol.insert_one(record)
    logging.info(x)
