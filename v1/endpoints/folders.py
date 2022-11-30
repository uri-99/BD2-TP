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

users = {
    '6373e8c9ea6af1dc84089d97': {
        'id': '6373e8c9ea6af1dc84089d97',
        'username': "user1",
        'mail': "user1@gmail.com",
        'notes': [
            "6373eee1d9c1f8cd2703e2f0"
        ],
        'favourites': [

        ]
    },
    '6373e902a5e607af97b4b1fb': {
        'id': '6373e902a5e607af97b4b1fb',
        'username': "user2",
        'mail': "user2@gmail.com",
        'notes': [
            '6373f2bf27a4e3b55da2cc3c'
        ],
        'favourites': [
            '6373eee1d9c1f8cd2703e2f0'
        ]
    }
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
    response_model=List[Folder],
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found documents list'},
        400: {'description': 'Sent wrong query param'}
    }
)
def get_folders(limit: int = 10, page: int = 1, title: Union[str, None] = None, author: Union[str, None] = None):
    if limit < 0:
        raise HTTPException(status_code=400, detail='Page size must be higher than zero')
    if page < 1:
        raise HTTPException(status_code=400, detail='Page number must be a positive integer')
    # vvv Dummy code vvv
    doc_list = list(documents.values())
    if title is not None:
        doc_list = list(filter(lambda doc: doc['title'] == title, doc_list))
    if author is not None:
        doc_list = list(filter(lambda doc: doc['owner'] == author, doc_list))
    return doc_list[(page - 1) * limit: page * limit]


@router.post(
    "",
    response_model=Folder,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {'description': 'Document successfully created'}
    }
)
def create_folder(doc: NewDocument):
    if doc.createdBy not in users:
        raise HTTPException(status_code=400, detail='Creator user sent does not exist')
    new_doc_id = binascii.b2a_hex(os.urandom(12)).decode('utf-8')
    documents[new_doc_id] = {
        '_id': new_doc_id,
        'createdBy': doc.createdBy,
        'created': 'ISODate("2022-11-15T19:51:36Z")',
        'lastEditedBy': '',
        'lastEdited': '',
        'editors': [
            doc.createdBy
        ],
        'title': doc.title,
        'description': doc.description,
        'content': doc.content,
        'public': doc.public
    }
    return documents[new_doc_id]


@router.get(
    "/{id}",
    response_model=Folder,
    status_code=status.HTTP_200_OK,
    responses={
        200: {'description': 'Found document'},
        404: {'description': 'Document not found for id sent'},
    }
)
def get_folder(id: int):
    if id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    return documents[id]


@router.put(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Modified document'},
        404: {'description': 'Document not found'}
    }
)
def modify_folder(id: int):
    return {"Hello": "World"}


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {'description': 'Deleted document'},
        404: {'description': 'Document not found'}
    }
)
def delete_folder(id: int):
    return {"Hello": "World"}
