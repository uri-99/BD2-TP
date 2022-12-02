from typing import List
from bson import ObjectId


def oidlist_to_str(oidlist: List[ObjectId]):
    list_str = list()
    for item in oidlist:
        list_str.append(str(item))
    return list_str
