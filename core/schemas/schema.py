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
    readers: List[str]
    writers: List[str]
    allCanRead: bool
    allCanWrite: bool


class UpdateDocument(BaseModel):
    readers: List[str]
    writers: List[str]
    allCanRead: bool
    allCanWrite: bool
    title: str
    description: str
    content: List[str]


class Document(BaseModel):
    createdBy: str
    createdOn: str            # Deberia ser una fecha
    lastEditedBy: str
    lastEdited: str         # Deberia ser una fecha
    readers: List[str]
    writers: List[str]
    allCanRead: bool
    allCanWrite: bool
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
    title: str
    description: str
    writers: List[str]
    readers: List[str]
    allCanWrite: bool
    allCanRead: bool


class UpdateFolder(BaseModel):
    title: str
    description: str
    content: List[str]
    writers: List[str]
    readers: List[str]
    allCanWrite: Optional[bool] = False
    allCanRead: Optional[bool] = False


class NewFolder(BaseModel):
    title: str
    description: str
    content: Optional[List[str]]
    writers: Optional[List[str]]
    readers: Optional[List[str]]
    allCanWrite: Optional[bool] = False
    allCanRead: Optional[bool] = False
