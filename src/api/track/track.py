from datetime import datetime

import ujson as json
from fastapi import APIRouter, Depends, HTTPException

from src.api.user.user import get_current_active_user
from src.db.legacy import run
from src.models.track.track import Track
from src.models.user.user import User
from src.schemas.pydantic.country import (
    CreateTrack,
    TrackResponse,
    UpdateTrack,
)
from src.service.service import get_variable
from src.utils.utils import validated_string_time, verify_exists_by_id, verify_id

# GET - Read
# POST - Create
# PATCH - Update
# DELETE - Delete
# OPTIONS - Show Routes

# Router for the API
ROUTER = APIRouter()

# Environment Variables
DATABASE = get_variable("RDB_DB", str) or "LEAGUE"

# Global Variables
TABLE = "track"


async def verify_exists(track: Track):
    operation = "filter"
    data = json.loads(track.json())
    data = {"name": track.name, "deleted_at": None}
    payload = {"database": DATABASE, "table": TABLE, "filter": json.dumps(data)}
    database_obj = await run(operation, payload)
    if len(database_obj.get("response_message")) != 0:
        return True
    else:
        return False


@ROUTER.get("/{identifier}", response_model=Track)
async def get_track(identifier: str, current_user: User = Depends(get_current_active_user)):
    operation = "get"
    payload = {"database": DATABASE, "table": TABLE, "identifier": identifier}
    database_obj = await run(operation, payload)
    if database_obj.get("status_code") != 200:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't get the object with the ID {identifier}. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
        )
    elif (
        database_obj.get("status_code") == 200
        and Track.parse_obj(database_obj.get("response_message")).deleted_at is not None
    ):
        raise HTTPException(status_code=409, detail=f"Object with ID {identifier} is deleted.")
    else:
        return Track.parse_obj(database_obj.get("response_message"))


@ROUTER.post("/", response_model=TrackResponse)
async def create_track(track: CreateTrack, current_user: User = Depends(get_current_active_user)):
    exists = await verify_exists_by_id(track.country, DATABASE, "country")
    if not exists:
        raise HTTPException(status_code=404, detail="Country not found")
    operation = "insert"
    data = track.model_dump()
    fixed_id = False
    if data.get("id"):
        fixed_id = True
    else:
        data.pop("id", None)

    payload = {"database": DATABASE, "table": TABLE, "data": data}
    database_obj = await run(operation, payload)
    if database_obj.get("status_code") != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Database couldn't create the object. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
        )
    else:
        if not fixed_id:
            data.update({"id": database_obj.get("response_message").get("generated_keys")[0]})
        return TrackResponse(**data)


@ROUTER.patch("/{identifier}", response_model=TrackResponse)
async def update_track(
    body: UpdateTrack, identifier: str, current_user: User = Depends(get_current_active_user)
):
    exist = await verify_exists_by_id(identifier, DATABASE, TABLE)
    if exist:
        update_data = body.model_dump(exclude_unset=True)
        if update_data.get("record") and not validated_string_time(update_data.get("record")):
            raise HTTPException(
                status_code=422, detail="Wrong time format for track record. Expected: HH:MM:SS.mmm"
            )
        operation = "update"
        now = str(datetime.now())
        update_data.update({"updated_at": now})
        payload = {
            "database": DATABASE,
            "table": TABLE,
            "identifier": identifier,
            "data": update_data,
        }
        database_obj = await run(operation, payload)
        if database_obj.get("status_code") != 200:
            raise HTTPException(
                status_code=409,
                detail=f"Database couldn't update the object with the ID {identifier}. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
            )
        else:
            return TrackResponse(
                **database_obj.get("response_message").get("changes")[0].get("new_val")
            )
    else:
        raise HTTPException(status_code=403, detail="Object not found on database.")


@ROUTER.delete("/{identifier}")
async def remove_track(identifier: str, current_user: User = Depends(get_current_active_user)):
    operation = "update"
    now = str(datetime.now())
    data = {}
    data.update({"updated_at": now})
    data.update({"deleted_at": now})
    payload = {
        "database": DATABASE,
        "table": TABLE,
        "identifier": identifier,
        "data": data,
    }
    database_obj = await run(operation, payload)
    if database_obj.get("status_code") != 200:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't delete the object with the ID {identifier}. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
        )
    else:
        return {"detail": f"{identifier} deleted"}


@ROUTER.options("/")
async def describe_route(current_user: User = Depends(get_current_active_user)):
    return {
        "GET": "/v1/track/{identifier}",
        "DELETE": "/v1/track/{identifier}",
        "PATCH": "/v1/track/{identifier}",
        "POST": "/v1/track/",
    }
