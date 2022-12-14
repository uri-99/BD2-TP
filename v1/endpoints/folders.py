import datetime

import elasticsearch

from core.auth.models import LoggedUser
from core.auth.utils import get_current_user, user_has_permission, verify_logged_in, verify_existing_users
from core.helpers.converters import get_parsed_folder
from core.helpers.db_client import ElasticManager
from core.models.database import DBFolder
from . import *

router = APIRouter(
    prefix="/folders",
    tags=["folders"],
    responses={
        401: {'description': 'User must be logged in to perform this action'},
        404: {"description": "Folder not found"}
    }
)

tag_metadata = {
        'name': 'folders',
        'description': 'Operations with document folders'
}

elastic = ElasticManager.get_instance()

folders_page_size = 10
folders_db = MongoManager.get_instance().BD2.Folder
users_db = MongoManager.get_instance().BD2.User


@router.get(
    "",
    response_model=List[Folder],
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found documents list'},
        400: {'description': 'Sent wrong query param'}
    }
)
def get_folders(request: Request, response: Response, page: int = 1,
                title: Union[str, None] = None, owner: Union[str, None] = None,
                current_user: LoggedUser = Depends(get_current_user)):
    if page < 1:
        raise HTTPException(status_code=400, detail='Page number must be a positive integer')

    folder_filter = {}
    if title is not None:
        folder_filter["title"] = {'$regex': ".*" + str(title) + ".*"}
    if owner is not None:
        try:
            folder_filter["createdBy"] = {'$regex': ".*" + str(owner) + ".*"}
        except bson.errors.InvalidId:
            return []
    if current_user is None:
        folder_filter["$or"] = [
            {"allCanRead": True},
            {"allCanWrite": True}
        ]
    else:
        folder_filter["$or"] = [
            {"allCanRead": True},
            {"allCanWrite": True},
            {"readers": current_user.username},
            {"writers": current_user.username},
            {"createdBy": current_user.username}
        ]
    result = folders_db.find(folder_filter).skip((page - 1) * folders_page_size).limit(folders_page_size)
    folder_count = folders_db.count_documents({})
    folders = list()
    for folder in result:
        folders.append(Folder(
            self=str(request.url.remove_query_params(["title", "author", "page"])) + "/" + str(folder['_id']),
            id=str(folder['_id']),
            createdBy=folder['createdBy'],
            lastEditedBy=folder['lastEditedBy'],
            createdOn=str(folder['createdOn']),
            lastEdited=str(folder['lastEdited']),
            title=folder['title'],
            description=folder['description'],
            content=folder['content'],
            writers=folder['writers'],
            readers=folder['readers'],
            allCanWrite=folder['allCanWrite'],
            allCanRead=folder['allCanRead'],
        ))
    response.headers.append("first", str(request.url.remove_query_params(["page"]).include_query_params(page=1)))
    response.headers.append("last", str(request.url.remove_query_params(["page"]).include_query_params(
                page=str(int((folder_count - 1) / folders_page_size) + 1))))
    return folders


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {'description': 'Document successfully created'},
        400: {'description': 'Sent wrong param'}
    }
)
def create_folder(doc: NewFolder, request: Request, response: Response,
                  current_user: LoggedUser = Depends(get_current_user)):
    verify_logged_in(current_user)
    are_writers = doc.writers is not None
    are_readers = doc.readers is not None
    are_docs = doc.content is not None
    verify_existing_users(doc.writers, doc.readers)
    if are_docs and docs_exist(doc.content) is False:
        raise HTTPException(status_code=400, detail='Document to include on folder does not exist')
    if are_docs and is_docs_owner(doc.content, current_user) is False:
        raise HTTPException(status_code=400, detail='User is not owner of document included in folder')
    now = datetime.datetime.now()
    result = folders_db.insert_one({
        'createdBy': current_user.username,
        'lastEditedBy': current_user.username,
        'createdOn': now,
        'lastEdited': now,
        'title': doc.title,
        'description': doc.description,
        'content': doc.content if are_docs else [],
        'writers': doc.writers if are_writers else [],
        'allCanWrite': doc.allCanWrite if doc.allCanWrite is not None else False,
        'readers': doc.readers if are_readers else [],
        'allCanRead': doc.allCanRead if doc.allCanRead is not None else False
    })
    users_db.update_one({"_id": ObjectId(current_user.id)}, {
        "$addToSet": {
            "folders": str(result.inserted_id)
        }
    })
    response.headers.append("Location", str(request.url) + "/" + str(result.inserted_id))
    return {}


