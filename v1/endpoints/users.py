import json

import bson.errors
from bson import json_util
from fastapi import Request, Response

from core.helpers.converters import oidlist_to_str
from . import *
from core.db_client import MongoManager

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "User not found"}}
)

tag_metadata = {
        'name': 'users',
        'description': 'Operations with users'
}

users_db = MongoManager.get_instance().BD2.User

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
async def get_users(limit: int = 10, page: int = 1, username: Union[str, None] = None):
    if limit < 0:
        raise HTTPException(status_code=400, detail='Page size must be higher than zero')
    if page < 1:
        raise HTTPException(status_code=400, detail='Page number must be a positive integer')

    username_filter = {}
    if username is not None:
        username_filter = {"username": username}
    result = users_db.find(username_filter, {"password": 0}).skip((page - 1) * limit).limit(limit)
    users = list()
    for user in result:
        users.append({
            'id': str(user['_id']),
            'username': user['username'],
            'mail': user['mail'],
            'notes': oidlist_to_str(user['notes']),
            'favorites': oidlist_to_str(user['favorites']),
            'folders': oidlist_to_str(user['folders'])
        })
    return json.loads(json_util.dumps(users))


# TODO: Error checking when post fails
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {'description': 'User successfully created'},
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
    response.headers.append("Location", request.url._url + "/" + str(result.inserted_id))
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
def get_user(id: str):
    try:
        user_id = ObjectId(id)
    except bson.errors.InvalidId:
        raise HTTPException(status_code=404, detail="User not found")

    result = users_db.find_one({"_id": user_id}, {"password": 0})
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return json.loads(json_util.dumps({
        'id': str(result['_id']),
        'username': result['username'],
        'mail': result['mail'],
        'notes': oidlist_to_str(result['notes']),
        'favorites': oidlist_to_str(result['favorites']),
        'folders': oidlist_to_str(result['folders'])
    }))


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Deleted user'},
        404: {'description': 'User not found for id sent'},
    },
    tags=['users']
)
def delete_user(id: str):
    try:
        user_id = ObjectId(id)
    except bson.errors.InvalidId:
        raise HTTPException(status_code=404, detail="User not found")

    result = users_db.delete_one({"_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
