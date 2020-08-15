import ujson as json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from environs import Env
from src.utils.utils import verify_id, verify_exists_by_id
from src.models.race.race import Race
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
TABLE = "race"


async def verify_exists(race: Race):
    # TODO: Define a better way to search for an existing race
    operation = "filter"
    data = json.loads(race.json())
    data = {"track": str(race.track), "date": str(race.date), "deleted_at": None}
    payload = {"database": DATABASE, "table": TABLE, "filter": json.dumps(data)}
    database_obj = await run(operation, payload)
    if len(database_obj.get("response_message")) != 0:
        return True
    else:
        return False


@ROUTER.get("/{identifier}", response_model=Race)
async def get_race(
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
        and Race.parse_obj(database_obj.get("response_message")).deleted_at != None
    ):
        raise HTTPException(
            status_code=409, detail=f"Object with ID {identifier} is deleted."
        )
    else:
        return Race.parse_obj(database_obj.get("response_message"))


@ROUTER.post("/", response_model=Race)
async def create_race(
    race: Race, current_user: User = Depends(get_current_active_user)
):
    exists = await verify_exists(race)
    if not exists:
        operation = "insert"
        data = json.loads(race.json())
        fixed_id = verify_id(race)
        if fixed_id:
            database_obj = await run(operation, data)
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
                data.update(
                    {
                        "id": database_obj.get("response_message").get(
                            "generated_keys"
                        )[0]
                    }
                )
            return Race.parse_obj(data)
    else:
        raise HTTPException(
            status_code=403, detail=f"Object already exists on database."
        )


@ROUTER.patch("/{identifier}", response_model=Race)
async def update_race(
    body: dict, identifier: str, current_user: User = Depends(get_current_active_user)
):
    exist = await verify_exists_by_id(identifier, DATABASE, TABLE)
    if exist:
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
            return Race.parse_obj(
                database_obj.get("response_message").get("changes")[0].get("new_val")
            )
    else:
        raise HTTPException(status_code=403, detail=f"Object not found on database.")


@ROUTER.delete("/{identifier}")
async def remove_race(
    identifier: str, current_user: User = Depends(get_current_active_user)
):
    # Soft remove (no data is deleted)
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
        "GET": "/v1/race/{identifier}",
        "DELETE": "/v1/race/{identifier}",
        "PATCH": "/v1/race/{identifier}",
        "POST": "/v1/race/",
    }
