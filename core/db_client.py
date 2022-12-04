import pymongo
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv
from core.settings import Settings

settings = Settings()

load_dotenv(settings.Config.env_file)


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
            MongoManager.__instance = pymongo.MongoClient(os.environ.get(settings.mongo_pass))



class ElasticManager:
    __instance = None

    @staticmethod
    def get_instance():
        if ElasticManager.__instance is None:
            ElasticManager()
        return ElasticManager.__instance

    def __init__(self):
        if ElasticManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            client = Elasticsearch( # Create the client instance
                cloud_id=settings.elastic_class_id,
                basic_auth=(settings.elastic_user, settings.elastic_password)
            )
            # print(client.info())
            ElasticManager.__instance = client
