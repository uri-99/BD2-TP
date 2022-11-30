from fastapi import APIRouter, Depends, HTTPException, status
from core.schemas.schema import *
from typing import Union
import binascii
import os
