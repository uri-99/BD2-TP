from typing import Optional

from .. import *


class NewUser(BaseModel):
    username: str
    password: str


class User(BaseModel):
    self: str
    id: str
    username: str
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
    parentFolder: str


class UpdateDocument(BaseModel):
    readers: Optional[List[str]]
    writers: Optional[List[str]]
    allCanRead: Optional[bool]
    allCanWrite: Optional[bool]
    title: Optional[str]
    description: Optional[str]
    content: Optional[List[str]]


class Document(BaseModel):
    self: str
    id: str
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
    title: Optional[str]
    description: Optional[str]
    content: Optional[List[str]]
    writers: Optional[List[str]]
    readers: Optional[List[str]]
    allCanWrite: Optional[bool]
    allCanRead: Optional[bool]


class NewFolder(BaseModel):
    title: str
    description: str
    content: Optional[List[str]]
    writers: Optional[List[str]]
    readers: Optional[List[str]]
    allCanWrite: Optional[bool] = False
    allCanRead: Optional[bool] = False
