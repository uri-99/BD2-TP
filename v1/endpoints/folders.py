import datetime

from bson.errors import InvalidId

from core.auth.models import LoggedUser
from core.auth.utils import get_current_user, user_has_permission, verify_logged_in
from core.helpers.converters import get_parsed_folder
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
                title: Union[str, None] = None, author: Union[str, None] = None):
    if page < 1:
        raise HTTPException(status_code=400, detail='Page number must be a positive integer')

    folder_filter = {}
    if title is not None:
        folder_filter["title"] = title
    if author is not None:
        try:
            folder_filter["author"] = ObjectId(author)
        except bson.errors.InvalidId:
            return []
    result = folders_db.find(folder_filter, {"editors": 0}).skip((page - 1) * folders_page_size).limit(folders_page_size)
    folder_count = folders_db.count_documents({})
    folders = list()
    for folder in result:
        folders.append(Folder(
            self=str(request.url.remove_query_params(["title", "author", "page"])) + "/" + str(folder['_id']),
            id=str(folder['_id']),
            createdBy=str(folder['createdBy']),
            lastEditedBy=str(folder['lastEditedBy']),
            createdOn=str(folder['createdOn']),
            lastEdited=str(folder['lastEdited']),
            title=folder['title'],
            description=folder['description'],
            content=folder['content'],
            writers=folder['writers'],
            readers=folder['readers'],
            allCanWrite=folder['allCanWrite'],
            allCanRead=folder['allCanWrite'],
        ))
    response.headers.append("first", str(request.url.remove_query_params(["page"])) + "?page=1")
    response.headers.append("last", str(request.url.remove_query_params(["page"]))
                            + "?page=" + str(int((folder_count - 1) / folders_page_size) + 1))
    return json.loads(json_util.dumps(folders))


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
    if are_writers and users_exist(doc.writers) is False:
        raise HTTPException(status_code=400, detail='Writer sent does not exist')
    if are_readers and users_exist(doc.readers) is False:
        raise HTTPException(status_code=400, detail='Reader sent does not exist')
    if are_docs and docs_exist(doc.content) is False:
        raise HTTPException(status_code=400, detail='Document to include on folder does not exist')
    now = datetime.datetime.now()
    result = folders_db.insert_one({
        'createdBy': current_user.id,
        'lastEditedBy': current_user.id,
        'createdOn': now,
        'lastEdited': now,
        'title': doc.title,
        'description': doc.description,
        'content': doc.content,
        'writers': doc.writers if are_writers else [],
        'allCanWrite': doc.allCanWrite if doc.allCanWrite is not None else False,
        'readers': doc.readers if are_readers else [],
        'allCanRead': doc.allCanRead if doc.allCanRead is not None else False
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
def get_folder(id: str, request: Request):
    try:
        folder = folders_db.find_one({'_id': ObjectId(id)}, {'public': 0})
    except InvalidId:
        raise HTTPException(status_code=404, detail='Folder not found')
    if folder is None:
        raise HTTPException(status_code=404, detail='Folder not found')
    return Folder(
        self=str(request.url),
        id=str(folder['_id']),
        createdBy=str(folder['createdBy']),
        lastEditedBy=str(folder['lastEditedBy']),
        createdOn=str(folder['createdOn']),
        lastEdited=str(folder['lastEdited']),
        title=folder['title'],
        description=folder['description'],
        content=oidlist_to_str(folder['content']),
        editors=oidlist_to_str(folder['editors'])
    )


@router.put(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Modified Folder'},
        403: {'description': 'User has no permission for attempted action'},
        404: {'description': 'Folder not found'}
    }
)
def modify_folder(id: str, folder: UpdateFolder, request: Request,
                  current_user: LoggedUser = Depends(get_current_user)):
    folder = get_parsed_folder(id, folders_db, None if current_user is None else current_user.id)
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")
    if user_has_permission(folder, current_user, request.method.title()) is False:
        raise HTTPException(status_code=403, detail="User has no permission to modify this folder")
    print("Modifico carpeta...")
    # TODO: Chequeo de que el current user tenga permisos
    return {}


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Deleted document'},
        404: {'description': 'Document not found'}
    }
)
def delete_folder(id: str, current_user: LoggedUser = Depends(get_current_user)):
    # TODO: Chequeo de que el current user tenga permisos

    return {}


# TODO: Check for more optimized way of doing it (one request for all)
def users_exist(user_list: List[str]):
    try:
        for user in user_list:
            if users_db.find_one({'_id': ObjectId(user)}) is None:
                return False
    except InvalidId:
        return False


def docs_exist(doc_list: List[str]):
    return True