import pymongo
from dotenv import dotenv_values
from elasticsearch import Elasticsearch

from core.settings import SingletonSettings


secrets = dotenv_values(SingletonSettings.get_instance().Config.env_file)

mongo_pass = secrets['MONGODB_PASS']
elastic_cloud_id = secrets['ELASTIC_CLASS_ID']
elastic_user = secrets['ELASTIC_USER']
elastic_password = secrets['ELASTIC_PASSWORD']


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
            MongoManager.__instance = pymongo.MongoClient(mongo_pass)


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
                cloud_id=elastic_cloud_id,
                basic_auth=(elastic_user, elastic_password)
            )
            # print(client.info())
            ElasticManager.__instance = client
