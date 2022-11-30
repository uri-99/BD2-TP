from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Los Notilokos"
    mongo_pass: str
    page_size: int = 10
