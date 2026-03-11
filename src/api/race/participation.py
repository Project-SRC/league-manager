from datetime import datetime

import ujson as json
from fastapi import APIRouter, Depends, HTTPException

from src.api.user.user import get_current_active_user
from src.db.legacy import run
from src.models.race.participation import Participation
from src.models.user.user import User
from src.schemas.pydantic.participation import (
    CreateParticipation,
    ParticipationResponse,
    UpdateParticipation,
)
from src.service.service import get_variable
from src.utils.utils import verify_exists_by_id, verify_id

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
        and Participation.parse_obj(database_obj.get("response_message")).deleted_at is not None
    ):
        raise HTTPException(status_code=409, detail=f"Object with ID {identifier} is deleted.")
    else:
        return Participation.parse_obj(database_obj.get("response_message"))


@ROUTER.post("/{race}/participation", response_model=ParticipationResponse)
async def create_participation(
    participation: CreateParticipation,
    race: str,
    current_user: User = Depends(get_current_active_user),
):
    race_exist = await verify_exists_by_id(race, DATABASE, RACE_TABLE)
    if not race_exist:
        raise HTTPException(status_code=404, detail=f"The Race with ID {race} doesn't exist")

    driver_exist = await verify_exists_by_id(str(participation.driver_id), DATABASE, DRIVER_TABLE)
    if not driver_exist:
        raise HTTPException(
            status_code=404,
            detail=f"The Driver with ID {participation.driver_id} doesn't exist",
        )
    operation = "insert"
    data = participation.model_dump()
    data["race_id"] = data.pop("race_id", race)
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
        return ParticipationResponse(**data)


@ROUTER.patch("/{race}/participation/{identifier}", response_model=ParticipationResponse)
async def update_participation(
    body: UpdateParticipation,
    race: str,
    identifier: str,
    current_user: User = Depends(get_current_active_user),
):
    exist = await verify_exists_by_id(identifier, DATABASE, TABLE)
    if exist:
        operation = "update"
        now = str(datetime.now())
        update_data = body.model_dump(exclude_unset=True)
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
            return ParticipationResponse(
                **database_obj.get("response_message").get("changes")[0].get("new_val")
            )
    else:
        raise HTTPException(status_code=403, detail="Object not found on database.")


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
