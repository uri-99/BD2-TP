import json
from typing import List, Union

import bson
from bson import json_util, ObjectId
from fastapi import APIRouter, status, Request, Response, HTTPException, Depends

from core.auth.models import SingletonPasswordBearer
from core.helpers.converters import oidlist_to_str
from core.helpers.db_client import MongoManager
from core.schemas.schema import *
