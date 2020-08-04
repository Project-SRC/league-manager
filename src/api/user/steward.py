import ujson as json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from environs import Env
from src.utils.utils import verify_id, verify_exists_by_id
from src.models.user.steward import Steward
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
TABLE = "steward"


@ROUTER.get("/{user}/steward/{identifier}", response_model=Steward)
async def get_steward(
    user: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    pass


@ROUTER.post("/{user}/steward/", response_model=Steward)
async def create_steward(
    steward: Steward, user: str, current_user: User = Depends(get_current_active_user)
):
    pass


@ROUTER.patch("/{user}/steward/{identifier}", response_model=Steward)
async def update_steward(
    body: dict,
    user: str,
    identifier: str,
    current_user: User = Depends(get_current_active_user),
):
    pass


@ROUTER.delete("/{user}/steward/{identifier}")
async def remove_steward(
    user: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    pass


@ROUTER.options("/steward")
async def describe_route(current_user: User = Depends(get_current_active_user)):
    return {
        "GET": "/v1/user/{user}/steward/{identifier}",
        "DELETE": "/v1/user/{user}/steward/{identifier}",
        "PATCH": "/v1/user/{user}/steward/{identifier}",
        "POST": "/v1/user/steward",
    }
