from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
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

@ROUTER.get("/{identifier}", response_model=Manager)
async def get_manager(identifier: str, current_user: User = Depends(get_current_active_user)):
    pass

@ROUTER.post("/", response_model=Manager)
async def create_manager(current_user: User = Depends(get_current_active_user)):
    pass

@ROUTER.patch("/{identifier}", response_model=Manager)
async def update_manager(identifier: str, current_user: User = Depends(get_current_active_user)):
    pass

@ROUTER.delete("/{identifier}", response_model=Manager)
async def remove_manager(identifier: str, current_user: User = Depends(get_current_active_user)):
    # Soft remove (no data is deleted)
    pass

@ROUTER.options("/")
async def describe_route(current_user: User = Depends(get_current_active_user)):
    pass