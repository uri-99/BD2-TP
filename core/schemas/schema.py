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
    createdBy: str
    parentFolder: str
    editors: List[str]
    public: bool


class Document(BaseModel):
    createdBy: str
    createdOn: str            # Deberia ser una fecha
    lastEditedBy: str
    lastEdited: str         # Deberia ser una fecha
    editors: List[str]
    title: str
    description: str
    content: List[str]


class Folder(BaseModel):
    content: List[str]
    createdBy: str
    created: str            # Deberia ser una fecha
    lastEditedBy: str
    lastEdited: str         # Deberia ser una fecha
    editors: List[str]
    title: str
    description: str


class NewFolder(BaseModel):
    createdBy: str
    created: str            # Deberia ser una fecha
    lastEditedBy: str
    lastEdited: str         # Deberia ser una fecha
    editors: List[str]
    title: str
    description: str
    content: List[str]
