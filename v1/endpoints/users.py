from . import *

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "User not found"}}
)

tag_metadata = {
        'name': 'users',
        'description': 'Operations with users'
}

users = {
    '6373e8c9ea6af1dc84089d97': {
        'id': '6373e8c9ea6af1dc84089d97',
        'username': "user1",
        'mail': "user1@gmail.com",
        'notes': [
            "6373eee1d9c1f8cd2703e2f0"
        ],
        'favorites': [

        ],
        'folders': [

        ]
    },
    '6373e902a5e607af97b4b1fb': {
        'id': '6373e902a5e607af97b4b1fb',
        'username': "user2",
        'mail': "user2@gmail.com",
        'notes': [
            '6373f2bf27a4e3b55da2cc3c'
        ],
        'favorites': [
            '6373eee1d9c1f8cd2703e2f0'
        ],
        'folders': [

        ]
    }
}


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
    # vvv Dummy code vvv
    user_list = list(users.values())
    if username is not None:
        user_list = list(filter(lambda user: user['username'] == username, user_list))
    return user_list[(page - 1) * limit: page * limit]


@router.post(
    "",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {'description': 'User successfully created'},
    },
    tags=['users']
)
def create_user(new_user: NewUser):
    # Mongo generaría el id cuando le mandamos el insert, pero acá lo hacemos automático
    new_user_id = binascii.b2a_hex(os.urandom(12)).decode('utf-8')
    # La contraseña se almacenaría pero no se devuelve
    users[new_user_id] = {
        '_id': new_user_id,
        'username': new_user.username,
        'mail': new_user.mail,
        'notes': [],
        'favourites': []
    }
    return users[new_user_id]


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
def get_user(id: int):
    if id in users:
        return users[id]
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Deleted user'},
        404: {'description': 'User not found for id sent'},
    },
    tags=['users']
)
def get_user(id: int):
    if id in users:
        users[id] = {}
    else:
        raise HTTPException(status_code=404, detail="User not found")
