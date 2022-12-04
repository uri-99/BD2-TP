import pymongo
import os
from dotenv import load_dotenv
from core.settings import SingletonSettings

load_dotenv(SingletonSettings.get_instance().Config.env_file)


class MongoManager:
    __instance = None

    @staticmethod
    def get_instance():
        if MongoManager.__instance is None:
            MongoManager()
        return MongoManager.__instance

    def __init__(self):
        if MongoManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            MongoManager.__instance = pymongo.MongoClient(os.environ.get(SingletonSettings.get_instance().mongo_pass))
