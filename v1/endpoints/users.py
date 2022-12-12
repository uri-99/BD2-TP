from typing import Union

from bson import ObjectId
from fastapi import APIRouter, status, Request, Response, HTTPException, Depends

from core.auth.models import LoggedUser
from core.auth.utils import get_current_user, get_password_hash, verify_logged_in
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
folders_db = MongoManager.get_instance().BD2.Folder

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
    if page < 1:
        raise HTTPException(status_code=400, detail='Page number must be a positive integer')

    username_filter = {}
    if username is not None:
        username_filter = {"username": username}
    result = users_db.find(username_filter, {"password": 0}).skip((page - 1) * users_page_size).limit(users_page_size)
    user_count = users_db.count_documents({})
    users = list()
    for user in result:
        users.append(User(
            self=str(request.url.remove_query_params(["page", "username"])) + "/" + str(user['_id']),
            id=str(user['_id']),
            username=user['username'],
            notes=user['notes'],
            folders=user['folders']
        ))
    response.headers.append("first", str(request.url.remove_query_params(["page", "username"])) + "?page=1")
    response.headers.append("last", str(request.url.remove_query_params(["page", "username"]))
                            + "?page=" + str(int((user_count - 1) / users_page_size) + 1))
    return users


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
            'password': get_password_hash(new_user.password),
            'notes': [],
            'favorites': [],
            'folders': []
    })
    response.headers.append("Location", str(request.url) + "/" + str(result.inserted_id))
    return {}


@router.get(
    "/{username}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found user'},
        404: {'description': 'User not found for id sent'},
    },
    tags=['users']
)
def get_user(username: str, request: Request):
    result = users_db.find_one({"username": username}, {"password": 0})
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return User(
        self=str(request.url),
        id=str(result['_id']),
        username=result['username'],
        notes=result['notes'],
        folders=result['folders']
    )


@router.delete(
    "/{username}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Deleted user'},
        403: {'description': 'Tried to delete other user account'}
    },
    tags=['users']
)
def delete_user(username: str, current_user: LoggedUser = Depends(get_current_user)):
    verify_logged_in(current_user)
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="Can't delete other users accounts")
    db_user = users_db.find_one({"username": username}, {"password": 0})
    if db_user is None:
        return
    # TODO: Borrar notas en cascada en elastic
    folders_db.delete_many({'_id': {'$in': db_user['folders']}})
    users_db.delete_one({"_id": db_user['_id']})
