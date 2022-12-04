import datetime

from bson.errors import InvalidId

from core.auth.models import LoggedUser
from core.auth.utils import get_current_user
from . import *

router = APIRouter(
    prefix="/folders",
    tags=["folders"],
    responses={404: {"description": "Folder not found"}}
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

    folder_filter = {'public': 'false'}
    if title is not None:
        folder_filter["title"] = title
    if author is not None:
        try:
            folder_filter["author"] = ObjectId(author)
        except bson.errors.InvalidId:
            return []
    result = folders_db.find(folder_filter, {"public": 0}).skip((page - 1) * folders_page_size).limit(folders_page_size)
    folder_count = folders_db.count_documents({})
    folders = list()
    for folder in result:
        folders.append({
            'self': str(request.url.remove_query_params(["title", "author"])) + "/" + str(folder['_id']),
            'id': str(folder['_id']),
            'createdBy': str(folder['createdBy']),
            'lastEditedBy': str(folder['lastEditedBy']),
            'createdOn': str(folder['createdOn']),
            'lastEdited': str(folder['lastEdited']),
            'title': folder['title'],
            'description': folder['description'],
            'content': oidlist_to_str(folder['content']),
            'editors': oidlist_to_str(folder['editors'])
        })
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
    now = datetime.datetime.now()
    result = folders_db.insert_one({
        'createdBy': current_user.id,
        'createdOn': now,
        'lastEditedBy': current_user.id,
        'lastEdited': now,
        'editors': [
            current_user.id
        ],
        'title': doc.title,
        'description': doc.description,
        'content': doc.content,
        'public': doc.public if doc.public is not None else 'true'
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
        204: {'description': 'Modified document'},
        404: {'description': 'Document not found'}
    }
)
def modify_folder(id: str, current_user: LoggedUser = Depends(get_current_user)):
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