@router.get(
    "/{id}",
    response_model=Folder,
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found folder'},
        404: {'description': 'Folder not found for id sent'},
    }
)
def get_folder(id: str, request: Request, current_user: LoggedUser = Depends(get_current_user)):
    folder_obj = get_parsed_folder(id, folders_db, None if current_user is None else current_user.username)       # Filtro complejo para que no se devuelva una carpeta con 1000 lectores o escritores
    if folder_obj is None:
        raise HTTPException(status_code=404, detail='Folder not found')
    folder = DBFolder(
        id=str(folder_obj['id']),
        createdBy=folder_obj['createdBy'],
        lastEditedBy=folder_obj['lastEditedBy'],
        createdOn=str(folder_obj['createdOn']),
        lastEdited=str(folder_obj['lastEdited']),
        title=folder_obj['title'],
        description=folder_obj['description'],
        content=folder_obj['content'],
        writers=folder_obj['writers'],
        readers=folder_obj['readers'],
        allCanWrite=folder_obj['allCanWrite'],
        allCanRead=folder_obj['allCanRead'],
    )
    if not user_has_permission(folder, current_user, request.method.title()):
        raise HTTPException(status_code=403, detail='User has no permission to access this folder')
    return Folder(
        self=str(request.url),
        id=str(folder.id),
        createdBy=folder.createdBy,
        lastEditedBy=folder.lastEditedBy,
        createdOn=str(folder.createdOn),
        lastEdited=str(folder.lastEdited),
        title=folder.title,
        description=folder.description,
        content=folder.content,
        writers=folder.writers,
        readers=folder.readers,
        allCanWrite=folder.allCanWrite,
        allCanRead=folder.allCanRead,
    )


@router.patch(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Modified Folder'},
        400: {'description': 'Invalid param sent'},
        403: {'description': 'User has no permission for attempted action'},
        404: {'description': 'Folder not found'}
    }
)
def modify_folder(id: str, update_folder: UpdateFolder,
                  current_user: LoggedUser = Depends(get_current_user)):
    verify_logged_in(current_user)
    folder_obj = get_parsed_folder(id, folders_db, current_user.username)
    if folder_obj is None:
        raise HTTPException(status_code=404, detail="Folder not found")
    folder = DBFolder(
        id=str(folder_obj['id']),
        createdBy=folder_obj['createdBy'],
        lastEditedBy=folder_obj['lastEditedBy'],
        createdOn=str(folder_obj['createdOn']),
        lastEdited=str(folder_obj['lastEdited']),
        title=folder_obj['title'],
        description=folder_obj['description'],
        content=folder_obj['content'],
        writers=folder_obj['writers'],
        readers=folder_obj['readers'],
        allCanWrite=folder_obj['allCanWrite'],
        allCanRead=folder_obj['allCanRead'],
    )
    are_writers = update_folder.writers is not None
    are_readers = update_folder.readers is not None
    are_docs = update_folder.content is not None

    verify_existing_users(update_folder.writers, update_folder.readers)
    if are_docs and is_docs_owner(update_folder.content, current_user) is False:
        raise HTTPException(status_code=400, detail='Document to include on folder does not exist or User is not owner')
    if current_user.username != folder.createdBy:
        if update_folder.writers is not None:
            raise HTTPException(status_code=403, detail="User has no permission to edit writers")
        if update_folder.readers is not None:
            raise HTTPException(status_code=403, detail="User has no permission to edit readers")

    folders_db.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "lastEditedBy": current_user.username,
            "lastEdited": datetime.datetime.now(),
            "title": folder.title if update_folder.title is None else update_folder.title,
            "description": folder.description if update_folder.description is None else update_folder.description,
            "content": folder.content if update_folder.content is None else update_folder.content,
            "writers": folder.writers if update_folder.writers is None else update_folder.writers,
            "readers": folder.readers if update_folder.readers is None else update_folder.readers,
            "allCanWrite": folder.allCanWrite if update_folder.allCanWrite is None else update_folder.allCanWrite,
            "allCanRead": folder.allCanRead if update_folder.allCanRead is None else update_folder.allCanRead,
        }
    })


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Deleted document'},
        403: {'description': 'User has no permission to delete the folder'}
    }
)
def delete_folder(id: str, request: Request, current_user: LoggedUser = Depends(get_current_user)):
    verify_logged_in(current_user)
    folder_obj = get_parsed_folder(id, folders_db, current_user.username)
    if folder_obj is None:
        return
    folder = DBFolder(
        id=folder_obj['id'],
        createdBy=folder_obj['createdBy'],
        createdOn=str(folder_obj['createdOn']),
        lastEditedBy=folder_obj['lastEditedBy'],
        lastEdited=str(folder_obj['lastEdited']),
        title=folder_obj['title'],
        description=folder_obj['description'],
        content=folder_obj['content'],
        writers=folder_obj['writers'],
        readers=folder_obj['readers'],
        allCanRead=folder_obj['allCanRead'],
        allCanWrite=folder_obj['allCanWrite'],
    )
    if user_has_permission(folder, current_user, request.method.title()) is False:
        raise HTTPException(status_code=403, detail="User has no permission to modify this folder")
    if len(folder.content) > 0:
        elastic.delete_by_query(index="documents", query={
            "bool": {
                "must": [
                    {
                        "match": {"createdBy": folder['content']}
                    }
                ]
            }
        })
    folders_db.delete_one({"_id": id})


# TODO: Check for more optimized way of doing it (one request for all)
def users_exist(user_list: List[str]):
    return len(list(users_db.find({'username': {'$in': user_list}}))) == len(user_list)


def docs_exist(doc_list: List[str]):
    try:
        for doc in doc_list:
            elastic.get(index="documents", id=doc)
    except elasticsearch.NotFoundError:
        return False
    return True


def is_docs_owner(doc_list: List[str], user: LoggedUser):
    try:
        for doc in doc_list:
            aux_doc = elastic.get(index="documents", id=doc)['_source']
            if aux_doc['createdBy'] != user.username:
                return False
    except elasticsearch.NotFoundError:
        return False
    return True
