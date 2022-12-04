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

    elastic_user = "elastic"
    elastic_password = "Z2FQDZpR8flTzHPK4xhCP3s6"
    elastic_class_id = "Elastic_Notilokos:c291dGhhbWVyaWNhLWVhc3QxLmdjcC5lbGFzdGljLWNsb3VkLmNvbTo0NDMkMzg5NTI3YWE0MGMyNGE4N2JjZDdhNzM5MzliZDlmYWYkNzc5MGVjNmYxMmVjNDhmNTk3MDI3YWZiZjcwZWNhNmM="

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
