import ujson as json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from environs import Env
from src.utils.utils import verify_id, verify_exists_by_id
from src.models.user.driver import Driver
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
TABLE = "driver"


@ROUTER.get("/{user}/driver/{identifier}", response_model=Driver)
async def get_driver(
    user: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    pass


@ROUTER.post("/{user}/driver/", response_model=Driver)
async def create_driver(
    driver: Driver, user: str, current_user: User = Depends(get_current_active_user)
):
    pass


@ROUTER.patch("/{user}/driver/{identifier}", response_model=Driver)
async def update_driver(
    body: dict,
    user: str,
    identifier: str,
    current_user: User = Depends(get_current_active_user),
):
    pass


@ROUTER.delete("/{user}/driver/{identifier}")
async def remove_driver(
    user: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    pass


@ROUTER.options("/driver")
async def describe_route(current_user: User = Depends(get_current_active_user)):
    return {
        "GET": "/v1/user/{user}/driver/{identifier}",
        "DELETE": "/v1/user/{user}/driver/{identifier}",
        "PATCH": "/v1/user/{user}/driver/{identifier}",
        "POST": "/v1/user/driver",
    }
