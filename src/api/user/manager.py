import ujson as json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from environs import Env
from src.utils.utils import verify_id, verify_exists_by_id
from src.models.user.manager import Manager
from src.models.user.user import User
from src.api.user.user import get_current_active_user
from src.db.db import run
from uuid import uuid4 as uuid

# GET - Read
# POST - Create
# PATCH - Update
# DELETE - Delete
# OPTIONS - Show Routes

# Router for the API
ROUTER = APIRouter()

# Environment Variables
env = Env()
env.read_env()
DATABASE = env.str("RDB_DB", default="LEAGUE")

# Global Variables
TABLE = "manager"


@ROUTER.get("/{user}/manager/{identifier}", response_model=Manager)
async def get_manager(
    user: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    pass


@ROUTER.post("/{user}/manager/", response_model=Manager)
async def create_manager(
    manager: Manager, user: str, current_user: User = Depends(get_current_active_user)
):
    pass


@ROUTER.patch("/{user}/manager/{identifier}", response_model=Manager)
async def update_manager(
    body: dict,
    user: str,
    identifier: str,
    current_user: User = Depends(get_current_active_user),
):
    pass


@ROUTER.delete("/{user}/manager/{identifier}")
async def remove_manager(
    user: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    pass


@ROUTER.options("/manager")
async def describe_route(current_user: User = Depends(get_current_active_user)):
    return {
        "GET": "/v1/user/{user}/manager/{identifier}",
        "DELETE": "/v1/user/{user}/manager/{identifier}",
        "PATCH": "/v1/user/{user}/manager/{identifier}",
        "POST": "/v1/user/manager",
    }
