import uuid

import elasticsearch
from datetime import datetime

from core.auth.models import LoggedUser
from core.auth.utils import get_current_user, verify_logged_in, verify_existing_users, verify_existing_folder, \
    add_newDocId_to_mongo_folder, remove_docId_from_mongo_folder, verify_patch_content

from . import *
from core.helpers.db_client import ElasticManager

elastic = ElasticManager.get_instance()
users_db = MongoManager.get_instance().BD2.User
folders_db = MongoManager.get_instance().BD2.Folder

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
    response_model=List[Document],
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found documents list'},
        400: {'description': 'Sent wrong query param'}
    }
)
def get_documents(request: Request, page: int = 1, title: Union[str, None] = "", author: Union[str, None] = "",
                  description: Union[str, None] = "", content: Union[str, None] = "",
                  current_user: LoggedUser = Depends(get_current_user)):
    wildContent = "*" + content + "*"
    wildTitle = "*" + title + "*"
    wildDescription = "*" + description + "*"
    if page < 1:
        raise HTTPException(status_code=400, detail='Page number must be a positive integer')
    if current_user is None:
        username = ""
    else:
        username = current_user.username
    resp = elastic.search(index="documents", body={
        "from": (page - 1) * 10,
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
                    {"fuzzy": {"title": title}},
                    {"fuzzy": {"createdBy": author}},
                    {"fuzzy": {"description": description}},
                    {"wildcard": {"title": {"value": wildTitle}}},
                    {"wildcard": {"description": {"value": wildDescription}}},
                    {"wildcard": {"content": {"value": wildContent}}}
                ]
            }
        }})
    toRet = list()
    for document in resp["hits"]["hits"]:
        toRet.append(Document(
            self=str(request.url.remove_query_params(["title", "author", "description", "content", "page"])) +
                 "/" + document['_id'],
            id=document['_id'],
            createdBy=document['_source']['createdBy'],
            createdOn=str(document['_source']['createdOn']),
            lastEditedBy=document['_source']['lastEditedBy'],
            lastEdited=str(document['_source']['lastEdited']),
            readers=document['_source']['readers'],
            writers=document['_source']['writers'],
            allCanRead=document['_source']['allCanRead'],
            allCanWrite=document['_source']['allCanWrite'],
            title=document['_source']['title'],
            description=document['_source']['description'],
            content=document['_source']['content'],
            parentFolder=document['_source']['parentFolder']
        ))
    return toRet


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {'description': 'Document successfully created'},
        401: {'description': 'User must be logged in'},
        403: {'description': 'User has no access to this folder'},
        406: {'description': 'User does not exist'},
        407: {'description': 'Wrong Folder Id Format'}
    }
)
def create_document(doc: NewDocument, request: Request, response: Response,
                    current_user: LoggedUser = Depends(get_current_user)):
    verify_logged_in(current_user)
    verify_existing_users(doc.writers, doc.readers)

    verify_existing_folder(doc.parentFolder, current_user.username)

    document = {
        'createdBy': current_user.username,
        'createdOn': datetime.now(),
        'lastEditedBy': current_user.username,
        'lastEdited': datetime.now(),
        'readers': doc.readers if doc.readers is not None else [],
        'writers': doc.writers if doc.writers is not None else [],
        'allCanRead': doc.allCanRead if doc.allCanRead is not None else False,
        'allCanWrite': doc.allCanWrite if doc.allCanWrite is not None else False,
        'title': doc.title,
        'description': doc.description,
        'content': doc.content if doc.content is not None else [],
        'parentFolder': doc.parentFolder if doc.parentFolder is not None else ""
    }
    doc_id = uuid.uuid1()
    resp = elastic.index(index="documents", id=doc_id, document=document)
    add_newDocId_to_mongo_folder(doc_id, doc.parentFolder)
    users_db.update_one({"_id": ObjectId(current_user.id)}, {
        "$addToSet": {
            "notes": resp['_id']
        }
    })
    response.headers.append("Location", str(request.url) + "/" + str(doc_id))
    return {}


