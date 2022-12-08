from . import *


class User(BaseModel):
    _id: str
    username: str
    mail: str
    notes: List[str]
    favourites: List[str]


class Document(BaseModel):
    _id: str
    createdBy: str
    created: str            # Deberia ser una fecha
    lastEditedBy: str
    lastEdited: str         # Deberia ser una fecha
    title: str
    description: str
    content: List[str]
    writers: List[str]
    readers: List[str]
    allCanWrite: bool
    allCanRead: bool


class Folder(BaseModel):
    _id: str
    createdBy: str
    created: str  # Deberia ser una fecha
    lastEditedBy: str
    lastEdited: str  # Deberia ser una fecha
    title: str
    description: str
    content: List[str]
    writers: List[str]
    readers: List[str]
    allCanWrite: bool
    allCanRead: bool
