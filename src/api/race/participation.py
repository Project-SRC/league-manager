import ujson as json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from environs import Env
from src.utils.utils import verify_id, verify_exists_by_id
from src.models.race.participation import Participation
from src.models.user.user import User
from src.api.user.user import get_current_active_user
from src.db.db import run

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
RACE_TABLE = "race"
DRIVER_TABLE = "driver"


async def verify_exists(participation: Participation):
    operation = "filter"
    data = {"driver": str(participation.driver), "deleted_at": None}
    payload = {"database": DATABASE, "table": TABLE, "filter": json.dumps(data)}
    database_obj = await run(operation, payload)
    if len(database_obj.get("response_message")) != 0:
        return True
    else:
        return False


@ROUTER.get("/{race}/participation/{identifier}", response_model=Participation)
async def get_participation(
    race: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    operation = "filter"
    payload = {
        "database": DATABASE,
        "table": TABLE,
        "filter": {"id": identifier, "race": race},
    }
    database_obj = await run(operation, payload)
    if database_obj.get("status_code") != 200:
        raise HTTPException(
            status_code=404,
            detail=f"Database couldn't get the object with the ID {identifier}. Check the database connection and parameters. Traceback: {database_obj.get('response_message')}",
        )
    elif (
        database_obj.get("status_code") == 200
        and Participation.parse_obj(database_obj.get("response_message")).deleted_at
        is not None
    ):
        raise HTTPException(
            status_code=409, detail=f"Object with ID {identifier} is deleted."
        )
    else:
        return Participation.parse_obj(database_obj.get("response_message"))


@ROUTER.post("/{race}/participation", response_model=Participation)
async def create_participation(
    participation: Participation,
    race: str,
    current_user: User = Depends(get_current_active_user),
):
    race_exist = await verify_exists_by_id(race, DATABASE, RACE_TABLE)
    if not race_exist:
        raise HTTPException(
            status_code=404, detail=f"The Race with ID {race} doesn't exist"
        )

    driver_exist = await verify_exists_by_id(
        str(participation.driver), DATABASE, DRIVER_TABLE
    )
    if not driver_exist:
        raise HTTPException(
            status_code=404,
            detail=f"The Driver with ID {participation.driver} doesn't exist",
        )
    exists = await verify_exists(participation)
    if not exists:
        operation = "insert"
        data = json.loads(participation.json())
        fixed_id = verify_id(participation)
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
            return Participation.parse_obj(data)
    else:
        raise HTTPException(
            status_code=403, detail=f"Participation already exists for the race."
        )


@ROUTER.patch("/{race}/participation/{identifier}", response_model=Participation)
async def update_participation(
    body: dict,
    race: str,
    identifier: str,
    current_user: User = Depends(get_current_active_user),
):
    # TODO: Verify if the race is the correct one for the participation
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
            return Participation.parse_obj(
                database_obj.get("response_message").get("changes")[0].get("new_val")
            )
    else:
        raise HTTPException(status_code=403, detail=f"Object not found on database.")


@ROUTER.delete("/{race}/participation/{identifier}")
async def remove_participation(
    race: str, identifier: str, current_user: User = Depends(get_current_active_user)
):
    operation = "update"
    now = str(datetime.now())
    data = {}
    data.update({"updated_at": now})
    data.update({"terminated_at": now})
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


@ROUTER.options("/participation")
async def describe_route(current_user: User = Depends(get_current_active_user)):
    return {
        "GET": "/v1/race/{race}/participation/{identifier}",
        "DELETE": "/v1/race/{race}/participation/{identifier}",
        "PATCH": "/v1/race/{race}/participation/{identifier}",
        "POST": "/v1/race/participation",
    }
