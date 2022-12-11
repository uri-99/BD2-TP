import os
from datetime import timedelta, datetime

from bson import ObjectId
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, Request
from core.helpers.db_client import MongoManager
from core.auth.models import *
from jose import jwt, JWTError

from core.models.database import DBDocument, DBFolder
from core.settings import SingletonSettings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

load_dotenv(SingletonSettings.get_instance().Config.env_file)
jwt_key = os.getenv('JWT_KEY')


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_key, algorithm=ALGORITHM)
    return encoded_jwt


# def not_logged_catcher(): #this does not work
#     try:
#         ret = Depends(SingletonPasswordBearer.get_instance())
#         print("\n\nin")
#     except HTTP_401_UNAUTHORIZED:
#         print("\n\ncatched")
#         return None
#     else:
#         return ret

# async def get_current_user(token: str = not_logged_catcher()):
async def get_current_user(token: str = Depends(SingletonPasswordBearer.get_instance())):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        return None
    try:
        payload = jwt.decode(token, jwt_key, algorithms=[ALGORITHM])
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


def verify_logged_in(current_user):
    if current_user is None:
        raise HTTPException(status_code=401, detail="User must be logged in")


def user_has_permission(obj: Union[DBDocument, DBFolder], current_user: LoggedUser, request_method: str):
    """Checks if the user has permission to access the requested Document or Folder

        Parameters
        ----------
        obj : Document, Folder
            The document or folder to check access to
        current_user: LoggedUser
            User making the request (or None if no user present)
        request : Request
            HTTP Request made

        Returns
        -------
        bool
            A boolean that tells whether the user has access to the object or not
        """
    user_is_not_none = current_user is not None
    if user_is_not_none and str(obj.createdBy) == current_user.id:                       # User is owner
        return True
    if user_is_not_none and \
            (obj.allCanWrite is True or str(obj.writers[0]) == current_user.id):                                  # Object is editable by everyone/someone
        return request_method != 'DELETE'
    if obj.allCanRead is True or \
            (user_is_not_none and str(obj.readers[0]) == current_user.id):                 # Object is readable by everyone/someone
        return request_method == 'GET'
    return False
