from . import *

description = """
Notilokos API lets you manage user and documents data of the app.
Authorization is managed via JWT tokens on each request

## Requests

You can **read and create users and documents**, while also being able to **modify** the latter ones.
"""


class Settings(BaseSettings):
    app_name = "Los Notilokos"
    description = description
    mongo_pass = "MONGODB_PASS"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
