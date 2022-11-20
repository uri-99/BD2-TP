# Usuario 1: 6373e8c9ea6af1dc84089d97
# Usuario 2: 6373e902a5e607af97b4b1fb
# Nota de usuario 1: 6373eee1d9c1f8cd2703e2f0

from typing import Union, List
from fastapi import FastAPI, HTTPException, Response, status
from models import NewUser, User, NewDocument, Document

import binascii
import os

description = """
NotNotion API lets you manage user and documents data of the app.
Authorization is managed via JWT tokens on each request

## Requests

You can **read and create users and documents**, while also being able to **modify** the latter ones.
"""

tags_metadata = [
    {
        'name': 'users',
        'description': 'Operations with users'
    },
    {
        'name': 'documents',
        'description': 'Managing of documents'
    }
]

app = FastAPI(
    title="NotNotion",
    description=description,
    version="0.0.1",
    openapi_tags=tags_metadata
)


users = {
    '6373e8c9ea6af1dc84089d97': {
        'id': '6373e8c9ea6af1dc84089d97',
        'username': "user1",
        'mail': "user1@gmail.com",
        'notes': [
            "6373eee1d9c1f8cd2703e2f0"
        ],
        'favourites': [

        ]
    },
    '6373e902a5e607af97b4b1fb': {
        'id': '6373e902a5e607af97b4b1fb',
        'username': "user2",
        'mail': "user2@gmail.com",
        'notes': [
            '6373f2bf27a4e3b55da2cc3c'
        ],
        'favourites': [
            '6373eee1d9c1f8cd2703e2f0'
        ]
    }
}

documents = {
    '6373eee1d9c1f8cd2703e2f0': {
        'id': '6373eee1d9c1f8cd2703e2f0',
        "createdBy": "6373e8c9ea6af1dc84089d97",
        "created": 'ISODate("2016-05-18T16:00:00Z")',
        "lastEditedBy": "6373e902a5e607af97b4b1fb",
        "lastEdited": 'ISODate("2016-06-10T16:30:05Z")',
        "editors": ["6373e8c9ea6af1dc84089d97", "6373e902a5e607af97b4b1fb"],
        "title": "Persistencia poliglota",
        "description": "Cosas a tener en cuenta",
        "content": ["## Introducción", "### Concepto", "La persistencia poliglota consiste en ..."],
        "public": True
    },
    '6373f2bf27a4e3b55da2cc3c': {
        'id': '6373f2bf27a4e3b55da2cc3c',
        "createdBy": "6373e902a5e607af97b4b1fb",
        "created": 'ISODate("2016-05-18T16:00:00Z")',
        "lastEditedBy": "6373e902a5e607af97b4b1fb",
        "lastEdited": 'ISODate("2016-05-18T16:00:00Z")',
        "editors": ["6373e902a5e607af97b4b1fb"],
        "title": "Por qué usar Elastic Search para búsqueda",
        "description": "Nota sobre ES y sus múltiples beneficios",
        "content": ["## Abstract", "Elastic Search es una herramienta muy usada hoy en dia..."],
        "public": True
    }
}


@app.get(
    "/users",
    response_model=List[User],
    responses={
        200: {'description': 'Found users list'},
        400: {'description': 'Sent wrong query param'}
    },
    tags=['users']
)
def get_users(limit: int = 10, page: int = 1, username: Union[str, None] = None):
    if limit < 0:
        raise HTTPException(status_code=400, detail='Page size must be higher than zero')
    if page < 1:
        raise HTTPException(status_code=400, detail='Page number must be a positive integer')
    # vvv Dummy code vvv
    user_list = list(users.values())
    if username is not None:
        user_list = list(filter(lambda user: user['username'] == username, user_list))
    return user_list[(page - 1) * limit: page * limit]


@app.post(
    "/users",
    response_model=User,
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


@app.get(
    "/users/{id}",
    response_model=User,
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


@app.get(
    "/documents",
    response_model=List[Document],
    responses={
        200: {'description': 'Found documents list'},
        400: {'description': 'Sent wrong query param'}
    },
    tags=['documents']
)
def get_documents(limit: int = 10, page: int = 1, title: Union[str, None] = None, author: Union[str, None] = None):
    if limit < 0:
        raise HTTPException(status_code=400, detail='Page size must be higher than zero')
    if page < 1:
        raise HTTPException(status_code=400, detail='Page number must be a positive integer')
    # vvv Dummy code vvv
    doc_list = list(documents.values())
    if title is not None:
        doc_list = list(filter(lambda doc: doc['title'] == title, doc_list))
    if author is not None:
        doc_list = list(filter(lambda doc: doc['owner'] == author, doc_list))
    return doc_list[(page - 1) * limit: page * limit]


@app.post(
    "/documents",
    response_model=Document,
    responses={
        201: {'description': 'Document successfully created'}
    },
    tags=['documents']
)
def create_document(doc: NewDocument):
    if doc.createdBy not in users:
        raise HTTPException(status_code=400, detail='Creator user sent does not exist')
    new_doc_id = binascii.b2a_hex(os.urandom(12)).decode('utf-8')
    documents[new_doc_id] = {
        '_id': new_doc_id,
        'createdBy': doc.createdBy,
        'created': 'ISODate("2022-11-15T19:51:36Z")',
        'lastEditedBy': '',
        'lastEdited': '',
        'editors': [
            doc.createdBy
        ],
        'title': doc.title,
        'description': doc.description,
        'content': doc.content,
        'public': doc.public
    }
    return documents[new_doc_id]


@app.get(
    "/documents/{id}",
    response_model=Document,
    responses={
        200: {'description': 'Found document'},
        404: {'description': 'Document not found for id sent'},
    },
    tags=['documents']
)
def get_document(id):
    if id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    return documents[id]


@app.put(
    "/documents/{id}",
    tags=['documents']
)
def modify_document():
    return {"Hello": "World"}


@app.delete(
    "/documents/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['documents']
)
def delete_document():
    return {"Hello": "World"}
