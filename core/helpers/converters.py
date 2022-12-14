from typing import List
from bson import ObjectId
from bson.errors import InvalidId


def oidlist_to_str(oidlist: List[ObjectId]):
    list_str = list()
    for item in oidlist:
        list_str.append(str(item))
    return list_str


def strlist_to_oidlist(str_list: List[str]):
    oid_list = list()
    for item in str_list:
        oid_list.append(ObjectId(item))
    return oid_list


def get_parsed_folder(folder_id: str, folder_db, user_username: str):
    try:
        if user_username is None:
            return_folder = folder_db.find_one(
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
                    'title': 1,
                    'description': 1,
                    'content': 1,
                    'allCanRead': 1,
                    'allCanWrite': 1
                }
            )
            return_folder['writers'] = []
            return_folder['readers'] = []
            return return_folder

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
                    'writers': 1,
                    'title': 1,
                    'description': 1,
                    'content': 1,
                    'readers': 1,
                    'allCanRead': 1,
                    'allCanWrite': 1,
                }
            }
        ]))[0]
        if user_username != folder["createdBy"]:
            folder["writers"] = [user_username] if user_username in folder["writers"] else []
            folder["readers"] = [user_username] if user_username in folder["readers"] else []

        folder['id'] = str(folder['id'])
        return folder
    except InvalidId:
        return None
