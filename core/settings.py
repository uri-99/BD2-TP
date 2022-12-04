from dotenv import load_dotenv

from . import *

description = """
Notilokos API lets you manage user and documents data of the app.
Authorization is managed via JWT tokens on each request

## Requests

You can **read and create users and documents**, while also being able to **modify** the latter ones.
"""


class SingletonSettings:
    __instance = None

    @staticmethod
    def get_instance():
        if SingletonSettings.__instance is None:
            SingletonSettings()
        return SingletonSettings.__instance

    def __init__(self):
        if SingletonSettings.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            SingletonSettings.__instance = Settings()


class Settings(BaseSettings):
    app_name = "Los Notilokos"
    description = description
    mongo_pass = "MONGODB_PASS"
    jwt_key = "JWT_KEY"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
