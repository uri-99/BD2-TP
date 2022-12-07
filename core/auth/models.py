from typing import Union

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel


class SingletonPasswordBearer:
    __instance = None

    @staticmethod
    def get_instance():
        if SingletonPasswordBearer.__instance is None:
            SingletonPasswordBearer()
        return SingletonPasswordBearer.__instance

    def __init__(self):
        if SingletonPasswordBearer.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            SingletonPasswordBearer.__instance = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


class SingletonCryptContext:
    __instance = None

    @staticmethod
    def get_instance():
        if SingletonCryptContext.__instance is None:
            SingletonCryptContext()
        return SingletonCryptContext.__instance

    def __init__(self):
        if SingletonCryptContext.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            SingletonCryptContext.__instance = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str
    username: Union[str, None] = None


class LoggedUser(BaseModel):
    id: str
    username: str
