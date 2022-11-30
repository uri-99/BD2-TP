from fastapi import FastAPI
from v1.endpoints import users, documents, folders, favorites
from pymongo import MongoClient

description = """
Notilokos API lets you manage user and documents data of the app.
Authorization is managed via JWT tokens on each request

## Requests

You can **read and create users and documents**, while also being able to **modify** the latter ones.
"""


app = FastAPI(
    title="Los Notilokos",
    description=description,
    version="0.0.1"
)


app.include_router(users.router)
app.include_router(documents.router)
app.include_router(folders.router)
app.include_router(favorites.router)

app.openapi_tags = [
    users.tag_metadata,
    documents.tag_metadata,
    folders.tag_metadata,
    favorites.tag_metadata
]


client = MongoClient('mongodb+srv://admin:3ZmSBmNUYaKWfWrb@bd2.rvwdrjj.mongodb.net/test')
BD2 = client.BD2
notes = BD2.File
users = BD2.User
print(notes.find_one())
print(users.find_one())
