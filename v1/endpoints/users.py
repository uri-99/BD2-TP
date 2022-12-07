import json
from typing import List, Union

import bson
from bson import json_util, ObjectId
from fastapi import APIRouter, status, Request, Response, HTTPException, Depends

from core.auth.models import LoggedUser
from core.auth.utils import get_current_user
from core.helpers.converters import oidlist_to_str
from core.helpers.db_client import MongoManager
from core.schemas.schema import *

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        401: {'description': 'User must be logged in to perform this action'},
        404: {"description": "User not found"}
    }
)

tag_metadata = {
        'name': 'users',
        'description': 'Operations with users'
}

users_db = MongoManager.get_instance().BD2.User
documents_db = MongoManager.get_instance().BD2.File

users_page_size = 10
document_page_size = 10


@router.get(
    "",
    response_model=List[User],
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found users list'},
        400: {'description': 'Sent wrong query param'}
    },
    tags=['users']
)
async def get_users(request: Request, response: Response,
                    page: int = 1, username: Union[str, None] = None):
    print(request.method)
    if page < 1:
        raise HTTPException(status_code=400, detail='Page number must be a positive integer')

    username_filter = {}
    if username is not None:
        username_filter = {"username": username}
    result = users_db.find(username_filter, {"password": 0}).skip((page - 1) * users_page_size).limit(users_page_size)
    user_count = users_db.count_documents({})
    users = list()
    for user in result:
        users.append({
            'self': str(request.url.remove_query_params(["page", "username"])) + "/" + str(user['_id']),
            'id': str(user['_id']),
            'username': user['username'],
            'mail': user['mail'],
            'notes': oidlist_to_str(user['notes']),
            'folders': oidlist_to_str(user['folders'])
        })
    response.headers.append("first", str(request.url.remove_query_params(["page", "username"])) + "?page=1")
    response.headers.append("last", str(request.url.remove_query_params(["page", "username"]))
                            + "?page=" + str(int((user_count - 1) / users_page_size) + 1))
    return json.loads(json_util.dumps(users))


# TODO: Error checking when post fails
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {'description': 'User created'},
    },
    tags=['users']
)
def create_user(new_user: NewUser, request: Request, response: Response):
    result = users_db.insert_one({
            'username': new_user.username,
            'mail': new_user.mail,
            'password': new_user.password,
            'notes': [],
            'favorites': [],
            'folders': []
    })
    response.headers.append("Location", str(request.url) + "/" + str(result.inserted_id))
    return {}


@router.get(
    "/{id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found user'},
        404: {'description': 'User not found for id sent'},
    },
    tags=['users']
)
def get_user(id: str, request: Request):
    try:
        user_id = ObjectId(id)
    except bson.errors.InvalidId:
        raise HTTPException(status_code=404, detail="User not found")

    result = users_db.find_one({"_id": user_id}, {"password": 0})
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return json.loads(json_util.dumps({
        'self': str(request.url),
        'id': str(result['_id']),
        'username': result['username'],
        'mail': result['mail'],
        'notes': oidlist_to_str(result['notes']),
        'folders': oidlist_to_str(result['folders'])
    }))


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Deleted user'},
        403: {'description': 'Tried to delete other user account'},
        404: {'description': 'User not found for id sent'},
    },
    tags=['users']
)
def delete_user(id: str, current_user: LoggedUser = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="User must be logged in to delete its account")
    if id != current_user.id:
        raise HTTPException(status_code=403, detail="Cant delete other users accounts")
    try:
        user_id = ObjectId(id)
    except bson.errors.InvalidId:
        raise HTTPException(status_code=404, detail="User not found")

    result = users_db.delete_one({"_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")


# TODO: Add filters (author, etc)
@router.get(
    "/{id}/favorites",
    response_model=List[Document],
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found user favorites list'},
        400: {'description': 'Sent wrong query param'},
        403: {'description': 'Tried to access other user favorite list'},
        404: {'description': 'User not found'}
    }
)
def get_favorites(request: Request, response: Response, id: str, page: int = 1,
                  current_user: LoggedUser = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="User must be logged in to get its favorites")
    if id != current_user.id:
        raise HTTPException(status_code=403, detail="Cant access favorites list of other users")
    if page < 1:
        raise HTTPException(status_code=400, detail='Page number must be a positive integer')
    favorites_oidlist = users_db.find_one({"_id": ObjectId(id)}, {"favorites": 1, "_id": 0})['favorites']
    favorite_docs = documents_db.find({"_id": {"$in": favorites_oidlist}})\
        .skip((page - 1) * document_page_size).limit(document_page_size)
    favorites = list()
    for favorite in favorite_docs:
        favorites.append({
            'self': str(request.url.remove_query_params(["page", "username"])) + "/" + str(favorite['_id']),
            'id': str(favorite['_id']),
            'createdBy': str(favorite['createdBy']),
            'lastEditedBy': str(favorite['lastEditedBy']),
            'createdOn': str(favorite['createdOn']),
            'lastEdited': str(favorite['lastEdited']),
            'title': favorite['title'],
            'description': favorite['description'],
            'content': favorite['content'],
            'editors': oidlist_to_str(favorite['editors'])
        })
    response.headers.append("first", str(request.url.remove_query_params(["page"])) + "?page=1")
    response.headers.append("last", str(request.url.remove_query_params(["page"]))
                            + "?page=" + str(int((len(favorites_oidlist) - 1) / document_page_size) + 1))
    return json.loads(json_util.dumps(favorites))


@router.put(
    "/{id}/favorites/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Added document to user favorites'},
        403: {'description': 'Tried to access other user favorite list'},
        404: {'description': 'Document/User not found'}
    }
)
def add_favorite(id: str, doc_id: str, current_user: LoggedUser = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="User must be logged in to add a favorite")
    if id != current_user.id:
        raise HTTPException(status_code=403, detail="Cant add favorites to other user list")
    try:
        if documents_db.find_one({"_id": ObjectId(doc_id)}) is None:
            raise HTTPException(status_code=404, detail="Document not found")
    except bson.errors.InvalidId:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        if users_db.update_one({"_id": ObjectId(id)}, {"$addToSet": {"favorites": doc_id}}).matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
    except bson.errors.InvalidId:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete(
    "/{id}/favorites/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Removed document from user favorites'},
        403: {'description': 'Tried to access other user favorite list'},
        404: {'description': 'Document/User not found'}
    }
)
def remove_favorite(id: str, doc_id: str, current_user: LoggedUser = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="User must be logged in to remove a favorite")
    if id != current_user.id:
        raise HTTPException(status_code=403, detail="Cant remove favorite from other user list")
    try:
        if documents_db.find_one({"_id": ObjectId(doc_id)}) is None:
            raise HTTPException(status_code=404, detail="Document not found")
    except bson.errors.InvalidId:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        if users_db.update_one({"_id": ObjectId(id)}, {"$pull": {"favorites": doc_id}}).matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
    except bson.errors.InvalidId:
        raise HTTPException(status_code=404, detail="User not found")
