import json
from typing import List, Union

import elasticsearch
from bson import ObjectId, json_util
from fastapi import APIRouter, status, Request, Response, Depends, HTTPException

from core.auth.models import LoggedUser
from core.auth.utils import verify_logged_in, get_current_user, user_has_permission
from core.helpers.db_client import MongoManager, ElasticManager
from core.schemas.schema import Document
from core.models.database import DBDocument

users_db = MongoManager.get_instance().BD2.User
elastic = ElasticManager.get_instance()

router = APIRouter(
    prefix="/favorites",
    tags=["favorites"],
    responses={
        401: {"description": "User must be logged in to perform this action"}
    }
)

tag_metadata = {
        'name': 'favorites',
        'description': 'Operations with user favorite documents'
}

document_page_size = 10


@router.get(
    "",
    response_model=List[Document],
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found user favorites list'},
        400: {'description': 'Sent wrong query param'}
    }
)
def get_favorites(request: Request, response: Response, page: int = 1,
                  title: Union[str, None] = "", author: Union[str, None] = "",
                  description: Union[str, None] = "", content: Union[str, None] = "",
                  current_user: LoggedUser = Depends(get_current_user)):
    verify_logged_in(current_user)
    wild_content = "*" + content + "*"
    wild_title = "*" + title + "*"
    wild_description = "*" + description + "*"
    if page < 1:
        raise HTTPException(status_code=400, detail='Page number must be a positive integer')
    favorites_list = users_db.find_one({"_id": ObjectId(current_user.id)}, {"favorites": 1, "_id": 0})['favorites']
    favorite_docs = elastic.search(index="documents", body={
        "from": (page - 1) * document_page_size,
        "size": document_page_size,
        "query": {
            "bool": {
                "must": [
                    {"terms": {"_id": favorites_list}},
                ],
                "should": [
                    {"fuzzy": {"title": title}},
                    {"fuzzy": {"createdBy": author}},
                    {"fuzzy": {"description": description}},
                    {"wildcard": {"title": {"value": wild_title}}},
                    {"wildcard": {"description": {"value": wild_description}}},
                    {"wildcard": {"content": {"value": wild_content}}}
                ]
            }
        }
    })
    favorite_count = favorite_docs['hits']['total']['value']
    favorites = list()
    for favorite in favorite_docs["hits"]["hits"]:
        favorites.append(Document(
            self=str(request.base_url.remove_query_params(["page", "title", "author", "description", "content"])) + "documents/" + str(favorite['_id']),
            id=favorite['_id'],
            createdBy=favorite['_source']['createdBy'],
            lastEditedBy=favorite['_source']['lastEditedBy'],
            createdOn=str(favorite['_source']['createdOn']),
            lastEdited=str(favorite['_source']['lastEdited']),
            title=favorite['_source']['title'],
            description=favorite['_source']['description'],
            content=favorite['_source']['content'],
            readers=favorite['_source']['readers'],
            writers=favorite['_source']['writers'],
            allCanRead=favorite['_source']['allCanRead'],
            allCanWrite=favorite['_source']['allCanWrite']
        ))
    response.headers.append("first", str(request.url.remove_query_params(["page"]).include_query_params(page=1)))
    response.headers.append("last", str(request.url.remove_query_params(["page"]).include_query_params(
        page=str(int((favorite_count - 1) / document_page_size) + 1))))
    return favorites
    # return json.loads(json_util.dumps(favorites))


@router.put(
    "/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Added document to user favorites'},
        403: {'description': 'Tried to add as favorite an unaccessable document'},
        404: {'description': 'Document not found'}
    }
)
def add_favorite(doc_id: str, current_user: LoggedUser = Depends(get_current_user)):
    verify_logged_in(current_user)
    try:
        elastic_doc = elastic.get(index="documents", id=doc_id)
    except elasticsearch.NotFoundError:
        raise HTTPException(status_code=404, detail="Document id not found")
    if not user_has_permission(request_method="GET", current_user=current_user, obj=DBDocument(
        _id=elastic_doc['_id'],
        createdBy=elastic_doc['_source']['createdBy'],
        createdOn=str(elastic_doc['_source']['createdOn']),
        lastEditedBy=elastic_doc['_source']['lastEditedBy'],
        lastEdited=str(elastic_doc['_source']['lastEdited']),  # Deberia ser una fecha
        title=elastic_doc['_source']['title'],
        description=elastic_doc['_source']['description'],
        content=elastic_doc['_source']['content'],
        writers=elastic_doc['_source']['writers'],
        readers=elastic_doc['_source']['readers'],
        allCanWrite=elastic_doc['_source']['allCanWrite'],
        allCanRead=elastic_doc['_source']['allCanRead'],
    )):
        raise HTTPException(status_code=403, detail="User has no permission to access this document")
    users_db.update_one({"_id": ObjectId(current_user.id)}, {"$addToSet": {"favorites": elastic_doc['_id']}})


@router.delete(
    "/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Removed document from user favorites'},
        404: {'description': 'Document not found'}
    }
)
def remove_favorite(doc_id: str, current_user: LoggedUser = Depends(get_current_user)):
    verify_logged_in(current_user)
    try:
        elastic.get(index="documents", id=doc_id)
    except elasticsearch.NotFoundError:
        raise HTTPException(status_code=404, detail="Document id not found")
    # No hace falta chequear si tiene permiso, porque se supone que al ya estar en la lista de favs, si lo tiene
    users_db.update_one({"_id": ObjectId(current_user.id)}, {"$pull": {"favorites": doc_id}})
