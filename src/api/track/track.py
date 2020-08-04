import ujson as json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from environs import Env
from src.utils.utils import validated_string_time, verify_id, verify_exists_by_id
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

# Environment Variables
env = Env()
env.read_env()
DATABASE = env.str("RDB_DB", default="LEAGUE")

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
async def get_track(
    identifier: str, current_user: User = Depends(get_current_active_user)
):
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
        and Track.parse_obj(database_obj.get("response_message")).deleted_at != None
    ):
        raise HTTPException(
            status_code=409, detail=f"Object with ID {identifier} it's deleted."
        )
    else:
        return Track.parse_obj(database_obj.get("response_message"))


@ROUTER.post("/", response_model=Track)
async def create_track(
    track: Track, current_user: User = Depends(get_current_active_user)
):
    exists = await verify_exists(track)
    if not exists:
        operation = "insert"
        data = json.loads(track.json())
        fixed_id = verify_id(track)
        if fixed_id:
            database_obj = run(operation, data)
        else:
            data.pop("id")

        payload = {"database": DATABASE, "table": TABLE, "data": data}
        database_obj = await run(operation, payload)
        if database_obj.get("status_code") != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Database couldn't create the object. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
            )
        else:
            if not fixed_id:
                track.id = database_obj.get("response_message").get("generated_keys")[
                    0
                ]
        return track
    else:
        raise HTTPException(
            status_code=403, detail=f"Object already exists on database."
        )


@ROUTER.patch("/{identifier}", response_model=Track)
async def update_track(
    body: dict, identifier: str, current_user: User = Depends(get_current_active_user)
):
    exist = await verify_exists_by_id(identifier, DATABASE, TABLE)
    if exist:
        if "record" in body.keys() and not validated_string_time(body.get("record")):
            operation = "update"
            now = str(datetime.now())
            body.update({"updated_at": now})
            payload = {
                "database": DATABASE,
                "table": TABLE,
                "identifier": identifier,
                "data": body,
            }
            database_obj = await run(operation, payload)
            if database_obj.get("status_code") != 200:
                raise HTTPException(
                    status_code=409,
                    detail=f"Database couldn't update the object with the ID {identifier}. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
                )
            else:
                return Track.parse_obj(
                    database_obj.get("response_message").get("changes")[0].get("new_val")
                )
        else:
            raise HTTPException(status_code=422, detail=f"Wrong time format for track record. Expected: HH:MM:SS.mmm")
    else:
        raise HTTPException(status_code=403, detail=f"Object not found on database.")


@ROUTER.delete("/{identifier}")
async def remove_track(
    identifier: str, current_user: User = Depends(get_current_active_user)
):
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
