from typing import List
from bson import ObjectId


def oidlist_to_str(oidlist: List[ObjectId]):
    list_str = list()
    for item in oidlist:
        list_str.append(str(item))
    return list_str


def get_parsed_folder(folder_id: str, folder_db, user_id: str):
    if user_id is None:
        return folder_db.find_one(
            {
                '_id': ObjectId(folder_id)
            },
            {
                '_id': 0,
                'id': '$_id',
                'editors': 0,
                'readers': 0
            }
        )
    editors_filter = {
        '$filter': {
            'input': '$editors',
            'as': 'editor',
            'cond': {
                '$eq': [user_id, '$$editor']
            }
        }
    }
    readers_filter = {
        '$filter': {
            'input': '$readers',
            'as': 'reader',
            'cond': {
                '$or': [{
                    '$eq': [user_id, '$$reader']
                }]
            }
        }
    }
    folder = list(folder_db.aggregate([
        {
            '$match': {
                '_id': ObjectId(folder_id)
            }
        },
        {
            '$project': {
                '_id': 0,
                'id': '$_id',
                'createdBy': 1,
                'createdOn': 1,
                'lastEditedBy': 1,
                'lastEdited': 1,
                'editors': editors_filter,
                'title': 1,
                'description': 1,
                'content': 1,
                'readers': readers_filter
            }
        }
    ]))[0]
    folder['id'] = str(folder['id'])
    return folder
