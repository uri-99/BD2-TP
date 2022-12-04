from datetime import timedelta, datetime
from typing import Union

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from core.helpers.db_client import MongoManager
from core.auth.models import *
from jose import jwt, JWTError

SECRET_KEY = "97396ca67734559070cc916b2da5fde8880350fb8ffd5fcec17e70738212e08c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(SingletonPasswordBearer.get_instance())):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("sub")
        if id is None:
            raise credentials_exception
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(id=id, username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_id(token_data.id)
    if user is None:
        raise credentials_exception
    return LoggedUser(id=str(user['_id']), username=user['username'])


def verify_password(plain_password, hashed_password):
    return SingletonCryptContext.get_instance().verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return SingletonCryptContext.get_instance().hash(password)


def get_user_by_id(id: str):
    return MongoManager.get_instance().BD2.User.find_one({"_id": ObjectId(id)})


def get_user_by_username(username: str):
    return MongoManager.get_instance().BD2.User.find_one({"username": username})


def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user['password']):
        return False
    return user
