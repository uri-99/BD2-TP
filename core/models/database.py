from . import *


class User(BaseModel):
    _id: str
    username: str
    notes: List[str]
    favorites: List[str]


class DBDocument(BaseModel):
    _id: str
    createdBy: str
    createdOn: str            # Deberia ser una fecha
    lastEditedBy: str
    lastEdited: str         # Deberia ser una fecha
    title: str
    description: str
    content: List[str]
    writers: List[str]
    readers: List[str]
    allCanWrite: bool
    allCanRead: bool


class DBFolder(BaseModel):
    id: str
    createdBy: str
    createdOn: str  # Deberia ser una fecha
    lastEditedBy: str
    lastEdited: str  # Deberia ser una fecha
    title: str
    description: str
    content: List[str]
    writers: List[str]
    readers: List[str]
    allCanWrite: bool
    allCanRead: bool
