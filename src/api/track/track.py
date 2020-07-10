from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from src.models.track.track import Track
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

@ROUTER.get("/{identifier}", response_model=Track)
async def get_track(identifier: str, current_user: User = Depends(get_current_active_user)):
    pass

@ROUTER.post("/", response_model=Track)
async def create_track(current_user: User = Depends(get_current_active_user)):
    pass

@ROUTER.patch("/{identifier}", response_model=Track)
async def update_track(identifier: str, current_user: User = Depends(get_current_active_user)):
    pass

@ROUTER.delete("/{identifier}", response_model=Track)
async def remove_track(identifier: str, current_user: User = Depends(get_current_active_user)):
    # Soft remove (no data is deleted)
    pass

@ROUTER.options("/")
async def describe_route(current_user: User = Depends(get_current_active_user)):
    pass