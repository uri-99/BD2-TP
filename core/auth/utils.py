import os
from datetime import timedelta, datetime

from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, Request
from core.helpers.db_client import MongoManager
from core.auth.models import *
from jose import jwt, JWTError

from core.models.database import DBDocument, DBFolder
from core.settings import SingletonSettings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

load_dotenv(SingletonSettings.get_instance().Config.env_file)
jwt_key = os.getenv('JWT_KEY')

users_db = MongoManager.get_instance().BD2.User
folders_db = MongoManager.get_instance().BD2.Folder


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_key, algorithm=ALGORITHM)
    return encoded_jwt


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
        raise HTTPException(status_code=401, detail="User must be logged in to perform this action")


def verify_existing_users(writers, readers):
    if writers is not None:
        for writer in writers:
            if users_db.find_one({'username': writer}) is None:
                raise HTTPException(status_code=404, detail="User '{}' does not exist".format(writer))
    if readers is not None:
        for reader in readers:
            if users_db.find_one({'username': reader}) is None:
                raise HTTPException(status_code=404, detail="User '{}' does not exist".format(reader))


def verify_existing_folder(folderId, username):
    try:
        folder = folders_db.find_one({'_id': ObjectId(folderId)})
        if folder is None:
            raise HTTPException(status_code=404, detail="Folder '{}' does not exist".format(folderId))
        if folder["createdBy"] != username:
            if folder["allCanWrite"] is False:
                if username not in folder["writers"]:
                    raise HTTPException(status_code=403, detail="User has no access to this folder")
    except InvalidId:
        raise HTTPException(status_code=400, detail="Wrong Folder Id Format")


def add_newDocId_to_mongo_folder(newDocId, parentFolderId):
    if parentFolderId != "":
        folder = folders_db.find_one({'_id': ObjectId(parentFolderId)})
        if folder is None:
            raise HTTPException(status_code=404, detail="Folder '{}' does not exist".format(parentFolderId))

        newContent = folder["content"]
        newContent.append(str(newDocId))
        folders_db.update_one({'_id': ObjectId(parentFolderId)}, {"$set": {"content": newContent}})


def remove_docId_from_mongo_folder(docId, parentFolderId):
    folder = folders_db.find_one({'_id': ObjectId(parentFolderId)})
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder '{}' does not exist".format(parentFolderId))

    newContent = folder["content"]
    try:
        newContent.remove(docId)
    except:
        raise HTTPException(status_code=500, detail="Server error, folder doesn't contain document Id. This is a deprecated version folder")
    folders_db.update_one({'_id': ObjectId(parentFolderId)}, {"$set": {"content": newContent}})


def user_has_permission(obj: Union[DBDocument, DBFolder], current_user: LoggedUser, request_method: str):
    """Checks if the user has permission to access the requested Document or Folder

        Parameters
        ----------
        obj : DBDocument, DBFolder
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
    if user_is_not_none and obj.createdBy == current_user.username:                                               # User is owner
        return True
    if user_is_not_none and \
            (obj.allCanWrite is True or (len(obj.writers) > 0 and obj.writers[0] == current_user.username)):      # Object is editable by everyone/someone
        return request_method.lower() != 'delete'
    if obj.allCanRead is True or \
            (user_is_not_none and (len(obj.readers) > 0 and obj.readers[0] == current_user.username)):            # Object is readable by everyone/someone
        return request_method.lower() == 'get'
    return False

def verify_patch_content(body_request):
    try:
        del body_request['readers']
    except:
        a=0 #nothing
    try:
        del body_request['writers']
    except:
        a=0 #nothing
    try:
        del body_request['allCanRead']
    except:
        a=0 #nothing
    try:
        del body_request['allCanWrite']
    except:
        a=0 #nothing
    try:
        del body_request['description']
    except:
        a=0 #nothing
    try:
        del body_request['content']
    except:
        a=0 #nothing
    try:
        del body_request['title']
    except:
        a=0 #nothing
    try:
        del body_request['parentFolder']
    except:
        a=0 #nothing

    if len(body_request) != 0:
        raise HTTPException(status_code=405, detail="Wrong Patch format, {} unacceptable".format(body_request))