@router.get(
    "/{id}",
    response_model=Document,
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found document'},
        403: {'description': 'User has no access to this document'},
        404: {'description': 'Document not found for id sent'}
    }
)
async def get_document(id: str, request: Request, current_user: LoggedUser = Depends(get_current_user)):
    try:
        elastic_doc = elastic.get(index="documents", id=id)
    except elasticsearch.NotFoundError:
        raise HTTPException(status_code=404, detail="Document id not found")

    toRet = Document(
        self=str(request.url),
        id=elastic_doc['_id'],
        createdBy=elastic_doc['_source']['createdBy'],
        createdOn=str(elastic_doc['_source']['createdOn']),
        lastEditedBy=elastic_doc['_source']['lastEditedBy'],
        lastEdited=str(elastic_doc['_source']['lastEdited']),
        readers=elastic_doc['_source']['readers'],
        writers=elastic_doc['_source']['writers'],
        allCanRead=elastic_doc['_source']['allCanRead'],
        allCanWrite=elastic_doc['_source']['allCanWrite'],
        title=elastic_doc['_source']['title'],
        description=elastic_doc['_source']['description'],
        content=elastic_doc['_source']['content'],
        parentFolder=elastic_doc['_source']['parentFolder']
    )

    if elastic_doc["_source"]["allCanRead"] is True or elastic_doc["_source"]["allCanWrite"] is True:
        return toRet
    else:  # doc is not open to read
        if current_user is None:
            raise HTTPException(status_code=403, detail="User has no access to this document")
        else:
            if current_user.username in elastic_doc["_source"]["createdBy"] or current_user.username in \
                    elastic_doc["_source"]["readers"] or current_user.username in elastic_doc["_source"]["writers"]:
                return toRet
            else:
                raise HTTPException(status_code=403, detail="User has no access to this document")


@router.patch(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Modified document'},
        403: {'description': 'User has no access to this document'},
        404: {'description': 'Document not found'},
        405: {'description': 'Wrong Patch format'},
        406: {'description': 'User has no permission to edit writers'}
    }
)
async def modify_document(id: str, doc: UpdateDocument, request: Request,
                          current_user: LoggedUser = Depends(get_current_user)):
    verify_logged_in(current_user)
    try:
        elastic_doc = elastic.get(index="documents", id=id)
    except elasticsearch.NotFoundError:
        raise HTTPException(status_code=404, detail="Document id not found")

    if current_user.username not in elastic_doc["_source"]["writers"] and current_user.username not in \
            elastic_doc["_source"]["createdBy"]:
        raise HTTPException(status_code=403, detail="User has no access to this document")

    verify_existing_users(doc.writers, doc.readers)

    body_request = await request.json()
    verify_patch_content(body_request)

    if current_user.username != elastic_doc["_source"]["createdBy"] and doc.writers is not None:
        raise HTTPException(status_code=406, detail="User has no permission to edit writers")


    if doc.parentFolder is not None and doc.parentFolder != elastic_doc['_source']['parentFolder']:     # Change folders content field on parentFolder change
        folders_db.update_one({"_id": ObjectId(elastic_doc['_source']['parentFolder'])},
                              {"$pull": {"content": elastic_doc['_id']}})
        folders_db.update_one({"_id": ObjectId(doc.parentFolder)},
                              {"$addToSet": {"content": elastic_doc['_id']}})

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
        "parentFolder": elastic_doc["_source"]["parentFolder"] if doc.parentFolder is None else doc.parentFolder,
    }
    elastic.update(index="documents", id=id, doc=newDoc)


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

    if current_user.username == doc["_source"]["createdBy"]:
        resp = elastic.delete(index="documents", id=id)
    else:
        raise HTTPException(status_code=403, detail="User has no permission to delete this document")

    users_db.update_one({"_id": ObjectId(current_user.id)}, {"$pull": {"notes": id}})

    if parentFolderId != "":
        remove_docId_from_mongo_folder(doc["_id"], parentFolderId)
