# Usuario 1: 6373e8c9ea6af1dc84089d97
# Usuario 2: 6373e902a5e607af97b4b1fb
# Nota de usuario 1: 6373eee1d9c1f8cd2703e2f0

from typing import Union

from fastapi import FastAPI, HTTPException
app = FastAPI()

user_ids = ['6373e8c9ea6af1dc84089d97', '6373e902a5e607af97b4b1fb']
users = {
    '6373e8c9ea6af1dc84089d97': {
        'username': "user1",
        'mail': "user1@gmail.com",
        'notes': [
            "6373eee1d9c1f8cd2703e2f0"
        ],
    },
    '6373e902a5e607af97b4b1fb': {
        'username': "user2",
        'mail': "user2@gmail.com",
        'notes': [

        ]
    }
}

documents_ids = ['6373eee1d9c1f8cd2703e2f0', '6373f2bf27a4e3b55da2cc3c']
documents = {
    '6373eee1d9c1f8cd2703e2f0': {
        "createdBy": "6373e8c9ea6af1dc84089d97",
        "created": "ISODate(\"2016-05-18T16:00:00Z\")",
        "lastEditedBy": "6373e902a5e607af97b4b1fb",
        "lastEdited": "ISODate(\"2016-06-10T16:30:05Z\")",
        "editors": ["6373e8c9ea6af1dc84089d97", "6373e902a5e607af97b4b1fb"],
        "title": "Persistencia poliglota",
        "description": "Cosas a tener en cuenta",
        "content": ["## Introducción", "### Concepto", "La persistencia poliglota consiste en ..."],
        "public": "true"
    },
    '6373f2bf27a4e3b55da2cc3c': {
        "createdBy": "6373e902a5e607af97b4b1fb",
        "created": "ISODate(\"2016-05-18T16:00:00Z\")",
        "lastEditedBy": "6373e902a5e607af97b4b1fb",
        "lastEdited": "ISODate(\"2016-05-18T16:00:00Z\")",
        "editors": ["6373e902a5e607af97b4b1fb"],
        "title": "Por qué usar Elastic Search para búsqueda",
        "description": "Nota sobre ES y sus múltiples beneficios",
        "content": ["## Abstract", "Elastic Search es una herramienta muy usada hoy en dia..."],
        "public": "true"
    }
}

@app.get("/users")
def get_users():
    return {"Hello": "World"}

@app.post("/users")
def create_user():
    return {"Hello": "World"}

@app.get("/users/{id}")
def get_user(id):
    if id in user_ids:
        return {"Hello": "World"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/documents")
def get_documents():
    return {"Hello": "World"}

@app.post("/documents")
def create_document():
    return {"Hello": "World"}

@app.get("/documents/{id}")
def get_document(id):
    if id in documents_ids:
        return documents[id]
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@app.put("/documents/{id}")
def modify_document():
    return {"Hello": "World"}

@app.delete("/documents/{id}")
def delete_document():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
