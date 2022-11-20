from typing import List
from pydantic import BaseModel


class NewUser(BaseModel):
    username: str
    mail: str
    password: str


class User(BaseModel):
    _id: str
    username: str
    mail: str
    notes: List[str]
    favourites: List[str]


class NewDocument(BaseModel):
    createdBy: str
    title: str
    description: str
    content: List[str]
    public: bool


class Document(BaseModel):
    _id: str
    createdBy: str
    created: str            # Deberia ser una fecha
    lastEditedBy: str
    lastEdited: str         # Deberia ser una fecha
    editors: List[str]
    title: str
    description: str
    content: List[str]
    public: bool
