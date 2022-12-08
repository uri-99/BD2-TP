from typing import List
from bson import ObjectId
from bson.errors import InvalidId


def oidlist_to_str(oidlist: List[ObjectId]):
    list_str = list()
    for item in oidlist:
        list_str.append(str(item))
    return list_str


def get_parsed_folder(folder_id: str, folder_db, user_id: str):
    try:
        if user_id is None:
            return folder_db.find_one(
                {
                    '_id': ObjectId(folder_id)
                },
                {
                    '_id': 0,
                    'id': '$_id',
                    'createdBy': 1,
                    'createdOn': 1,
                    'lastEditedBy': 1,
                    'lastEdited': 1,
                    'writers': 1,
                    'title': 1,
                    'description': 1,
                    'content': 1,
                    'readers': 1,
                    'allCanRead': 1,
                    'allCanWrite': 1
                }
            )
        writers_filter = {
            '$filter': {
                'input': '$writers',
                'as': 'writers',
                'cond': {
                    '$eq': [user_id, '$$writers']
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
                    'writers': writers_filter,
                    'title': 1,
                    'description': 1,
                    'content': 1,
                    'readers': readers_filter
                }
            }
        ]))[0]
        folder['id'] = str(folder['id'])
        return folder
    except InvalidId:
        return None
