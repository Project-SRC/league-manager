import ujson as json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from environs import Env
from src.utils.utils import verify_id, verify_exists_by_id
from src.models.race.participation import Participation
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
TABLE = "participation"


@ROUTER.get("/{race}/participation/{identifier}", response_model=Participation)
async def get_participation(
    race: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    pass


@ROUTER.post("/{race}/participation", response_model=Participation)
async def create_participation(
    participation: Participation,
    race: str,
    current_user: User = Depends(get_current_active_user),
):
    pass


@ROUTER.patch("/{race}/participation/{identifier}", response_model=Participation)
async def update_participation(
    body: dict,
    race: str,
    identifier: str,
    current_user: User = Depends(get_current_active_user),
):
    pass


@ROUTER.delete("/{race}/participation/{identifier}")
async def remove_participation(
    race: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    pass


@ROUTER.options("/participation")
async def describe_route(current_user: User = Depends(get_current_active_user)):
    return {
        "GET": "/v1/race/{race}/participation/{identifier}",
        "DELETE": "/v1/race/{race}/participation/{identifier}",
        "PATCH": "/v1/race/{race}/participation/{identifier}",
        "POST": "/v1/race/participation",
    }
