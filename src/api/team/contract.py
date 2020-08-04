import ujson as json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from environs import Env
from src.utils.utils import verify_id, verify_exists_by_id
from src.models.team.contract import Contract
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
TABLE = "contract"

@ROUTER.get("/{team}/contract/{identifier}", response_model=Contract)
async def get_contract(team: str, identifier: str, current_user: User = Depends(get_current_active_user)):
    pass

@ROUTER.post("/{team}/contract/", response_model=Contract)
async def create_contract(contract: Contract, team: str, current_user: User = Depends(get_current_active_user)):
    pass

@ROUTER.patch("/{team}/contract/{identifier}", response_model=Contract)
async def update_contract(body: dict, team: str, identifier: str, current_user: User = Depends(get_current_active_user)):
    pass

@ROUTER.delete("/{team}/contract/{identifier}")
async def remove_contract(team: str, identifier: str, current_user: User = Depends(get_current_active_user)):
    pass

@ROUTER.options("/contract")
async def describe_route(current_user: User = Depends(get_current_active_user)):
    return {
        "GET": "/v1/team/{team}/contract/{identifier}",
        "DELETE": "/v1/team/{team}/contract/{identifier}",
        "PATCH": "/v1/team/{team}/contract/{identifier}",
        "POST": "/v1/team/contract",
    }