import binascii
import os

import elasticsearch
from datetime import datetime
from fastapi import Request, Response, Header

from core.auth.models import LoggedUser
from core.auth.utils import get_current_user, verify_logged_in, verify_existing_users, verify_existing_folder, \
    add_newDocId_to_mongo_folder, remove_docId_from_mongo_folder, verify_patch_content

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


@router.get(
    "",
    # response_model=List[Document],
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found documents list'},
        400: {'description': 'Sent wrong query param'}
    }
)
def get_documents(page: int = 1, title: Union[str, None] = "", author: Union[str, None] = "", description: Union[str, None] = "", content: Union[str, None] = "", current_user: LoggedUser = Depends(get_current_user)):
    wildContent = "*" + content + "*"
    wildTitle = "*" + title + "*"
    wildDescription = "*" + description + "*"
    if page < 1:
        raise HTTPException(status_code=400, detail='Page number must be a positive integer')
    if current_user is None:
        print("not logged in")
        username = ""
    else:
        print("logged in, {}".format(current_user.username))
        username = current_user.username
    resp = elastic.search(index="documents", body={
        "from": (page-1)*10,
        "size": 10,
        "query": {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "should": [
                                {
                                    "match": {"createdBy": username}
                                },
                                {
                                    "match": {"writers": username}
                                },
                                {
                                    "match": {"readers": username}
                                },
                                {
                                    "match": {"allCanRead": True}
                                },
                                {
                                    "match": {"allCanWrite": True}
                                }
                            ],
                            "minimum_should_match": 1
                        }
                    }
                ],
          "should": [
            { "fuzzy": {"title": title}},
            { "fuzzy": {"createdBy": author}},
            { "fuzzy": {"description": description}},
            { "wildcard": {"title": {"value": wildTitle}}},
            { "wildcard": {"description": {"value": wildDescription}}},
            { "wildcard" : {"content": {"value": wildContent}}}
          ]
        }
    }})
    # print(resp)
    return resp["hits"]["hits"]

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {'description': 'Document successfully created'},
        401: {'description': 'User must be logged in'},
        406: {'description': 'User does not exist'},
        407: {'description': 'Wrong Folder Id Format'},
        403: {'description': 'User has no access to this folder'}
    }
)
def create_document(doc: NewDocument, request: Request, response: Response, current_user: LoggedUser = Depends(get_current_user)):
    verify_logged_in(current_user)
    verify_existing_users(doc.writers, doc.readers)

    if doc.parentFolder == "":
        a=0 #nothing
    elif len(doc.parentFolder) != 24:
        raise HTTPException(status_code=407, detail="Wrong Folder Id Format")
    else:
        verify_existing_folder(doc.parentFolder, current_user.id)

    new_doc_id = binascii.b2a_hex(os.urandom(12)).decode('utf-8')
    validId = False
    while not validId:
        try:
            elastic.get(index="documents", id=new_doc_id)
        except elasticsearch.NotFoundError:
            validId = True
        else:
            new_doc_id = binascii.b2a_hex(os.urandom(12)).decode('utf-8')

    document = {
        'createdBy': current_user.username,
        'createdOn': datetime.now(),
        'lastEditedBy': current_user.username,
        'lastEdited': datetime.now(),
        'readers': doc.readers,
        'writers': doc.writers,
        'allCanRead': doc.allCanRead,
        'allCanWrite': doc.allCanWrite,
        'title': doc.title,
        'description': doc.description,
        'content': doc.content,
        'parentFolder': doc.parentFolder
    }
    resp = elastic.index(index="documents", id=new_doc_id, document=document)
    add_newDocId_to_mongo_folder(new_doc_id, doc.parentFolder)
    response.headers.append("Location", request.url._url + "/" + resp['_id'])
    return {}


@router.get(
    "/{id}",
    #response_model=Document,
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found document'},
        404: {'description': 'Document not found for id sent'},
        403: {'description': 'User has no access to this document'}
    }
)
async def get_document(id: str, current_user: LoggedUser = Depends(get_current_user)):
    try:
        elastic_doc = elastic.get(index="documents", id=id)
    except elasticsearch.NotFoundError:
        raise HTTPException(status_code=404, detail="Document id not found")

    if elastic_doc["_source"]["allCanRead"] is True or elastic_doc["_source"]["allCanWrite"] is True:
        return elastic_doc["_source"]
    else: #doc is not open to read
        if current_user is None:
            raise HTTPException(status_code=403, detail="User has no access to this document")
        else:
            if current_user.username in elastic_doc["_source"]["createdBy"] or current_user.username in elastic_doc["_source"]["readers"] or current_user.username in elastic_doc["_source"]["writers"]:
                return elastic_doc["_source"]
            else:
                raise HTTPException(status_code=403, detail="User has no access to this document")


@router.patch(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Modified document'},
        404: {'description': 'Document not found'},
        403: {'description': 'User has no access to this document'},
        405: {'description': 'Wrong Patch format'}
    }
)
async def modify_document(id: str, doc: UpdateDocument, request: Request, response: Response, current_user: LoggedUser = Depends(get_current_user)):
    verify_logged_in(current_user)
    try:
        elastic_doc = elastic.get(index="documents", id=id)
    except elasticsearch.NotFoundError:
        raise HTTPException(status_code=404, detail="Document id not found")

    if current_user.username not in elastic_doc["_source"]["writers"] and current_user.username not in elastic_doc["_source"]["createdBy"]:
        raise HTTPException(status_code=403, detail="User has no access to this document")

    verify_existing_users(doc.writers, doc.readers)

    body_request = await request.json()
    verify_patch_content(body_request)


    newDoc = {
        'lastEditedBy': current_user.username,
        'lastEdited': datetime.now(),
        "readers": elastic_doc["_source"]["readers"] if doc.readers is None else doc.readers,
        "writers": elastic_doc["_source"]["writers"] if doc.writers is None else doc.writers,
        "allCanRead": elastic_doc["_source"]["allCanRead"] if doc.allCanRead is None else doc.allCanRead,
        "allCanWrite": elastic_doc["_source"]["allCanWrite"] if doc.allCanWrite is None else doc.allCanWrite,
        "title": elastic_doc["_source"]["title"] if doc.title is None else doc.title,
        "description": elastic_doc["_source"]["description"] if doc.description is None else doc.description,
        "content": elastic_doc["_source"]["content"] if doc.content is None else doc.content,
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
    verify_logged_in(current_user)
    try:
        doc = elastic.get(index="documents", id=id)
    except elasticsearch.NotFoundError:
        raise HTTPException(status_code=404, detail="Document id not found")
    parentFolderId = doc["_source"]["parentFolder"]
    print("parent:{}".format(parentFolderId))

    if current_user.username == doc["_source"]["createdBy"]:
        resp = elastic.delete(index="documents", id=id)
    else:
        raise HTTPException(status_code=403, detail="User has no permission to delete this document")

    if parentFolderId != "":
        remove_docId_from_mongo_folder(doc["_id"], parentFolderId)
    return {}
