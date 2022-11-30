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
    editors: List[str]
    title: str
    description: str
    content: List[str]
    public: bool


class Folder(BaseModel):
    _id: str
    createdBy: str
    created: str  # Deberia ser una fecha
    lastEditedBy: str
    lastEdited: str  # Deberia ser una fecha
    editors: List[str]
    title: str
    description: str
    content: List[str]
    public: bool
