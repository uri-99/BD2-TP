from typing import Optional

from pydantic import HttpUrl

from .. import *


class NewUser(BaseModel):
    username: str
    mail: str
    password: str


class User(BaseModel):
    self: str
    id: str
    username: str
    mail: str
    notes: List[str]
    folders: List[str]


class NewDocument(BaseModel):
    title: str
    description: str
    content: List[str]
    parentFolder: str
    editors: List[str]
    readers: List[str]


class UpdateDocument(BaseModel):
    editors: List[str]
    readers: List[str]
    title: str
    description: str
    content: List[str]


class Document(BaseModel):
    createdBy: str
    createdOn: str            # Deberia ser una fecha
    lastEditedBy: str
    lastEdited: str         # Deberia ser una fecha
    editors: List[str]
    readers: List[str]
    title: str
    description: str
    content: List[str]


class Folder(BaseModel):
    self: str
    id: str
    content: List[str]
    createdBy: str
    createdOn: str            # Deberia ser una fecha
    lastEditedBy: str
    lastEdited: str         # Deberia ser una fecha
    editors: List[str]
    title: str
    description: str


class UpdateFolder(BaseModel):
    editors: List[str]
    title: str
    description: str
    content: List[str]
    public: bool



class NewFolder(BaseModel):
    title: str
    description: str
    content: Optional[List[str]]
    public: Optional[bool]
