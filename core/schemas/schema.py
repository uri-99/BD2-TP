from bson import ObjectId

from .. import *


class NewUser(BaseModel):
    username: str
    mail: str
    password: str


class User(BaseModel):
    id: str
    username: str
    mail: str
    notes: List[str]
    folders: List[str]
    favorites: List[str]


class NewDocument(BaseModel):
    title: str
    description: str
    content: List[str]
    createdBy: str
    parentFolder: str
    editors: List[str]
    public: bool

class UpdateDocument(BaseModel):
    lastEditedBy: str
    editors: List[str]
    title: str
    description: str
    content: List[str]
    public: bool


class Document(BaseModel):
    createdBy: str
    created: str            # Deberia ser una fecha
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
