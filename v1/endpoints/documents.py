import binascii
import os

import elasticsearch
from datetime import datetime
from fastapi import Request, Response, Header

from core.auth.models import LoggedUser
from core.auth.utils import get_current_user

from . import *
from core.helpers.db_client import ElasticManager
elastic = ElasticManager.get_instance()


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Document not found"}}
)

tag_metadata = {
        'name': 'documents',
        'description': 'Managing of documents'
}

documents = {
    '6373eee1d9c1f8cd2703e2f0': {
        'id': '6373eee1d9c1f8cd2703e2f0',
        "createdBy": "6373e8c9ea6af1dc84089d97",
        "created": 'ISODate("2016-05-18T16:00:00Z")',
        "lastEditedBy": "6373e902a5e607af97b4b1fb",
        "lastEdited": 'ISODate("2016-06-10T16:30:05Z")',
        "editors": ["6373e8c9ea6af1dc84089d97", "6373e902a5e607af97b4b1fb"],
        "title": "Persistencia poliglota",
        "description": "Cosas a tener en cuenta",
        "content": ["## Introducción", "### Concepto", "La persistencia poliglota consiste en ..."],
        "public": True
    },
    '6373f2bf27a4e3b55da2cc3c': {
        'id': '6373f2bf27a4e3b55da2cc3c',
        "createdBy": "6373e902a5e607af97b4b1fb",
        "created": 'ISODate("2016-05-18T16:00:00Z")',
        "lastEditedBy": "6373e902a5e607af97b4b1fb",
        "lastEdited": 'ISODate("2016-05-18T16:00:00Z")',
        "editors": ["6373e902a5e607af97b4b1fb"],
        "title": "Por qué usar Elastic Search para búsqueda",
        "description": "Nota sobre ES y sus múltiples beneficios",
        "content": ["## Abstract", "Elastic Search es una herramienta muy usada hoy en dia..."],
        "public": True
    }
}


@router.get(
    "",
    # response_model=List[Document],
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found documents list'},
        400: {'description': 'Sent wrong query param'}
    }
)
def get_documents(limit: int = 10, page: int = 1, title: Union[str, None] = "", author: Union[str, None] = "", description: Union[str, None] = "", content: Union[str, None] = ""):
    wildContent = "*" + content + "*"
    wildTitle = "*" + title + "*"
    wildDescription = "*" + description + "*"
    if limit < 0:
        raise HTTPException(status_code=400, detail='Page size must be higher than zero')
    if page < 1:
        raise HTTPException(status_code=400, detail='Page number must be a positive integer')
    # vvv Dummy code vvv
    # doc_list = list(documents.values())
    # if title is not None:
    #     doc_list = list(filter(lambda doc: doc['title'] == title, doc_list))
    # if author is not None:
    #     doc_list = list(filter(lambda doc: doc['owner'] == author, doc_list))
    # return doc_list[(page - 1) * limit: page * limit]
    print(title)
    resp = elastic.search(index="documents", query={"bool": {
      "should": [
        { "fuzzy": {"title": title}},
        { "fuzzy": {"createdBy": author}},
        { "fuzzy": {"description": description}},
        { "wildcard": {"title": {"value": wildTitle}}},
        { "wildcard": {"description": {"value": wildDescription}}},
        { "wildcard" : {"content": {"value": wildContent}}}
      ],
      "filter": [
        {"term": {
          "public": "true"
        }}
      ]
    }})
    print(resp)
    return resp["hits"]["hits"]



@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {'description': 'Document successfully created'}
    }
)
def create_document(doc: NewDocument, request: Request, response: Response, current_user: LoggedUser = Depends(get_current_user)):

    # TODO : catch repeated random
    editors = doc.editors
    if current_user.username not in editors:
        editors.append(current_user.username)

    new_doc_id = binascii.b2a_hex(os.urandom(12)).decode('utf-8')
    document = {
        # '_id': new_doc_id,
        'createdBy': current_user.username,
        'createdOn': datetime.now(),
        'lastEditedBy': current_user.username,
        'lastEdited': datetime.now(),
        'editors': editors,
        'title': doc.title,
        'description': doc.description,
        'content': doc.content,
        'public': doc.public
    }
    resp = elastic.index(index="documents", id=new_doc_id, document=document)
    response.headers.append("Location", request.url._url + "/" + resp['_id'])
    return {}


@router.get(
    "/{id}",
    response_model=Document,
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found document'},
        404: {'description': 'Document not found for id sent'},
    }
)
async def get_document(id: str, request: Request, response: Response, authorization: Union[List[str], None] = Header(default=None)):
    try:
        elastic_doc = elastic.get(index="documents", id=id)
    except elasticsearch.NotFoundError:
        raise HTTPException(status_code=404, detail="Document id not found")

    if "*" in elastic_doc["_source"]["editors"]: #TODO : use new doc format with readers+writers
        return elastic_doc["_source"]
    else: #doc is not open to read
        if authorization is None:
            raise HTTPException(status_code=403, detail="User has no access to this document")
        else:
            token = authorization[0][7:] #remove "Bearer "
            user = await get_current_user(token)
            if user.username not in elastic_doc["_source"]["editors"]: #TODO : use new doc format with readers+writers
                raise HTTPException(status_code=403, detail="User has no access to this document")
            else:
                return elastic_doc["_source"]


@router.put(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Modified document'},
        404: {'description': 'Document not found'},
        403: {'description': 'User has no access to this document'}
    }
)
def modify_document(id: str, doc: UpdateDocument, request: Request, response: Response, current_user: LoggedUser = Depends(get_current_user)):
    try:
        elastic_doc = elastic.get(index="documents", id=id)
    except elasticsearch.NotFoundError:
        raise HTTPException(status_code=404, detail="Document id not found")

    if current_user.username not in elastic_doc["_source"]["editors"]:
        raise HTTPException(status_code=403, detail="User has no access to this document")

    editors = doc.editors
    if elastic_doc["_source"]["createdBy"] not in editors:
        editors.append(elastic_doc["_source"]["createdBy"])

    newDoc = {
        'lastEditedBy': current_user.username,
        'lastEdited': datetime.now(),
        'editors': editors,
        'title': doc.title,
        'description': doc.description,
        'content': doc.content,
        'public': doc.public
    }
    resp = elastic.update(index="documents", id=id, doc=newDoc)
    response.headers.append("Location", request.url._url)
    # print(resp)
    return {}



@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Deleted document'},
        404: {'description': 'Document not found'}
    }
)
def delete_document(id: str, current_user: LoggedUser = Depends(get_current_user)):
    try:
        doc = elastic.get(index="documents", id=id)
    except elasticsearch.NotFoundError:
        raise HTTPException(status_code=404, detail="Document id not found")

    print(doc["_source"]["editors"])
    print(current_user.username)
    if current_user.username == doc["_source"]["createdBy"]: #TODO check
        resp = elastic.delete(index="documents", id=id)
        #TODO : else reply no auth
    return doc
